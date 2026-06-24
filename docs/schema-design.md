# Schema Design

## Design Principle

The schema separates raw news records, structured news records, and event-level records. This avoids mixing raw source differences with downstream analysis.

## Raw News Item (RawNewsItem)

Normalized from APIs, RSS feeds, and HTTP scraping:

```json
{
  "news_id": "hash-derived unique id",
  "title": "headline",
  "url": "source link",
  "source": "source name",
  "source_type": "research | media | community",
  "published_at": "ISO 8601 datetime",
  "language": "zh | en",
  "summary": "description or first paragraph",
  "content": "full text if available",
  "collected_at": "fetch timestamp",
  "missing_fields": ["fields absent from source"],
  "quality_score": 0.0-1.0
}
```

## Structured News Item (StructuredNewsItem)

Produced after cleaning and LLM extraction:

```json
{
  "news_id": "links to raw item",
  "title": "headline",
  "source": "source name",
  "published_at": "ISO 8601",
  "entities": ["companies, institutions, people"],
  "technologies": ["tech keywords"],
  "event_type": "research | model_release | funding | regulation | ...",
  "industry_area": "foundation_model | ai_agent | chip_compute | ...",
  "key_facts": ["factual statements from source"],
  "sentiment": "positive | neutral | negative | mixed",
  "impact_scope": ["developers | industry | research"],
  "risk_tags": ["privacy | security | compliance | ..."],
  "opportunity_tags": ["productivity | enterprise_adoption | ..."],
  "importance_score": 1-5,
  "confidence": "low | medium | high",
  "evidence": ["quotes or paraphrases from source text"]
}
```

## Event Item (EventItem)

Groups related news into analysis units:

```json
{
  "event_id": "unique event identifier",
  "event_name": "concise factual name",
  "related_news_ids": ["linked news items"],
  "main_entities": ["key organizations"],
  "core_topic": "one-paragraph summary of the event",
  "event_type": "same enum as structured",
  "industry_area": "same enum",
  "technologies": ["relevant tech"],
  "key_facts": ["consolidated facts"],
  "evidence": ["supporting evidence"],
  "why_it_matters": "importance explanation",
  "impact_scope": ["affected domains"],
  "risk_tags": ["identified risks"],
  "opportunity_tags": ["identified opportunities"],
  "confidence": "low | medium | high",
  "published_at": "earliest related news date"
}
```

## Enum Values

**Event Types**: product_release, model_release, funding, acquisition, partnership, regulation, research, open_source, infrastructure, security_risk, business_update, market_commentary, other

**Industry Areas**: foundation_model, ai_agent, multimodal_ai, ai_infrastructure, chip_compute, enterprise_ai, consumer_ai, developer_tools, ai_safety, policy_regulation, research, capital_market, other

**Risk Tags**: privacy, copyright, security, compliance, misinformation, job_displacement, market_bubble, dependency_risk, model_safety, none

**Opportunity Tags**: productivity, enterprise_adoption, developer_ecosystem, cost_reduction, new_market, open_source_growth, ai_native_product, infrastructure_growth, research_breakthrough, none

## Validation

- Required fields must be present
- Enum values must be valid
- Scores must be in range (1-5 for importance, 0-5 for breakdown dimensions)
- Evidence must exist for high-importance items
- Low-confidence items flagged for review
