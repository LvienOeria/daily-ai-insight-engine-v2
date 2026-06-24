import * as d3 from "d3";
import { useEffect, useMemo, useRef, useState } from "react";
import type { RiskOpportunityDatum } from "../types";

const W = 440;
const H = 320;
const M = { top: 28, right: 28, bottom: 52, left: 56 };
const IW = W - M.left - M.right;
const IH = H - M.top - M.bottom;

const EVENT_COLORS: Record<string, string> = {
  research: "#3B82F6", model_release: "#F87171", product_release: "#FB923C",
  funding: "#34D399", partnership: "#A78BFA", regulation: "#FBBF24",
  security_risk: "#EF4444", open_source: "#22D3EE", infrastructure: "#818CF8",
  business_update: "#F472B6", acquisition: "#C084FC", market_commentary: "#94A3B8",
  other: "#64748B",
};
const COLOR_DEFAULT = "#94a3b8";

/* ---- force anti-overlap ---- */

interface LayoutItem {
  datum: RiskOpportunityDatum; x: number; y: number; dx: number; dy: number;
}

function computeLayout(data: RiskOpportunityDatum[]): LayoutItem[] {
  const items: LayoutItem[] = data.map((d) => ({
    datum: d, x: d.opportunity_level, y: d.risk_level, dx: 0, dy: 0,
  }));
  if (items.length <= 1) return items;
  const minDist = 0.32, iters = 50, step = 0.045, pull = 0.12;
  for (let iter = 0; iter < iters; iter++) {
    for (let i = 0; i < items.length; i++) {
      for (let j = i + 1; j < items.length; j++) {
        const a = items[i], b = items[j];
        const ax = a.x + a.dx, ay = a.y + a.dy;
        const bx = b.x + b.dx, by = b.y + b.dy;
        const dx = ax - bx, dy = ay - by;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < minDist && dist > 0.001) {
          const f = (minDist - dist) / dist * step;
          a.dx += dx * f; a.dy += dy * f;
          b.dx -= dx * f; b.dy -= dy * f;
        }
      }
    }
    for (const it of items) { it.dx *= (1 - pull); it.dy *= (1 - pull); }
  }
  return items;
}

/* ---- component ---- */

export function MatrixChart({ data }: MatrixChartProps) {
  const [hovered, setHovered] = useState<RiskOpportunityDatum | null>(null);
  const [selected, setSelected] = useState<RiskOpportunityDatum | null>(null);
  const [tooltipPos, setTooltipPos] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const layout = useMemo(() => computeLayout(data), [data]);

  useEffect(() => {
    const svgEl = svgRef.current;
    if (!svgEl) return;
    const svg = d3.select(svgEl);
    const g = svg.select<SVGGElement>("g.zoom-group");
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.8, 5])
      .on("zoom", (evt) => g.attr("transform", evt.transform.toString()));
    svg.call(zoom);
    svg.on("contextmenu", (evt) => { evt.preventDefault(); resetZoom(); });
    svg.on("dblclick.zoom", () => resetZoom());
    function resetZoom() {
      (svg as any).transition().duration(250).call(zoom.transform, d3.zoomIdentity);
    }
  }, []);

  const x = d3.scaleLinear().domain([0, 5]).range([0, IW]);
  const y = d3.scaleLinear().domain([5, 0]).range([0, IH]);

  const active = hovered || selected;

  return (
    <figure
      className="chart matrix-chart"
      ref={containerRef}
      onMouseMove={(e) => {
        const rect = containerRef.current?.getBoundingClientRect();
        if (rect) setTooltipPos({ x: e.clientX - rect.left + 14, y: e.clientY - rect.top - 10 });
      }}
    >
      <figcaption>
        <span>Risk / Opportunity Matrix</span>
      </figcaption>
      {data.length === 0 ? (
        <p className="muted chart-empty">No events available.</p>
      ) : (
        <div style={{ position: "relative" }}>
          <svg ref={svgRef} viewBox={`0 0 ${W} ${H}`} role="img" style={{ cursor: "grab", display: "block" }}>
            <g className="zoom-group" transform={`translate(${M.left},${M.top})`}>
              {[0, 1, 2, 3, 4, 5].map((t) => (
                <g key={`g-${t}`}>
                  <line x1={x(t)} x2={x(t)} y1={y(5)} y2={y(0)} className="grid-line" />
                  <line x1={x(0)} x2={x(5)} y1={y(t)} y2={y(t)} className="grid-line" />
                  <text x={x(t)} y={IH + 22} textAnchor="middle" className="axis-label">{t}</text>
                  <text x={-14} y={y(t) + 4} textAnchor="end" className="axis-label">{t}</text>
                </g>
              ))}
              <text x={IW / 2} y={IH + 44} textAnchor="middle" className="axis-title">Opportunity →</text>
              <text transform={`translate(-42, ${IH / 2}) rotate(-90)`} textAnchor="middle" className="axis-title">Risk →</text>
              {layout.map(({ datum, dx, dy }) => {
                const cx = x(datum.opportunity_level + dx);
                const cy = y(datum.risk_level + dy);
                const color = EVENT_COLORS[datum.event_type] || COLOR_DEFAULT;
                const r = datum.confidence === "high" ? 6 : datum.confidence === "medium" ? 5 : 3.5;
                const isActive = active?.event_id === datum.event_id;
                return (
                  <g key={datum.event_id}>
                    {(Math.abs(dx) > 0.005 || Math.abs(dy) > 0.005) && (
                      <line x1={x(datum.opportunity_level)} y1={y(datum.risk_level)} x2={cx} y2={cy} className="jitter-line" />
                    )}
                    <circle cx={cx} cy={cy} r={r} fill={color}
                      className={`matrix-dot ${datum.confidence} ${isActive ? "active" : ""}`}
                      onMouseEnter={() => setHovered(datum)}
                      onMouseLeave={() => setHovered(null)}
                      onClick={() => setSelected(datum)}
                    />
                    <title>{datum.event_name + "\n"}risk={datum.risk_level.toFixed(2)} opp={datum.opportunity_level.toFixed(2)} {datum.event_type}</title>
                  </g>
                );
              })}
            </g>
          </svg>

          {/* floating tooltip */}
          <div
            className="matrix-tooltip"
            style={{
              left: tooltipPos.x,
              top: tooltipPos.y,
              opacity: hovered ? 1 : 0,
              pointerEvents: "none",
            }}
          >
            {hovered && (
              <>
                <strong>{hovered.event_name}</strong>
                <span>Risk {hovered.risk_level.toFixed(2)} · Opp {hovered.opportunity_level.toFixed(2)}</span>
                <span className="muted">{hovered.event_type} · {hovered.confidence}</span>
              </>
            )}
          </div>
        </div>
      )}

      {/* inline legend */}
      <div className="matrix-legend">
        {Object.entries(EVENT_COLORS).slice(0, 8).map(([type, color]) => (
          <span key={type} className="legend-chip">
            <i style={{ background: color }} />
            {type.replace(/_/g, " ")}
          </span>
        ))}
      </div>
    </figure>
  );
}

interface MatrixChartProps { data: RiskOpportunityDatum[]; }
