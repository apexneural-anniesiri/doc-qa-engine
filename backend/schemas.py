from pydantic import BaseModel
from typing import Optional, List


class UploadResponse(BaseModel):
    doc_id: str
    chunk_count: int
    status: str = "ready"  # Always ready after indexing


class ChatRequest(BaseModel):
    question: str
    doc_id: str


class Source(BaseModel):
    text: str
    chunk_index: Optional[int] = None
    score: Optional[float] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]


class ErrorResponse(BaseModel):
    error: str
    provider: Optional[str] = None  # "GroundX" | "OpenAI" | "Server"
    status: Optional[int] = None
    details: Optional[str] = None
