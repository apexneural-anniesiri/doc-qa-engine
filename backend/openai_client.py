import os
import httpx
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is required in .env")

OPENAI_MODEL = "gpt-4o"
OPENAI_BASE_URL = "https://api.openai.com/v1/chat/completions"


def _log_request(provider: str, method: str, url: str, status_code: int = None, response_text: str = None):
    """Log outbound API requests with details."""
    print(f"[{provider}] {method} {url}")
    if status_code is not None:
        print(f"[{provider}] Status: {status_code}")
    if response_text:
        # Safely truncate response body
        truncated = response_text[:500] + "..." if len(response_text) > 500 else response_text
        print(f"[{provider}] Response: {truncated}")


async def generate_answer(question: str, chunks: List[Dict[str, Any]], context_text: str = None) -> str:
    """Generate a grounded answer using OpenAI with retrieved context."""
    if len(chunks) == 0:
        return "I couldn't find any relevant information in the document to answer your question."

    # Use provided context_text if available, otherwise build from chunks
    if context_text:
        context = context_text
    else:
        # Build context from chunks with separators and metadata
        context_parts = []
        for idx, chunk in enumerate(chunks):
            page_info = f" (Page {chunk['page']})" if chunk.get("page") is not None else ""
            context_parts.append(f"[Context {idx + 1}{page_info}]:\n{chunk['text']}")
        context = "\n\n---\n\n".join(context_parts)

    system_prompt = """You are a helpful assistant that answers questions based ONLY on the provided context from a document. 
Rules:
- Answer the question using ONLY the information provided in the context below.
- If the context does not contain enough information to answer the question, say "I don't have enough information in the document to answer this question."
- Do not make up information or use knowledge outside the provided context.
- If you reference specific information, mention which context section it came from (e.g., "According to Context 1...").
- Be concise but complete."""

    user_prompt = f"""Context from document:

{context}

Question: {question}

Answer:"""

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.3,  # Lower temperature for more grounded responses
        "max_tokens": 1000,
    }

    _log_request("OpenAI", "POST", OPENAI_BASE_URL)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(OPENAI_BASE_URL, json=payload, headers=headers)

    response_text = response.text
    _log_request("OpenAI", "POST", OPENAI_BASE_URL, response.status_code, response_text)

    if response.status_code >= 400:
        raise Exception(
            f"OpenAI API failed: {response.status_code} {response_text}"
        )

    data = response.json()
    answer = data.get("choices", [{}])[0].get("message", {}).get("content")

    if not answer:
        raise Exception("OpenAI did not return a valid answer")

    return answer
