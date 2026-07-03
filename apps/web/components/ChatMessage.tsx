import type { ChatTurn } from "@/lib/types";
import { CitationCard } from "./CitationCard";

export function ChatMessage({ turn }: { turn: ChatTurn }) {
  return (
    <div className="turn">
      <div className="question">{turn.question}</div>

      {turn.loading && <div className="answer hint">Buscando en las fuentes…</div>}

      {turn.error && <div className="answer error">{turn.error}</div>}

      {turn.response && (
        <div className="answer">
          <span
            className={`badge ${turn.response.grounded ? "grounded" : "ungrounded"}`}
          >
            {turn.response.grounded ? "grounded" : "no encontrado en fuentes"}
          </span>
          <div>{turn.response.answer}</div>

          {turn.response.citations.length > 0 && (
            <div className="citations">
              <h3>Fuentes</h3>
              {turn.response.citations.map((c) => (
                <CitationCard key={c.chunk_id} citation={c} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
