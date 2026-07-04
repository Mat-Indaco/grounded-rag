"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { evalMeta, evalRuns } from "@/lib/evalData";
import type { Stats } from "@/lib/types";

const pct = (x: number) => `${(x * 100).toFixed(1)}%`;

const METRICS: { key: keyof (typeof evalRuns)[0]["metrics"]; label: string }[] = [
  { key: "retrieval_hit_rate", label: "Retrieval hit rate" },
  { key: "groundedness", label: "Groundedness" },
  { key: "refusal_accuracy", label: "Refusal accuracy" },
  { key: "domain_answer_rate", label: "Domain answer rate" },
];

export default function EvalsPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/stats")
      .then((r) => r.json())
      .then((d) => setStats(d))
      .catch(() => setStats(null))
      .finally(() => setLoading(false));
  }, []);

  return (
    <main className="container">
      <div className="header">
        <h1>Dashboard de evaluación</h1>
        <p>
          <Link href="/" className="navlink">
            ← volver al chat
          </Link>
        </p>
      </div>

      <section className="panel-section">
        <h2>Métricas de la suite</h2>
        <p className="hint">
          {evalMeta.n_cases} casos ({evalMeta.n_domain} de dominio +{" "}
          {evalMeta.n_out_of_domain} fuera de dominio) · juez de groundedness:{" "}
          {evalMeta.judge_model}
        </p>
        <div className="table-wrap">
          <table className="metrics-table">
            <thead>
              <tr>
                <th>Métrica</th>
                {evalRuns.map((run) => (
                  <th key={run.label} className="num">
                    {run.label}
                    <div className="cfg">
                      chunk {run.config.chunk_size} · overlap {run.config.overlap} · k{" "}
                      {run.config.top_k}
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {METRICS.map((m) => (
                <tr key={m.key}>
                  <td>{m.label}</td>
                  {evalRuns.map((run) => (
                    <td key={run.label} className="num">
                      {pct(run.metrics[m.key])}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="hint">
          Bajar el chunk de 1000 a 400 subió groundedness de 93.5% a 97.0% sin tocar
          el hit rate. Las preguntas fuera de dominio miden si el sistema sabe decir
          &ldquo;no sé&rdquo;: 100% de abstención correcta.
        </p>
      </section>

      <section className="panel-section">
        <h2>Observabilidad en vivo</h2>
        <p className="hint">Costo y latencia por consulta, logueados en cada /query.</p>

        {loading && <p className="hint">Cargando…</p>}
        {!loading && (!stats || stats.total_queries === 0) && (
          <p className="hint">
            Todavía no hay consultas registradas. Hacé una pregunta en el chat y volvé.
          </p>
        )}

        {stats && stats.total_queries > 0 && (
          <>
            <div className="stat-cards">
              <div className="stat-card">
                <div className="stat-value">{stats.total_queries}</div>
                <div className="stat-label">consultas</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">
                  {stats.grounded_rate != null ? pct(stats.grounded_rate) : "—"}
                </div>
                <div className="stat-label">grounded</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{stats.avg_latency_ms ?? "—"} ms</div>
                <div className="stat-label">latencia media</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">
                  ${stats.estimated_cost_usd?.toFixed(4) ?? "—"}
                </div>
                <div className="stat-label">costo estimado</div>
              </div>
            </div>

            <div className="table-wrap">
              <table className="metrics-table">
                <thead>
                  <tr>
                    <th>Consulta</th>
                    <th className="num">grounded</th>
                    <th className="num">tok in/out</th>
                    <th className="num">latencia</th>
                  </tr>
                </thead>
                <tbody>
                  {stats.recent.map((q, i) => (
                    <tr key={i}>
                      <td className="q-cell">{q.question}</td>
                      <td className="num">{q.grounded ? "✓" : "—"}</td>
                      <td className="num">
                        {q.tokens_in}/{q.tokens_out}
                      </td>
                      <td className="num">{q.latency_ms} ms</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </section>
    </main>
  );
}
