"""MCP server that provides web search tools for Chinese AI news sources.

Backends (tried in order):
1. GNews API  (GNEWS_API_KEY)  — search across news sources by domain/language
2. NewsAPI     (NEWS_API_KEY)   — search across news sources
3. Direct HTTP scraping          — fallback for accessible sites

Run as: python -m daily_ai_insight.mcp_search
"""

from __future__ import annotations

import os
import re
from datetime import datetime, timedelta
from typing import Any
from urllib.parse import urljoin, urlparse
from zoneinfo import ZoneInfo

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

mcp = FastMCP("daily-ai-insight-websearch")

SITE_CONFIG: dict[str, dict[str, Any]] = {
    "qbitai.com": {
        "name": "量子位",
        "language": "zh",
        "source_type": "media",
        "homepage": "https://www.qbitai.com/",
    },
    "jiqizhixin.com": {
        "name": "机器之心",
        "language": "zh",
        "source_type": "media",
        "homepage": "https://www.jiqizhixin.com/",
    },
    "zhihu.com": {
        "name": "知乎",
        "language": "zh",
        "source_type": "community",
        "homepage": "https://www.zhihu.com/",
    },
}

_HTML_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")
_GNEWS_API = "https://gnews.io/api/v4/search"
_NEWS_API = "https://newsapi.org/v2/everything"


@mcp.tool()
def search_ai_news(
    site: str,
    query: str = "",
    max_results: int = 10,
) -> list[dict[str, Any]]:
    """Search for recent AI news on a specific Chinese tech site.

    Args:
        site: Site domain, e.g. 'qbitai.com', 'jiqizhixin.com', 'zhihu.com'.
        query: Optional search terms.
        max_results: Maximum results (default 10).

    Returns:
        List of dicts with: title, url, source, summary, published_at, language, source_type.
    """
    config = SITE_CONFIG.get(site)
    if not config:
        raise ValueError(f"Unsupported site: {site}. Supported: {list(SITE_CONFIG)}")

    results: list[dict[str, Any]] = []

    # 1) Try GNews API
    gnews_key = os.getenv("GNEWS_API_KEY")
    if gnews_key:
        try:
            results = _gnews_search(site, config, query, max_results, gnews_key)
        except Exception:
            pass

    # 2) Try NewsAPI
    newsapi_key = os.getenv("NEWS_API_KEY")
    if not results and newsapi_key:
        try:
            results = _newsapi_search(site, config, query, max_results, newsapi_key)
        except Exception:
            pass

    # 3) Fallback to direct HTTP
    if not results:
        results = _direct_fetch(site, config, max_results)

    return results[:max_results] if results else []


@mcp.tool()
def fetch_article_content(url: str) -> dict[str, Any]:
    """Fetch the full content of a single article by URL.

    Args:
        url: Full URL of the article to fetch.

    Returns:
        Dict with keys: url, title, content (plain text), published_at if found.
    """
    try:
        resp = httpx.get(
            url, timeout=15, follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            },
            verify=False,
        )
        resp.raise_for_status()
    except Exception as exc:
        raise RuntimeError(f"Failed to fetch {url}: {exc}") from exc

    html = resp.text
    title = _extract_title(html) or url
    content = _extract_text(html)
    published = _extract_published(html) or ""

    return {
        "url": url,
        "title": _clean(title)[:200],
        "content": _clean(content)[:8000],
        "published_at": published,
    }


# ---- GNews backend ----

def _gnews_search(
    site: str,
    config: dict[str, Any],
    query: str,
    max_results: int,
    api_key: str,
) -> list[dict[str, Any]]:
    """Search via GNews API, client-side domain filter."""
    # Strip site:domain prefixes from query (not supported by GNews)
    clean_query = re.sub(rf"site:{re.escape(site)}\s*", "", query).strip()
    clean_query = re.sub(r"site:\S+\s*", "", clean_query).strip()
    if not clean_query:
        clean_query = "AI artificial intelligence"

    params: dict[str, Any] = {
        "token": api_key,
        "q": clean_query,
        "max": min(max_results * 3, 30),
        "sortby": "publishedAt",
    }
    resp = httpx.get(_GNEWS_API, params=params, timeout=20)
    resp.raise_for_status()
    data = resp.json()

    results: list[dict[str, Any]] = []
    for article in data.get("articles", []):
        url = article.get("url", "")
        if site not in urlparse(url).netloc:
            continue
        results.append({
            "title": _clean(article.get("title", "")),
            "url": url,
            "source": config["name"],
            "source_type": config["source_type"],
            "summary": _clean(article.get("description", "")),
            "published_at": article.get("publishedAt", ""),
            "language": config["language"],
        })
        if len(results) >= max_results:
            break
    return results


# ---- NewsAPI backend ----

def _newsapi_search(
    site: str,
    config: dict[str, Any],
    query: str,
    max_results: int,
    api_key: str,
) -> list[dict[str, Any]]:
    """Search via NewsAPI."""
    clean_query = re.sub(r"site:\S+\s*", "", query).strip()
    if not clean_query:
        clean_query = "AI artificial intelligence"

    params: dict[str, Any] = {
        "apiKey": api_key,
        "q": clean_query,
        "domains": site,
        "pageSize": min(max_results, 20),
        "sortBy": "publishedAt",
        "language": "zh",
    }
    resp = httpx.get(_NEWS_API, params=params, timeout=20)
    resp.raise_for_status()
    data = resp.json()

    results: list[dict[str, Any]] = []
    for article in data.get("articles", []):
        results.append({
            "title": _clean(article.get("title", "")),
            "url": article.get("url", ""),
            "source": config["name"],
            "source_type": config["source_type"],
            "summary": _clean(article.get("description", "")),
            "published_at": article.get("publishedAt", ""),
            "language": config["language"],
        })
    return results


# ---- Direct HTTP fallback ----

def _direct_fetch(
    site: str,
    config: dict[str, Any],
    max_results: int,
) -> list[dict[str, Any]]:
    """Direct HTTP scraping fallback."""
    try:
        return _do_direct_fetch(site, config, max_results)
    except Exception:
        return []


def _do_direct_fetch(
    site: str,
    config: dict[str, Any],
    max_results: int,
) -> list[dict[str, Any]]:
    homepage = config["homepage"]
    resp = httpx.get(
        homepage,
        timeout=15,
        follow_redirects=True,
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
    links = _extract_article_links(html, site)

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
            # Try meta description first, then first meaningful paragraph
            summary = _extract_meta_description(art_html)
            if not summary or len(summary) < 40:
                summary = _extract_first_paragraph(art_html) or _extract_text(art_html)[:500]
            published = (
                _extract_published(art_html)
                or _guess_published_from_url(article_url)
                or _guess_published_from_url(homepage)  # today as fallback
            )

            if title and len(_clean(summary)) >= 30:
                results.append({
                    "title": _clean(title)[:200],
                    "url": article_url,
                    "source": config["name"],
                    "source_type": config["source_type"],
                    "summary": _clean(summary)[:500],
                    "published_at": published,
                    "language": config["language"],
                })
        except Exception:
            continue

    return results


# ---- HTML extraction helpers ----

def _extract_article_links(html: str, site: str) -> list[dict[str, str]]:
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
        if not _looks_like_article(href, site) or len(text) < 8:
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


def _looks_like_article(href: str, site: str) -> bool:
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
        html = re.sub(
            rf"<{tag}[^>]*>.*?</{tag}>", "", html, flags=re.DOTALL | re.IGNORECASE
        )
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
        from datetime import datetime
        from zoneinfo import ZoneInfo

        now = datetime.now(ZoneInfo("Asia/Shanghai"))
        y, mo = int(m.group(1)), int(m.group(2))
        if y == now.year and mo == now.month:
            return now.replace(microsecond=0).isoformat()
        return f"{m.group(1)}-{m.group(2)}-01T00:00:00+08:00"
    return None


def _extract_first_paragraph(html: str) -> str | None:
    """Extract the first substantive paragraph from article body."""
    # Remove script/style/nav
    for tag in ["script", "style", "nav", "footer", "header"]:
        html = re.sub(
            rf"<{tag}[^>]*>.*?</{tag}>", "", html, flags=re.DOTALL | re.IGNORECASE
        )
    # Find <p> tags with substantial content
    for m in re.finditer(r"<p[^>]*>(.*?)</p>", html, re.DOTALL | re.IGNORECASE):
        text = _clean(_HTML_RE.sub(" ", m.group(1)))
        if len(text) >= 50:
            return text
    return None


def _clean(text: str) -> str:
    # Also decode common HTML entities
    text = text.replace("&#8211;", "–").replace("&#8212;", "—").replace("&#8216;", "'")
    text = text.replace("&#8217;", "'").replace("&#8220;", '"').replace("&#8221;", '"')
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    text = text.replace("&nbsp;", " ").replace("&#8230;", "…")
    return _WHITESPACE_RE.sub(" ", text).strip()


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
