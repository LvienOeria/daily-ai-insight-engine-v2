import { useMemo, useState } from "react";
import { ExternalLink, Search } from "lucide-react";
import type { EventItem, RankedEvent, StructuredNewsItem } from "../types";
import { getEventSources, getNewsById, getRankedByEventId } from "../utils";

/* ---- label maps ---- */
const TYPE_LABELS: Record<string, string> = {
  product_release: "产品发布", model_release: "模型发布", funding: "融资",
  acquisition: "收购", partnership: "合作", regulation: "监管政策",
  research: "学术研究", open_source: "开源", infrastructure: "基础设施",
  security_risk: "安全风险", business_update: "业务更新",
  market_commentary: "市场评论", other: "其他",
};
const AREA_LABELS: Record<string, string> = {
  foundation_model: "基础模型", ai_agent: "AI Agent", multimodal_ai: "多模态AI",
  ai_infrastructure: "AI基础设施", chip_compute: "芯片算力", enterprise_ai: "企业AI",
  consumer_ai: "消费AI", developer_tools: "开发者工具", ai_safety: "AI安全",
  policy_regulation: "政策监管", research: "研究", capital_market: "资本市场", other: "其他",
};

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
      ].join(" ").toLowerCase();
      return haystack.includes(query.toLowerCase().trim());
    });

  return (
    <section className="section">
      <div className="section-heading stacked-heading">
        <div>
          <h2>Events</h2>
          <span>{filtered.length} / {events.length}</span>
        </div>
        <label className="search-box">
          <Search size={16} aria-hidden />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="搜索实体、主题、类型..."
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
            {event.published_at ? formatDate(event.published_at) : ""}
            {ranked ? <span className="rank-badge">#{ranked.rank}</span> : null}
            <span className="type-chip">{TYPE_LABELS[event.event_type] || event.event_type}</span>
            <span className="area-chip">{AREA_LABELS[event.industry_area] || event.industry_area}</span>
          </p>
          <h3>{event.event_name}</h3>
        </div>
        <span className={`confidence ${event.confidence}`}>{event.confidence}</span>
      </header>
      {event.core_topic ? <p className="event-topic">{event.core_topic}</p> : null}
      <div className="tag-row">
        {event.main_entities.slice(0, 6).map((e) => <span key={e}>{e}</span>)}
        {event.technologies.slice(0, 4).map((t) => <span key={t}>{t}</span>)}
      </div>
      <div className="event-stats">
        <div><span>Score</span><strong>{ranked?.final_importance_score ?? "—"}</strong></div>
        <div><span>Event ID</span><code>{event.event_id}</code></div>
        <div><span>News</span><strong>{event.related_news_ids.length}</strong></div>
      </div>
      {ranked?.score_breakdown ? (
        <div className="breakdown-grid">
          {Object.entries(ranked.score_breakdown).map(([name, value]) => (
            <div key={name}><span>{name.replace(/_/g, " ")}</span><strong>{value}</strong></div>
          ))}
        </div>
      ) : null}
      <div className="source-links">
        <h4>来源链接</h4>
        {sources.length === 0 ? (
          <p className="muted">无可用链接</p>
        ) : (
          <ul>
            {sources.map((s) => (
              <li key={s.news_id}>
                {s.url ? (
                  <a href={s.url} target="_blank" rel="noreferrer">
                    <ExternalLink size={14} />
                    <span>{s.source}: {s.title.slice(0, 80)}</span>
                  </a>
                ) : (
                  <span>{s.source}: {s.title.slice(0, 80)}</span>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
      <div className="evidence-block">
        <h4>证据</h4>
        <ul>
          {(event.evidence.length ? event.evidence : event.key_facts).slice(0, 4).map((ev) => (
            <li key={ev}>{ev}</li>
          ))}
        </ul>
      </div>
    </article>
  );
}
