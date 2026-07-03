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
