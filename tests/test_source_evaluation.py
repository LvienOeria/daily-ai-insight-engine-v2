from __future__ import annotations

from daily_ai_insight.fetchers import _raw_item
from daily_ai_insight.models import CandidateSource
from daily_ai_insight.source_evaluation import evaluate_source


def test_complete_media_source_is_core() -> None:
    candidate = CandidateSource(
        source_name="Example Media",
        source_type="media",
        access_method="api",
        language="en",
        coverage="AI news",
        enabled=True,
    )
    items = [
        _raw_item(
            candidate=candidate,
            title=f"AI item {index}",
            url=f"https://example.com/{index}",
            source="Example",
            published_at="2026-06-24T09:00:00+08:00",
            summary="A complete AI news item with enough text for evaluation.",
            content=None,
            raw_payload={},
        )
        for index in range(3)
    ]

    profile = evaluate_source(candidate, items)
    assert profile.recommended_tier == "core"
    assert profile.field_completeness.title == "yes"
    assert profile.observed_item_count == 3


def test_community_source_is_auxiliary_even_when_complete() -> None:
    candidate = CandidateSource(
        source_name="Example Community",
        source_type="community",
        access_method="api",
        language="en",
        coverage="AI discussion",
        enabled=True,
    )
    items = [
        _raw_item(
            candidate=candidate,
            title="AI discussion",
            url="https://example.com/community",
            source="Example Community",
            published_at="2026-06-24T09:00:00+08:00",
            summary="A complete community signal about AI.",
            content=None,
            raw_payload={},
        )
    ]

    profile = evaluate_source(candidate, items)
    assert profile.recommended_tier == "auxiliary"
    assert "Community source" in " ".join(profile.weaknesses)

