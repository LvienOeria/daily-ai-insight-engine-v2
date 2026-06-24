# Data Source Decisions

## Purpose

This document records how data sources are selected for the Daily AI Insight Engine MVP.

The goal is to make source selection explainable and reproducible.

## Source Selection Strategy

MVP data collection uses API and RSS feeds.

For Chinese-language compatibility, three candidate sources were evaluated:

- **量子位** (`qbitai.com`) — ✅ accessible via direct HTTP scraping
- **机器之心** (`jiqizhixin.com`) — ❌ SSL handshake timeout from non-China IPs
- **知乎** (`zhihu.com`) — ❌ redirects to login wall, cannot scrape

DeepSeek API's `enable_search` parameter was tested as an alternative path (using DeepSeek's China-based servers as a proxy), but the API does not actually trigger web search — the feature is only available on DeepSeek's web chat interface, not through the Chat Completions API.

**Result**: only 量子位 provides usable Chinese data for the MVP. Machine之心 and 知乎 are disabled and documented as "future" sources pending either a China-side proxy or DeepSeek API web search support.

Crawler-first collection is not prioritized because:

- The main evaluation focus is structured processing, analysis logic, and validation.
- News website HTML structures vary heavily.
- Crawlers add maintenance, access, anti-bot, and compliance complexity.
- APIs and RSS feeds are more stable for retrieving title, summary, source, published time, and URL.

## Required Item Fields

A main analysis item should contain:

- title
- summary/content/description
- source
- published_at
- url or unique identifier when possible

Items missing title, source, or published_at should not enter the main analysis set unless manually repaired with traceable evidence.

## Chinese Source Evaluation Results

Three Chinese sources were evaluated for MVP inclusion:

| Source | Type | Access Method | Result | Tier | Reason |
|---|---|---|---|---|---|
| 量子位 | media | Direct HTTP scraping (fallback) | ✅ 10 items fetched, fields complete, dates from URL | core | Accessible from non-China IP; article pages return 200; title/summary/date extractable |
| 机器之心 | media | Direct HTTP / DeepSeek API | ❌ SSL handshake timeout; DS API web search unavailable | future | Geo-blocked from non-China IPs; DeepSeek API `enable_search` does not trigger actual web requests |
| 知乎 | community | Direct HTTP / DeepSeek API | ❌ Redirects to sign-in page; DS API web search unavailable | future | Requires authentication; not suitable for automated collection |

## Source Tiers

Core sources:

- Stable and field-complete enough for MVP analysis.
- Used in the main dataset.

Auxiliary sources:

- Useful signal but may have field gaps or limited reliability.
- Used for context or optional analysis.
- Chinese websearch results may remain auxiliary if they provide perspective but lack full structured fields.

Future sources:

- Valuable but not suitable for MVP due to crawler complexity, login, quota, cost, or unstable fields.

Rejected sources:

- Missing critical fields, low AI relevance, unverifiable, or too unstable.

## Final Selected Sources

| Source | Type | Language | Items (typical) | Fields | Limitations |
|---|---|---|---|---|---|
| arXiv cs.AI | research | en | ~20 | title, summary, source, published_at, URL | Abstracts only; research-focused |
| OpenAI News RSS | official | en | ~2 (in 3-day window) | title, summary, source, published_at, URL | Single-company perspective; irregular posting |
| Hacker News Algolia | community | en | ~1 (in 3-day window) | title, summary, source, published_at, URL | Short text; community signal |
| Google DeepMind RSS | official | en | ~0 (in 3-day window) | title, summary, source, published_at, URL | Infrequent updates within 3-day window |
| 量子位 | media | zh | ~10 | title, summary, source, published_at (from URL), URL | Dates inferred from URL year/month; article structure varies |

## Chinese Websearch Rules

When using DeepSeek websearch for Chinese sources:

- Restrict queries to the allowlisted sites: 量子位, 机器之心, and 知乎.
- Save the query text, collection time, returned title, URL, source/site, snippet/content, and any visible published date.
- Do not use a result in the main analysis set unless it has title, source/site, published_at or a traceable visible date, and summary/content.
- If published_at is absent or ambiguous, mark it as missing and keep the item out of Top-event primary evidence unless manually repaired with traceable evidence.
- Treat 知乎 primarily as community or sentiment signal. It can support risk/opportunity discussion, but should not be the sole source for a major factual event unless the item itself is complete and traceable.
- Keep websearch outputs separate from cleaned data until field validation and source evaluation pass.

## Known Limitations

- The MVP dataset is small, usually 10-20 items.
- API and RSS sources may not provide full article text.
- Manually curated items improve quality but reduce automation.
- The dataset may not represent full public opinion across all platforms.
- DeepSeek websearch output quality depends on search-result fields and page accessibility; observed results must be evaluated before source selection.
