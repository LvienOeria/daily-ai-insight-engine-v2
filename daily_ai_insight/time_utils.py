from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from dateutil import parser


def now_in_timezone(timezone: str) -> datetime:
    return datetime.now(ZoneInfo(timezone)).replace(microsecond=0)


def report_window_start(timezone: str, days: int) -> datetime:
    return now_in_timezone(timezone) - timedelta(days=days)


def normalize_datetime(value: str | None, timezone: str) -> str | None:
    if not value:
        return None
    try:
        parsed = parser.parse(value)
    except (TypeError, ValueError, OverflowError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=ZoneInfo(timezone))
    return parsed.astimezone(ZoneInfo(timezone)).replace(microsecond=0).isoformat()


def is_recent(value: str | None, timezone: str, days: int) -> bool:
    normalized = normalize_datetime(value, timezone)
    if not normalized:
        return False
    parsed = parser.parse(normalized)
    return parsed >= report_window_start(timezone, days)

