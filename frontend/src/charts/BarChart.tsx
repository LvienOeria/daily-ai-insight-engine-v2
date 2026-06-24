import * as d3 from "d3";
import { useState } from "react";
import type { DistributionDatum } from "../types";

const LABEL_MAP: Record<string, string> = {
  research: "研究", foundation_model: "基础模型", ai_agent: "AI Agent",
  multimodal_ai: "多模态AI", ai_infrastructure: "AI基础设施", chip_compute: "芯片算力",
  enterprise_ai: "企业AI", consumer_ai: "消费AI", developer_tools: "开发者工具",
  ai_safety: "AI安全", policy_regulation: "政策监管", capital_market: "资本市场", other: "其他",
};

function _shortLabel(name: string): string {
  if (LABEL_MAP[name]) return LABEL_MAP[name];
  return name.length > 8 ? name.slice(0, 7) + "…" : name;
}

interface BarChartProps {
  data: DistributionDatum[];
  label: string;
  description?: string;
  valueSuffix?: string;
  onSelect?: (name: string) => void;
}

export function BarChart({ data, label, description, valueSuffix = "", onSelect }: BarChartProps) {
  const [hovered, setHovered] = useState<DistributionDatum | null>(null);
  const width = 520;
  const height = 260;
  const margin = { top: 24, right: 24, bottom: 64, left: 42 };
  const innerWidth = width - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;
  const max = d3.max(data, (datum) => datum.count) ?? 1;
  const x = d3
    .scaleBand()
    .domain(data.map((datum) => datum.name))
    .range([0, innerWidth])
    .padding(0.22);
  const y = d3.scaleLinear().domain([0, max]).nice().range([innerHeight, 0]);

  const isEmpty = data.length === 0;

  return (
    <figure className="chart">
      <figcaption>
        <span>{label}</span>
        {hovered ? <em>{hovered.name}: {hovered.count}{valueSuffix}</em> : null}
      </figcaption>
      {description ? <p className="chart-description">{description}</p> : null}
      {isEmpty ? (
        <p className="muted chart-empty">No data available for this chart.</p>
      ) : (
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={label}>
        <g transform={`translate(${margin.left}, ${margin.top})`}>
          {y.ticks(4).map((tick) => (
            <g key={tick} transform={`translate(0, ${y(tick)})`}>
              <line x1={0} x2={innerWidth} className="grid-line" />
              <text x={-10} y={4} textAnchor="end" className="axis-label">
                {tick}
              </text>
            </g>
          ))}
          {data.map((datum) => {
            const barX = x(datum.name) ?? 0;
            const barY = y(datum.count);
            return (
              <g key={datum.name}>
                <rect
                  x={barX}
                  y={barY}
                  width={x.bandwidth()}
                  height={innerHeight - barY}
                  className={`bar ${hovered?.name === datum.name ? "active" : ""}`}
                  tabIndex={0}
                  role="button"
                  onMouseEnter={() => setHovered(datum)}
                  onMouseLeave={() => setHovered(null)}
                  onFocus={() => setHovered(datum)}
                  onBlur={() => setHovered(null)}
                  onClick={() => onSelect?.(datum.name)}
                />
                <text
                  x={barX + x.bandwidth() / 2}
                  y={barY - 6}
                  textAnchor="middle"
                  className="bar-value"
                >
                  {datum.count}{valueSuffix}
                </text>
                <text
                  x={barX + x.bandwidth() / 2}
                  y={innerHeight + 18}
                  textAnchor="end"
                  className="axis-label"
                  transform={`rotate(-35, ${barX + x.bandwidth() / 2}, ${innerHeight + 18})`}
                >
                  {_shortLabel(datum.name)}
                </text>
              </g>
            );
          })}
        </g>
      </svg>
      )}
    </figure>
  );
}
