import { ExternalLink } from "lucide-react";
import type { EventItem, RankedEvent } from "../types";

interface TopEventsProps {
  rankedEvents: RankedEvent[];
  events: EventItem[];
}

export function TopEvents({ rankedEvents, events }: TopEventsProps) {
  const eventById = new Map(events.map((event) => [event.event_id, event]));

  return (
    <section className="section">
      <div className="section-heading">
        <h2>Top Events</h2>
        <span>{rankedEvents.slice(0, 5).length} ranked</span>
      </div>
      <div className="event-list">
        {rankedEvents.slice(0, 5).map((ranked) => {
          const event = eventById.get(ranked.event_id);
          return (
            <article className="event-item" key={ranked.event_id}>
              <div className="rank">{ranked.rank}</div>
              <div className="event-body">
                <header>
                  <h3>{ranked.event_name}</h3>
                  <span className={`confidence ${ranked.confidence}`}>{ranked.confidence}</span>
                </header>
                <p>{ranked.ranking_reason}</p>
                <dl>
                  <div>
                    <dt>Score</dt>
                    <dd>{ranked.final_importance_score}</dd>
                  </div>
                  <div>
                    <dt>Event ID</dt>
                    <dd>{ranked.event_id}</dd>
                  </div>
                  <div>
                    <dt>News IDs</dt>
                    <dd>{event?.related_news_ids.join(", ") || "n/a"}</dd>
                  </div>
                </dl>
                <ul className="evidence-list">
                  {(ranked.supporting_evidence.length
                    ? ranked.supporting_evidence
                    : event?.evidence || []
                  ).map((evidence) => (
                    <li key={evidence}>
                      <ExternalLink size={14} aria-hidden />
                      <span>{evidence}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}

