# Setup

## Repository

This project is initialized as a git repository.

Keep generated datasets, structured outputs, reports, visualizations, and documentation in the repository when they are part of the reproducible MVP. Do not commit local secrets, caches, virtual environments, or machine-specific files.

## API Key Configuration

Create a local `.env` file from `.env.example`:

```bash
cp .env.example .env
```

Fill only the keys selected for the MVP after source evaluation.

### Required Now

The MVP will use DeepSeek for local LLM scripts.

Required local value:

- `DEEPSEEK_API_KEY`

Configured defaults:

- `LLM_PROVIDER=deepseek`
- `DEEPSEEK_BASE_URL=https://api.deepseek.com`
- `DEEPSEEK_MODEL=deepseek-v4-flash`
- `DEEPSEEK_REPORT_MODEL=deepseek-v4-pro`
- `DEEPSEEK_WEBSEARCH_ENABLED=true`
- `DEEPSEEK_WEBSEARCH_ALLOWED_SITES=qbitai.com,jiqizhixin.com,zhihu.com`
- `REPORT_TIMEZONE=Asia/Shanghai`
- `REPORT_WINDOW_DAYS=3`

DeepSeek's API is OpenAI-compatible, so local scripts can use the OpenAI SDK with the DeepSeek base URL.

### Likely Optional

- `NEWS_API_KEY` or `GNEWS_API_KEY`: useful if the selected collection path depends on a news aggregation API.
- `GITHUB_TOKEN`: useful if GitHub repositories, releases, or issues are used and unauthenticated rate limits are too low.
- `SERPAPI_API_KEY` or `TAVILY_API_KEY`: useful for search-based collection, but this should be treated as auxiliary or future scope unless source evaluation justifies it.

RSS feeds, arXiv, and Hacker News public APIs normally do not require API keys.

## Current MVP Defaults

The current default runtime settings are also captured in `config/defaults.json`.

- Reporting window: latest 3 days
- Reporting timezone: `Asia/Shanghai`
- LLM provider: DeepSeek API
- LLM execution mode: local scripts
- Data source policy: attempt candidate fetching first, evaluate observed data quality, then select core sources
- Chinese source compatibility path: DeepSeek websearch, restricted to 量子位, 机器之心, and 知乎

## Configuration To Decide Before Implementation

Before writing the workflow code, confirm or record:

- Data source mix after attempted fetches. Example: official AI company blogs, arXiv, Hacker News, selected RSS feeds, and optional manual static samples.
- Chinese websearch query templates and per-site result caps.
- Output locations for raw data, cleaned data, structured data, clustered events, rankings, visualizations, reports, and quality checks.
- Whether generated public news datasets should be committed for reproducibility.

## Chinese Websearch Constraints

Chinese websearch is a compatibility path, not a shortcut around source evaluation.

Implementation rules:

- Use DeepSeek websearch only for allowlisted pages from 量子位 (`qbitai.com`), 机器之心 (`jiqizhixin.com`), and 知乎 (`zhihu.com`).
- Store websearch observations separately before cleaning and validation.
- Accept a result into the main dataset only after it has title, source/site, published_at or traceable visible date, URL, and summary/content.
- Treat 知乎 as community signal by default. It should not become primary evidence for Top events unless the specific item is complete, traceable, and factually grounded.
- Record rejected or quarantined websearch results in source evaluation notes when they explain source-selection tradeoffs.

## Secret Handling Rules

- Do not paste real API keys into `AGENTS.md`, docs, source files, reports, or committed datasets.
- Store real keys only in local `.env` or the operating system secret manager.
- If a raw provider payload includes credentials, remove or redact the credential before saving the artifact.
