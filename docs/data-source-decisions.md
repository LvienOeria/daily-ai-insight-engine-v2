# Data Source Decisions

## Purpose

This document records how data sources are selected for the Daily AI Insight Engine MVP.

The goal is to make source selection explainable and reproducible.

## Source Selection Strategy

MVP data collection prioritizes API, RSS, and manually curated static data.

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
| TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

## Source Tiers

Core sources:

- Stable and field-complete enough for MVP analysis.
- Used in the main dataset.

Auxiliary sources:

- Useful signal but may have field gaps or limited reliability.
- Used for context or optional analysis.

Future sources:

- Valuable but not suitable for MVP due to crawler complexity, login, quota, cost, or unstable fields.

Rejected sources:

- Missing critical fields, low AI relevance, unverifiable, or too unstable.

## Final Selected Sources

Fill this section after source evaluation.

| Selected Source | Reason | Fields Available | Data Characteristics | Limitations |
|---|---|---|---|---|
| TBD | TBD | TBD | TBD | TBD |

## Known Limitations

- The MVP dataset is small, usually 10-20 items.
- API and RSS sources may not provide full article text.
- Manually curated items improve quality but reduce automation.
- The dataset may not represent full public opinion across all platforms.
