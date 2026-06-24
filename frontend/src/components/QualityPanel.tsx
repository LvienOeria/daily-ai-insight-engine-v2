import { AlertTriangle, CheckCircle2 } from "lucide-react";
import type { QualityCheck } from "../types";

interface QualityPanelProps {
  quality: QualityCheck;
}

export function QualityPanel({ quality }: QualityPanelProps) {
  const failures = Object.entries(quality.requirement_check).filter(([, passed]) => !passed);
  const issues = [
    ...quality.missing_items,
    ...quality.weak_points,
    ...quality.unsupported_claims,
    ...quality.data_quality_issues,
    ...quality.visualization_issues,
  ];

  return (
    <section className="section quality-section">
      <div className="quality-state">
        {quality.passed ? <CheckCircle2 size={22} /> : <AlertTriangle size={22} />}
        <div>
          <h2>质量检查</h2>
          <p>{quality.passed ? "通过" : "待审查"}</p>
        </div>
      </div>
      <div className="quality-grid">
        <div>
          <h3>未通过项</h3>
          {failures.length === 0 ? (
            <p className="muted">无</p>
          ) : (
            <ul>
              {failures.map(([name]) => (
                <li key={name}>{name}</li>
              ))}
            </ul>
          )}
        </div>
        <div>
          <h3>问题</h3>
          {issues.length === 0 ? (
            <p className="muted">无</p>
          ) : (
            <ul>
              {issues.slice(0, 8).map((issue) => (
                <li key={issue}>{issue}</li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </section>
  );
}

