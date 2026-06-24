"""Web scraper for fetching AI news from Chinese and English tech sites."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any
from urllib.parse import urljoin, urlparse
from zoneinfo import ZoneInfo

import httpx

_HTML_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")


def fetch_articles(
    site: str,
    homepage: str,
    source_name: str,
    source_type: str,
    language: str,
    max_results: int = 10,
) -> list[dict[str, Any]]:
    """Scrape article links from a homepage and fetch each article's metadata."""
    try:
        return _do_fetch(site, homepage, source_name, source_type, language, max_results)
    except Exception:
        return []


def _do_fetch(
    site: str,
    homepage: str,
    source_name: str,
    source_type: str,
    language: str,
    max_results: int,
) -> list[dict[str, Any]]:
    resp = httpx.get(
        homepage, timeout=15, follow_redirects=True,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        },
        verify=False,
    )
    resp.raise_for_status()
    html = resp.text
    results: list[dict[str, Any]] = []
    links = _extract_article_links(html)

    for link in links[:max_results * 3]:
        if len(results) >= max_results:
            break
        try:
            article_url = urljoin(homepage, link["href"])
            if not article_url.startswith("http"):
                continue
            art_resp = httpx.get(
                article_url, timeout=10, follow_redirects=True,
                headers={"User-Agent": "Mozilla/5.0"},
                verify=False,
            )
            if art_resp.status_code != 200:
                continue
            art_html = art_resp.text
            title = link.get("title") or _extract_title(art_html) or link.get("text", "")
            summary = _extract_meta_description(art_html)
            if not summary or len(summary) < 40:
                summary = _extract_first_paragraph(art_html) or _extract_text(art_html)[:500]
            published = (
                _extract_published(art_html)
                or _guess_published_from_url(article_url)
                or _guess_published_from_url(homepage)
            )
            if title and len(_clean(summary)) >= 30:
                results.append({
                    "title": _clean(title)[:200],
                    "url": article_url,
                    "source": source_name,
                    "source_type": source_type,
                    "summary": _clean(summary)[:500],
                    "published_at": published,
                    "language": language,
                })
        except Exception:
            continue
    return results


def _extract_article_links(html: str) -> list[dict[str, str]]:
    links: list[dict[str, str]] = []
    href_pattern = re.compile(
        r'<a\s[^>]*href\s*=\s*["\']([^"\']+)["\'][^>]*>(.*?)</a>',
        re.DOTALL | re.IGNORECASE,
    )
    title_pattern = re.compile(r'title\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
    seen: set[str] = set()
    for match in href_pattern.finditer(html):
        href = match.group(1)
        inner = match.group(2)
        text = _clean(_HTML_RE.sub(" ", inner))
        if not _looks_like_article(href) or len(text) < 8:
            continue
        if href in seen:
            continue
        seen.add(href)
        link = {"href": href, "text": text}
        title_match = title_pattern.search(match.group(0))
        if title_match:
            link["title"] = _clean(title_match.group(1))
        links.append(link)
    return links


def _looks_like_article(href: str) -> bool:
    low = href.lower()
    skip = {
        "login", "signup", "register", "about", "contact", "privacy",
        "terms", "tag/", "category/", "author/", "search", "#", "javascript:",
    }
    if any(s in low for s in skip):
        return False
    path = urlparse(href).path
    return bool(path and path != "/")


def _extract_title(html: str) -> str | None:
    for pat in [
        r"<title[^>]*>(.*?)</title>",
        r'<meta\s+property="og:title"\s+content="([^"]+)"',
        r'<h1[^>]*>(.*?)</h1>',
    ]:
        m = re.search(pat, html, re.DOTALL | re.IGNORECASE)
        if m:
            return _clean(_HTML_RE.sub(" ", m.group(1)))
    return None


def _extract_meta_description(html: str) -> str | None:
    for pat in [
        r'<meta\s+name="description"\s+content="([^"]+)"',
        r'<meta\s+property="og:description"\s+content="([^"]+)"',
    ]:
        m = re.search(pat, html, re.IGNORECASE)
        if m:
            return m.group(1)
    return None


def _extract_text(html: str) -> str:
    for tag in ["script", "style", "nav", "footer", "header"]:
        html = re.sub(rf"<{tag}[^>]*>.*?</{tag}>", "", html, flags=re.DOTALL | re.IGNORECASE)
    return _clean(_HTML_RE.sub(" ", html))


def _extract_published(html: str) -> str | None:
    patterns = [
        r'<meta\s+(?:property="article:published_time"|name="pubdate"|name="date")\s+content="([^"]+)"',
        r"<time[^>]*datetime\s*=\s*[\"']([^\"']+)[\"']",
    ]
    for pat in patterns:
        m = re.search(pat, html, re.IGNORECASE)
        if m:
            return m.group(1)
    return None


def _guess_published_from_url(url: str) -> str | None:
    # Full date: /YYYY/MM/DD/
    m = re.search(r"/(\d{4})/(\d{2})/(\d{2})/", url)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}T00:00:00+08:00"
    # Year-month only (e.g. qbitai.com/2026/06/437198.html) — assume today
    m = re.search(r"/(\d{4})/(\d{2})/\d+", url)
    if m:
        now = datetime.now(ZoneInfo("Asia/Shanghai"))
        y, mo = int(m.group(1)), int(m.group(2))
        if y == now.year and mo == now.month:
            return now.replace(microsecond=0).isoformat()
        return f"{m.group(1)}-{m.group(2)}-01T00:00:00+08:00"
    return None


def _extract_first_paragraph(html: str) -> str | None:
    for tag in ["script", "style", "nav", "footer", "header"]:
        html = re.sub(rf"<{tag}[^>]*>.*?</{tag}>", "", html, flags=re.DOTALL | re.IGNORECASE)
    for m in re.finditer(r"<p[^>]*>(.*?)</p>", html, re.DOTALL | re.IGNORECASE):
        text = _clean(_HTML_RE.sub(" ", m.group(1)))
        if len(text) >= 50:
            return text
    return None


def _clean(text: str) -> str:
    text = text.replace("&#8211;", "–").replace("&#8212;", "—").replace("&#8216;", "'")
    text = text.replace("&#8217;", "'").replace("&#8220;", '"').replace("&#8221;", '"')
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    text = text.replace("&nbsp;", " ").replace("&#8230;", "…")
    return _WHITESPACE_RE.sub(" ", text).strip()
