from __future__ import annotations

from .models import CleanedNewsItem, RawNewsItem
from .time_utils import is_recent, normalize_datetime


def clean_news_items(
    raw_items: list[RawNewsItem],
    *,
    timezone: str,
    window_days: int,
) -> list[CleanedNewsItem]:
    cleaned: list[CleanedNewsItem] = []
    seen_keys: set[str] = set()

    for item in raw_items:
        published_at = normalize_datetime(item.published_at, timezone)
        title = _compact(item.title)
        source = _compact(item.source)
        summary = _compact(item.summary or item.content)
        url = _compact(item.url)

        missing = []
        if not title:
            missing.append("title")
        if not source:
            missing.append("source")
        if not published_at:
            missing.append("published_at")
        if not summary:
            missing.append("summary_or_content")

        if missing:
            continue
        if not is_recent(published_at, timezone, window_days):
            continue

        dedupe_key = (url or f"{source}:{title}:{published_at}").lower()
        if dedupe_key in seen_keys:
            continue
        seen_keys.add(dedupe_key)

        quality_score = _quality_score(
            title=title,
            source=source,
            published_at=published_at,
            summary=summary,
            url=url,
            original=item.quality_score,
        )

        cleaned.append(
            CleanedNewsItem(
                news_id=item.news_id,
                title=title,
                url=url,
                source=source,
                source_type=item.source_type,
                published_at=published_at,
                language=item.language,
                summary=summary,
                content=_compact(item.content),
                collected_at=item.collected_at,
                missing_fields=missing,
                quality_score=quality_score,
                review_required=quality_score < 0.7,
            )
        )

    cleaned.sort(key=lambda row: row.published_at, reverse=True)
    return cleaned


def _compact(value: str | None) -> str | None:
    if value is None:
        return None
    text = " ".join(str(value).split())
    return text or None


def _quality_score(
    *,
    title: str | None,
    source: str | None,
    published_at: str | None,
    summary: str | None,
    url: str | None,
    original: float,
) -> float:
    score = 0.0
    score += 0.2 if title else 0
    score += 0.2 if source else 0
    score += 0.2 if published_at else 0
    score += 0.25 if summary and len(summary) >= 80 else 0.15 if summary else 0
    score += 0.15 if url else 0.05
    return max(0.0, min(1.0, round(max(score, original), 3)))

