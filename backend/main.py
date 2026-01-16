from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import uuid
import traceback
from dotenv import load_dotenv

from pdf_extractor import extract_text_from_pdf
from text_chunker import chunk_text
from embeddings import create_embeddings, create_embedding
from simple_vector_store import store_document, search_document
from openai_client import generate_answer
from schemas import UploadResponse, ChatRequest, ChatResponse, ErrorResponse

# Load environment variables
load_dotenv()

# Validate required environment variables at startup
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is required in .env file")

app = FastAPI(title="Document Q&A Engine API")

# CORS middleware for localhost dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Document Q&A Engine API - RAG System"}


@app.post("/api/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload a PDF file for ingestion and indexing."""
    try:
        # Validate file type
        if file.content_type != "application/pdf":
            return JSONResponse(
                status_code=400,
                content=ErrorResponse(
                    error="File must be a PDF",
                    provider="Server",
                    status=400
                ).dict()
            )

        # Validate file size (50MB default)
        MAX_SIZE = 50 * 1024 * 1024  # 50MB
        contents = await file.read()
        file_size_mb = len(contents) / (1024 * 1024)
        
        if len(contents) > MAX_SIZE:
            return JSONResponse(
                status_code=400,
                content=ErrorResponse(
                    error=f"File size exceeds limit of {MAX_SIZE / 1024 / 1024}MB",
                    provider="Server",
                    status=400
                ).dict()
            )

        filename = file.filename or "document.pdf"
        
        print(f"[Upload] Processing PDF: {filename} ({file_size_mb:.2f}MB)")
        
        # Step 1: Extract text from PDF
        print("[Upload] Step 1: Extracting text from PDF...")
        try:
            text, page_count = extract_text_from_pdf(contents)
            print(f"[Upload] Extracted {len(text)} characters from {page_count} pages")
        except Exception as e:
            raise Exception(f"PDF extraction failed: {str(e)}")
        
        # Step 2: Chunk text
        print("[Upload] Step 2: Chunking text...")
        try:
            chunks = chunk_text(text)
            print(f"[Upload] Created {len(chunks)} chunks")
        except Exception as e:
            raise Exception(f"Text chunking failed: {str(e)}")
        
        if len(chunks) == 0:
            raise Exception("No chunks created from PDF. PDF may be empty or unreadable.")
        
        # Step 3: Create embeddings
        print("[Upload] Step 3: Creating embeddings...")
        try:
            # Ensure chunks have "text" field
            chunk_texts = []
            for chunk in chunks:
                if "text" not in chunk:
                    raise ValueError(f"Chunk missing 'text' field: {chunk}")
                chunk_texts.append(chunk["text"])
            
            embeddings = await create_embeddings(chunk_texts)
            print(f"[Upload] Created {len(embeddings)} embeddings")
        except Exception as e:
            raise Exception(f"Embedding creation failed: {str(e)}")
        
        # Step 4: Store in vector database
        print("[Upload] Step 4: Storing in vector database...")
        try:
            doc_id = str(uuid.uuid4())
            chunk_count = await store_document(doc_id, chunks, embeddings)
            print(f"[Upload] Stored {chunk_count} chunks for document {doc_id}")
        except Exception as e:
            raise Exception(f"Vector storage failed: {str(e)}")
        
        return UploadResponse(
            doc_id=doc_id,
            chunk_count=chunk_count,
            status="ready"
        )
        
    except Exception as e:
        error_details = traceback.format_exc()
        error_message = str(e)
        print("=" * 50)
        print("UPLOAD ERROR:")
        print(error_details)
        print("=" * 50)
        
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="Upload and indexing failed",
                provider="Server",
                status=500,
                details=error_message
            ).dict()
        )


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Ask a question about the document."""
    try:
        question = request.question
        doc_id = request.doc_id

        if not question or not doc_id:
            return JSONResponse(
                status_code=400,
                content=ErrorResponse(
                    error="question and doc_id are required",
                    provider="Server",
                    status=400
                ).dict()
            )

        print(f"[Chat] Question: {question[:100]}...")
        print(f"[Chat] Document ID: {doc_id}")
        
        # Step 1: Create embedding for the question
        print("[Chat] Step 1: Creating query embedding...")
        try:
            query_embedding = await create_embedding(question)
        except Exception as e:
            raise Exception(f"Query embedding failed: {str(e)}")
        
        # Step 2: Search for similar chunks
        print("[Chat] Step 2: Searching vector database...")
        try:
            top_k = 5
            search_results = await search_document(doc_id, query_embedding, top_k=top_k)
            print(f"[Chat] Found {len(search_results)} relevant chunks")
        except Exception as e:
            raise Exception(f"Vector search failed: {str(e)}")

        if len(search_results) == 0:
            return ChatResponse(
                answer="I couldn't find any relevant information in the document to answer your question.",
                sources=[],
            )

        # Step 3: Build context from retrieved chunks
        sources = []
        context_parts = []
        
        for result in search_results:
            sources.append({
                "text": result["text"],
                "chunk_index": result.get("chunk_index"),
                "score": result.get("score")
            })
            context_parts.append(result["text"])
        
        context_text = "\n\n---\n\n".join(context_parts)
        
        # Trim context if too long (to avoid OpenAI token overflow)
        MAX_CONTEXT_LENGTH = 10000  # ~2500 tokens
        if len(context_text) > MAX_CONTEXT_LENGTH:
            context_text = context_text[:MAX_CONTEXT_LENGTH] + "... [truncated]"
            sources = sources[:top_k]

        # Step 4: Generate answer using OpenAI
        print("[Chat] Step 3: Generating answer with OpenAI...")
        try:
            answer = await generate_answer(question, sources, context_text)
        except Exception as e:
            raise Exception(f"Answer generation failed: {str(e)}")

        return ChatResponse(answer=answer, sources=sources)

    except Exception as e:
        error_message = str(e)
        error_details = traceback.format_exc()
        print("=" * 50)
        print("CHAT ERROR:")
        print(error_details)
        print("=" * 50)
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="Chat request failed",
                provider="OpenAI" if "OpenAI" in error_message else "Server",
                status=500,
                details=error_message
            ).dict()
        )


if __name__ == "__main__":
    import uvicorn

    PORT = int(os.getenv("PORT", "3001"))
    uvicorn.run(app, host="0.0.0.0", port=PORT)
