# Daily AI Insight Engine

Reproducible MVP workflow for AI news intelligence:

```text
fetch (RSS + HTTP + API) -> clean -> structured extraction (DeepSeek)
-> event clustering -> importance scoring -> daily report -> React/D3 dashboard -> quality check
```

## Data Sources

| Source | Method | Language | Coverage |
|:---|:---|:---|:---|
| arXiv | API | en | AI/ML/CL research preprints |
| 量子位 (qbitai.com) | HTTP scraping | zh | Chinese AI industry & technology |
| TechCrunch AI | RSS | en | Startup funding, product launches |
| The Verge | RSS + AI filter | en | Consumer tech & AI coverage |

## Runtime

Python:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
```

Frontend:

```bash
cd frontend
pnpm install
```

Requires Node.js 20+. Verified with Node 22.22.2.

## Configuration

Copy `.env.example` to `.env` and set:

```text
DEEPSEEK_API_KEY=sk-...
```

Defaults:
- LLM: DeepSeek (`deepseek-v4-flash` for extraction, `deepseek-v4-pro` for reports)
- Reporting window: latest 3 days
- Timezone: `Asia/Shanghai`
- RSS cache: 1 hour (`data/cache/`)

## Run

```bash
# Real LLM run
.venv/bin/python -m daily_ai_insight run

# Dev mode (no LLM calls, deterministic extraction)
.venv/bin/python -m daily_ai_insight run --mock-llm

# Start dashboard
cd frontend && pnpm dev
```

## Pipeline

```
sources.json -> fetch -> source_evaluation.json
    -> raw_news.json -> clean -> cleaned_news.json
    -> structure (DeepSeek) -> structured_news.json
    -> cluster (DeepSeek) -> clustered_events.json
    -> score -> importance_scores.json
    -> visualize -> visualization_data.json
    -> report (DeepSeek) -> daily_ai_report.md
    -> quality check -> quality_check.json
    -> frontend/public/data/latest.json
```

## Verification

```bash
.venv/bin/python -m pytest
cd frontend && pnpm build
```
