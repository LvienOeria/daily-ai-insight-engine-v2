---
name: event-clustering
description: "Use when: grouping structured AI news records into events, merging duplicate reports, identifying related news IDs, and preparing event-level evidence for daily AI reports."
---

# Event Clustering Skill

## Purpose

Group structured news records into event-level units for daily analysis.

A daily report should rank and analyze events, not merely list isolated news items.

## When To Use

Use after news items have been structured with the `news-structuring` skill.

## Inputs

A list of structured news records containing at least:

- news_id
- title
- source
- published_at
- entities
- technologies
- event_type
- industry_area
- key_facts
- summary
- risk_tags
- opportunity_tags
- importance_score
- confidence
- evidence

## Output Format

```json
{
  "events": [
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
      "impact_scope": [],
      "risk_tags": [],
      "opportunity_tags": [],
      "confidence": "low | medium | high"
    }
  ]
}
```

## Clustering Rules

Group news together only when they describe the same event or tightly connected event chain.

Valid reasons to group:

- Same company or institution announcing the same product, model, policy, partnership, funding, research result, or incident
- Multiple sources reporting the same release or business event
- Official announcement plus media coverage of the same event
- Same open source release or research result discussed by multiple sources

Do not group solely because:

- They share a broad topic such as AI agents or chips
- They mention the same company but describe different events
- They have similar sentiment but unrelated facts
- They are from the same day but unrelated

## Deduplication Guidance

Use deterministic checks first when possible:

- Same URL
- Same title
- Same source and same published_at

Then use semantic judgment for:

- Slightly different titles describing the same event
- Official source plus media analysis
- Chinese and English reports of the same event

## Event Naming

Event names should be concise and factual.

Good examples:

- `OpenAI releases new model update`
- `NVIDIA announces AI infrastructure expansion`
- `EU publishes new AI regulatory guidance`

Avoid vague names:

- `AI is changing fast`
- `Big trend in AI`
- `Important industry news`

## Evidence Rules

Each event must include evidence from related news records.

Evidence should include:

- related news IDs
- key facts
- source names
- factual statements supporting the event definition

## Confidence Guidance

High confidence:

- Multiple records clearly refer to the same event, or one official source is explicit

Medium confidence:

- Records are likely related, but details differ or are incomplete

Low confidence:

- Relationship is ambiguous; keep separate unless necessary

## Quality Checks

Before returning results, check:

- Every `related_news_ids` value exists in the input
- No unrelated items were merged
- Every event has evidence
- Single-news events are allowed when important and well supported
- Broad trend categories are not mistaken for events
