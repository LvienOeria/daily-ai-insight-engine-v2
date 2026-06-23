import * as d3 from "d3";
import type { DistributionDatum } from "../types";

interface BarChartProps {
  data: DistributionDatum[];
  label: string;
}

export function BarChart({ data, label }: BarChartProps) {
  const width = 520;
  const height = 220;
  const margin = { top: 16, right: 24, bottom: 48, left: 42 };
  const innerWidth = width - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;
  const max = d3.max(data, (datum) => datum.count) ?? 1;
  const x = d3
    .scaleBand()
    .domain(data.map((datum) => datum.name))
    .range([0, innerWidth])
    .padding(0.22);
  const y = d3.scaleLinear().domain([0, max]).nice().range([innerHeight, 0]);

  return (
    <figure className="chart">
      <figcaption>{label}</figcaption>
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
                  className="bar"
                />
                <text
                  x={barX + x.bandwidth() / 2}
                  y={barY - 6}
                  textAnchor="middle"
                  className="bar-value"
                >
                  {datum.count}
                </text>
                <text
                  x={barX + x.bandwidth() / 2}
                  y={innerHeight + 20}
                  textAnchor="middle"
                  className="axis-label"
                >
                  {datum.name.length > 12 ? `${datum.name.slice(0, 11)}…` : datum.name}
                </text>
              </g>
            );
          })}
        </g>
      </svg>
    </figure>
  );
}

