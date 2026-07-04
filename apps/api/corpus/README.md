# Corpus

Documentación oficial real, acotada al *stack de retrieval* del proyecto: el
tutorial de **FastAPI** (backend) y las guías de **Supabase** sobre pgvector,
índices vectoriales, embeddings, funciones SQL y RLS. Es la doc que leerías para
construir este mismo sistema — corpus enfocado y explicable en entrevista.

Se deja Next.js afuera a propósito: es solo el frontend fino y mantener el corpus
acotado rinde más en retrieval y en la narrativa.

## Contenido (13 docs)

- **FastAPI (6):** first-steps, path-params, query-params, body, response-model, handling-errors
- **Supabase (7):** vector-columns, semantic-search, embeddings, functions, RLS, HNSW indexes, IVFFlat indexes

## Cómo se arma (reproducible)

```bash
./fetch.sh          # baja el markdown crudo a _raw/  (gitignored)
python clean.py     # limpia MkDocs/MDX -> docs/*.md
```

`clean.py` saca frontmatter, includes de código MkDocs (`{* ... *}`), anclas de
heading, marcadores de admonition (`/// tip`) y componentes JSX de MDX (`<Tabs>`,
`<TabPanel>`, `<Admonition>`), dejando prosa + bloques de código.

## Ingestar

```bash
python scripts/ingest_docs.py ./corpus/docs
```

> `_raw/` está gitignoreado; se regenera con `fetch.sh`. Versionamos solo `docs/`
> (el corpus limpio) + los scripts, para que el estado sea reproducible.
