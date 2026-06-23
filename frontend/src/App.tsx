import { useEffect, useState } from "react";
import { Activity, Database, FileText } from "lucide-react";
import { loadDashboardData } from "./api";
import { BarChart } from "./charts/BarChart";
import { DonutChart } from "./charts/DonutChart";
import { MatrixChart } from "./charts/MatrixChart";
import { QualityPanel } from "./components/QualityPanel";
import { SourcePanel } from "./components/SourcePanel";
import { TopEvents } from "./components/TopEvents";
import type { DashboardData } from "./types";

export function App() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData().then(setData).catch((err: unknown) => {
      setError(err instanceof Error ? err.message : "Unknown data loading error");
    });
  }, []);

  if (error) {
    return (
      <main className="shell">
        <section className="empty-state">
          <h1>Daily AI Insight Engine</h1>
          <p>{error}</p>
          <code>daily-ai-insight run --mock-llm</code>
        </section>
      </main>
    );
  }

  if (!data) {
    return (
      <main className="shell">
        <section className="empty-state">
          <h1>Daily AI Insight Engine</h1>
          <p>Loading dashboard data...</p>
        </section>
      </main>
    );
  }

  const visualization = data.visualization_data;

  return (
    <main className="shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">Daily AI Insight Engine</p>
          <h1>AI Intelligence Dashboard</h1>
        </div>
        <div className="header-meta">
          <span>{data.report.timezone}</span>
          <span>{data.report.window_days} days</span>
          <span>{new Date(data.generated_at).toLocaleString()}</span>
        </div>
      </header>

      <section className="metric-row">
        <div className="metric">
          <Database size={18} />
          <span>Structured News</span>
          <strong>{data.structured_news.length}</strong>
        </div>
        <div className="metric">
          <Activity size={18} />
          <span>Events</span>
          <strong>{data.events.length}</strong>
        </div>
        <div className="metric">
          <FileText size={18} />
          <span>Top Ranked</span>
          <strong>{data.ranked_events.slice(0, 5).length}</strong>
        </div>
      </section>

      <div className="dashboard-grid">
        <DonutChart data={visualization.source_type_distribution} label="Source Types" />
        <DonutChart data={visualization.event_type_distribution} label="Event Types" />
        <BarChart data={visualization.top_event_scores.map((event) => ({
          name: `#${event.rank}`,
          count: Math.round(event.score * 10),
        }))} label="Top Event Scores x10" />
        <MatrixChart data={visualization.risk_opportunity_matrix} />
      </div>

      <TopEvents rankedEvents={data.ranked_events} events={data.events} />
      <SourcePanel sources={data.source_profiles} />
      <QualityPanel quality={data.quality_check} />
    </main>
  );
}

