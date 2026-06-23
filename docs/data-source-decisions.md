# Data Source Decisions

## Purpose

This document records how data sources are selected for the Daily AI Insight Engine MVP.

The goal is to make source selection explainable and reproducible.

## Source Selection Strategy

MVP data collection prioritizes API, RSS, and manually curated static data.

For Chinese-language compatibility, the MVP may also use DeepSeek websearch as a constrained collection path. This path is limited to webpages from:

- 量子位 (`qbitai.com`)
- 机器之心 (`jiqizhixin.com`)
- 知乎 (`zhihu.com`)

DeepSeek websearch results are not automatically accepted as core data. The workflow must first attempt retrieval, inspect observed fields, and then evaluate each source/result against the same required-field and credibility rules as APIs or RSS feeds.

Crawler-first collection is not prioritized because:

- The task allows manually curated static data.
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

## Candidate Source Pool

Record candidate sources here before final selection.

| Source | Type | Access Method | Language | Expected Fields | Strengths | Risks | Tier |
|---|---|---|---|---|---|---|---|
| 量子位 | media | DeepSeek websearch allowlisted webpage | zh | title, snippet/content, source, URL, published_at if visible | Chinese AI industry coverage, useful local-market perspective | Date/content completeness must be verified from fetched result; search snippets may be incomplete | Pending observed evaluation |
| 机器之心 | media | DeepSeek websearch allowlisted webpage | zh | title, snippet/content, source, URL, published_at if visible | Chinese AI research/product coverage, strong technical orientation | Date/content completeness must be verified from fetched result; article structure may vary | Pending observed evaluation |
| 知乎 | community | DeepSeek websearch allowlisted webpage | zh | title, answer/post excerpt, source, URL, published_at if visible | Community signal and discussion context | Not a primary evidence source by default; author credibility, date, and factuality vary | Auxiliary pending observed evaluation |

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

Fill this section after source evaluation.

| Selected Source | Reason | Fields Available | Data Characteristics | Limitations |
|---|---|---|---|---|
| TBD | TBD | TBD | TBD | TBD |

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
