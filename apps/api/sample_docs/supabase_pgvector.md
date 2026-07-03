# Supabase — pgvector y búsqueda vectorial

Supabase es una plataforma sobre Postgres. La extensión `pgvector` agrega un tipo de dato
`vector` para almacenar embeddings y hacer búsqueda por similitud dentro de la base.

## Activar la extensión

Se activa una sola vez con `create extension if not exists vector;`. A partir de ahí se
puede declarar una columna `embedding vector(1024)`, donde 1024 es la dimensión del modelo
de embeddings que se use.

## Operadores de distancia

pgvector expone varios operadores: `<->` para distancia euclídea (L2), `<=>` para distancia
coseno y `<#>` para producto interno negativo. Para similitud semántica normalmente se usa
coseno; la similitud se obtiene como `1 - (a <=> b)`.

## Índices

Para acelerar la búsqueda hay dos tipos de índice: `ivfflat` y `hnsw`. `ivfflat` es más
simple y rápido de construir, adecuado para corpus chicos. `hnsw` da mejor recall y latencia
cuando el corpus crece, a costa de más memoria y tiempo de construcción.

## RPC

Una función SQL se puede exponer como RPC y llamarla desde el cliente. Es el patrón típico
para encapsular la query de similitud (por ejemplo `match_chunks`) y devolver los k vecinos
más cercanos.
