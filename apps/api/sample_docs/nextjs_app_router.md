# Next.js — App Router

El App Router es el modelo de ruteo de Next.js basado en el directorio `app/`. Cada carpeta
representa un segmento de ruta y un archivo `page.tsx` define la UI de esa ruta.

## Server vs Client Components

Por defecto, los componentes dentro de `app/` son Server Components: se renderizan en el
servidor y no envían su JavaScript al cliente. Para usar estado o efectos (hooks como
`useState` o `useEffect`) hay que marcar el archivo con la directiva `"use client"` al tope.

## Route Handlers

Un archivo `route.ts` dentro de `app/` define un endpoint HTTP (por ejemplo `app/api/query/route.ts`).
Se exportan funciones nombradas según el método: `export async function POST(request) { ... }`.
Es el lugar ideal para proxear llamadas a un backend manteniendo las API keys del lado del servidor.

## Layouts

Un `layout.tsx` envuelve a las páginas de su segmento y se comparte entre navegaciones sin
re-renderizarse. El layout raíz (`app/layout.tsx`) es obligatorio y debe incluir las etiquetas
`<html>` y `<body>`.

## Variables de entorno

Las variables sin prefijo solo están disponibles del lado del servidor. Las que empiezan con
`NEXT_PUBLIC_` se exponen también al navegador. Nunca poner secretos en variables `NEXT_PUBLIC_`.
