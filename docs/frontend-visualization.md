# Frontend and Visualization

## Decision

The MVP frontend uses:

- React
- Vite
- pnpm
- D3.js

## Role Boundary

The frontend is a display layer only.

Python scripts produce the authoritative artifacts:

- raw news
- cleaned news
- structured news
- clustered events
- importance scores
- visualization data
- daily report
- quality check result

The React app reads those artifacts and renders a dashboard. It must not call LLMs, create facts, alter rankings, or generate untraceable conclusions.

## Dashboard Data Contract

The pipeline exports frontend-ready data to:

```text
frontend/public/data/latest.json
```

The dashboard may include:

- source distribution
- event type distribution
- industry area distribution
- Top event ranking
- risk and opportunity matrix
- report summary and evidence links

## Evidence Requirements

Top events, trends, risks, and opportunities must preserve traceability through:

- `news_id`
- `event_id`
- source names
- source URLs
- key facts
- evidence snippets

## Repository Rules

- Commit frontend source files.
- Commit `pnpm-lock.yaml` after dependencies are installed.
- Do not commit `node_modules/`.
- Do not treat built frontend assets as source unless a later delivery requirement explicitly asks for static build output.
