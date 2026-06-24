from __future__ import annotations

from statistics import mean

from .models import EventItem, RankedEvent, ScoreBreakdown, StructuredNewsItem


def score_events(events: list[EventItem], structured: list[StructuredNewsItem]) -> list[RankedEvent]:
    news_by_id = {item.news_id: item for item in structured}
    ranked: list[RankedEvent] = []

    for event in events:
        related = [news_by_id[news_id] for news_id in event.related_news_ids if news_id in news_by_id]
        breakdown = _score_breakdown(event, related)
        # Weighted importance: business > source > tech > impact, exclude risk
        weights = {
            "business_impact": 5,
            "source_authority": 4,
            "technical_impact": 3,
            "impact_scope": 2,
            "novelty": 1,
            "multi_source_support": 1,
            "opportunity_level": 1,
            "recency": 1,
        }
        dims = breakdown.model_dump()
        weighted_sum = sum(v * weights.get(k, 1) for k, v in dims.items() if k != "risk_level")
        total_weight = sum(weights.get(k, 1) for k in dims if k != "risk_level")
        final = round(weighted_sum / total_weight, 2)
        ranked.append(
            RankedEvent(
                event_id=event.event_id,
                event_name=event.event_name,
                final_importance_score=final,
                rank=0,
                score_breakdown=breakdown,
                ranking_reason=_ranking_reason(event, breakdown, related),
                supporting_evidence=event.evidence[:5],
                confidence=event.confidence,
            )
        )

    ranked.sort(key=lambda item: item.final_importance_score, reverse=True)
    for index, event in enumerate(ranked, start=1):
        event.rank = index
    return ranked


def _score_breakdown(event: EventItem, related: list[StructuredNewsItem]) -> ScoreBreakdown:
    # Source credibility by name, not just type
    _AUTHORITY_MAP: dict[str, int] = {
        "arXiv": 5, "OpenAI News": 5, "Google DeepMind Blog": 5,
        "TechCrunch AI": 4, "The Verge": 4, "36氪": 4,
        "量子位": 3, "Hacker News": 2,
    }
    sources = {item.source for item in related}
    source_authority = max(
        (_AUTHORITY_MAP.get(s, 3) for s in sources), default=0
    )
    # Multi-source boost: different outlets corroborating = stronger signal
    if len(sources) >= 2:
        source_authority = min(5, source_authority + 1)

    multi_source_support = 5 if len({item.source for item in related}) >= 2 else 3 if related else 0
    risk_level = _granular_score(event.risk_tags, related, event.confidence, event.event_id, "risk")
    opportunity_level = _granular_score(
        event.opportunity_tags, related, event.confidence, event.event_id, "opp"
    )

    impact_scope = 0
    if event.impact_scope:
        impact_scope = min(5, 2 + len(set(event.impact_scope)))
    if event.industry_area in {"foundation_model", "ai_infrastructure", "policy_regulation"}:
        impact_scope = max(impact_scope, 4)

    novelty = 3
    if event.event_type in {"model_release", "regulation", "funding", "security_risk"}:
        novelty = 4
    if event.event_type in {"research", "business_update", "other"}:
        novelty = 3

    technical_impact = 4 if event.industry_area in {
        "foundation_model",
        "ai_agent",
        "multimodal_ai",
        "ai_infrastructure",
        "chip_compute",
        "research",
    } else 2

    business_impact = 4 if event.industry_area in {
        "enterprise_ai",
        "capital_market",
        "ai_infrastructure",
        "chip_compute",
        "consumer_ai",
    } else 2
    if event.event_type in {"funding", "partnership", "acquisition", "business_update"}:
        business_impact = max(business_impact, 4)

    confidence_penalty = 1 if event.confidence == "low" else 0

    return ScoreBreakdown(
        impact_scope=max(0, impact_scope - confidence_penalty),
        source_authority=max(0, source_authority - confidence_penalty),
        novelty=max(0, novelty - confidence_penalty),
        multi_source_support=max(0, multi_source_support - confidence_penalty),
        technical_impact=max(0, technical_impact - confidence_penalty),
        business_impact=max(0, business_impact - confidence_penalty),
        risk_level=risk_level,
        opportunity_level=opportunity_level,
        recency=5,
    )


def _granular_score(
    tags: list[str],
    related: list[StructuredNewsItem],
    confidence: str,
    event_id: str,
    kind: str,
) -> float:
    """Compute a granular 0-5 score with 3-decimal precision for matrix differentiation."""
    distinct = set(t for t in tags if t != "none")
    if not distinct:
        base = 0.0
    else:
        # Base from tag count: 1 tag=2.0, 2 tags=3.0, 3+ tags=4.0
        n = len(distinct)
        base = min(5.0, 1.5 + n * 0.8)

    # Adjust by source count (more sources covering risk/opp = higher)
    source_count = len({item.source for item in related})
    source_bonus = min(0.5, source_count * 0.12)

    # Confidence modifier
    conf_mod = {"high": 0.15, "medium": 0.0, "low": -0.15}[confidence]

    # Tiny unique fraction from event_id hash (0.000–0.099)
    import hashlib
    h = int(hashlib.sha1(f"{kind}:{event_id}".encode()).hexdigest()[:3], 16)
    unique = (h % 100) / 1000

    score = base + source_bonus + conf_mod + unique
    return round(max(0.0, min(5.0, score)), 3)


def _ranking_reason(
    event: EventItem,
    breakdown: ScoreBreakdown,
    related: list[StructuredNewsItem],
) -> str:
    sources = ", ".join(sorted({item.source for item in related})) or "unknown source"
    return (
        f"该事件来自 {sources}，影响范围评分 {breakdown.impact_scope}，"
        f"来源权威性评分 {breakdown.source_authority}，技术影响评分 "
        f"{breakdown.technical_impact}，商业影响评分 {breakdown.business_impact}。"
    )

