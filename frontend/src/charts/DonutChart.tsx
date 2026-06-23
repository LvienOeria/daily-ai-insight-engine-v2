import * as d3 from "d3";
import type { DistributionDatum } from "../types";

interface DonutChartProps {
  data: DistributionDatum[];
  label: string;
}

const colors = ["#2563eb", "#059669", "#dc2626", "#7c3aed", "#d97706", "#0891b2"];

export function DonutChart({ data, label }: DonutChartProps) {
  const width = 280;
  const height = 220;
  const radius = 78;
  const pie = d3.pie<DistributionDatum>().value((datum) => datum.count).sort(null);
  const arc = d3.arc<d3.PieArcDatum<DistributionDatum>>().innerRadius(46).outerRadius(radius);
  const total = d3.sum(data, (datum) => datum.count);

  return (
    <figure className="chart compact-chart">
      <figcaption>{label}</figcaption>
      <div className="donut-layout">
        <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={label}>
          <g transform={`translate(${width / 2}, ${height / 2})`}>
            {pie(data).map((slice, index) => (
              <path
                key={slice.data.name}
                d={arc(slice) ?? undefined}
                fill={colors[index % colors.length]}
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
            <li key={datum.name}>
              <span style={{ backgroundColor: colors[index % colors.length] }} />
              <b>{datum.name}</b>
              <em>{datum.count}</em>
            </li>
          ))}
        </ul>
      </div>
    </figure>
  );
}

