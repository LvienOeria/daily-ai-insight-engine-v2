import { useMemo, useState } from "react";
import { ExternalLink, Search } from "lucide-react";
import type { EventItem, RankedEvent, StructuredNewsItem } from "../types";
import { getEventSources, getNewsById, getRankedByEventId } from "../utils";

interface EventsExplorerProps {
  events: EventItem[];
  rankedEvents: RankedEvent[];
  news: StructuredNewsItem[];
}

export function EventsExplorer({ events, rankedEvents, news }: EventsExplorerProps) {
  const [query, setQuery] = useState("");
  const newsById = useMemo(() => getNewsById(news), [news]);
  const rankedById = useMemo(() => getRankedByEventId(rankedEvents), [rankedEvents]);

  const filtered = events
    .map((event) => ({ event, ranked: rankedById.get(event.event_id) }))
    .sort((a, b) => (a.ranked?.rank ?? 999) - (b.ranked?.rank ?? 999))
    .filter(({ event }) => {
      const haystack = [
        event.event_name,
        event.core_topic,
        event.event_type,
        event.industry_area,
        event.main_entities.join(" "),
        event.technologies.join(" "),
      ]
        .join(" ")
        .toLowerCase();
      return haystack.includes(query.toLowerCase().trim());
    });

  return (
    <section className="section">
      <div className="section-heading stacked-heading">
        <div>
          <h2>All Events</h2>
          <span>{filtered.length} visible / {events.length} total</span>
        </div>
        <label className="search-box">
          <Search size={16} aria-hidden />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Filter by entity, topic, type..."
          />
        </label>
      </div>
      <div className="all-events-list">
        {filtered.map(({ event, ranked }) => (
          <EventCard
            key={event.event_id}
            event={event}
            ranked={ranked}
            sources={getEventSources(event, newsById)}
          />
        ))}
      </div>
    </section>
  );
}

interface EventCardProps {
  event: EventItem;
  ranked?: RankedEvent;
  sources: StructuredNewsItem[];
}

function formatDate(iso: string): string {
  try { return new Date(iso).toLocaleDateString("zh-CN", { year: "numeric", month: "2-digit", day: "2-digit" }); }
  catch { return iso.slice(0, 10); }
}

function EventCard({ event, ranked, sources }: EventCardProps) {
  return (
    <article className="event-card">
      <header>
        <div>
          <p className="event-kicker">
            {event.published_at ? formatDate(event.published_at) + " · " : ""}
            {ranked ? `#${ranked.rank}` : "unranked"} · {event.event_type} ·{" "}
            {event.industry_area}
          </p>
          <h3>{event.event_name}</h3>
        </div>
        <span className={`confidence ${event.confidence}`}>{event.confidence}</span>
      </header>
      <p>{event.core_topic}</p>
      <div className="tag-row">
        {event.main_entities.slice(0, 5).map((entity) => (
          <span key={entity}>{entity}</span>
        ))}
        {event.technologies.slice(0, 5).map((technology) => (
          <span key={technology}>{technology}</span>
        ))}
      </div>
      <dl className="score-grid">
        <div>
          <dt>Score</dt>
          <dd>{ranked?.final_importance_score ?? "n/a"}</dd>
        </div>
        <div>
          <dt>Event ID</dt>
          <dd>{event.event_id}</dd>
        </div>
        <div>
          <dt>News IDs</dt>
          <dd>{event.related_news_ids.join(", ")}</dd>
        </div>
      </dl>
      {ranked?.score_breakdown ? (
        <div className="breakdown-grid">
          {Object.entries(ranked.score_breakdown).map(([name, value]) => (
            <div key={name}>
              <span>{name.replace(/_/g, " ")}</span>
              <strong>{value}</strong>
            </div>
          ))}
        </div>
      ) : null}
      <div className="source-links">
        <h4>Source Links</h4>
        {sources.length === 0 ? (
          <p className="muted">No source URL available.</p>
        ) : (
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
        )}
      </div>
      <div className="evidence-block">
        <h4>Evidence</h4>
        <ul>
          {(event.evidence.length ? event.evidence : event.key_facts).slice(0, 4).map((evidence) => (
            <li key={evidence}>{evidence}</li>
          ))}
        </ul>
      </div>
    </article>
  );
}
