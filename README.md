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
- [x] **Fase 3 — Evals.** Dataset de 40 casos + 3 métricas + LLM-as-judge. ✅ (ver abajo)
- [ ] **Fase 4 — Dashboard + observabilidad.** Página `/evals` + costo/latencia por consulta.
- [ ] **Fase 5 (stretch) — MCP.** Exponer el retrieval como server MCP.

## Resultados de evaluación

Suite de 40 casos (33 de dominio + 7 fuera de dominio) sobre el corpus real. Juez de
groundedness: `claude-haiku-4-5`. Corré con `python evals/run_evals.py`; resultados
versionados en [`evals/results/`](./evals/results/).

| Configuración | Retrieval hit rate | Groundedness | Refusal accuracy | Domain answer rate |
|---|---|---|---|---|
| Baseline (chunk 1000, overlap 150) | 100% | 93.5% | 100% | 93.9% |
| **Chunk 400, overlap 80** | 100% | **97.0%** | 100% | **100%** |

Las preguntas fuera de dominio (`must_refuse`) miden si el sistema sabe decir "no sé":
100% de abstención correcta. Esa métrica sola ya es una historia de entrevista.

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

Ingestá el corpus (13 docs reales de FastAPI + Supabase; ver [`corpus/`](./apps/api/corpus/README.md)):

```bash
python scripts/ingest_docs.py ./corpus/docs
# Voyage free tier sin método de pago = 3 RPM. Si te limita, agregá delay:
# python scripts/ingest_docs.py ./corpus/docs 22
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
- **Tamaño de chunk 400 en vez de 1000 (medido en Fase 3):** con chunks de 1000 tokens un
  fragmento mezclaba varios temas y la generación quedaba menos anclada. Bajar a 400 con
  overlap 80 subió groundedness de 93.5% a 97.0% sin tocar el hit rate. La config está en
  [`core/chunking.py`](./apps/api/core/chunking.py) y quedó versionada en cada corrida de evals.
- **Los evals cazan preguntas malas, no solo bugs del sistema (Fase 3):** dos casos de dominio
  daban abstención. Mi hipótesis era que el chunk grande no traía el fragmento correcto; el eval
  mostró que estaba equivocado — el "answer conocido" que yo había escrito **no estaba en el
  corpus** (ej: "stored procedures" no aparece en la doc de Supabase). El sistema hacía lo
  correcto al abstenerse. Corregir esas preguntas llevó el domain answer rate a 100%. La
  moraleja: un RAG que se abstiene bien te obliga a tener un dataset honesto.
- **Límite conocido (honestidad):** una pregunta sobre headers custom en `HTTPException` queda
  no-grounded porque al limpiar la doc de FastAPI saqué los includes de código (`{* ... *}`), así
  que el mecanismo exacto no está en el contexto y el modelo lo completa de memoria. Inlinear ese
  código al corpus lo resolvería.
