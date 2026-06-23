# Schema Design

## Purpose

This document explains the structured data model used by the Daily AI Insight Engine.

The schema is designed to support:

- Structured extraction beyond summary
- Event clustering
- Importance scoring
- Trend analysis
- Risk and opportunity detection
- Visualization
- Evidence traceability

## Design Principle

The schema separates raw news records, structured news records, and event-level records.

This separation avoids mixing raw source differences with downstream analysis logic.

## Raw News Item

Raw items normalize data from APIs, RSS feeds, and static manual inputs.

Suggested fields:

```json
{
  "news_id": "",
  "title": "",
  "url": "",
  "source": "",
  "source_type": "",
  "published_at": "",
  "language": "",
  "summary": "",
  "content": "",
  "collected_at": "",
  "raw_provider": "",
  "raw_payload": {},
  "missing_fields": [],
  "quality_score": 0
}
```

## Structured News Item

Structured items are produced after cleaning and LLM extraction.

Suggested fields:

```json
{
  "news_id": "",
  "title": "",
  "source": "",
  "source_type": "",
  "published_at": "",
  "language": "",
  "url": "",
  "entities": [],
  "technologies": [],
  "event_type": "",
  "industry_area": "",
  "key_facts": [],
  "summary": "",
  "sentiment": "neutral",
  "impact_scope": [],
  "risk_tags": [],
  "opportunity_tags": [],
  "importance_score": 1,
  "confidence": "medium",
  "evidence": []
}
```

## Event Item

Events group related news into analysis units.

Suggested fields:

```json
{
  "event_id": "",
  "event_name": "",
  "related_news_ids": [],
  "main_entities": [],
  "core_topic": "",
  "event_type": "",
  "industry_area": "",
  "technologies": [],
  "key_facts": [],
  "evidence": [],
  "why_it_matters": "",
  "impact_analysis": "",
  "trend_direction": "",
  "risk_level": 0,
  "opportunity_level": 0,
  "final_importance_score": 0,
  "confidence": "medium"
}
```

## Field Design Rationale

- `entities`: supports company, institution, and person tracking.
- `technologies`: supports technology trend visualization.
- `event_type`: supports event category statistics.
- `industry_area`: supports domain-level trend analysis.
- `key_facts`: ensures report claims are grounded.
- `risk_tags`: supports risk warning.
- `opportunity_tags`: supports opportunity analysis.
- `importance_score`: supports Top event ranking.
- `confidence`: marks uncertain extraction.
- `evidence`: supports traceability and hallucination checks.

## Enum Policy

Use fixed enum values where possible. This improves consistency and visualization quality.

Free-text fields are allowed for summaries, evidence, and analysis, but classification fields should be constrained.

## Validation Requirements

Before using structured data in reports:

- Required fields must be present.
- Enum values must be valid.
- Scores must be in range.
- Evidence should exist for important events.
- Low-confidence data should not be overused in Top event analysis.
