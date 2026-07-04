// Resultados de la suite de evals (calculados offline con evals/run_evals.py y
// versionados en evals/results/). Se muestran acá para el dashboard; son estáticos.

export interface EvalRun {
  label: string;
  config: { chunk_size: number; overlap: number; top_k: number };
  metrics: {
    retrieval_hit_rate: number;
    groundedness: number;
    refusal_accuracy: number;
    domain_answer_rate: number;
  };
}

export const evalRuns: EvalRun[] = [
  {
    label: "Baseline",
    config: { chunk_size: 1000, overlap: 150, top_k: 5 },
    metrics: {
      retrieval_hit_rate: 1.0,
      groundedness: 0.935,
      refusal_accuracy: 1.0,
      domain_answer_rate: 0.939,
    },
  },
  {
    label: "Chunk 400 (producción)",
    config: { chunk_size: 400, overlap: 80, top_k: 5 },
    metrics: {
      retrieval_hit_rate: 1.0,
      groundedness: 0.97,
      refusal_accuracy: 1.0,
      domain_answer_rate: 1.0,
    },
  },
];

export const evalMeta = {
  n_cases: 40,
  n_domain: 33,
  n_out_of_domain: 7,
  judge_model: "claude-haiku-4-5",
};
