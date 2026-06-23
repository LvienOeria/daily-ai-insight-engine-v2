from __future__ import annotations

import re
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import feedparser
import httpx

from .config import AppConfig
from .io_utils import read_json, stable_id
from .models import CandidateSource, RawNewsItem, utc_now_iso
from .time_utils import normalize_datetime, report_window_start


class SourceFetchError(RuntimeError):
    pass


@dataclass
class FetchResult:
    candidate: CandidateSource
    items: list[RawNewsItem]
    error: str | None = None


def load_candidates(path: Path) -> list[CandidateSource]:
    raw_sources = read_json(path)
    return [CandidateSource.model_validate(raw) for raw in raw_sources]


def fetch_candidate(candidate: CandidateSource, config: AppConfig) -> FetchResult:
    if not candidate.enabled:
        return FetchResult(candidate=candidate, items=[], error="source disabled")
    try:
        if candidate.access_method == "rss":
            return FetchResult(candidate, _fetch_rss(candidate, config))
        if candidate.source_name == "arXiv AI Search":
            return FetchResult(candidate, _fetch_arxiv(candidate, config))
        if candidate.source_name == "Hacker News Algolia AI Search":
            return FetchResult(candidate, _fetch_hacker_news(candidate, config))
        if candidate.access_method == "deepseek_websearch":
            return FetchResult(candidate, _fetch_websearch_observations(candidate, config))
    except Exception as exc:  # Fetch failures are recorded for source evaluation.
        return FetchResult(candidate=candidate, items=[], error=str(exc))
    return FetchResult(candidate=candidate, items=[], error="unsupported source configuration")


def _fetch_rss(candidate: CandidateSource, config: AppConfig) -> list[RawNewsItem]:
    if not candidate.endpoint_url:
        raise SourceFetchError("missing RSS endpoint_url")
    parsed = feedparser.parse(candidate.endpoint_url)
    if parsed.bozo and not parsed.entries:
        raise SourceFetchError(f"RSS parse failed: {parsed.bozo_exception}")

    items: list[RawNewsItem] = []
    for entry in parsed.entries:
        published = (
            getattr(entry, "published", None)
            or getattr(entry, "updated", None)
            or getattr(entry, "created", None)
        )
        published_at = normalize_datetime(published, config.report.timezone)
        summary = _clean_text(getattr(entry, "summary", None) or getattr(entry, "description", None))
        title = _clean_text(getattr(entry, "title", None))
        url = getattr(entry, "link", None)
        items.append(
            _raw_item(
                candidate=candidate,
                title=title,
                url=url,
                source=candidate.source_name.replace(" RSS", ""),
                published_at=published_at,
                summary=summary,
                content=None,
                raw_payload=_safe_payload(dict(entry)),
            )
        )
    return items


def _fetch_arxiv(candidate: CandidateSource, config: AppConfig) -> list[RawNewsItem]:
    if not candidate.endpoint_url:
        raise SourceFetchError("missing arXiv endpoint_url")
    params = dict(candidate.params)
    params["search_query"] = candidate.query or "cat:cs.AI"

    response = httpx.get(candidate.endpoint_url, params=params, timeout=30)
    response.raise_for_status()

    root = ET.fromstring(response.text)
    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom",
    }
    items: list[RawNewsItem] = []
    for entry in root.findall("atom:entry", ns):
        title = _clean_text(_xml_text(entry, "atom:title", ns))
        summary = _clean_text(_xml_text(entry, "atom:summary", ns))
        published_at = normalize_datetime(_xml_text(entry, "atom:published", ns), config.report.timezone)
        url = _xml_text(entry, "atom:id", ns)
        authors = [
            _clean_text(author.findtext("atom:name", default="", namespaces=ns))
            for author in entry.findall("atom:author", ns)
        ]
        raw_payload = {
            "id": url,
            "title": title,
            "summary": summary,
            "authors": [author for author in authors if author],
            "published": _xml_text(entry, "atom:published", ns),
            "updated": _xml_text(entry, "atom:updated", ns),
        }
        items.append(
            _raw_item(
                candidate=candidate,
                title=title,
                url=url,
                source="arXiv",
                published_at=published_at,
                summary=summary,
                content=None,
                raw_payload=raw_payload,
            )
        )
        time.sleep(0.1)
    return items


def _fetch_hacker_news(candidate: CandidateSource, config: AppConfig) -> list[RawNewsItem]:
    if not candidate.endpoint_url:
        raise SourceFetchError("missing Hacker News endpoint_url")
    params = dict(candidate.params)
    params["query"] = candidate.query or "AI"
    start = report_window_start(config.report.timezone, config.report.window_days)
    params["numericFilters"] = f"created_at_i>{int(start.timestamp())}"

    response = httpx.get(candidate.endpoint_url, params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()

    items: list[RawNewsItem] = []
    for hit in payload.get("hits", []):
        title = _clean_text(hit.get("title") or hit.get("story_title"))
        url = hit.get("url") or hit.get("story_url")
        created_at = normalize_datetime(hit.get("created_at"), config.report.timezone)
        summary = _clean_text(hit.get("story_text") or hit.get("comment_text") or title)
        items.append(
            _raw_item(
                candidate=candidate,
                title=title,
                url=url or f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                source="Hacker News",
                published_at=created_at,
                summary=summary,
                content=None,
                raw_payload=hit,
            )
        )
    return items


def _fetch_websearch_observations(candidate: CandidateSource, config: AppConfig) -> list[RawNewsItem]:
    websearch_config = config.defaults["source_selection"]["chinese_websearch"]
    observation_file = Path(
        config.root
        / (
            websearch_config.get("observation_file")
            or "data/manual/chinese_websearch_observations.json"
        )
    )
    if not observation_file.exists():
        raise SourceFetchError(
            "DeepSeek websearch has no standalone Chat Completions endpoint in the current "
            "implementation. Add observations to "
            f"{observation_file.relative_to(config.root)} after running allowlisted DeepSeek websearch."
        )

    observations = read_json(observation_file)
    if not isinstance(observations, list):
        raise SourceFetchError("websearch observation file must contain a JSON array")

    allowed_domains = {
        domain
        for source in websearch_config["allowed_sources"]
        for domain in source["domains"]
    }
    items: list[RawNewsItem] = []
    for obs in observations:
        url = obs.get("url")
        if not _is_allowed_url(url, allowed_domains):
            continue
        source_name = obs.get("source") or obs.get("site") or candidate.source_name
        if not _observation_matches_candidate(candidate, source_name, url):
            continue
        summary = _clean_text(obs.get("snippet_or_content") or obs.get("summary") or obs.get("content"))
        published_at = normalize_datetime(
            obs.get("visible_published_at") or obs.get("published_at"),
            config.report.timezone,
        )
        items.append(
            _raw_item(
                candidate=candidate,
                title=_clean_text(obs.get("title")),
                url=url,
                source=source_name,
                published_at=published_at,
                summary=summary,
                content=_clean_text(obs.get("content")),
                raw_payload=obs,
                collected_at=obs.get("collected_at"),
            )
        )
    return items


def _raw_item(
    *,
    candidate: CandidateSource,
    title: str | None,
    url: str | None,
    source: str | None,
    published_at: str | None,
    summary: str | None,
    content: str | None,
    raw_payload: dict[str, Any],
    collected_at: str | None = None,
) -> RawNewsItem:
    missing = []
    if not title:
        missing.append("title")
    if not source:
        missing.append("source")
    if not published_at:
        missing.append("published_at")
    if not (summary or content):
        missing.append("summary_or_content")
    if not url:
        missing.append("url")

    quality = 1 - (len([m for m in missing if m != "url"]) / 4)
    if not url:
        quality -= 0.1
    quality = max(0.0, min(1.0, quality))

    return RawNewsItem(
        news_id=stable_id("news", source, title, url, published_at),
        title=title,
        url=url,
        source=source,
        source_type=candidate.source_type,
        published_at=published_at,
        language=candidate.language,
        summary=summary,
        content=content,
        collected_at=collected_at or utc_now_iso(),
        raw_provider=candidate.source_name,
        raw_payload=raw_payload,
        missing_fields=missing,
        quality_score=quality,
    )


def _xml_text(entry: ET.Element, path: str, ns: dict[str, str]) -> str | None:
    child = entry.find(path, ns)
    if child is None or child.text is None:
        return None
    return child.text


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def _safe_payload(payload: dict[str, Any]) -> dict[str, Any]:
    safe: dict[str, Any] = {}
    for key, value in payload.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            safe[key] = value
        elif isinstance(value, list):
            safe[key] = [
                item
                for item in value
                if isinstance(item, (str, int, float, bool)) or item is None
            ]
        else:
            safe[key] = str(value)
    return safe


def _is_allowed_url(url: str | None, allowed_domains: set[str]) -> bool:
    if not url:
        return False
    hostname = urlparse(url).hostname or ""
    return any(hostname == domain or hostname.endswith(f".{domain}") for domain in allowed_domains)


def _observation_matches_candidate(candidate: CandidateSource, source_name: str, url: str | None) -> bool:
    name = candidate.source_name
    hostname = urlparse(url or "").hostname or ""
    if "量子位" in name:
        return "qbitai.com" in hostname or "量子位" in source_name
    if "机器之心" in name:
        return "jiqizhixin.com" in hostname or "机器之心" in source_name
    if "知乎" in name:
        return "zhihu.com" in hostname or "知乎" in source_name
    return True

