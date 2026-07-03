# /evals — el corazón del proyecto

> Esta carpeta es lo que separa este proyecto de los mil demos de "chateá con tu PDF".
> Es lo que un senior abre primero. **Si hay que recortar por tiempo, se recortan features
> del chat, nunca los evals.**

**Estado:** scaffolding. La implementación completa es la **Fase 3**.

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

## Archivos (a implementar en Fase 3)

- `dataset.jsonl` — 30–50 casos con respuesta conocida (incluye fuera de dominio).
- `run_evals.py` — corre la suite contra la API y escribe resultados.
- `metrics.py` — hit rate, groundedness (juez LLM), refusal accuracy.
- `results/` — históricos por corrida, para mostrar la tabla "antes vs después".

## El experimento que vende

Correr la suite, cambiar **un** parámetro (tamaño de chunk, `k`, umbral de similitud),
volver a correr, y guardar ambos resultados. Esa tabla comparativa es la mejor prueba de
criterio técnico del proyecto.
