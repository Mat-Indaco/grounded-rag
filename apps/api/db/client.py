"""Cliente de Supabase (única instancia) y helpers de acceso a datos."""
from __future__ import annotations

from functools import lru_cache

from supabase import Client, create_client

from core.config import get_settings


@lru_cache
def get_client() -> Client:
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_service_key)


def _to_pgvector(embedding: list[float]) -> str:
    """pgvector acepta el literal '[0.1,0.2,...]' vía PostgREST."""
    return "[" + ",".join(str(x) for x in embedding) + "]"


def insert_document(title: str, source_url: str | None) -> str:
    client = get_client()
    res = (
        client.table("documents")
        .insert({"title": title, "source_url": source_url})
        .execute()
    )
    return res.data[0]["id"]


def insert_chunks(
    document_id: str,
    chunks: list[str],
    embeddings: list[list[float]],
) -> int:
    client = get_client()
    rows = [
        {
            "document_id": document_id,
            "content": content,
            "chunk_index": i,
            "embedding": _to_pgvector(emb),
        }
        for i, (content, emb) in enumerate(zip(chunks, embeddings))
    ]
    client.table("chunks").insert(rows).execute()
    return len(rows)


def match_chunks(query_embedding: list[float], match_count: int) -> list[dict]:
    """Devuelve [{id, content, document_id, similarity}, ...] ordenado por cercanía."""
    client = get_client()
    res = client.rpc(
        "match_chunks",
        {"query_embedding": query_embedding, "match_count": match_count},
    ).execute()
    return res.data or []


def get_document_titles(document_ids: list[str]) -> dict[str, str]:
    """Mapa {document_id: title} para armar las citas."""
    if not document_ids:
        return {}
    client = get_client()
    res = (
        client.table("documents")
        .select("id, title")
        .in_("id", list(set(document_ids)))
        .execute()
    )
    return {row["id"]: row["title"] for row in (res.data or [])}


def list_documents() -> list[dict]:
    client = get_client()
    res = (
        client.table("documents")
        .select("id, title, source_url, created_at")
        .order("created_at", desc=True)
        .execute()
    )
    return res.data or []


def log_query(
    question: str,
    answer: str,
    retrieved_ids: list[str],
    grounded: bool,
    tokens_in: int,
    tokens_out: int,
    latency_ms: int,
) -> None:
    """Best-effort: si falla el log no queremos tumbar la respuesta al usuario."""
    try:
        get_client().table("query_logs").insert(
            {
                "question": question,
                "answer": answer,
                "retrieved_ids": retrieved_ids,
                "grounded": grounded,
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "latency_ms": latency_ms,
            }
        ).execute()
    except Exception:  # noqa: BLE001 — observabilidad no crítica
        pass
