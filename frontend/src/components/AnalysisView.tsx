import { findReportSection } from "../utils";
import { ReportText } from "./ReportText";

interface AnalysisViewProps {
  markdown: string;
}

const requiredSections = [
  { key: "今日概览", label: "概览" },
  { key: "今日 AI 领域 Top", label: "热点事件" },
  { key: "重要事件深度总结", label: "深度分析" },
  { key: "趋势判断", label: "趋势判断" },
  { key: "风险与机会提示", label: "风险与机会" },
  { key: "可视化说明", label: "可视化说明" },
  { key: "数据与方法说明", label: "数据与方法" },
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
