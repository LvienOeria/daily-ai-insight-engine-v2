from __future__ import annotations

from daily_ai_insight.fetchers import _is_allowed_url


def test_chinese_websearch_allowlist_accepts_only_configured_domains() -> None:
    allowed = {"qbitai.com", "jiqizhixin.com", "zhihu.com"}
    assert _is_allowed_url("https://www.qbitai.com/2026/example", allowed)
    assert _is_allowed_url("https://www.jiqizhixin.com/articles/2026-06-24", allowed)
    assert _is_allowed_url("https://www.zhihu.com/question/123", allowed)
    assert not _is_allowed_url("https://example.com/ai", allowed)
    assert not _is_allowed_url(None, allowed)

