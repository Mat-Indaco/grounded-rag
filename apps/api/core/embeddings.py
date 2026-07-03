"""Wrapper de embeddings sobre Voyage AI.

Voyage distingue el input_type: "document" al indexar, "query" al buscar. Usar el
tipo correcto mejora el retrieval (los vectores quedan mejor alineados).
"""
from __future__ import annotations

import voyageai

from core.config import get_settings

_settings = get_settings()
_client = voyageai.Client(api_key=_settings.voyage_api_key)


def embed_documents(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    result = _client.embed(
        texts,
        model=_settings.embed_model,
        input_type="document",
        output_dimension=_settings.embed_dim,
    )
    return result.embeddings


def embed_query(text: str) -> list[float]:
    result = _client.embed(
        [text],
        model=_settings.embed_model,
        input_type="query",
        output_dimension=_settings.embed_dim,
    )
    return result.embeddings[0]
