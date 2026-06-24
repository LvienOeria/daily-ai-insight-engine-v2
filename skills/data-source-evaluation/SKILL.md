---
name: data-source-evaluation
description: "Use when: evaluating candidate data sources for the Daily AI Insight Engine, including APIs, RSS feeds, official blogs, technical communities, research sources, and manually curated static data."
---

# Data Source Evaluation Skill

## Purpose

Evaluate candidate sources before they enter the AI daily insight workflow.

This skill helps decide whether a source should be a core MVP source, an auxiliary source, or a future enhancement.

## When To Use

Use this skill when:

- Building the initial candidate source pool
- Comparing APIs, RSS feeds, official blogs, research sources, or community sources
- Deciding whether a source is suitable for the MVP
- Explaining data source selection reasons in documentation
- Checking whether a source satisfies required fields

## Inputs

For each candidate source, collect as much of the following as possible:

- source_name
- source_type
- access_method
- documentation_url or homepage_url
- sample_response or example_item
- language
- coverage
- update_frequency
- cost_or_limit
- known_constraints

## Evaluation Dimensions

Evaluate each source using these dimensions:

1. Field completeness
   - title
   - summary/content/description
   - source
   - published_at
   - url or unique identifier

2. AI topic relevance
   - Does it regularly cover AI model releases, AI applications, AI infrastructure, AI policy, research, open source, or capital events?

3. Source credibility
   - Is it an official source, reputable media source, research platform, developer community, or unverified social source?

4. Data structure stability
   - Is the response structured and predictable?
   - Does it require crawling dynamic pages?

5. Reproducibility
   - Can the data be fetched again or saved as a static dataset?
   - Are there API key, quota, or paywall issues?

6. Perspective value
   - Does the source contribute a distinct view such as official fact, industry interpretation, developer sentiment, research trend, Chinese market, or capital movement?

## Source Profile Output

Produce one profile per source:

```json
{
  "source_name": "",
  "source_type": "news_api | rss | official | community | research | manual_static | other",
  "access_method": "api | rss | manual | crawler | other",
  "coverage": "",
  "language": "zh | en | mixed | other",
  "field_completeness": {
    "title": "yes | no | unknown",
    "summary_or_content": "yes | no | partial | unknown",
    "source": "yes | no | unknown",
    "published_at": "yes | no | unknown",
    "url": "yes | no | unknown"
  },
  "strengths": [],
  "weaknesses": [],
  "risks": [],
  "recommended_tier": "core | auxiliary | future | reject",
  "reason": ""
}
```

## Tiering Rules

Core source:

- Provides most required fields
- Has high AI relevance
- Is stable and reproducible
- Can support the main analysis set

Auxiliary source:

- Provides useful signal but may lack some fields
- Useful for community discussion, research trend, or market context
- Should not be the only evidence source for Top events

Future source:

- Valuable but too costly, unstable, or complex for MVP
- May require crawler, login, paid API, or advanced integration

Reject:

- Missing critical fields
- Low AI relevance
- Cannot be verified
- Too unstable or legally risky for the current project

## Important Rules

- Do not assume a source has fields unless sample data or documentation supports it.
- If source quality is uncertain, mark it as auxiliary or future, not core.
- A missing full article body is acceptable if a useful summary or description exists.
- Missing title, source, and published_at are serious issues for MVP use.
- Prefer reproducibility over breadth for this MVP.

## Documentation Output

When documenting source choices, include:

- Why selected sources were chosen
- Which required fields they provide
- What perspectives they cover
- Why crawler-first collection was not chosen for MVP
- Which sources were deferred and why
