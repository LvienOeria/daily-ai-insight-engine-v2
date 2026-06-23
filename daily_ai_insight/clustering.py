from __future__ import annotations

import json

from .io_utils import stable_id
from .llm import DeepSeekClient
from .models import EventItem, StructuredNewsItem


def cluster_events(
    structured: list[StructuredNewsItem],
    *,
    llm: DeepSeekClient | None,
    mock_llm: bool = False,
) -> list[EventItem]:
    if mock_llm or llm is None:
        return [_single_item_event(item) for item in structured]

    payload = {"items": [item.model_dump(mode="json") for item in structured]}
    response = llm.complete_json(
        system=_CLUSTERING_SYSTEM,
        user=json.dumps(payload, ensure_ascii=False),
    )
    records = response.get("events")
    if not isinstance(records, list):
        raise ValueError("clustering LLM output must contain events list")
    valid_news_ids = {item.news_id for item in structured}
    events = [EventItem.model_validate(record) for record in records]
    for event in events:
        unknown = set(event.related_news_ids) - valid_news_ids
        if unknown:
            raise ValueError(f"event {event.event_id} references unknown news IDs: {unknown}")
        if not event.evidence:
            raise ValueError(f"event {event.event_id} has no evidence")
    return events


_CLUSTERING_SYSTEM = """
You are the event-clustering module for the Daily AI Insight Engine.
Return valid JSON only: {"events": [EventItem, ...]}.

Group records only when they describe the same concrete event or tightly connected event chain.
Do not group records merely because they share a broad topic, same day, same sentiment,
or the same company with different facts.

Each event must include:
event_id, event_name, related_news_ids, main_entities, core_topic, event_type,
industry_area, technologies, key_facts, evidence, why_it_matters, impact_scope,
risk_tags, opportunity_tags, confidence.

Every related_news_ids value must come from the input. Every event must include evidence.
Single-news events are allowed when they are well supported.
"""


def _single_item_event(item: StructuredNewsItem) -> EventItem:
    event_name = item.title[:120]
    return EventItem(
        event_id=stable_id("event", item.news_id, item.title),
        event_name=event_name,
        related_news_ids=[item.news_id],
        main_entities=item.entities,
        core_topic=item.summary[:180],
        event_type=item.event_type,
        industry_area=item.industry_area,
        technologies=item.technologies,
        key_facts=item.key_facts,
        evidence=item.evidence or item.key_facts,
        why_it_matters=_why_it_matters(item),
        impact_scope=item.impact_scope,
        risk_tags=item.risk_tags,
        opportunity_tags=item.opportunity_tags,
        confidence=item.confidence,
    )


def _why_it_matters(item: StructuredNewsItem) -> str:
    if item.importance_score >= 4:
        return "该条信息在单新闻重要性评分中较高，可能影响相关技术、企业或行业议题。"
    return "该条信息提供了当日 AI 领域的补充信号，重要性需结合其他事件判断。"

