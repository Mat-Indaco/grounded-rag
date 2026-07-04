export interface Citation {
  chunk_id: string;
  document_title: string;
  snippet: string;
  similarity: number;
}

export interface QueryResponse {
  answer: string;
  grounded: boolean;
  citations: Citation[];
}

export interface ChatTurn {
  question: string;
  response?: QueryResponse;
  error?: string;
  loading?: boolean;
}

export interface RecentQuery {
  question: string;
  grounded: boolean | null;
  tokens_in: number | null;
  tokens_out: number | null;
  latency_ms: number | null;
  created_at: string;
}

export interface Stats {
  total_queries: number;
  grounded_rate?: number;
  avg_latency_ms?: number | null;
  p50_latency_ms?: number | null;
  total_tokens_in?: number;
  total_tokens_out?: number;
  estimated_cost_usd?: number;
  recent: RecentQuery[];
}
