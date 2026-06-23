from __future__ import annotations

from collections import Counter
from statistics import mean

from .models import EventItem, RankedEvent, StructuredNewsItem, VisualizationData, utc_now_iso


def build_visualization_data(
    structured: list[StructuredNewsItem],
    events: list[EventItem],
    ranked_events: list[RankedEvent],
) -> VisualizationData:
    source_type_counts = Counter(item.source_type for item in structured)
    event_type_counts = Counter(event.event_type for event in events)
    industry_counts = Counter(item.industry_area for item in structured)
    technology_counts: Counter[str] = Counter()
    for item in structured:
        technology_counts.update(item.technologies)

    risk_opportunity = []
    event_by_id = {event.event_id: event for event in events}
    for ranked in ranked_events:
        event = event_by_id.get(ranked.event_id)
        if not event:
            continue
        risk = ranked.score_breakdown.risk_level
        opportunity = ranked.score_breakdown.opportunity_level
        risk_opportunity.append(
            {
                "event_id": event.event_id,
                "event_name": event.event_name,
                "risk_level": risk,
                "opportunity_level": opportunity,
                "confidence": event.confidence,
                "event_type": event.event_type,
            }
        )

    return VisualizationData(
        generated_at=utc_now_iso(),
        source_type_distribution=_counter_rows(source_type_counts),
        event_type_distribution=_counter_rows(event_type_counts),
        industry_area_distribution=_counter_rows(industry_counts),
        technology_distribution=_counter_rows(technology_counts, limit=12),
        top_event_scores=[
            {
                "event_id": event.event_id,
                "event_name": event.event_name,
                "rank": event.rank,
                "score": event.final_importance_score,
                "confidence": event.confidence,
            }
            for event in ranked_events[:5]
        ],
        risk_opportunity_matrix=risk_opportunity,
    )


def summarize_score(values: list[int]) -> float:
    if not values:
        return 0.0
    return round(mean(values), 2)


def _counter_rows(counter: Counter, limit: int | None = None) -> list[dict[str, int | str]]:
    rows = [{"name": str(name), "count": count} for name, count in counter.most_common(limit)]
    return rows

