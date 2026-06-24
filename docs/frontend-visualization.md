# Frontend and Visualization

## Stack

- React 18
- Vite 6
- pnpm
- D3.js 7
- lucide-react (icons)

## Role

The frontend is display-only. Python scripts produce all authoritative data artifacts. The React app reads `frontend/public/data/latest.json` and renders a dashboard. It does not call LLMs, create facts, or alter rankings.

## Dashboard Views

- **Overview**: metrics row, donut charts (source types, event types), risk/opportunity matrix, Top 5 events
- **Events**: searchable list with full event details, score breakdowns, evidence, source links
- **Analysis**: report text with 7 sections rendered as structured cards
- **Sources**: source evaluation table with tier, status, item counts
- **Quality**: quality check results with pass/fail, issues list

## Charts

| Chart | Library | Description |
|:---|:---|:---|
| Source type distribution | D3 Donut | Research vs media vs community |
| Event type distribution | D3 Donut | Clustering categories |
| Risk/Opportunity Matrix | D3 Scatter | Color by event type, size by confidence, zoom/pan |

## Data Contract

The pipeline writes one file that the frontend consumes:

```text
frontend/public/data/latest.json
```

## Repository Rules

- Commit source files and `pnpm-lock.yaml`
- Do not commit `node_modules/` or `dist/`
