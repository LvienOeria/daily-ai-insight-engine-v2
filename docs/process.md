# Core Process

## Purpose

This document describes the end-to-end workflow from raw information to the final Daily AI Insight report.

## Workflow Overview

```text
1. Define report scope
2. Build candidate source pool
3. Evaluate candidate sources
4. Select MVP data sources
5. Collect 10-20 raw AI news items
6. Normalize raw data
7. Clean and validate data
8. Extract structured fields with LLM
9. Validate structured output
10. Cluster news into events
11. Score event importance
12. Generate visualization data
13. Generate daily report
14. Run quality check
15. Finalize documentation
```

## Step 1: Define Report Scope

Decide the MVP focus:

- Reporting window
- AI topic coverage
- Chinese/English source mix
- Target audience
- Output format
- Manual vs API/RSS data collection boundary

## Step 2: Build Candidate Source Pool

List possible sources across:

- News aggregation
- Official AI company sources
- Research sources
- Technical communities
- Chinese AI media
- Manual static data

## Step 3: Evaluate Candidate Sources

Use the `data-source-evaluation` skill.

Record:

- Field completeness
- AI relevance
- Credibility
- Stability
- Cost or access limits
- Recommended tier

## Step 4: Select MVP Sources

Choose sources that can produce enough high-quality data for the MVP.

Prefer a small balanced set over a large unstable source list.

## Step 5: Collect Raw Data

Collect 10-20 recent AI-related items.

Each main item should include:

- title
- summary/content/description
- source
- published_at
- url or traceable identifier when possible

## Step 6: Normalize Raw Data

Map different API/RSS/manual fields into a common RawNewsItem schema.

Preserve raw payloads or original text where possible.

## Step 7: Clean and Validate Data

Apply deterministic checks:

- Required field check
- Date normalization
- Source normalization
- Language tagging
- Duplicate removal
- AI relevance filtering
- Quality scoring

## Step 8: Structured Extraction

Use the `news-structuring` skill.

Extract:

- entities
- technologies
- event_type
- industry_area
- key_facts
- sentiment
- impact_scope
- risk_tags
- opportunity_tags
- importance_score
- confidence
- evidence

## Step 9: Validate Structured Output

Check:

- JSON validity
- Required fields
- Enum validity
- Score ranges
- Evidence presence
- Low-confidence items

## Step 10: Event Clustering

Use the `event-clustering` skill.

Group related news into events using:

- URL/title duplicate checks
- Entity overlap
- Event type
- Key facts
- Semantic similarity

## Step 11: Importance Scoring

Use the `importance-scoring` skill.

Rank events by:

- impact scope
- source authority
- novelty
- multi-source support
- technical impact
- business impact
- risk level
- opportunity level
- recency

Select Top 3-5 events.

## Step 12: Visualization

Generate charts from structured data.

Recommended charts:

- Source type distribution
- Event type distribution
- Technology topic distribution
- Top event importance ranking
- Risk/opportunity matrix

For this project, visualization is implemented in a React + Vite frontend using D3.js. Python pipeline output remains the source of truth and exports dashboard data to `frontend/public/data/latest.json`.

Frontend rules:

- The frontend displays generated artifacts only.
- It must not call the LLM or invent additional analysis.
- Chart data must match `data/visualization_data.json` and ranked event artifacts.
- Evidence links or IDs must remain visible for Top events and major conclusions.

## Step 13: Daily Report Generation

Use the `daily-report-generation` skill.

The report should include:

- Today's overview
- Top 3-5 events
- Deep analysis
- Trend judgments
- Risk and opportunity notes
- Visualization explanation
- Data and method notes

## Step 14: Quality Check

Use the `report-quality-check` skill.

Check:

- Task completeness
- Evidence traceability
- Unsupported claims
- Schema validity
- Visualization consistency
- Documentation gaps

## Step 15: Finalize Documentation

Update:

- Data source decisions
- Schema design
- AI usage
- Core process
- Known limitations

## Final Deliverables

Expected MVP deliverables:

- Source evaluation notes
- Raw or cleaned data file
- Structured data file
- Event/ranking data file
- Visualization output
- Final daily report
- Documentation files

## Operating Principle

Human defines rules, deterministic processing ensures stability, LLM handles semantic understanding, and human review confirms key conclusions.
