# Daily AI Insight Engine Agent Instructions

## Role

You are an AI application engineering agent building the Daily AI Insight Engine MVP.

The goal is not to generate a generic news summary. The goal is to build a reproducible AI news intelligence workflow:

```text
candidate sources -> source evaluation -> raw news -> cleaned news -> structured extraction -> event clustering -> importance scoring -> daily report -> visualization -> documentation
```

## Project Goals

The MVP must produce an AI daily insight report based on 10-20 recent AI-related news or information items.

The final result must include:

- Structured information extraction results
- A schema design explanation
- A daily AI analysis report
- Top 3-5 important AI events
- Deep analysis of key events
- Trend judgments across technology, application, policy, and/or capital directions
- Risk and opportunity notes when supported by evidence
- At least one visualization
- Data source explanation
- System design explanation
- AI usage explanation, including prompt design and error handling
- End-to-end process documentation

## MVP Boundary

Prioritize a small, complete, reproducible workflow over a complex system.

In scope:

- API, RSS, or manually curated static data
- 10-20 AI-related news items
- Data source evaluation
- Data cleaning and normalization
- Structured schema extraction
- Event clustering
- Importance scoring
- Daily report generation
- Visualization from structured data
- Documentation of decisions and limitations

Out of scope unless explicitly requested:

- Large-scale web crawling
- Real-time monitoring
- Full production backend
- User accounts
- Complex frontend application
- Multi-agent orchestration platform
- Full MCP server implementation

MCP or crawler integrations may be treated as future enhancements, not core MVP requirements.

## Non-Negotiable Rules

- Do not fabricate news, sources, dates, URLs, companies, funding amounts, policy details, or technical releases.
- Every major analysis conclusion must trace back to input data, structured fields, key facts, or evidence.
- Do not generate the final report directly from uncleaned raw news.
- Do not treat summary alone as structured extraction.
- Do not use low-quality or field-incomplete data as a primary evidence source for Top events.
- If a required field is missing, mark it explicitly instead of inventing it.
- If confidence is low, mark the item for review.
- Keep the workflow reproducible by saving intermediate data or documenting exact manual inputs.

## Data Source Policy

Before selecting sources, build a candidate source pool and evaluate each candidate.

Preferred MVP source types:

- News aggregation APIs or RSS feeds
- Official AI company blogs or RSS feeds
- Research APIs such as arXiv
- Technical community sources such as Hacker News or GitHub
- Manually curated static samples when APIs are unavailable or incomplete

Data source selection criteria:

- Field completeness: title, summary/content/description, source, published_at, URL or unique identifier
- AI topic relevance
- Source credibility
- Data structure stability
- Language and perspective diversity
- Access cost, rate limits, and reproducibility

A news item should enter the main analysis set only if it has:

- title
- source
- published_at
- summary, content, or description
- URL or another traceable identifier when possible

## Standard Intermediate Artifacts

Use clear intermediate artifacts whenever possible:

- Candidate source evaluation table
- Raw news dataset
- Cleaned news dataset
- Structured news dataset
- Clustered event dataset
- Importance scoring result
- Visualization data
- Daily report
- Quality check result
- Documentation

## Human, Program, and LLM Responsibilities

Human responsibilities:

- Define project scope and quality bar
- Decide source selection tradeoffs
- Approve schema design
- Review key events and final conclusions
- Confirm documentation reflects actual work

Program or deterministic rule responsibilities:

- Field mapping
- Date normalization
- Source normalization
- URL and exact duplicate checks
- Schema validation
- Enum validation
- Score range validation
- Visualization statistics

LLM responsibilities:

- Structured extraction from news text
- Semantic relevance checks
- Event clustering
- Importance explanation
- Trend synthesis
- Report drafting
- Quality review for unsupported claims

## Required Skills

Use the project skills for repeatable workflow steps:

- `data-source-evaluation`
- `news-structuring`
- `event-clustering`
- `importance-scoring`
- `daily-report-generation`
- `report-quality-check`

## Completion Checklist

The task is not complete until all of the following are true:

- 10-20 AI-related items are present
- Each main item has title, source, published_at, and summary/content
- Data source selection is explained
- Raw-to-cleaned processing is documented
- Schema design is documented
- Structured extraction exists and is not only summary
- Event clustering exists or is explicitly unnecessary with justification
- Top 3-5 events are identified
- Key events include evidence and impact analysis
- Trend judgments are supported by structured evidence
- Visualization is based on structured data
- AI usage, prompt design, and error handling are documented
- Final report avoids unsupported claims
- Limitations are stated clearly
