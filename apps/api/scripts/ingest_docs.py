"""Ingesta por lote de una carpeta de .md/.txt al corpus.

Uso:
    python scripts/ingest_docs.py ./corpus/docs [delay_segundos]

Cada archivo se ingesta como un documento (title = nombre del archivo). Llama al
mismo pipeline que el endpoint /ingest, sin pasar por HTTP.

`delay_segundos` (opcional) espera entre archivos para respetar el rate limit de
Voyage. El free tier sin método de pago es 3 RPM / 10K TPM → usar ~21s. Con método
de pago cargado (los 200M tokens gratis igual aplican), no hace falta delay.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

# Permite correr el script desde apps/api con los imports de paquete.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.chunking import chunk_text  # noqa: E402
from core.embeddings import embed_documents  # noqa: E402
from db import client as db  # noqa: E402

SUPPORTED = {".md", ".txt"}
EMBED_RETRIES = 6
RETRY_BACKOFF = 30  # segundos entre reintentos ante rate limit


def _embed_with_retry(chunks: list[str]) -> list[list[float]]:
    for attempt in range(1, EMBED_RETRIES + 1):
        try:
            return embed_documents(chunks)
        except Exception as e:  # noqa: BLE001
            if "RateLimit" not in type(e).__name__ and "rate limit" not in str(e).lower():
                raise
            if attempt == EMBED_RETRIES:
                raise
            print(f"    rate limit; reintento {attempt}/{EMBED_RETRIES} en {RETRY_BACKOFF}s")
            time.sleep(RETRY_BACKOFF)
    raise RuntimeError("unreachable")


def ingest_file(path: Path) -> int:
    content = path.read_text(encoding="utf-8")
    chunks = chunk_text(content)
    if not chunks:
        print(f"  [skip] {path.name}: vacio")
        return 0
    embeddings = _embed_with_retry(chunks)
    document_id = db.insert_document(title=path.stem, source_url=None)
    created = db.insert_chunks(document_id, chunks, embeddings)
    print(f"  [ok] {path.name}: {created} chunks", flush=True)
    return created


def main() -> None:
    if len(sys.argv) not in (2, 3):
        print("Uso: python scripts/ingest_docs.py <carpeta> [delay_segundos]")
        sys.exit(1)

    folder = Path(sys.argv[1])
    delay = float(sys.argv[2]) if len(sys.argv) == 3 else 0.0
    if not folder.is_dir():
        print(f"No existe la carpeta: {folder}")
        sys.exit(1)

    files = sorted(p for p in folder.rglob("*") if p.suffix.lower() in SUPPORTED)
    if not files:
        print(f"No hay archivos {SUPPORTED} en {folder}")
        sys.exit(1)

    print(f"Ingestando {len(files)} archivo(s) desde {folder} (delay={delay}s)...", flush=True)
    total = 0
    for i, p in enumerate(files):
        total += ingest_file(p)
        if delay and i < len(files) - 1:
            time.sleep(delay)
    print(f"Listo. {total} chunks en total.")


if __name__ == "__main__":
    main()
