# Data Source Decisions

## Purpose

This document records how data sources are selected for the Daily AI Insight Engine.

## Source Selection Strategy

MVP data collection uses three access methods:

1. **API** — structured, field-complete, reproducible (arXiv)
2. **RSS** — stable feeds with title, summary, date, and URL (TechCrunch AI, The Verge)
3. **Direct HTTP scraping** — for sites without RSS feeds (量子位)

## Required Item Fields

A main analysis item must contain:

- title
- summary/content/description
- source
- published_at (or URL-inferrable date)
- url

Items missing title, source, or published_at are excluded from the main dataset.

## Source Tiers

- **Core**: stable, field-complete sources used in the main dataset
- **Auxiliary**: useful signal with potential field gaps, used for context
- **Future**: valuable but not yet accessible
- **Reject**: missing critical fields or low AI relevance

## Candidate Source Evaluation

Three Chinese sources were evaluated for MVP:

| Source | Method | Result | Tier | Reason |
|---|---|---|---|---|
| 量子位 (qbitai.com) | Direct HTTP | ✅ 10 items, field-complete | core | Accessible, article pages return 200 |
| 机器之心 (jiqizhixin.com) | Direct HTTP | ❌ SSL timeout | future | Geo-blocked from non-China IPs |
| 知乎 (zhihu.com) | Direct HTTP | ❌ Login wall | future | Requires authentication |

DeepSeek API's `enable_search` was tested as a proxy but does not trigger actual web requests — the feature is web-chat only, not API-accessible.

## Final Selected Sources

| Source | Type | Method | Language | Items (typical) | Limitations |
|---|---|---|---|---|---|
| arXiv | research | API | en | ~20 | Abstracts only |
| 量子位 | media | HTTP scrape | zh | ~10 | Date from URL; HTML structure may change |
| TechCrunch AI | media | RSS | en | ~19 | AI category only; few in 3-day window |
| The Verge | media | RSS + filter | en | ~1 | General feed; AI keyword filter needed |

## Known Limitations

- Dataset is capped at 20 items (configurable in `defaults.json`)
- 3-day window excludes many quality items from infrequently updated sources
- Chinese coverage is limited to a single source (量子位)
- Direct HTTP scraping is fragile; site HTML changes may break extraction
