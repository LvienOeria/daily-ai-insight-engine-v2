# Setup

## Repository

Keep generated datasets and reports in the repository for reproducibility. Never commit `.env`, caches, virtual environments, or `node_modules/`.

## API Key Configuration

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Required:

- `DEEPSEEK_API_KEY` — for LLM-powered structuring, clustering, and report generation

Optional (for additional source connectivity):

- `TAVILY_API_KEY` — alternative search backend

RSS feeds, arXiv API, and direct HTTP scraping do not require API keys.

## Current MVP Defaults

Configured in `config/defaults.json`:

- Reporting window: 3 days
- Timezone: `Asia/Shanghai`
- LLM provider: DeepSeek API
- Extraction model: `deepseek-v4-flash`
- Report model: `deepseek-v4-pro`
- Frontend: React + Vite + pnpm + D3.js

## Data Sources

Four sources configured in `config/sources.json`:

| Source | Method | Language |
|:---|:---|:---|
| arXiv AI Search | API | en |
| 量子位 (qbitai.com) | Direct HTTP scraping | zh |
| TechCrunch AI | RSS | en |
| The Verge | RSS + AI keyword filter | en |

To add a new RSS source, add an entry with `"access_method": "rss"` and an `"endpoint_url"`. For an HTTP-scraped source, use `"access_method": "direct_http"`.

## Frontend

- Python scripts own data collection, cleaning, structuring, clustering, scoring, reporting, and quality checks.
- The React app is display-only. It reads `frontend/public/data/latest.json`.
- D3 charts show source distribution, event type distribution, and a risk/opportunity matrix.
- Commit `pnpm-lock.yaml`. Do not commit `node_modules/`.

## Secret Handling

- Store real keys only in local `.env`.
- Never paste API keys into docs, source files, or committed datasets.
