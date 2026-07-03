"""Ingesta: documento → chunks → embeddings → pgvector."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from core.chunking import chunk_text
from core.embeddings import embed_documents
from db import client as db
from models import DocumentInfo, IngestRequest, IngestResponse

router = APIRouter(tags=["ingest"])


@router.post("/ingest", response_model=IngestResponse)
def ingest(req: IngestRequest) -> IngestResponse:
    chunks = chunk_text(req.content)
    if not chunks:
        raise HTTPException(status_code=400, detail="El documento no tiene contenido.")

    embeddings = embed_documents(chunks)
    document_id = db.insert_document(req.title, req.source_url)
    created = db.insert_chunks(document_id, chunks, embeddings)

    return IngestResponse(document_id=document_id, chunks_created=created)


@router.get("/documents", response_model=list[DocumentInfo])
def documents() -> list[DocumentInfo]:
    return [DocumentInfo(**d) for d in db.list_documents()]
