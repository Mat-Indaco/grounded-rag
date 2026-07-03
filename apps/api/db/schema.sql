-- Grounded RAG — schema de Supabase (pgvector)
-- Corré este archivo entero en el SQL Editor de Supabase.
-- La dimensión del vector (1024) coincide con voyage-3.5. Si cambiás de modelo de
-- embeddings, ajustá vector(N) y el arg de match_chunks a la nueva dimensión.

create extension if not exists vector;

create table if not exists documents (
  id          uuid primary key default gen_random_uuid(),
  title       text not null,
  source_url  text,
  created_at  timestamptz default now()
);

create table if not exists chunks (
  id          uuid primary key default gen_random_uuid(),
  document_id uuid references documents(id) on delete cascade,
  content     text not null,
  chunk_index int  not null,
  embedding   vector(1024),
  created_at  timestamptz default now()
);

-- Índice para búsqueda por similitud coseno.
-- Usamos HNSW: da buen recall y latencia, y —clave— devuelve resultados correctos
-- con cualquier tamaño de corpus. (ivfflat parte los vectores en `lists` clusters y
-- con un corpus chico deja casi todas las listas vacías, devolviendo 0 filas en
-- algunas queries: un footgun clásico. HNSW no tiene ese problema.)
create index if not exists chunks_embedding_idx
  on chunks using hnsw (embedding vector_cosine_ops);

-- Registro de cada consulta: base de la observabilidad y los evals (Fases 3-4).
create table if not exists query_logs (
  id            uuid primary key default gen_random_uuid(),
  question      text,
  answer        text,
  retrieved_ids uuid[],
  grounded      boolean,
  tokens_in     int,
  tokens_out    int,
  latency_ms    int,
  created_at    timestamptz default now()
);

-- Búsqueda vectorial: devuelve los match_count chunks más cercanos por coseno.
create or replace function match_chunks(query_embedding vector(1024), match_count int)
returns table (id uuid, content text, document_id uuid, similarity float)
language sql stable as $$
  select c.id, c.content, c.document_id,
         1 - (c.embedding <=> query_embedding) as similarity
  from chunks c
  order by c.embedding <=> query_embedding
  limit match_count;
$$;
