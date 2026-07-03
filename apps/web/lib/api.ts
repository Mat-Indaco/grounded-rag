import type { QueryResponse } from "./types";

/** Llama al route handler de Next (/api/query), que a su vez proxea al backend. */
export async function askQuestion(question: string): Promise<QueryResponse> {
  const res = await fetch("/api/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });

  if (!res.ok) {
    const detail = await res.text().catch(() => "");
    throw new Error(detail || `Error ${res.status}`);
  }

  return res.json();
}
