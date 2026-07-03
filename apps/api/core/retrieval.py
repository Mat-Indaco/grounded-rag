"""Recuperación: pregunta → embedding → top-k chunks con su documento."""
from __future__ import annotations

from dataclasses import dataclass

from core.embeddings import embed_query
from db import client as db


@dataclass
class RetrievedChunk:
    chunk_id: str
    content: str
    document_id: str
    document_title: str
    similarity: float


def retrieve(question: str, top_k: int) -> list[RetrievedChunk]:
    query_embedding = embed_query(question)
    rows = db.match_chunks(query_embedding, top_k)

    titles = db.get_document_titles([r["document_id"] for r in rows])
    return [
        RetrievedChunk(
            chunk_id=r["id"],
            content=r["content"],
            document_id=r["document_id"],
            document_title=titles.get(r["document_id"], "(sin título)"),
            similarity=r["similarity"],
        )
        for r in rows
    ]
