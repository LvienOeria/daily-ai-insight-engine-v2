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

No external API key is strictly required before implementation if the MVP uses RSS, arXiv, Hacker News public APIs, official feeds, and manually curated static data.

### Likely Optional

- `OPENAI_API_KEY`: needed only if local scripts call the OpenAI API directly for extraction, clustering, scoring, or report drafting.
- `NEWS_API_KEY` or `GNEWS_API_KEY`: useful if the selected collection path depends on a news aggregation API.
- `GITHUB_TOKEN`: useful if GitHub repositories, releases, or issues are used and unauthenticated rate limits are too low.
- `SERPAPI_API_KEY` or `TAVILY_API_KEY`: useful for search-based collection, but this should be treated as auxiliary or future scope unless source evaluation justifies it.

RSS feeds, arXiv, and Hacker News public APIs normally do not require API keys.

## Configuration To Decide Before Implementation

Before writing the workflow code, confirm or record:

- Reporting date and timezone. Default: `Asia/Shanghai`.
- Reporting window. Example: latest 1-7 days, depending on source freshness.
- Data source mix. Example: official AI company blogs, arXiv, Hacker News, selected RSS feeds, and optional manual static samples.
- Output locations for raw data, cleaned data, structured data, clustered events, rankings, visualizations, reports, and quality checks.
- Whether LLM calls are performed through local API scripts or manually through the current Codex session.
- Whether generated public news datasets should be committed for reproducibility.

## Secret Handling Rules

- Do not paste real API keys into `AGENTS.md`, docs, source files, reports, or committed datasets.
- Store real keys only in local `.env` or the operating system secret manager.
- If a raw provider payload includes credentials, remove or redact the credential before saving the artifact.

