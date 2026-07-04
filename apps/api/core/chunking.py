"""Split de texto en chunks con overlap.

Estrategia: partir por párrafos y agrupar hasta ~chunk_size caracteres, con un
overlap de las últimas ~overlap para no cortar ideas al medio. El tamaño de chunk
es el primer parámetro que vamos a barrer en los evals (Fase 3): chunks chicos
mejoran el recall pero fragmentan el contexto.
"""
from __future__ import annotations

DEFAULT_CHUNK_SIZE = 400
DEFAULT_OVERLAP = 80


def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP,
) -> list[str]:
    text = text.strip()
    if not text:
        return []

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current = ""

    for para in paragraphs:
        # Si un solo párrafo excede el tamaño, lo cortamos duro.
        if len(para) > chunk_size:
            if current:
                chunks.append(current)
                current = ""
            for i in range(0, len(para), chunk_size - overlap):
                chunks.append(para[i : i + chunk_size])
            continue

        if len(current) + len(para) + 2 <= chunk_size:
            current = f"{current}\n\n{para}" if current else para
        else:
            chunks.append(current)
            # Arranca el próximo chunk con el tail del anterior (overlap).
            tail = current[-overlap:] if overlap else ""
            current = f"{tail}\n\n{para}" if tail else para

    if current:
        chunks.append(current)

    return chunks
