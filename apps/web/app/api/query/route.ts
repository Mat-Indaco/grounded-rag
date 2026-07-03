import { NextResponse } from "next/server";

// Proxy al backend FastAPI. Mantiene la URL del backend del lado del servidor.
const API_BASE_URL = process.env.API_BASE_URL ?? "http://localhost:8000";

export async function POST(request: Request) {
  const body = await request.json();

  try {
    const res = await fetch(`${API_BASE_URL}/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch {
    return NextResponse.json(
      { detail: "No se pudo contactar al backend." },
      { status: 502 },
    );
  }
}
