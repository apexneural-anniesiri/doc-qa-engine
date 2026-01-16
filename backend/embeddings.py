"""
OpenAI embeddings module.
Creates embeddings for text chunks and queries.
"""
import os
from typing import List
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is required in .env")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Embedding model
EMBEDDING_MODEL = "text-embedding-3-small"  # Good balance of cost and quality
# Alternative: "text-embedding-3-large" for better quality (more expensive)


async def create_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Create embeddings for a list of texts.
    
    Args:
        texts: List of text strings to embed
    
    Returns:
        List[List[float]]: List of embedding vectors
    """
    if not texts:
        return []
    
    try:
        # OpenAI embeddings API
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=texts
        )
        
        embeddings = [item.embedding for item in response.data]
        return embeddings
    
    except Exception as e:
        raise Exception(f"Failed to create embeddings: {str(e)}")


async def create_embedding(text: str) -> List[float]:
    """
    Create embedding for a single text.
    
    Args:
        text: Text string to embed
    
    Returns:
        List[float]: Embedding vector
    """
    embeddings = await create_embeddings([text])
    return embeddings[0] if embeddings else []
