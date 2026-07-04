# /evals — el corazón del proyecto

> Esta carpeta es lo que separa este proyecto de los mil demos de "chateá con tu PDF".
> Es lo que un senior abre primero. **Si hay que recortar por tiempo, se recortan features
> del chat, nunca los evals.**

**Estado:** implementado. Corré la suite con `python evals/run_evals.py` (desde la raíz del repo).

## Qué se va a medir (3 métricas)

1. **Retrieval hit rate** — ¿el chunk correcto entró en el top-k? Aísla si el problema
   es *buscar* o *generar*.
2. **Groundedness** — de las respuestas dadas, ¿qué % están respaldadas por el contexto?
   Mide alucinación. Se calcula con un juez LLM barato (`claude-haiku-4-5`).
3. **Refusal accuracy** — en preguntas **fuera del corpus**, ¿cuántas veces se abstuvo bien?
   Un RAG que contesta cualquier cosa reprueba acá; uno que dice "no sé" demuestra criterio.

## Formato del dataset (`dataset.jsonl`)

Una línea por caso. Ver [`dataset.example.jsonl`](./dataset.example.jsonl):

```json
{"id": 1, "question": "¿Qué operador usa pgvector para distancia coseno?", "expected_answer": "<=>", "relevant_doc": "supabase_pgvector", "must_refuse": false}
{"id": 2, "question": "¿Cuál es la capital de Francia?", "expected_answer": null, "relevant_doc": null, "must_refuse": true}
```

Los casos con `must_refuse: true` son preguntas **fuera de dominio** a propósito: miden si el
sistema sabe decir "no sé".

## Archivos

- `dataset.jsonl` — 40 casos con respuesta conocida (33 de dominio + 7 fuera de dominio).
- `run_evals.py` — importa el pipeline (retrieve + generate) directo, corre la suite y escribe resultados. Flags: `--limit N`, `--delay S` (throttle para el free tier de Voyage).
- `metrics.py` — hit rate, groundedness, refusal accuracy.
- `judge.py` — juez de groundedness (LLM-as-judge con `claude-haiku-4-5`, salida estructurada).
- `results/` — un JSON por corrida (config + métricas + detalle por caso), para la tabla "antes vs después".

```bash
python evals/run_evals.py               # corrida completa
python evals/run_evals.py --limit 5      # smoke test
python evals/run_evals.py --delay 22     # si Voyage te limita (free tier 3 RPM)
```

## El experimento que vende

Correr la suite, cambiar **un** parámetro (tamaño de chunk, `k`, umbral de similitud),
volver a correr, y guardar ambos resultados. Esa tabla comparativa es la mejor prueba de
criterio técnico del proyecto.
