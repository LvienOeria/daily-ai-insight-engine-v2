# Daily AI Insight Engine

Reproducible MVP workflow for AI news intelligence:

```text
candidate sources -> source evaluation -> raw news -> cleaned news -> structured extraction
-> event clustering -> importance scoring -> daily report -> React/D3 dashboard -> quality check
```

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

Use Node.js 20 or newer. This workspace was verified with:

```bash
PATH=/Users/chx/.nvm/versions/node/v22.22.2/bin:$PATH pnpm build
```

## Configuration

Copy `.env.example` to `.env` and fill local secrets only in `.env`.

Required for real LLM execution:

```text
DEEPSEEK_API_KEY
```

Defaults:

- LLM provider: DeepSeek
- LLM model: `deepseek-v4-flash` for both extraction and report generation
- Reporting window: latest 3 days
- Timezone: `Asia/Shanghai`
- Frontend data artifact: `frontend/public/data/latest.json`

## Run

Development run without LLM calls:

```bash
.venv/bin/python -m daily_ai_insight run --mock-llm
```

Real LLM run:

```bash
.venv/bin/python -m daily_ai_insight run
```

Start dashboard:

```bash
cd frontend
PATH=/Users/chx/.nvm/versions/node/v22.22.2/bin:$PATH pnpm dev
```

## Chinese Websearch Compatibility

Chinese DeepSeek websearch is constrained to:

- 量子位: `qbitai.com`
- 机器之心: `jiqizhixin.com`
- 知乎: `zhihu.com`

The current implementation consumes saved websearch observations from:

```text
data/manual/chinese_websearch_observations.json
```

If the file is absent, those sources are marked as future/fetch issue in source evaluation. Websearch results are accepted only after allowlist and required-field validation.

## Verification

```bash
.venv/bin/python -m pytest
.venv/bin/ruff check daily_ai_insight tests
cd frontend && PATH=/Users/chx/.nvm/versions/node/v22.22.2/bin:$PATH pnpm build
```
