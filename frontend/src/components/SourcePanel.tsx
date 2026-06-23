import type { SourceProfile } from "../types";

interface SourcePanelProps {
  sources: SourceProfile[];
}

export function SourcePanel({ sources }: SourcePanelProps) {
  return (
    <section className="section">
      <div className="section-heading">
        <h2>Sources</h2>
        <span>{sources.length} evaluated</span>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Source</th>
              <th>Type</th>
              <th>Access</th>
              <th>Observed</th>
              <th>Tier</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {sources.map((source) => (
              <tr key={source.source_name}>
                <td>{source.source_name}</td>
                <td>{source.source_type}</td>
                <td>{source.access_method}</td>
                <td>{source.observed_item_count}</td>
                <td>{source.recommended_tier}</td>
                <td>{source.fetch_status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

