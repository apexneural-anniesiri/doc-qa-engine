# Document Q&A Engine - RAG System

A modern full-stack Document Q&A Engine using **RAG (Retrieval-Augmented Generation)** that lets you upload PDFs and ask questions about their content.

## ✨ Features

- **PDF Upload & Processing**: Extract text from PDFs of any size using PyPDF2
- **Intelligent Chunking**: Split documents into overlapping chunks for better context
- **Semantic Search**: Find relevant sections using OpenAI embeddings
- **Simple Vector Store**: File-based storage (no external database needed)
- **Grounded Answers**: GPT-4o generates answers strictly from document content
- **Source Citations**: See which parts of the document were used
- **Zero External Dependencies**: No Docker, no database setup required

## 🏗️ Architecture

- **Backend**: Python + FastAPI + Uvicorn
- **Frontend**: React + Vite + TypeScript + Tailwind CSS
- **Vector Store**: Simple file-based vector store (numpy-based, no external database)
- **LLM**: OpenAI (embeddings + chat completion)

## 📁 Project Structure

```
doc QA/
├── backend/                    # Python FastAPI server
│   ├── main.py                # Main server & API endpoints
│   ├── pdf_extractor.py       # PDF text extraction (PyPDF2)
│   ├── text_chunker.py        # Text chunking with overlap
│   ├── embeddings.py           # OpenAI embeddings
│   ├── simple_vector_store.py # File-based vector storage (numpy)
│   ├── openai_client.py       # OpenAI chat completion (GPT-4o)
│   ├── schemas.py             # Pydantic models
│   ├── requirements.txt       # Python dependencies
│   ├── .env                   # Environment variables
│   └── vector_storage/        # Local storage directory (auto-created)
├── frontend/                  # React + Vite app
│   ├── src/
│   │   ├── App.tsx            # Main app component
│   │   ├── api.ts             # API client functions
│   │   ├── components/
│   │   │   ├── UploadArea.tsx # File upload UI
│   │   │   ├── Chat.tsx       # Chat interface
│   │   │   └── MessageBubble.tsx # Message display
│   │   └── index.css          # Tailwind CSS styles
│   └── package.json
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** (Python 3.11+ recommended for best compatibility)
- **Node.js 18+** or **Bun**
- **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com)
- **No external databases or Docker required!**

### 1. No External Database Needed!

The vector store uses a simple file-based system with numpy. No Docker or external services required!

### 2. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

**`.env` file:**
```env
OPENAI_API_KEY=your_openai_api_key_here
PORT=3001
VECTOR_STORAGE_DIR=./vector_storage  # Local storage for embeddings (optional, defaults to ./vector_storage)
```

**Start backend:**
```bash
uvicorn main:app --reload --port 3001
```

### 3. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install
# or
bun install

# Start dev server
npm run dev
# or
bun run dev
```

Frontend will run on `http://localhost:5173`

## 📖 How It Works

### 1. Document Upload & Indexing

1. User uploads a PDF via drag-and-drop or file picker
2. **PDF Extraction**: Server extracts text using `PyPDF2`
3. **Chunking**: Text is split into chunks (~1000 tokens) with overlap (~150 tokens)
4. **Embeddings**: OpenAI creates embeddings for each chunk using `text-embedding-3-small`
5. **Storage**: Chunks + embeddings stored in local JSON files (numpy-based vector store)
6. Returns `doc_id` to client

### 2. Question Answering

1. User asks a question in the chat interface
2. **Query Embedding**: Server creates embedding for the question using OpenAI
3. **Vector Search**: Simple vector store finds top 5 most similar chunks using cosine similarity
4. **Context Building**: Retrieved chunks are combined as context
5. **Answer Generation**: OpenAI GPT-4o generates answer using context (strictly grounded)
6. Frontend displays answer with source citations

### 3. Grounding

- Answers are **strictly grounded** in retrieved context
- If context is insufficient, the model says "I don't have enough information"
- Sources are displayed with chunk indices and similarity scores

## 🔧 Configuration

### Chunking Parameters

Edit `backend/text_chunker.py`:
- `CHUNK_SIZE_TOKENS`: Target chunk size (default: 1000 tokens)
- `CHUNK_OVERLAP_TOKENS`: Overlap between chunks (default: 150 tokens)

### Embedding Model

Edit `backend/embeddings.py`:
- `EMBEDDING_MODEL`: OpenAI embedding model (default: "text-embedding-3-small")
- Options: "text-embedding-3-small" (cheaper) or "text-embedding-3-large" (better quality)

### Search Parameters

Edit `backend/main.py` in `/api/chat`:
- `top_k`: Number of chunks to retrieve (default: 5)

### File Size Limits

Edit `backend/main.py`:
- `MAX_SIZE`: Maximum file size (default: 50MB)

## 🐛 Troubleshooting

### Vector Store Errors

**Problem**: "Vector storage failed" or "Cannot find document"

**Solutions**:
1. Ensure `VECTOR_STORAGE_DIR` directory is writable (default: `./vector_storage`)
2. Check that the `doc_id` matches the uploaded document
3. Verify JSON files exist in `vector_storage/` directory
4. If corrupted, delete the specific `doc_*.json` file and re-upload

### PDF Extraction Errors

**Problem**: "Failed to extract text from PDF"

**Solutions**:
1. Ensure PDF is not password-protected
2. Try a different PDF to verify the file isn't corrupted
3. Check server logs for detailed error messages

### Embedding Errors

**Problem**: "Failed to create embeddings"

**Solutions**:
1. Verify `OPENAI_API_KEY` is correct in `.env`
2. Check OpenAI API quota/limits
3. For large PDFs, embeddings are created in batches automatically

### Large File Issues

**Problem**: Upload fails or times out for large PDFs

**Solutions**:
1. Large PDFs (50MB+) may take 1-2 minutes to process - be patient
2. Ensure server has enough RAM (2GB+ recommended)
3. Check OpenAI API rate limits for large embedding batches
4. Consider splitting very large PDFs into smaller documents

### Installation Issues (Windows)

**Problem**: Build errors when installing dependencies

**Solutions**:
1. Use Python 3.11 or earlier (Python 3.13 may require build tools)
2. See `backend/INSTALL_WINDOWS.md` for detailed Windows setup instructions
3. The simple vector store (numpy-based) works on all Python versions without compilation

## 📝 API Endpoints

### POST /api/upload

Upload a PDF file for ingestion and indexing.

**Request**: `multipart/form-data` with field `file`

**Response**:
```json
{
  "doc_id": "uuid-string",
  "chunk_count": 42,
  "status": "ready"
}
```

### POST /api/chat

Ask a question about the document.

**Request**:
```json
{
  "question": "What is the main topic?",
  "doc_id": "uuid-string"
}
```

**Response**:
```json
{
  "answer": "The main topic is...",
  "sources": [
    {
      "text": "chunk text...",
      "chunk_index": 0,
      "score": 0.95
    }
  ]
}
```

## 🎨 Frontend Features

- **Dark mode UI** with gradient backgrounds
- **Drag-and-drop upload** with progress indicator
- **Real-time indexing status** during processing
- **Modern chat interface** with message bubbles
- **Source citations** with expandable sections
- **Responsive design** for mobile and desktop

## 🔒 Security Notes

- API keys are **never exposed** to the browser
- All OpenAI calls happen server-side
- File validation prevents non-PDF uploads
- CORS is configured for localhost development (adjust for production)

## 🚢 Production Deployment

### Backend

1. Set production environment variables in `.env`
2. Use process manager (PM2, systemd, etc.) to keep server running
3. Configure reverse proxy (nginx, Caddy) for HTTPS
4. Enable HTTPS with SSL certificates
5. Adjust CORS origins in `main.py` for production domain
6. **Backup `vector_storage/` directory** regularly (contains all document embeddings)
7. Set appropriate file size limits and timeouts

### Frontend

1. Build: `npm run build` or `bun run build`
2. Serve static files via nginx, Vercel, Netlify, etc.
3. Set `VITE_API_URL` environment variable to production backend URL
4. Update CORS settings on backend to allow your frontend domain

### Vector Storage

For production:
- **Backup strategy**: Regularly backup `vector_storage/` directory (contains all document data)
- **Storage location**: Use absolute path for `VECTOR_STORAGE_DIR` in production
- **Disk space**: Monitor disk usage as embeddings are stored locally
- **Performance**: For very large document collections (1000+ docs), consider migrating to a dedicated vector database

## 📊 Limitations & Tuning Tips

### Large PDFs

- **Processing time**: Large PDFs (50MB+) may take 1-2 minutes to index
- **Memory**: Ensure server has enough RAM (2GB+ recommended)
- **Chunking**: Adjust chunk size for better context retention

### Quality Tuning

- **Chunk size**: Smaller chunks (500-800 tokens) = more precise, larger chunks (1200-1500) = more context
- **Overlap**: More overlap (200-300 tokens) = better context continuity
- **Top K**: Increase `top_k` (5-10) for complex questions requiring more context

### Cost Optimization

- **Embeddings**: Already using `text-embedding-3-small` (cheapest option)
- **Chat Model**: Consider `gpt-4o-mini` for ~90% cost reduction (change in `openai_client.py`)
- **Top K**: Reduce `top_k` (default: 5) if answers are consistently good with fewer chunks
- **Embeddings are cached**: Re-uploading the same document doesn't re-create embeddings (stored in `vector_storage/`)

**Typical Costs:**
- Upload: ~$0.0026 per document (less than 1 cent)
- Per question: ~$0.016 (1.6 cents with gpt-4o)
- Monthly (50 docs, 200 questions): ~$3.25/month

## 💰 Cost Estimate

- **Upload**: ~$0.0026 per document (less than 1 cent)
- **Per Question**: ~$0.016 (1.6 cents with gpt-4o)
- **Monthly (typical usage)**: $1-5/month

See detailed cost breakdown in the Configuration section above.

## 📄 License

MIT

---

**Built with ❤️ using FastAPI, React, OpenAI, and NumPy**
