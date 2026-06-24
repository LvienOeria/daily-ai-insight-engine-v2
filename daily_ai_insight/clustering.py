from __future__ import annotations

import json

from .io_utils import stable_id
from .llm import DeepSeekClient
from .models import EventItem, StructuredNewsItem
from .skill_loader import load_prompt


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
        system=load_prompt("event-clustering"),
        user=json.dumps(payload, ensure_ascii=False),
    )
    records = response.get("events")
    if not isinstance(records, list):
        raise ValueError("clustering LLM output must contain events list")
    valid_news_ids = {item.news_id for item in structured}
    events = [
        EventItem.model_validate(_normalize_event_record(record, valid_news_ids))
        for record in records
    ]
    for event in events:
        unknown = set(event.related_news_ids) - valid_news_ids
        if unknown:
            raise ValueError(f"event {event.event_id} references unknown news IDs: {unknown}")
        if not event.evidence:
            raise ValueError(f"event {event.event_id} has no evidence")
    return events


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


def _normalize_event_record(record: dict, valid_news_ids: set[str]) -> dict:
    for field in [
        "related_news_ids",
        "main_entities",
        "technologies",
        "key_facts",
        "evidence",
        "impact_scope",
        "risk_tags",
        "opportunity_tags",
    ]:
        record[field] = _as_list(record.get(field))

    record["related_news_ids"] = [
        news_id for news_id in record["related_news_ids"] if news_id in valid_news_ids
    ]

    if not record.get("event_id"):
        record["event_id"] = stable_id(
            "event",
            ",".join(record.get("related_news_ids", [])),
            record.get("event_name"),
        )
    if not record.get("event_name"):
        record["event_name"] = record.get("core_topic") or record["event_id"]
    if not record.get("core_topic"):
        record["core_topic"] = record.get("event_name") or record["event_id"]
    if not record.get("why_it_matters"):
        record["why_it_matters"] = "该事件的重要性需要结合结构化证据和评分结果判断。"

    if record.get("event_type") not in {
        "product_release",
        "model_release",
        "funding",
        "acquisition",
        "partnership",
        "regulation",
        "research",
        "open_source",
        "infrastructure",
        "security_risk",
        "business_update",
        "market_commentary",
        "other",
    }:
        record["event_type"] = "other"

    if record.get("industry_area") not in {
        "foundation_model",
        "ai_agent",
        "multimodal_ai",
        "ai_infrastructure",
        "chip_compute",
        "enterprise_ai",
        "consumer_ai",
        "developer_tools",
        "ai_safety",
        "policy_regulation",
        "research",
        "capital_market",
        "other",
    }:
        record["industry_area"] = "other"

    if record.get("confidence") not in {"low", "medium", "high"}:
        record["confidence"] = "medium"
    if not record.get("evidence"):
        record["evidence"] = record.get("key_facts", [])
    if not record.get("risk_tags"):
        record["risk_tags"] = ["none"]
    if not record.get("opportunity_tags"):
        record["opportunity_tags"] = ["none"]

    return record


def _as_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    return [str(value)]


def _why_it_matters(item: StructuredNewsItem) -> str:
    parts: list[str] = []
    if item.entities:
        parts.append(f"涉及主体: {'、'.join(item.entities[:5])}")
    if item.impact_scope and item.impact_scope != ["none"]:
        parts.append(f"影响范围: {'、'.join(item.impact_scope)}")
    if item.importance_score >= 4:
        parts.append("该事件在单新闻评分中重要性较高，建议关注后续发展。")
    elif item.importance_score >= 3:
        parts.append("该事件提供了当日 AI 领域的重要信号。")
    else:
        parts.append("该事件为当日 AI 领域补充信息。")
    return "。".join(parts) if parts else "重要性需结合其他事件判断。"
