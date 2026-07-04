#!/usr/bin/env bash
# Descarga el markdown crudo de las docs oficiales a _raw/.
# Después correr: python clean.py  (produce docs/*.md limpios para ingestar).
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p _raw

FA="https://raw.githubusercontent.com/fastapi/fastapi/master/docs/en/docs/tutorial"
for f in first-steps path-params query-params body response-model handling-errors; do
  curl -sf "$FA/$f.md" -o "_raw/fastapi_$f.md" && echo "[ok] fastapi_$f"
done

SB="https://raw.githubusercontent.com/supabase/supabase/master/apps/docs/content/guides"
declare -A SBP=(
  [supabase_vector-columns]="ai/vector-columns.mdx"
  [supabase_semantic-search]="ai/semantic-search.mdx"
  [supabase_embeddings]="ai/quickstarts/generate-text-embeddings.mdx"
  [supabase_functions]="database/functions.mdx"
  [supabase_rls]="database/postgres/row-level-security.mdx"
  [supabase_indexes-hnsw]="ai/vector-indexes/hnsw-indexes.mdx"
  [supabase_indexes-ivfflat]="ai/vector-indexes/ivf-indexes.mdx"
)
for name in "${!SBP[@]}"; do
  curl -sf "$SB/${SBP[$name]}" -o "_raw/$name.mdx" && echo "[ok] $name"
done

echo "Listo. Ahora: python clean.py"
