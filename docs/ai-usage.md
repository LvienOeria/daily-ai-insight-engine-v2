# AI Usage, Prompt Design, and Error Handling

## Purpose

This document explains how AI/LLM capabilities are used in the Daily AI Insight Engine MVP.

The system treats LLMs as analysis modules inside a controlled workflow, not as unrestricted report writers.

## AI Usage Overview

LLMs are used for:

1. Structured extraction
   - Extract entities, technologies, event types, key facts, risks, opportunities, and confidence from news text.

2. Constrained Chinese websearch compatibility
   - Use DeepSeek websearch only for allowlisted Chinese webpages from 量子位, 机器之心, and 知乎 when API/RSS coverage is insufficient.
   - Preserve query text, returned URLs, snippets/content, visible dates, and collection timestamps for reproducibility.
   - Treat websearch as data collection assistance, not as evidence validation.

3. Semantic event clustering
   - Determine whether multiple news items describe the same event.

4. Importance explanation
   - Explain why ranked events matter based on structured evidence.

5. Daily report generation
   - Convert structured event data into a readable Chinese analysis report.

6. Quality review
   - Detect unsupported claims, missing sections, weak logic, and possible hallucinations.

LLMs are not used to:

- Invent news
- Invent sources, dates, URLs, companies, or facts
- Replace field validation
- Directly generate reports from uncleaned raw data
- Make unsupported investment or policy claims
- Use non-allowlisted Chinese webpages through websearch for the MVP Chinese source path

## Prompt Design Principles

Every reusable prompt or skill should specify:

- Role
- Input format
- Output format
- Required fields
- Allowed enum values
- Evidence requirements
- Confidence requirements
- Forbidden behavior
- Error handling behavior

## Core Prompt/Skill Modules

The MVP uses these reusable skill modules:

- `data-source-evaluation`
- `news-structuring`
- `event-clustering`
- `importance-scoring`
- `daily-report-generation`
- `report-quality-check`

## Chinese Websearch Prompt Pattern

Key constraints:

- Use DeepSeek websearch only with site restrictions for `qbitai.com`, `jiqizhixin.com`, or `zhihu.com`.
- Return structured search observations, not final analysis.
- Required fields per returned item: query, title, url, source/site, snippet_or_content, visible_published_at, collected_at, and missing_fields.
- If a date, URL, source, funding amount, policy detail, company name, or technical claim is not visible in the result/page text, mark it missing instead of inferring it.
- Keep 知乎 results marked as `community` source type unless a more specific source type is justified by the item itself.
- Do not merge websearch observations into the main dataset until deterministic field validation passes.

## Structured Extraction Prompt Pattern

Key constraints:

- Output valid JSON.
- Use only input text.
- Unknown fields should be `null`, `[]`, or `other`.
- Include evidence for important judgments.
- Include confidence.
- Do not output unsupported facts.

## Report Generation Prompt Pattern

Key constraints:

- Generate report from structured event data only.
- Top events must reference event IDs or news IDs.
- Trends must be supported by key facts or multiple events.
- Risks and opportunities must map to structured tags or evidence.
- Do not overstate weak evidence.

## Error Types

### Data Errors

Examples:

- Missing title
- Missing source
- Missing published_at
- Missing summary/content
- Inconsistent date format
- Duplicate news
- Weak AI relevance
- Websearch result from a non-allowlisted Chinese site
- Search snippet without a traceable visible date

Handling:

- Normalize dates and source names.
- Mark missing fields.
- Remove or down-rank low-quality data.
- Keep traceable raw payloads where possible.
- Reject or quarantine Chinese websearch results outside the allowlist.

### LLM Output Errors

Examples:

- Invalid JSON
- Missing required fields
- Invalid enum values
- Scores outside valid range
- Evidence missing
- Unsupported facts
- Low confidence extraction

Handling:

- Re-run or repair invalid JSON.
- Map invalid enum values to `other` when appropriate.
- Fill missing optional fields with `null` or `[]`.
- Remove hallucinated facts.
- Send low-confidence items to review.

### Analysis Errors

Examples:

- Unrelated items merged into one event
- Top event ranking lacks evidence
- Trend judgment based on a single weak item
- Risk or opportunity claim without support

Handling:

- Require related news IDs for events.
- Use rule-based scoring plus LLM explanation.
- Require evidence for each major claim.
- Review Top events manually.

### Output Errors

Examples:

- Chart counts do not match structured data
- Report mentions nonexistent news
- Data source explanation is missing
- Schema explanation is too shallow

Handling:

- Run final quality check.
- Verify chart data source.
- Check all report claims against structured data.

## Human Review Points

Manual review is required for:

- Final source selection
- Schema approval
- Low-confidence important news
- Top 3-5 event ranking
- Final report conclusions
- Documentation accuracy

## Limitations

- LLM extraction may still miss subtle context.
- Some sources may provide only short summaries.
- Small sample size limits trend confidence.
- Human review remains necessary for high-impact claims.
