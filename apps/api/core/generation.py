"""Generación con citas usando Claude y salida estructurada (JSON schema).

La respuesta se fuerza a un JSON validado (answer / grounded / citations) — es la
base del guardrail de salida estructurada de la Fase 2. Claude debe citar los
chunk_id que efectivamente usó; el router mapea esos ids a título + snippet.
"""
from __future__ import annotations

import json
from dataclasses import dataclass

from anthropic import Anthropic

from core.config import get_settings
from core.retrieval import RetrievedChunk

_settings = get_settings()
_client = Anthropic(api_key=_settings.anthropic_api_key)

SYSTEM_PROMPT = """You are a precise question-answering assistant over a documentation corpus.

Rules:
- Answer ONLY using the provided CONTEXT chunks. Do not use outside knowledge.
- Cite every claim: each citation references the `chunk_id` you drew it from, with a short verbatim `quote` from that chunk.
- If the CONTEXT does not contain enough information to answer, set `grounded` to false and say you don't have that information in the sources. Do not guess.
- Keep the answer concise and directly responsive to the question."""

# Salida estructurada: garantiza JSON parseable (structured outputs en Opus 4.8).
OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": "string"},
        "grounded": {"type": "boolean"},
        "citations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "chunk_id": {"type": "string"},
                    "quote": {"type": "string"},
                },
                "required": ["chunk_id", "quote"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["answer", "grounded", "citations"],
    "additionalProperties": False,
}


@dataclass
class GenerationResult:
    answer: str
    grounded: bool
    cited_chunk_ids: list[str]
    tokens_in: int
    tokens_out: int


def _build_user_prompt(question: str, chunks: list[RetrievedChunk]) -> str:
    context_blocks = "\n\n".join(
        f"[chunk_id: {c.chunk_id}] (from: {c.document_title})\n{c.content}"
        for c in chunks
    )
    return (
        f"CONTEXT:\n{context_blocks}\n\n"
        f"QUESTION: {question}\n\n"
        "Answer using only the context above and cite the chunk_ids you used."
    )


def generate_answer(question: str, chunks: list[RetrievedChunk]) -> GenerationResult:
    if not chunks:
        return GenerationResult(
            answer="No encontré nada en las fuentes para responder esto.",
            grounded=False,
            cited_chunk_ids=[],
            tokens_in=0,
            tokens_out=0,
        )

    response = _client.messages.create(
        model=_settings.gen_model,
        max_tokens=4096,
        thinking={"type": "disabled"},  # snappy para chat; groundedness la refuerza Fase 2
        system=SYSTEM_PROMPT,
        output_config={"effort": "low", "format": {"type": "json_schema", "schema": OUTPUT_SCHEMA}},
        messages=[{"role": "user", "content": _build_user_prompt(question, chunks)}],
    )

    text = "".join(block.text for block in response.content if block.type == "text")
    data = json.loads(text)

    return GenerationResult(
        answer=data["answer"],
        grounded=bool(data["grounded"]),
        cited_chunk_ids=[c["chunk_id"] for c in data.get("citations", [])],
        tokens_in=response.usage.input_tokens,
        tokens_out=response.usage.output_tokens,
    )
