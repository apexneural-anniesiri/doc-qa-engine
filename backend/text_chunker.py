"""
Text chunking module.
Splits text into chunks with overlap for better context retention.
"""
import tiktoken
from typing import List


# Chunking parameters
CHUNK_SIZE_TOKENS = 1000  # ~800-1200 tokens target
CHUNK_OVERLAP_TOKENS = 150  # ~100-200 tokens overlap
CHUNK_SIZE_CHARS = 4000  # Fallback if tiktoken fails
CHUNK_OVERLAP_CHARS = 500  # Fallback overlap in chars


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE_TOKENS, overlap: int = CHUNK_OVERLAP_TOKENS) -> List[dict]:
    """
    Split text into chunks with overlap.
    
    Args:
        text: Text to chunk
        chunk_size: Target chunk size in tokens (or chars if encoding fails)
        overlap: Overlap size in tokens (or chars)
    
    Returns:
        List[dict]: List of chunks with metadata
        Each chunk: { "text": str, "chunk_index": int, "start_char": int, "end_char": int }
    """
    if not text or len(text.strip()) == 0:
        return []
    
    chunks = []
    
    # Try to use tiktoken for token-based chunking
    try:
        encoding = tiktoken.get_encoding("cl100k_base")  # GPT-4 encoding
        tokens = encoding.encode(text)
        
        chunk_size_tokens = chunk_size
        overlap_tokens = overlap
        
        i = 0
        chunk_index = 0
        
        while i < len(tokens):
            # Get chunk tokens
            chunk_tokens = tokens[i:i + chunk_size_tokens]
            chunk_text = encoding.decode(chunk_tokens)
            
            # Find character positions for this chunk
            # Approximate: tokens before this chunk
            tokens_before = tokens[:i]
            start_char = len(encoding.decode(tokens_before))
            end_char = start_char + len(chunk_text)
            
            chunks.append({
                "text": chunk_text,
                "chunk_index": chunk_index,
                "start_char": start_char,
                "end_char": end_char
            })
            
            # Move forward with overlap
            i += chunk_size_tokens - overlap_tokens
            chunk_index += 1
            
            # Prevent infinite loop
            if i >= len(tokens):
                break
            if i == 0:  # Safety check
                i = chunk_size_tokens - overlap_tokens
    
    except Exception as e:
        # Fallback to character-based chunking
        print(f"[Chunker] Token encoding failed, using char-based chunking: {e}")
        
        chunk_size_chars = CHUNK_SIZE_CHARS
        overlap_chars = CHUNK_OVERLAP_CHARS
        
        i = 0
        chunk_index = 0
        text_len = len(text)
        
        while i < text_len:
            end = min(i + chunk_size_chars, text_len)
            chunk_text = text[i:end]
            
            chunks.append({
                "text": chunk_text,
                "chunk_index": chunk_index,
                "start_char": i,
                "end_char": end
            })
            
            # Move forward with overlap
            i += chunk_size_chars - overlap_chars
            chunk_index += 1
            
            # Prevent infinite loop
            if i >= text_len:
                break
            if i == 0:  # Safety check
                i = chunk_size_chars - overlap_chars
    
    return chunks
