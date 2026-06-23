from __future__ import annotations

from daily_ai_insight.cleaning import clean_news_items
from daily_ai_insight.config import load_config
from daily_ai_insight.fetchers import _raw_item
from daily_ai_insight.models import CandidateSource


def test_load_config_defaults() -> None:
    config = load_config()
    assert config.report.timezone == "Asia/Shanghai"
    assert config.report.window_days == 3
    assert config.llm.provider == "deepseek"
    assert config.frontend_data_output.name == "latest.json"


def test_clean_news_filters_missing_required_fields() -> None:
    candidate = CandidateSource(
        source_name="Test RSS",
        source_type="rss",
        access_method="rss",
        language="en",
        coverage="test",
        enabled=True,
    )
    valid = _raw_item(
        candidate=candidate,
        title="AI model release",
        url="https://example.com/a",
        source="Example",
        published_at="2026-06-24T10:00:00+08:00",
        summary="A sufficiently descriptive AI news summary about a release and its impact.",
        content=None,
        raw_payload={},
    )
    missing_title = _raw_item(
        candidate=candidate,
        title=None,
        url="https://example.com/b",
        source="Example",
        published_at="2026-06-24T10:00:00+08:00",
        summary="Another sufficiently descriptive AI news summary.",
        content=None,
        raw_payload={},
    )

    cleaned = clean_news_items(
        [valid, missing_title],
        timezone="Asia/Shanghai",
        window_days=3,
    )
    assert [item.news_id for item in cleaned] == [valid.news_id]
    assert cleaned[0].quality_score > 0.7

