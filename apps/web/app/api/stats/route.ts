import { NextResponse } from "next/server";

const API_BASE_URL = process.env.API_BASE_URL ?? "http://localhost:8000";

export async function GET() {
  try {
    const res = await fetch(`${API_BASE_URL}/stats`, { cache: "no-store" });
    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch {
    return NextResponse.json(
      { detail: "No se pudo contactar al backend." },
      { status: 502 },
    );
  }
}
