"""
Simple in-memory vector store using numpy.
No external dependencies that require compilation.
Works on all Python versions and platforms.
"""
import os
import json
import uuid
from typing import List, Dict, Any, Optional
import numpy as np
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Storage directory for persistence
STORAGE_DIR = Path(os.getenv("VECTOR_STORAGE_DIR", "./vector_storage"))
STORAGE_DIR.mkdir(exist_ok=True)


def _cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors."""
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot_product / (norm1 * norm2)


class SimpleVectorStore:
    """Simple in-memory vector store with file-based persistence."""
    
    def __init__(self, doc_id: str):
        self.doc_id = doc_id
        self.storage_file = STORAGE_DIR / f"doc_{doc_id}.json"
        self.embeddings: List[np.ndarray] = []
        self.chunks: List[Dict[str, Any]] = []
        self._load()
    
    def _load(self):
        """Load data from disk if exists."""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.embeddings = [np.array(emb) for emb in data.get("embeddings", [])]
                    self.chunks = data.get("chunks", [])
            except Exception as e:
                print(f"[VectorStore] Error loading {self.doc_id}: {e}")
                self.embeddings = []
                self.chunks = []
    
    def _save(self):
        """Save data to disk."""
        try:
            data = {
                "doc_id": self.doc_id,
                "embeddings": [emb.tolist() for emb in self.embeddings],
                "chunks": self.chunks
            }
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
        except Exception as e:
            print(f"[VectorStore] Error saving {self.doc_id}: {e}")
    
    def add(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]):
        """Add chunks and embeddings."""
        if len(chunks) != len(embeddings):
            raise ValueError(f"Mismatch: {len(chunks)} chunks but {len(embeddings)} embeddings")
        
        self.chunks = chunks
        self.embeddings = [np.array(emb) for emb in embeddings]
        self._save()
        print(f"[VectorStore] Stored {len(chunks)} chunks for document {self.doc_id}")
    
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar chunks."""
        if len(self.embeddings) == 0:
            return []
        
        query_vec = np.array(query_embedding)
        
        # Calculate similarities
        similarities = []
        for i, emb in enumerate(self.embeddings):
            sim = _cosine_similarity(query_vec, emb)
            similarities.append((i, sim))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Get top K results
        results = []
        for idx, score in similarities[:top_k]:
            chunk = self.chunks[idx].copy()
            chunk["score"] = float(score)
            results.append(chunk)
        
        return results


# Global store registry
_stores: Dict[str, SimpleVectorStore] = {}


def get_or_create_store(doc_id: str) -> SimpleVectorStore:
    """Get or create a vector store for a document."""
    if doc_id not in _stores:
        _stores[doc_id] = SimpleVectorStore(doc_id)
    return _stores[doc_id]


async def store_document(
    doc_id: str,
    chunks: List[Dict[str, Any]],
    embeddings: List[List[float]]
) -> int:
    """
    Store document chunks and embeddings.
    
    Args:
        doc_id: Unique document identifier
        chunks: List of chunk dictionaries with text and metadata
        embeddings: List of embedding vectors
    
    Returns:
        int: Number of chunks stored
    """
    if len(chunks) != len(embeddings):
        raise ValueError(f"Mismatch: {len(chunks)} chunks but {len(embeddings)} embeddings")
    
    store = get_or_create_store(doc_id)
    store.add(chunks, embeddings)
    
    return len(chunks)


async def search_document(
    doc_id: str,
    query_embedding: List[float],
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Search for similar chunks in a document.
    
    Args:
        doc_id: Document identifier
        query_embedding: Query embedding vector
        top_k: Number of results to return
    
    Returns:
        List[Dict]: List of results with text, score, and metadata
    """
    store = get_or_create_store(doc_id)
    results = store.search(query_embedding, top_k)
    
    # Format results to match expected structure
    sources = []
    for result in results:
        sources.append({
            "text": result.get("text", ""),
            "score": result.get("score", 0.0),
            "chunk_index": result.get("chunk_index", 0),
            "metadata": {k: v for k, v in result.items() if k not in ["text", "score"]}
        })
    
    return sources


def delete_document(doc_id: str) -> bool:
    """Delete a document and its storage file."""
    try:
        if doc_id in _stores:
            del _stores[doc_id]
        storage_file = STORAGE_DIR / f"doc_{doc_id}.json"
        if storage_file.exists():
            storage_file.unlink()
        return True
    except Exception as e:
        print(f"[VectorStore] Error deleting document {doc_id}: {e}")
        return False
