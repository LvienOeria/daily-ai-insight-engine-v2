---
name: importance-scoring
description: "Use when: scoring clustered AI events for daily report ranking using impact, source authority, novelty, multi-source support, risk, opportunity, and recency."
---

# Importance Scoring Skill

## Purpose

Rank AI events for the daily report in a way that is explainable and evidence-based.

Do not rely on free-form LLM judgment alone. Use a scoring framework and then generate explanations.

## When To Use

Use after event clustering and before daily report generation.

## Inputs

Each event should include:

- event_id
- event_name
- related_news_ids
- main_entities
- event_type
- industry_area
- technologies
- key_facts
- evidence
- impact_scope
- risk_tags
- opportunity_tags
- source information
- published_at values
- confidence

## Output Format

```json
{
  "ranked_events": [
    {
      "event_id": "",
      "event_name": "",
      "final_importance_score": 0,
      "rank": 1,
      "score_breakdown": {
        "impact_scope": 0,
        "source_authority": 0,
        "novelty": 0,
        "multi_source_support": 0,
        "technical_impact": 0,
        "business_impact": 0,
        "risk_level": 0,
        "opportunity_level": 0,
        "recency": 0
      },
      "ranking_reason": "",
      "supporting_evidence": [],
      "confidence": "low | medium | high"
    }
  ]
}
```

## Scoring Dimensions

Use a 0-5 score for each dimension unless another documented scale is chosen.

1. impact_scope
   - 0: unclear or narrow
   - 3: affects a company, product segment, or developer group
   - 5: affects industry direction, major market, regulation, or global ecosystem

2. source_authority
   - 0: weak or unverifiable source
   - 3: reputable media or known community source
   - 5: official source, primary document, or multiple reputable sources

3. novelty
   - 0: repetitive or minor update
   - 3: meaningful product, policy, research, or business update
   - 5: major new model, platform shift, regulatory milestone, breakthrough, or high-impact business event

4. multi_source_support
   - 0: unsupported or duplicate weak signals
   - 3: at least one credible source
   - 5: multiple independent sources or official plus media coverage

5. technical_impact
   - 0: little technical relevance
   - 3: affects developers, model capability, infrastructure, or workflows
   - 5: may shift technical architecture, model competition, or infrastructure demand

6. business_impact
   - 0: little business relevance
   - 3: affects a company, market segment, or adoption path
   - 5: affects major platform competition, revenue models, capital markets, or enterprise adoption

7. risk_level
   - 0: no clear risk
   - 3: moderate compliance, safety, security, copyright, or market risk
   - 5: high regulatory, safety, financial, or public trust risk

8. opportunity_level
   - 0: no clear opportunity
   - 3: practical adoption or ecosystem opportunity
   - 5: major new market, platform, productivity, or infrastructure opportunity

9. recency
   - 0: stale or unclear date
   - 3: recent within the reporting window
   - 5: highly current and central to today's report

## Ranking Rules

- Rank Top 3-5 events by final score and editorial relevance.
- Do not rank low-confidence events highly unless evidence is strong.
- Do not over-rank a single weak-source story simply because it sounds exciting.
- Explain every Top event with evidence.
- If scoring and LLM intuition conflict, explain the conflict and prefer evidence.

## Quality Checks

Before returning results, check:

- Every score is within the documented range
- Each Top event has supporting evidence
- Ranking reasons are specific, not generic
- Single-source events are not over-weighted without justification
- Trends are not ranked as events unless tied to specific evidence
