import { useEffect, useState } from "react";
import { Activity, Database, FileText, Link2 } from "lucide-react";
import { loadDashboardData } from "./api";
import { BarChart } from "./charts/BarChart";
import { DonutChart } from "./charts/DonutChart";
import { MatrixChart } from "./charts/MatrixChart";
import { AnalysisView } from "./components/AnalysisView";
import { EventsExplorer } from "./components/EventsExplorer";
import { NavBar, type ViewKey } from "./components/NavBar";
import { QualityPanel } from "./components/QualityPanel";
import { SourcePanel } from "./components/SourcePanel";
import { TopEvents } from "./components/TopEvents";
import type { DashboardData } from "./types";
import { buildDashboardSummary } from "./utils";

export function App() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeView, setActiveView] = useState<ViewKey>("overview");

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
  const summary = buildDashboardSummary(data);
  const linkedNewsCount = data.structured_news.filter((item) => item.url).length;
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

      <NavBar active={activeView} onChange={setActiveView} />

      {activeView === "overview" ? (
        <>
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
              <span>Top Score</span>
              <strong>{summary.topScore}</strong>
            </div>
            <div className="metric">
              <Link2 size={18} />
              <span>Source Links</span>
              <strong>{linkedNewsCount}</strong>
            </div>
          </section>

          <section className="insight-strip">
            <article>
              <span>Evidence Coverage</span>
              <strong>{linkedNewsCount}/{data.structured_news.length}</strong>
            </article>
            <article>
              <span>Observed Sources</span>
              <strong>{summary.sourceCount}</strong>
            </article>
            <article>
              <span>High Confidence Events</span>
              <strong>{summary.highConfidence}</strong>
            </article>
          </section>

          <div className="dashboard-grid">
            <DonutChart
              data={visualization.source_type_distribution}
              label="Source Types"
            />
            <DonutChart
              data={visualization.event_type_distribution}
              label="Event Types"
            />
          </div>

          <MatrixChart data={visualization.risk_opportunity_matrix} />

          <TopEvents
            rankedEvents={data.ranked_events}
            events={data.events}
            news={data.structured_news}
          />
        </>
      ) : null}

      {activeView === "events" ? (
        <EventsExplorer
          events={data.events}
          rankedEvents={data.ranked_events}
          news={data.structured_news}
        />
      ) : null}

      {activeView === "analysis" ? <AnalysisView markdown={data.report.markdown} /> : null}

      {activeView === "sources" ? (
        <>
          <div className="dashboard-grid">
            <DonutChart
              data={visualization.source_type_distribution}
              label="Accepted Source Types"
              description="Distribution after cleaning and structured extraction."
            />
            <BarChart
              data={visualization.industry_area_distribution}
              label="Industry Areas"
              description="Topic coverage across structured items."
            />
          </div>
          <SourcePanel sources={data.source_profiles} />
        </>
      ) : null}

      {activeView === "quality" ? <QualityPanel quality={data.quality_check} /> : null}
    </main>
  );
}
