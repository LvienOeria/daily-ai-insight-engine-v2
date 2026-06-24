from __future__ import annotations

from collections import Counter

from .models import (
    CandidateSource,
    FieldCompleteness,
    RawNewsItem,
    SourceProfile,
    Tier,
)


def _ratio(items: list[RawNewsItem], field: str) -> float:
    if not items:
        return 0.0
    present = 0
    for item in items:
        value = getattr(item, field)
        if value:
            present += 1
    return present / len(items)


def _field_status(ratio: float, partial_allowed: bool = False) -> str:
    if ratio >= 0.9:
        return "yes"
    if ratio > 0 and partial_allowed:
        return "partial"
    if ratio > 0:
        return "unknown"
    return "no"


def _recommend_tier(candidate: CandidateSource, items: list[RawNewsItem], error: str | None) -> Tier:
    if error and not items:
        return "future"
    if not items:
        return "reject"

    title_ratio = _ratio(items, "title")
    source_ratio = _ratio(items, "source")
    date_ratio = _ratio(items, "published_at")
    text_ratio = max(_ratio(items, "summary"), _ratio(items, "content"))

    required_ok = title_ratio >= 0.9 and source_ratio >= 0.9 and date_ratio >= 0.8
    text_ok = text_ratio >= 0.8
    if required_ok and text_ok:
        if candidate.source_type == "community":
            return "auxiliary"
        return "core"
    if required_ok and text_ratio > 0:
        return "auxiliary"
    return "reject"


def evaluate_source(
    candidate: CandidateSource,
    items: list[RawNewsItem],
    error: str | None = None,
) -> SourceProfile:
    text_ratio = max(_ratio(items, "summary"), _ratio(items, "content"))
    field_completeness = FieldCompleteness(
        title=_field_status(_ratio(items, "title")),  # type: ignore[arg-type]
        summary_or_content=_field_status(text_ratio, partial_allowed=True),  # type: ignore[arg-type]
        source=_field_status(_ratio(items, "source")),  # type: ignore[arg-type]
        published_at=_field_status(_ratio(items, "published_at")),  # type: ignore[arg-type]
        url=_field_status(_ratio(items, "url")),  # type: ignore[arg-type]
    )

    tier = _recommend_tier(candidate, items, error)
    missing_counter: Counter[str] = Counter()
    for item in items:
        missing_counter.update(item.missing_fields)

    weaknesses: list[str] = []
    if missing_counter:
        weaknesses.append(
            "Observed missing fields: "
            + ", ".join(f"{name}={count}" for name, count in missing_counter.most_common())
        )
    if candidate.source_type == "community":
        weaknesses.append("Community source; use as auxiliary signal unless item is complete.")
    if error:
        weaknesses.append(f"Fetch issue: {error}")

    risks = list(candidate.known_constraints)

    strengths = [candidate.coverage]
    if items:
        strengths.append(f"Observed {len(items)} candidate items during fetch attempt.")

    if error and items:
        fetch_status = "partial"
    elif error:
        fetch_status = "failed"
    else:
        fetch_status = "success" if items else "skipped"

    return SourceProfile(
        source_name=candidate.source_name,
        source_type=candidate.source_type,
        access_method=candidate.access_method,
        coverage=candidate.coverage,
        language=candidate.language,
        field_completeness=field_completeness,
        strengths=strengths,
        weaknesses=weaknesses,
        risks=risks,
        observed_item_count=len(items),
        fetch_status=fetch_status,  # type: ignore[arg-type]
        fetch_error=error,
        recommended_tier=tier,
        reason=_reason_for_tier(tier, candidate, items, error),
    )


def _reason_for_tier(
    tier: Tier,
    candidate: CandidateSource,
    items: list[RawNewsItem],
    error: str | None,
) -> str:
    if tier == "core":
        return "Observed results satisfy required fields and are suitable for the main dataset."
    if tier == "auxiliary":
        return "Observed results provide useful signal but should not be the sole Top-event evidence."
    if tier == "future":
        return f"Fetch path needs implementation or access before MVP use: {error}"
    if tier == "reject":
        return "Observed results are missing required fields or produced no usable items."
    return "Pending additional observation."

