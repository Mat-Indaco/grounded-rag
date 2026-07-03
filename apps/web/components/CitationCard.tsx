import type { Citation } from "@/lib/types";

export function CitationCard({ citation }: { citation: Citation }) {
  return (
    <div className="citation">
      <div className="meta">
        <span className="title">{citation.document_title}</span>
        <span>similitud {citation.similarity.toFixed(3)}</span>
      </div>
      <div>{citation.snippet}</div>
    </div>
  );
}
