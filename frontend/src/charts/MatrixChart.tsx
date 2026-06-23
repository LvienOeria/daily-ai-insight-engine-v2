import * as d3 from "d3";
import type { RiskOpportunityDatum } from "../types";

interface MatrixChartProps {
  data: RiskOpportunityDatum[];
}

export function MatrixChart({ data }: MatrixChartProps) {
  const width = 420;
  const height = 300;
  const margin = { top: 24, right: 24, bottom: 46, left: 50 };
  const innerWidth = width - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;
  const x = d3.scaleLinear().domain([0, 5]).range([0, innerWidth]);
  const y = d3.scaleLinear().domain([0, 5]).range([innerHeight, 0]);

  return (
    <figure className="chart matrix-chart">
      <figcaption>Risk / Opportunity Matrix</figcaption>
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Risk opportunity matrix">
        <g transform={`translate(${margin.left}, ${margin.top})`}>
          {[0, 1, 2, 3, 4, 5].map((tick) => (
            <g key={`x-${tick}`}>
              <line x1={x(tick)} x2={x(tick)} y1={0} y2={innerHeight} className="grid-line" />
              <line x1={0} x2={innerWidth} y1={y(tick)} y2={y(tick)} className="grid-line" />
              <text x={x(tick)} y={innerHeight + 20} textAnchor="middle" className="axis-label">
                {tick}
              </text>
              <text x={-12} y={y(tick) + 4} textAnchor="end" className="axis-label">
                {tick}
              </text>
            </g>
          ))}
          {data.map((datum) => (
            <g key={datum.event_id}>
              <circle
                cx={x(datum.opportunity_level)}
                cy={y(datum.risk_level)}
                r={datum.confidence === "high" ? 8 : datum.confidence === "medium" ? 7 : 5}
                className={`matrix-dot ${datum.confidence}`}
              />
              <title>
                {datum.event_name}: risk {datum.risk_level}, opportunity{" "}
                {datum.opportunity_level}
              </title>
            </g>
          ))}
          <text x={innerWidth / 2} y={innerHeight + 42} textAnchor="middle" className="axis-title">
            Opportunity
          </text>
          <text
            transform={`translate(-38, ${innerHeight / 2}) rotate(-90)`}
            textAnchor="middle"
            className="axis-title"
          >
            Risk
          </text>
        </g>
      </svg>
    </figure>
  );
}

