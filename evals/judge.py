"""LLM-as-judge de groundedness.

Un segundo pase con un modelo barato (claude-haiku-4-5) decide si una respuesta
está *respaldada por el contexto recuperado*. Es la métrica que mide alucinación:
una respuesta puede sonar bien y ser correcta en el mundo, pero si no sale del
contexto, para un RAG cuenta como no-grounded.
"""
from __future__ import annotations

import json

from anthropic import Anthropic

from core.config import get_settings  # apps/api está en sys.path (lo agrega run_evals)

_settings = get_settings()
_client = Anthropic(api_key=_settings.anthropic_api_key)
_JUDGE_MODEL = _settings.judge_model

_SYSTEM = """You are a strict groundedness evaluator for a RAG system.
Given a QUESTION, the retrieved CONTEXT, and an ANSWER, decide whether the ANSWER
is fully supported by the CONTEXT.

Rules:
- "grounded" is true ONLY if every factual claim in the ANSWER can be verified from the CONTEXT.
- If the ANSWER uses outside knowledge not present in the CONTEXT, it is NOT grounded, even if factually correct.
- If the ANSWER declines to answer / says the info isn't in the sources, treat it as grounded (a correct abstention makes no unsupported claims)."""

_SCHEMA = {
    "type": "object",
    "properties": {
        "grounded": {"type": "boolean"},
        "reason": {"type": "string"},
    },
    "required": ["grounded", "reason"],
    "additionalProperties": False,
}


def judge_grounded(question: str, context: str, answer: str) -> tuple[bool, str]:
    prompt = (
        f"QUESTION:\n{question}\n\n"
        f"CONTEXT:\n{context}\n\n"
        f"ANSWER:\n{answer}\n\n"
        "Is the ANSWER fully supported by the CONTEXT?"
    )
    resp = _client.messages.create(
        model=_JUDGE_MODEL,
        max_tokens=512,
        system=_SYSTEM,
        output_config={"format": {"type": "json_schema", "schema": _SCHEMA}},
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join(b.text for b in resp.content if b.type == "text")
    data = json.loads(text)
    return bool(data["grounded"]), data.get("reason", "")
