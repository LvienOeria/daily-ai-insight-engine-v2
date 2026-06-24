from __future__ import annotations

from pathlib import Path

from .config import PROJECT_ROOT
from .models import (
    CleanedNewsItem,
    EventItem,
    QualityCheckResult,
    RankedEvent,
    SourceProfile,
    StructuredNewsItem,
    VisualizationData,
)

_DOCS_DIR = PROJECT_ROOT / "docs"
_REQUIRED_DOCS = {
    "数据源决策.md",
    "结构化设计.md",
    "AI使用方式.md",
    "核心流程.md",
}


def run_quality_check(
    *,
    cleaned: list[CleanedNewsItem],
    structured: list[StructuredNewsItem],
    events: list[EventItem],
    ranked_events: list[RankedEvent],
    source_profiles: list[SourceProfile],
    visualization_data: VisualizationData,
    report_markdown: str,
    min_items: int,
    max_items: int,
) -> QualityCheckResult:
    missing_items: list[str] = []
    weak_points: list[str] = []
    data_quality_issues: list[str] = []
    visualization_issues: list[str] = []
    unsupported_claims: list[str] = []
    suspected_hallucinations: list[str] = []
    recommended_fixes: list[str] = []

    item_count_ok = min_items <= len(cleaned) <= max_items
    if not item_count_ok:
        missing_items.append(
            f"cleaned item count should be {min_items}-{max_items}, observed {len(cleaned)}"
        )

    required_ok = True
    for item in cleaned:
        missing = []
        if not item.title:
            missing.append("title")
        if not item.source:
            missing.append("source")
        if not item.published_at:
            missing.append("published_at")
        if not item.summary:
            missing.append("summary")
        if missing:
            required_ok = False
            data_quality_issues.append(f"{item.news_id} missing {', '.join(missing)}")

    structured_ok = len(structured) == len(cleaned) and bool(structured)
    if not structured_ok:
        missing_items.append("structured output count does not match cleaned items")

    evidence_ok = True
    for item in structured:
        if item.importance_score >= 4 and not item.evidence:
            evidence_ok = False
            data_quality_issues.append(f"{item.news_id} has high importance without evidence")

    events_ok = bool(events)
    if not events_ok:
        missing_items.append("event clustering output is empty")

    if len(ranked_events) < 3:
        weak_points.append("fewer than 3 ranked events are available")

    top_evidence_ok = True
    for event in ranked_events[:5]:
        if not event.supporting_evidence:
            top_evidence_ok = False
            data_quality_issues.append(f"{event.event_id} has no supporting evidence")
        if event.confidence == "low" and event.rank <= 3:
            weak_points.append(f"low-confidence event ranked in Top 3: {event.event_id}")

    visualization_ok = bool(visualization_data.top_event_scores)
    if not visualization_ok:
        visualization_issues.append("top_event_scores is empty")
    if len(visualization_data.source_type_distribution) == 0 and structured:
        visualization_issues.append("source_type_distribution is empty despite structured data")

    report_sections = [
        "今日概览",
        "今日 AI 领域 Top",
        "重要事件深度总结",
        "趋势判断",
        "风险与机会提示",
        "可视化说明",
        "数据与方法说明",
    ]
    report_sections_ok = all(section in report_markdown for section in report_sections)
    if not report_sections_ok:
        missing = [section for section in report_sections if section not in report_markdown]
        missing_items.append("report missing sections: " + ", ".join(missing))

    source_explained = bool(source_profiles)
    if not source_explained:
        missing_items.append("source evaluation profiles are missing")

    has_core_or_aux = any(
        profile.recommended_tier in {"core", "auxiliary"} and profile.observed_item_count > 0
        for profile in source_profiles
    )
    if not has_core_or_aux:
        weak_points.append("no observed source was evaluated as core or auxiliary")

    docs_exist = all((_DOCS_DIR / doc).exists() for doc in _REQUIRED_DOCS)
    has_schema_doc = (_DOCS_DIR / "结构化设计.md").exists()
    has_ai_usage_doc = (_DOCS_DIR / "AI使用方式.md").exists()
    has_process_doc = (_DOCS_DIR / "核心流程.md").exists()
    has_data_source_doc = (_DOCS_DIR / "数据源决策.md").exists()

    if not docs_exist:
        missing_docs = [doc for doc in _REQUIRED_DOCS if not (_DOCS_DIR / doc).exists()]
        missing_items.append("documentation missing: " + ", ".join(missing_docs))

    if not has_schema_doc:
        missing_items.append("schema design documentation is missing")
    if not has_ai_usage_doc:
        missing_items.append("AI usage / prompt design / error handling documentation is missing")
    if not has_process_doc:
        missing_items.append("core process documentation is missing")
    if not has_data_source_doc:
        missing_items.append("data source explanation documentation is missing")

    requirement_check = {
        "has_10_to_20_items": item_count_ok,
        "items_have_required_fields": required_ok,
        "has_schema": has_schema_doc,
        "schema_design_explained": has_schema_doc,
        "not_only_summary": structured_ok,
        "has_top_events": bool(ranked_events[:5]),
        "has_deep_analysis": "重要事件深度总结" in report_markdown,
        "has_trend_judgment": "趋势判断" in report_markdown,
        "has_risk_or_opportunity": "风险与机会提示" in report_markdown,
        "has_visualization": visualization_ok,
        "has_data_source_explanation": has_data_source_doc,
        "has_system_design": docs_exist,
        "has_ai_usage_prompt_error_handling": has_ai_usage_doc,
        "has_core_process": has_process_doc,
    }

    if not evidence_ok:
        unsupported_claims.append("one or more high-importance structured items lack evidence")
    if not top_evidence_ok:
        unsupported_claims.append("one or more Top events lack supporting evidence")
    if not item_count_ok:
        recommended_fixes.append("adjust source collection or manual observations to reach 10-20 items")
    if not report_sections_ok:
        recommended_fixes.append("regenerate report with all required sections")
    if visualization_issues:
        recommended_fixes.append("regenerate visualization data from structured artifacts")

    passed = (
        all(requirement_check.values())
        and not unsupported_claims
        and not suspected_hallucinations
        and not data_quality_issues
        and not visualization_issues
    )

    return QualityCheckResult(
        passed=passed,
        requirement_check=requirement_check,
        missing_items=missing_items,
        weak_points=weak_points,
        unsupported_claims=unsupported_claims,
        suspected_hallucinations=suspected_hallucinations,
        data_quality_issues=data_quality_issues,
        visualization_issues=visualization_issues,
        recommended_fixes=recommended_fixes,
    )
