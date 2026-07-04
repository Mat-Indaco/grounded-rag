"""Corre la suite de evals y escribe resultados.

Uso (desde la raíz del repo):
    python evals/run_evals.py                 # corrida completa
    python evals/run_evals.py --limit 5        # smoke test
    python evals/run_evals.py --delay 21       # throttle para el free tier de Voyage (3 RPM)

Importa el pipeline (retrieve + generate) directamente, no vía HTTP, para poder
medir el retrieval hit rate: necesita ver TODOS los chunks recuperados (top-k),
no solo los citados en la respuesta.

Escribe un JSON por corrida en evals/results/ con la config (tamaño de chunk, k,
modelos) + métricas + detalle por caso. Esa config es lo que hace comparables dos
corridas: la tabla "antes vs después" al cambiar un parámetro.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# --- setup de paths ANTES de importar el pipeline (config lee .env del CWD) ---
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "apps" / "api"))
os.chdir(ROOT)  # para que config encuentre ./.env

from core.chunking import DEFAULT_CHUNK_SIZE, DEFAULT_OVERLAP  # noqa: E402
from core.config import get_settings  # noqa: E402
from core.generation import generate_answer  # noqa: E402
from core.retrieval import retrieve  # noqa: E402

sys.path.insert(0, str(ROOT / "evals"))
from judge import judge_grounded  # noqa: E402
from metrics import EvalRecord, summary  # noqa: E402

DATASET = ROOT / "evals" / "dataset.jsonl"
RESULTS_DIR = ROOT / "evals" / "results"


def load_dataset(limit: int | None) -> list[dict]:
    cases = []
    with DATASET.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                cases.append(json.loads(line))
    return cases[:limit] if limit else cases


def run_case(case: dict, top_k: int) -> EvalRecord:
    chunks = retrieve(case["question"], top_k)
    result = generate_answer(case["question"], chunks)

    # títulos de los docs recuperados (únicos, preservando orden)
    seen, retrieved_docs = set(), []
    for c in chunks:
        if c.document_title not in seen:
            seen.add(c.document_title)
            retrieved_docs.append(c.document_title)

    rec = EvalRecord(
        id=case["id"],
        question=case["question"],
        must_refuse=case.get("must_refuse", False),
        relevant_doc=case.get("relevant_doc"),
        retrieved_docs=retrieved_docs,
        top_similarity=round(chunks[0].similarity, 4) if chunks else None,
        answered=result.grounded,
        answer=result.answer,
    )

    # groundedness solo se juzga si el sistema efectivamente respondió
    if rec.answered:
        context = "\n\n".join(c.content for c in chunks)
        rec.judge_grounded, rec.judge_reason = judge_grounded(
            case["question"], context, result.answer
        )
    return rec


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None, help="correr solo N casos")
    ap.add_argument("--delay", type=float, default=0.0, help="segundos entre casos (rate limit Voyage)")
    args = ap.parse_args()

    settings = get_settings()
    cases = load_dataset(args.limit)
    print(f"Corriendo {len(cases)} casos (k={settings.top_k}, delay={args.delay}s)...\n")

    records: list[EvalRecord] = []
    started = time.monotonic()
    for i, case in enumerate(cases):
        rec = run_case(case, settings.top_k)
        records.append(rec)

        # marca de estado por caso
        if rec.must_refuse:
            ok = not rec.answered
            tag = "REFUSED-ok" if ok else "ANSWERED-BAD"
        else:
            hit = rec.relevant_doc in rec.retrieved_docs
            g = rec.judge_grounded
            tag = f"hit={'Y' if hit else 'N'} grounded={g}"
        print(f"  [{rec.id:>2}] {tag:<24} {rec.question[:60]}")

        if args.delay and i < len(cases) - 1:
            time.sleep(args.delay)

    elapsed = round(time.monotonic() - started, 1)
    stats = summary(records)

    config = {
        "chunk_size": DEFAULT_CHUNK_SIZE,
        "overlap": DEFAULT_OVERLAP,
        "top_k": settings.top_k,
        "embed_model": settings.embed_model,
        "gen_model": settings.gen_model,
        "judge_model": settings.judge_model,
    }

    RESULTS_DIR.mkdir(exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = RESULTS_DIR / f"{ts}.json"
    out.write_text(
        json.dumps(
            {
                "timestamp": ts,
                "elapsed_seconds": elapsed,
                "config": config,
                "metrics": stats,
                "cases": [rec.__dict__ for rec in records],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\n" + "=" * 50)
    print("CONFIG:", json.dumps(config))
    print(f"Retrieval hit rate : {stats['_pretty']['retrieval_hit_rate']}  "
          f"({stats['n_domain']} dominio)")
    print(f"Groundedness       : {stats['_pretty']['groundedness']}")
    print(f"Refusal accuracy   : {stats['_pretty']['refusal_accuracy']}  "
          f"({stats['n_out_of_domain']} fuera de dominio)")
    print(f"Tiempo: {elapsed}s  |  Resultados: {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
