"""Observabilidad: agrega query_logs para el dashboard. No llama a ningún LLM."""
from __future__ import annotations

from statistics import mean, median

from fastapi import APIRouter

from db import client as db

router = APIRouter(tags=["stats"])

# Precios aprox por 1M tokens (Claude Opus 4.8) para estimar costo acumulado.
PRICE_IN_PER_1M = 5.0
PRICE_OUT_PER_1M = 25.0


@router.get("/stats")
def stats() -> dict:
    rows = db.get_query_logs(limit=200)
    if not rows:
        return {"total_queries": 0, "recent": []}

    lat = [r["latency_ms"] for r in rows if r.get("latency_ms")]
    total_in = sum(r.get("tokens_in") or 0 for r in rows)
    total_out = sum(r.get("tokens_out") or 0 for r in rows)
    cost = (total_in * PRICE_IN_PER_1M + total_out * PRICE_OUT_PER_1M) / 1_000_000

    return {
        "total_queries": len(rows),
        "grounded_rate": sum(1 for r in rows if r.get("grounded")) / len(rows),
        "avg_latency_ms": round(mean(lat)) if lat else None,
        "p50_latency_ms": round(median(lat)) if lat else None,
        "total_tokens_in": total_in,
        "total_tokens_out": total_out,
        "estimated_cost_usd": round(cost, 4),
        "recent": [
            {
                "question": r.get("question"),
                "grounded": r.get("grounded"),
                "tokens_in": r.get("tokens_in"),
                "tokens_out": r.get("tokens_out"),
                "latency_ms": r.get("latency_ms"),
                "created_at": r.get("created_at"),
            }
            for r in rows[:12]
        ],
    }
