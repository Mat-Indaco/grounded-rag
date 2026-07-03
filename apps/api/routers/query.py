"""Query: pregunta → retrieve top-k → generación con citas → log."""
from __future__ import annotations

import time

from fastapi import APIRouter

from core.config import get_settings
from core.generation import generate_answer
from core.retrieval import retrieve
from db import client as db
from models import Citation, QueryRequest, QueryResponse

router = APIRouter(tags=["query"])
_settings = get_settings()


@router.post("/query", response_model=QueryResponse)
def query(req: QueryRequest) -> QueryResponse:
    started = time.monotonic()
    top_k = req.top_k or _settings.top_k

    chunks = retrieve(req.question, top_k)
    result = generate_answer(req.question, chunks)

    # Mapa chunk_id → chunk recuperado, para armar las citas con snippet + similarity.
    # Deduplicamos: el modelo puede citar el mismo chunk más de una vez (varios quotes),
    # y no queremos tarjetas repetidas (además de romper las keys en el front).
    by_id = {c.chunk_id: c for c in chunks}
    seen: set[str] = set()
    citations: list[Citation] = []
    for cid in result.cited_chunk_ids:
        if cid not in by_id or cid in seen:  # ignoramos ids alucinados o repetidos
            continue
        seen.add(cid)
        citations.append(
            Citation(
                chunk_id=cid,
                document_title=by_id[cid].document_title,
                snippet=by_id[cid].content[:300],
                similarity=round(by_id[cid].similarity, 4),
            )
        )

    latency_ms = int((time.monotonic() - started) * 1000)
    db.log_query(
        question=req.question,
        answer=result.answer,
        retrieved_ids=[c.chunk_id for c in chunks],
        grounded=result.grounded,
        tokens_in=result.tokens_in,
        tokens_out=result.tokens_out,
        latency_ms=latency_ms,
    )

    return QueryResponse(
        answer=result.answer,
        grounded=result.grounded,
        citations=citations,
    )
