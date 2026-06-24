---
name: report-quality-check
description: "Use when: checking the Daily AI Insight Engine outputs for task completeness, schema validity, evidence traceability, hallucinations, unsupported claims, visualization consistency, and documentation gaps."
---

# Report Quality Check Skill

## Purpose

Check whether the Daily AI Insight Engine MVP satisfies the task requirements and avoids unsupported AI-generated claims.

Use this skill before treating the project as complete.

## When To Use

Use after generating:

- Structured data
- Daily report
- Visualization
- Documentation

Also use after any major revision to the report or schema.

## Inputs

Provide:

- Task requirements
- Raw or cleaned news dataset
- Structured news dataset
- Clustered/ranked events
- Final report
- Visualization outputs or statistics
- Documentation files

## Output Format

```json
{
  "passed": true,
  "requirement_check": {
    "has_10_to_20_items": true,
    "items_have_required_fields": true,
    "has_schema": true,
    "schema_design_explained": true,
    "not_only_summary": true,
    "has_top_events": true,
    "has_deep_analysis": true,
    "has_trend_judgment": true,
    "has_risk_or_opportunity": true,
    "has_visualization": true,
    "has_data_source_explanation": true,
    "has_system_design": true,
    "has_ai_usage_prompt_error_handling": true,
    "has_core_process": true
  },
  "missing_items": [],
  "weak_points": [],
  "unsupported_claims": [],
  "suspected_hallucinations": [],
  "data_quality_issues": [],
  "visualization_issues": [],
  "recommended_fixes": []
}
```

## Requirement Checklist

Check that the project includes:

- 10-20 recent AI-related news or information items
- Mixed Chinese and English sources when possible
- Title, summary/content, source, and published_at for each main item
- Data source selection reasons
- Structured schema
- Schema design explanation
- Structured extraction beyond summary
- Data cleaning logic
- Batch processing or processing strategy
- Result validation logic
- Top 3-5 important events
- Key event deep analysis
- Trend judgments
- Risk and opportunity notes when supported
- Visualization
- AI usage explanation
- Prompt design explanation
- Error handling explanation
- End-to-end process documentation

## Evidence Traceability Check

For each major report claim, verify that it links to one of:

- news_id
- event_id
- source
- key_facts
- evidence
- visualization statistic

Flag claims that:

- Add new facts not in the dataset
- Mention entities not in structured data
- Give dates or amounts not in sources
- Make broad trend judgments from one weak item
- Present speculation as fact

## Schema Check

Verify:

- Required fields exist
- Enum fields use allowed values
- Scores are within valid range
- Confidence fields are present
- Evidence is not empty for important records
- Low-quality records are not used as strong evidence

## Visualization Check

Verify:

- Charts are generated from structured data
- Chart labels match schema values
- Counts are consistent with datasets
- Conclusions drawn from charts are not overstated

## Documentation Check

Verify documentation explains:

- Why sources were chosen
- Why crawler-first collection was not used for MVP, if applicable
- How data was cleaned
- How schema fields support analysis
- Where LLM was used
- How prompts constrain LLM output
- How errors and low-confidence results are handled
- What limitations remain

## Pass/Fail Guidance

Set `passed` to false if any of these are missing:

- Required data fields
- Structured schema
- Structured extraction result
- Analysis report
- Visualization
- Data source explanation
- AI usage and error handling explanation

Set `passed` to false if there are serious unsupported claims or fabricated facts.
