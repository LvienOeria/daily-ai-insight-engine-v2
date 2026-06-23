import { ExternalLink } from "lucide-react";
import type { EventItem, RankedEvent, StructuredNewsItem } from "../types";
import { getEventSources, getNewsById } from "../utils";

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString("zh-CN", {
      year: "numeric", month: "2-digit", day: "2-digit",
    });
  } catch { return iso.slice(0, 10); }
}

interface TopEventsProps {
  rankedEvents: RankedEvent[];
  events: EventItem[];
  news: StructuredNewsItem[];
}

export function TopEvents({ rankedEvents, events, news }: TopEventsProps) {
  const eventById = new Map(events.map((event) => [event.event_id, event]));
  const newsById = getNewsById(news);

  return (
    <section className="section">
      <div className="section-heading">
        <h2>Top Events</h2>
        <span>{rankedEvents.slice(0, 5).length} ranked</span>
      </div>
      <div className="event-list">
        {rankedEvents.slice(0, 5).map((ranked) => {
          const event = eventById.get(ranked.event_id);
          const sources = event ? getEventSources(event, newsById) : [];
          return (
            <article className="event-item" key={ranked.event_id}>
              <div className="rank">{ranked.rank}</div>
              <div className="event-body">
                <header>
                  <h3>{ranked.event_name}</h3>
                  <span className={`confidence ${ranked.confidence}`}>{ranked.confidence}</span>
                </header>
                {event?.published_at ? (
                  <p className="event-date">{formatDate(event.published_at)}</p>
                ) : null}
                <p>{ranked.ranking_reason}</p>
                {event ? (
                  <div className="tag-row">
                    {event.main_entities.slice(0, 6).map((entity) => (
                      <span key={entity}>{entity}</span>
                    ))}
                    {event.technologies.slice(0, 4).map((tech) => (
                      <span key={tech}>{tech}</span>
                    ))}
                  </div>
                ) : null}
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
                {sources.length ? (
                  <div className="source-links compact-links">
                    <h4>Source Links</h4>
                    <ul>
                      {sources.map((source) => (
                        <li key={source.news_id}>
                          {source.url ? (
                            <a href={source.url} target="_blank" rel="noreferrer">
                              <ExternalLink size={14} aria-hidden />
                              <span>{source.source}: {source.title}</span>
                            </a>
                          ) : (
                            <span>{source.source}: {source.title}</span>
                          )}
                        </li>
                      ))}
                    </ul>
                  </div>
                ) : null}
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
