"use client";

import { useState } from "react";
import Link from "next/link";
import { ChatMessage } from "@/components/ChatMessage";
import { askQuestion } from "@/lib/api";
import type { ChatTurn } from "@/lib/types";

export default function Home() {
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [input, setInput] = useState("");
  const [pending, setPending] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const question = input.trim();
    if (!question || pending) return;

    const index = turns.length;
    setTurns((prev) => [...prev, { question, loading: true }]);
    setInput("");
    setPending(true);

    try {
      const response = await askQuestion(question);
      setTurns((prev) =>
        prev.map((t, i) => (i === index ? { question, response } : t)),
      );
    } catch (err) {
      setTurns((prev) =>
        prev.map((t, i) =>
          i === index
            ? { question, error: err instanceof Error ? err.message : "Error" }
            : t,
        ),
      );
    } finally {
      setPending(false);
    }
  }

  return (
    <main className="container">
      <div className="header">
        <h1>Grounded RAG Assistant</h1>
        <p>
          Preguntá sobre la documentación indexada (FastAPI · Supabase). Cada
          respuesta viene con sus fuentes; si no está en el corpus, lo dice.{" "}
          <Link href="/evals" className="navlink">
            ver dashboard de evals →
          </Link>
        </p>
      </div>

      {turns.length === 0 && (
        <p className="hint">
          Ej: “¿Qué operador de distancia usa pgvector para similitud coseno?”
        </p>
      )}

      {turns.map((turn, i) => (
        <ChatMessage key={i} turn={turn} />
      ))}

      <form className="composer" onSubmit={handleSubmit}>
        <div className="composer-inner">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Escribí tu pregunta…"
            disabled={pending}
          />
          <button type="submit" disabled={pending || !input.trim()}>
            Preguntar
          </button>
        </div>
      </form>
    </main>
  );
}
