"""Las tres métricas del proyecto.

- retrieval_hit_rate: sobre las preguntas de dominio, ¿el doc relevante entró en el
  top-k recuperado? Aísla si el problema es *buscar* o *generar*.
- groundedness: de las respuestas que el sistema efectivamente dio, ¿qué % están
  respaldadas por el contexto? Mide alucinación.
- refusal_accuracy: en las preguntas fuera de dominio, ¿cuántas veces se abstuvo bien?
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EvalRecord:
    id: int
    question: str
    must_refuse: bool
    relevant_doc: str | None
    retrieved_docs: list[str] = field(default_factory=list)  # títulos top-k, en orden
    top_similarity: float | None = None
    answered: bool = False          # el sistema dio una respuesta sustantiva (grounded=True)
    answer: str = ""
    judge_grounded: bool | None = None
    judge_reason: str | None = None


def retrieval_hit_rate(records: list[EvalRecord]) -> float | None:
    domain = [r for r in records if not r.must_refuse and r.relevant_doc]
    if not domain:
        return None
    hits = sum(1 for r in domain if r.relevant_doc in r.retrieved_docs)
    return hits / len(domain)


def refusal_accuracy(records: list[EvalRecord]) -> float | None:
    ood = [r for r in records if r.must_refuse]
    if not ood:
        return None
    # abstención correcta == el sistema NO respondió
    correct = sum(1 for r in ood if not r.answered)
    return correct / len(ood)


def groundedness(records: list[EvalRecord]) -> float | None:
    judged = [r for r in records if r.answered and r.judge_grounded is not None]
    if not judged:
        return None
    grounded = sum(1 for r in judged if r.judge_grounded)
    return grounded / len(judged)


def summary(records: list[EvalRecord]) -> dict:
    def pct(x: float | None) -> str:
        return f"{x * 100:.1f}%" if x is not None else "n/a"

    hr = retrieval_hit_rate(records)
    gr = groundedness(records)
    ra = refusal_accuracy(records)
    dar = domain_answer_rate(records)
    return {
        "n_cases": len(records),
        "n_domain": sum(1 for r in records if not r.must_refuse),
        "n_out_of_domain": sum(1 for r in records if r.must_refuse),
        "retrieval_hit_rate": hr,
        "groundedness": gr,
        "refusal_accuracy": ra,
        "domain_answer_rate": dar,
        "_pretty": {
            "retrieval_hit_rate": pct(hr),
            "groundedness": pct(gr),
            "refusal_accuracy": pct(ra),
            "domain_answer_rate": pct(dar),
        },
    }


def domain_answer_rate(records: list[EvalRecord]) -> float | None:
    """De las preguntas de dominio, ¿en cuántas el sistema respondió (no declinó)?
    Baja cuando el chunk con la respuesta no entra en el top-k aunque el doc sí:
    la señal que el experimento de tamaño de chunk busca mejorar."""
    domain = [r for r in records if not r.must_refuse]
    if not domain:
        return None
    return sum(1 for r in domain if r.answered) / len(domain)
