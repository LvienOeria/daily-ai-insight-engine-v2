# AI Usage, Prompt Design, and Error Handling

## Purpose

This document explains how DeepSeek LLM is used in the Daily AI Insight Engine.

## AI Usage

DeepSeek is used for three pipeline stages:

1. **Structured extraction** — extract entities, technologies, event types, key facts, risks, opportunities, and confidence from cleaned news text. Batched in groups of 5 per API call.
2. **Event clustering** — determine whether multiple news items describe the same event. Single-news events are allowed when well-supported.
3. **Daily report generation** — convert structured event data into a professional Chinese analysis report with 7 required sections.

DeepSeek is not used for:

- Data collection (RSS, API, HTTP scraping are deterministic)
- Field validation (date normalization, dedup, required-field checks are programmatic)
- Final quality checks

## Prompt Design

### Structuring Prompt

- Returns valid JSON only
- Uses only input item text; must not invent companies, dates, URLs, amounts, or facts
- Unknown fields use `null`, `[]`, or `other`
- Evidence must quote or tightly paraphrase input fragments
- Event type and industry area are constrained to fixed enums
- Confidence: low / medium / high

### Clustering Prompt

- Groups records only when they describe the same concrete event
- Must not group by broad topic, same day, same sentiment, or same company with different facts
- Every event must include evidence and valid related_news_ids

### Report Prompt

- Generates professional Chinese Markdown with 7 sections
- Top events must cite event_id or news_id
- Trends must be supported by key facts or multiple events
- Risks/opportunities must map to structured tags
- Must not invent facts or overstate weak evidence

## Error Handling

### Data Errors

Missing fields, date inconsistencies, duplicates → handled programmatically in the cleaning step. Items are discarded or marked with `missing_fields`.

### LLM Output Errors

Invalid JSON, missing fields, invalid enums → `_normalize_structured_record` fills defaults, maps invalid values to `other`, clamps scores to 1-5. If JSON is completely unparseable, the pipeline raises `LLMError`.

### Analysis Errors

The quality check catches: unsupported claims, missing report sections, empty evidence for high-importance items, and documentation gaps.

## Mock Mode

`--mock-llm` replaces all DeepSeek calls with deterministic keyword-matching heuristics. Useful for development and testing without API costs. Quality is lower than real LLM extraction.
