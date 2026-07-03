# FastAPI — Fundamentos

FastAPI es un framework web de Python para construir APIs, basado en type hints estándar.
Se apoya en Starlette para la parte web y en Pydantic para la validación de datos.

## Path operations

Un endpoint se define con un decorador sobre una función: `@app.get("/items/{item_id}")`.
Los parámetros de path se declaran como argumentos de la función y FastAPI los convierte
y valida automáticamente según el type hint. Por ejemplo, `item_id: int` rechaza con un
error 422 cualquier valor que no sea un entero.

## Validación con Pydantic

El cuerpo de un request se modela con una clase que hereda de `BaseModel`. FastAPI usa ese
modelo para validar el JSON entrante, y si no valida devuelve un 422 con el detalle del error.
Esto es lo que permite tener "salida estructurada validada" sin escribir validaciones a mano.

## Documentación automática

FastAPI genera documentación interactiva a partir del código: Swagger UI en `/docs` y
ReDoc en `/redoc`. El esquema OpenAPI se sirve en `/openapi.json`.

## Async

Las path operations pueden ser `async def` o `def`. Si la función es `def` (síncrona),
FastAPI la corre en un threadpool para no bloquear el event loop.
