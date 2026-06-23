import { findReportSection } from "../utils";
import { ReportText } from "./ReportText";

interface AnalysisViewProps {
  markdown: string;
}

const requiredSections = [
  { key: "今日概览", label: "Overview" },
  { key: "今日 AI 领域 Top", label: "Top Events" },
  { key: "重要事件深度总结", label: "Deep Dives" },
  { key: "趋势判断", label: "Trend Judgments" },
  { key: "风险与机会提示", label: "Risks / Opportunities" },
  { key: "可视化说明", label: "Visualization Notes" },
  { key: "数据与方法说明", label: "Data & Method" },
];

export function AnalysisView({ markdown }: AnalysisViewProps) {
  return (
    <section className="analysis-grid">
      {requiredSections.map((section) => {
        const content = findReportSection(markdown, section.key);
        return (
          <article className="section analysis-card" key={section.key}>
            <div className="section-heading">
              <h2>{section.label}</h2>
              <span>{section.key}</span>
            </div>
            {content ? (
              <ReportText markdown={content.body} />
            ) : (
              <p className="muted">Report section not found.</p>
            )}
          </article>
        );
      })}
    </section>
  );
}
