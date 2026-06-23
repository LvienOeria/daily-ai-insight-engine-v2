import * as d3 from "d3";
import { useState } from "react";
import type { DistributionDatum } from "../types";

interface DonutChartProps {
  data: DistributionDatum[];
  label: string;
  description?: string;
}

const colors = ["#2563eb", "#059669", "#dc2626", "#7c3aed", "#d97706", "#0891b2"];

export function DonutChart({ data, label, description }: DonutChartProps) {
  const [hovered, setHovered] = useState<DistributionDatum | null>(null);
  const width = 280;
  const height = 220;
  const radius = 78;
  const pie = d3.pie<DistributionDatum>().value((datum) => datum.count).sort(null);
  const arc = d3.arc<d3.PieArcDatum<DistributionDatum>>().innerRadius(46).outerRadius(radius);
  const total = d3.sum(data, (datum) => datum.count);

  const isEmpty = data.length === 0;

  return (
    <figure className="chart compact-chart">
      <figcaption>
        <span>{label}</span>
        {hovered ? <em>{hovered.name}: {hovered.count}</em> : null}
      </figcaption>
      {description ? <p className="chart-description">{description}</p> : null}
      {isEmpty ? (
        <p className="muted chart-empty">No data available for this chart.</p>
      ) : (
        <div className="donut-layout">
          <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={label}>
            <g transform={`translate(${width / 2}, ${height / 2})`}>
              {pie(data).map((slice, index) => (
                <path
                  key={slice.data.name}
                  d={arc(slice) ?? undefined}
                  fill={colors[index % colors.length]}
                  className={hovered?.name === slice.data.name ? "donut-slice active" : "donut-slice"}
                  tabIndex={0}
                  onMouseEnter={() => setHovered(slice.data)}
                  onMouseLeave={() => setHovered(null)}
                  onFocus={() => setHovered(slice.data)}
                  onBlur={() => setHovered(null)}
                />
              ))}
              <text textAnchor="middle" y={-2} className="donut-total">
                {total}
              </text>
              <text textAnchor="middle" y={18} className="donut-caption">
                items
              </text>
            </g>
          </svg>
          <ul className="legend">
            {data.map((datum, index) => (
              <li
                key={datum.name}
                className={hovered?.name === datum.name ? "active" : ""}
                onMouseEnter={() => setHovered(datum)}
                onMouseLeave={() => setHovered(null)}
              >
                <span style={{ backgroundColor: colors[index % colors.length] }} />
                <b>{datum.name}</b>
                <em>{datum.count}</em>
              </li>
            ))}
          </ul>
        </div>
      )}
    </figure>
  );
}
