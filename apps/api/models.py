"""Contratos de request/response de la API (Pydantic)."""
from pydantic import BaseModel, Field


# ---- Ingest ----
class IngestRequest(BaseModel):
    title: str
    content: str
    source_url: str | None = None


class IngestResponse(BaseModel):
    document_id: str
    chunks_created: int


# ---- Query ----
class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int | None = None


class Citation(BaseModel):
    chunk_id: str
    document_title: str
    snippet: str
    similarity: float


class QueryResponse(BaseModel):
    answer: str
    grounded: bool
    citations: list[Citation]


# ---- Documents ----
class DocumentInfo(BaseModel):
    id: str
    title: str
    source_url: str | None
    created_at: str
