# Grounded RAG Assistant

Asistente de preguntas y respuestas sobre documentación técnica (FastAPI / Next.js / Supabase),
construido para explorar **cómo hacer que un LLM sea confiable en producción**: citas
verificables, guardrails contra alucinaciones y una suite de evaluación medible.

No es "chateá con tu PDF": es una demo de que sé *medir y controlar* el comportamiento
de un LLM. El diferenciador no es el chat, es la carpeta [`/evals`](./evals).

🔗 **Demo:** https://grounded-rag-cyan.vercel.app · 🎥 **Video 60s:** _(pendiente)_

## Stack

Next.js · TypeScript · FastAPI · Supabase (pgvector) · Claude API · Voyage AI (embeddings)

> **Nota sobre embeddings:** Anthropic no expone un endpoint de embeddings — solo generación.
> Los vectores los produce [Voyage AI](https://docs.voyageai.com/) (`voyage-3.5`, 1024 dims),
> el partner de embeddings recomendado por Anthropic. Claude se usa para la **generación con
> citas** (`claude-opus-4-8`) y como **juez de groundedness** en los evals (`claude-haiku-4-5`).

## Arquitectura

```
Pregunta ─▶ embedding (Voyage) ─▶ top-k por similitud coseno (pgvector)
        ─▶ prompt con contexto ─▶ Claude (salida estructurada con citas) ─▶ respuesta + citas
```

Ingesta: documento ─▶ chunks con overlap ─▶ embeddings ─▶ pgvector.

## Estructura

```
grounded-rag/
├── apps/
│   ├── api/          # FastAPI: ingest + query + retrieval + generación
│   └── web/          # Next.js: chat UI + panel de citas
├── evals/            # ⭐ el corazón del proyecto (Fase 3)
└── docker-compose.yml
```

## Roadmap

- [x] **Fase 1 — MVP.** Ingest + query + chat con citas. **Deployado y público** (Vercel + Render). ✅
- [ ] **Fase 2 — Guardrails.** Umbral de "no sé" + validación de salida + juez de groundedness.
- [ ] **Fase 3 — Evals.** Dataset de 30–50 casos + 3 métricas (hit rate, groundedness, refusal accuracy).
- [ ] **Fase 4 — Dashboard + observabilidad.** Página `/evals` + costo/latencia por consulta.
- [ ] **Fase 5 (stretch) — MCP.** Exponer el retrieval como server MCP.

## Cómo correrlo (local)

### 1. Base de datos (Supabase)

Creá un proyecto en [Supabase](https://supabase.com), abrí el SQL Editor y corré
[`apps/api/db/schema.sql`](./apps/api/db/schema.sql). Eso activa `pgvector`, crea las
tablas y la función `match_chunks`.

### 2. Variables de entorno

```bash
cp .env.example .env
# completá ANTHROPIC_API_KEY, VOYAGE_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_KEY
```

### 3. Backend

```bash
cd apps/api
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Ingestá el corpus de ejemplo:

```bash
python scripts/ingest_docs.py ./sample_docs
```

### 4. Frontend

```bash
cd apps/web
npm install
npm run dev   # http://localhost:3000
```

## Endpoints

| Método | Ruta          | Qué hace                                            |
|--------|---------------|-----------------------------------------------------|
| `POST` | `/ingest`     | Recibe un doc, lo chunkea, embebe y guarda          |
| `POST` | `/query`      | Pregunta → retrieve top-k → respuesta con citas     |
| `GET`  | `/documents`  | Lista lo indexado                                   |
| `GET`  | `/health`     | Healthcheck                                         |

## Decisiones de diseño

_(se irán completando con datos de los evals — Fase 3)_

- **Embeddings con Voyage, no Anthropic:** Anthropic no tiene endpoint de embeddings.
  Voyage es su partner recomendado y `voyage-3.5` da 1024 dims, que es lo que usa el índice.
- **Salida estructurada desde Fase 1:** la respuesta de `/query` es JSON validado
  (`answer`, `citations`, `grounded`), no texto libre — base para los guardrails de Fase 2.
- **HNSW en vez de ivfflat (bug encontrado en Fase 1):** el índice `ivfflat` con `lists=100`
  devolvía **0 filas** en algunas consultas sobre un corpus chico, porque parte los vectores en
  100 clusters y con pocos datos casi todas las listas quedan vacías (`probes=1` mira una sola).
  Lo detecté con una pregunta fuera de dominio que daba retrieval vacío en vez de traer los k
  vecinos. Migré a HNSW, que devuelve resultados correctos con cualquier tamaño de corpus.
  Medición: pregunta fuera de dominio → top similitud ~0.33; pregunta del corpus → ~0.55+.
  Esa brecha es la base del umbral de abstención de la Fase 2.
