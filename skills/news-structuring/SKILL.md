---
name: news-structuring
description: "Use when: extracting structured fields from AI news items for the Daily AI Insight Engine, including entities, technologies, event types, key facts, risks, opportunities, evidence, and confidence."
---

# News Structuring Skill

## Purpose

Convert cleaned AI-related news items into structured records that can support analysis, ranking, visualization, and report generation.

This skill must not produce only summaries. It must extract structured fields.

## When To Use

Use this skill after raw news has been collected, cleaned, deduplicated, and normalized into a standard input format.

## Input Format

Each input item should contain:

```json
{
  "news_id": "",
  "title": "",
  "source": "",
  "source_type": "",
  "published_at": "",
  "language": "",
  "url": "",
  "summary": "",
  "content": ""
}
```

`summary` or `content` must contain enough information to support extraction. If both are weak, mark confidence as low.

## Output Format

Output one structured record per news item:

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
  "sentiment": "positive | neutral | negative | mixed",
  "impact_scope": [],
  "risk_tags": [],
  "opportunity_tags": [],
  "importance_score": 1,
  "confidence": "low | medium | high",
  "evidence": []
}
```

## Event Type Enum

Use one of:

- product_release
- model_release
- funding
- acquisition
- partnership
- regulation
- research
- open_source
- infrastructure
- security_risk
- business_update
- market_commentary
- other

## Industry Area Enum

Use one of:

- foundation_model
- ai_agent
- multimodal_ai
- ai_infrastructure
- chip_compute
- enterprise_ai
- consumer_ai
- developer_tools
- ai_safety
- policy_regulation
- research
- capital_market
- other

## Risk Tags

Use zero or more:

- privacy
- copyright
- security
- compliance
- misinformation
- job_displacement
- market_bubble
- dependency_risk
- model_safety
- none

## Opportunity Tags

Use zero or more:

- productivity
- enterprise_adoption
- developer_ecosystem
- cost_reduction
- new_market
- open_source_growth
- ai_native_product
- infrastructure_growth
- research_breakthrough
- none

## Extraction Rules

- Use only information present in the input item.
- Do not invent companies, products, dates, amounts, model names, policies, or claims.
- `key_facts` must be factual, short, and traceable to the input.
- `evidence` should quote or paraphrase the exact input fragment supporting important judgments.
- Use `null`, `[]`, or `other` when information is insufficient.
- Assign `confidence` based on input richness and extraction certainty.
- Assign `importance_score` from 1 to 5 based on initial single-news importance only; event-level ranking happens later.

## Confidence Guidance

High confidence:

- Clear title and detailed summary/content
- Source and date available
- Event type and entities are explicit

Medium confidence:

- Core event is clear but some fields are inferred from limited text

Low confidence:

- Summary is too short
- Important fields are missing
- Event type or impact is ambiguous

## Quality Checks

Before returning results, check:

- JSON is valid
- Required fields are present
- Enum values are valid
- `importance_score` is between 1 and 5
- No unsupported facts were added
- Low-information items are marked low confidence
