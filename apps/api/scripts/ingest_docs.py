"""Ingesta por lote de una carpeta de .md/.txt al corpus.

Uso:
    python scripts/ingest_docs.py ./sample_docs

Cada archivo se ingesta como un documento (title = nombre del archivo). Llama al
mismo pipeline que el endpoint /ingest, sin pasar por HTTP.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Permite correr el script desde apps/api con los imports de paquete.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.chunking import chunk_text  # noqa: E402
from core.embeddings import embed_documents  # noqa: E402
from db import client as db  # noqa: E402

SUPPORTED = {".md", ".txt"}


def ingest_file(path: Path) -> int:
    content = path.read_text(encoding="utf-8")
    chunks = chunk_text(content)
    if not chunks:
        print(f"  [skip] {path.name}: vacio")
        return 0
    embeddings = embed_documents(chunks)
    document_id = db.insert_document(title=path.stem, source_url=None)
    created = db.insert_chunks(document_id, chunks, embeddings)
    print(f"  [ok] {path.name}: {created} chunks")
    return created


def main() -> None:
    if len(sys.argv) != 2:
        print("Uso: python scripts/ingest_docs.py <carpeta>")
        sys.exit(1)

    folder = Path(sys.argv[1])
    if not folder.is_dir():
        print(f"No existe la carpeta: {folder}")
        sys.exit(1)

    files = sorted(p for p in folder.rglob("*") if p.suffix.lower() in SUPPORTED)
    if not files:
        print(f"No hay archivos {SUPPORTED} en {folder}")
        sys.exit(1)

    print(f"Ingestando {len(files)} archivo(s) desde {folder}...")
    total = sum(ingest_file(p) for p in files)
    print(f"Listo. {total} chunks en total.")


if __name__ == "__main__":
    main()
