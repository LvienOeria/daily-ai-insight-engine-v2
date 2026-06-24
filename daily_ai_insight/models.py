from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


SourceType = Literal[
    "news_api",
    "rss",
    "official",
    "community",
    "research",
    "manual_static",
    "media",
    "other",
]
AccessMethod = Literal["api", "rss", "direct_http", "other"]
Tier = Literal["core", "auxiliary", "future", "reject", "pending"]

EventType = Literal[
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
]
IndustryArea = Literal[
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
]
Sentiment = Literal["positive", "neutral", "negative", "mixed"]
Confidence = Literal["low", "medium", "high"]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CandidateSource(StrictModel):
    source_name: str
    source_type: SourceType
    access_method: AccessMethod
    documentation_url: str | None = None
    endpoint_url: str | None = None
    language: Literal["zh", "en", "mixed", "other"]
    coverage: str
    update_frequency: str | None = None
    cost_or_limit: str | None = None
    known_constraints: list[str] = Field(default_factory=list)
    enabled: bool = True
    query: str | None = None
    params: dict[str, Any] = Field(default_factory=dict)


class FieldCompleteness(StrictModel):
    title: Literal["yes", "no", "unknown"]
    summary_or_content: Literal["yes", "no", "partial", "unknown"]
    source: Literal["yes", "no", "unknown"]
    published_at: Literal["yes", "no", "unknown"]
    url: Literal["yes", "no", "unknown"]


class SourceProfile(StrictModel):
    source_name: str
    source_type: SourceType
    access_method: AccessMethod
    coverage: str
    language: Literal["zh", "en", "mixed", "other"]
    field_completeness: FieldCompleteness
    strengths: list[str]
    weaknesses: list[str]
    risks: list[str]
    observed_item_count: int = 0
    fetch_status: Literal["success", "partial", "failed", "skipped"] = "skipped"
    fetch_error: str | None = None
    recommended_tier: Tier
    reason: str


class RawNewsItem(StrictModel):
    news_id: str
    title: str | None = None
    url: str | None = None
    source: str | None = None
    source_type: SourceType
    published_at: str | None = None
    language: Literal["zh", "en", "mixed", "other"]
    summary: str | None = None
    content: str | None = None
    collected_at: str
    raw_provider: str
    raw_payload: dict[str, Any] = Field(default_factory=dict)
    missing_fields: list[str] = Field(default_factory=list)
    quality_score: float = 0

    @field_validator("quality_score")
    @classmethod
    def valid_quality_score(cls, value: float) -> float:
        if value < 0 or value > 1:
            raise ValueError("quality_score must be between 0 and 1")
        return value


class CleanedNewsItem(StrictModel):
    news_id: str
    title: str
    url: str | None = None
    source: str
    source_type: SourceType
    published_at: str
    language: Literal["zh", "en", "mixed", "other"]
    summary: str
    content: str | None = None
    collected_at: str
    missing_fields: list[str] = Field(default_factory=list)
    quality_score: float
    review_required: bool = False


class StructuredNewsItem(StrictModel):
    news_id: str
    title: str
    source: str
    source_type: SourceType
    published_at: str
    language: Literal["zh", "en", "mixed", "other"]
    url: str | None = None
    entities: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    event_type: EventType
    industry_area: IndustryArea
    key_facts: list[str] = Field(default_factory=list)
    summary: str
    sentiment: Sentiment = "neutral"
    impact_scope: list[str] = Field(default_factory=list)
    risk_tags: list[str] = Field(default_factory=list)
    opportunity_tags: list[str] = Field(default_factory=list)
    importance_score: int = Field(ge=1, le=5)
    confidence: Confidence = "medium"
    evidence: list[str] = Field(default_factory=list)
    suspected_hallucinations: list[str] = Field(default_factory=list)


class EventItem(StrictModel):
    event_id: str
    event_name: str
    related_news_ids: list[str]
    main_entities: list[str] = Field(default_factory=list)
    core_topic: str
    event_type: EventType
    industry_area: IndustryArea
    technologies: list[str] = Field(default_factory=list)
    key_facts: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    why_it_matters: str
    impact_scope: list[str] = Field(default_factory=list)
    risk_tags: list[str] = Field(default_factory=list)
    opportunity_tags: list[str] = Field(default_factory=list)
    confidence: Confidence
    published_at: str | None = None


class ScoreBreakdown(StrictModel):
    impact_scope: int = Field(ge=0, le=5)
    source_authority: int = Field(ge=0, le=5)
    novelty: int = Field(ge=0, le=5)
    multi_source_support: int = Field(ge=0, le=5)
    technical_impact: int = Field(ge=0, le=5)
    business_impact: int = Field(ge=0, le=5)
    risk_level: float = Field(ge=0, le=5)
    opportunity_level: float = Field(ge=0, le=5)
    recency: int = Field(ge=0, le=5)


class RankedEvent(StrictModel):
    event_id: str
    event_name: str
    final_importance_score: float
    rank: int
    score_breakdown: ScoreBreakdown
    ranking_reason: str
    supporting_evidence: list[str] = Field(default_factory=list)
    confidence: Confidence


class VisualizationData(StrictModel):
    generated_at: str
    source_type_distribution: list[dict[str, Any]]
    event_type_distribution: list[dict[str, Any]]
    industry_area_distribution: list[dict[str, Any]]
    technology_distribution: list[dict[str, Any]]
    top_event_scores: list[dict[str, Any]]
    risk_opportunity_matrix: list[dict[str, Any]]


class QualityCheckResult(StrictModel):
    passed: bool
    requirement_check: dict[str, bool]
    missing_items: list[str] = Field(default_factory=list)
    weak_points: list[str] = Field(default_factory=list)
    unsupported_claims: list[str] = Field(default_factory=list)
    suspected_hallucinations: list[str] = Field(default_factory=list)
    data_quality_issues: list[str] = Field(default_factory=list)
    visualization_issues: list[str] = Field(default_factory=list)
    recommended_fixes: list[str] = Field(default_factory=list)


class PipelineManifest(StrictModel):
    generated_at: str
    report_timezone: str
    report_window_days: int
    source_profiles: list[SourceProfile]
    raw_count: int
    cleaned_count: int
    structured_count: int
    event_count: int
    ranked_event_count: int
    notes: list[str] = Field(default_factory=list)


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
