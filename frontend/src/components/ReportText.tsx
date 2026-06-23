import type { ReactNode } from "react";

interface ReportTextProps {
  markdown: string;
}

/** Lightweight Markdown → React renderer for the daily report. */
export function ReportText({ markdown }: ReportTextProps) {
  const lines = markdown.split(/\r?\n/);
  const nodes: ReactNode[] = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    // Skip horizontal rules.
    if (line.trim() === "---") {
      i++;
      continue;
    }

    // Code block (fenced).
    if (line.trim().startsWith("```")) {
      const codeLines: string[] = [];
      i++;
      while (i < lines.length && !lines[i].trim().startsWith("```")) {
        codeLines.push(lines[i]);
        i++;
      }
      i++; // skip closing ```
      nodes.push(
        <pre key={`code-${nodes.length}`} className="report-code">
          <code>{codeLines.join("\n")}</code>
        </pre>
      );
      continue;
    }

    // Table detection: at least 2 pipes on a line and followed by a separator line.
    if (
      line.includes("|") &&
      i + 2 < lines.length &&
      /^\s*\|?\s*:?---+:?\s*\|/.test(lines[i + 1] ?? "")
    ) {
      const headerLine = line;
      const sepLine = lines[i + 1] as string;
      const bodyLines: string[] = [];
      i += 2;
      while (i < lines.length && lines[i].includes("|")) {
        bodyLines.push(lines[i]);
        i++;
      }

      const headerCols = splitTableRow(headerLine);
      const align = splitTableRow(sepLine).map((col) => {
        if (col.startsWith(":") && col.endsWith(":")) return "center" as const;
        if (col.endsWith(":")) return "right" as const;
        return "left" as const;
      });

      nodes.push(
        <div key={`table-${nodes.length}`} className="table-wrap">
          <table>
            <thead>
              <tr>
                {headerCols.map((col, ci) => (
                  <th key={ci} style={{ textAlign: align[ci] ?? "left" }}>
                    <InlineFormat text={col} />
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {bodyLines.map((row, ri) => {
                const cols = splitTableRow(row);
                return (
                  <tr key={ri}>
                    {cols.map((col, ci) => (
                      <td key={ci} style={{ textAlign: align[ci] ?? "left" }}>
                        <InlineFormat text={col} />
                      </td>
                    ))}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      );
      continue;
    }

    // Headings.
    if (line.startsWith("# ")) {
      nodes.push(<h2 key={nodes.length}>{line.replace(/^#\s+/, "")}</h2>);
      i++;
      continue;
    }
    if (line.startsWith("## ")) {
      nodes.push(<h3 key={nodes.length}>{line.replace(/^##\s+/, "")}</h3>);
      i++;
      continue;
    }
    if (line.startsWith("### ")) {
      nodes.push(<h4 key={nodes.length}>{line.replace(/^###\s+/, "")}</h4>);
      i++;
      continue;
    }

    // Bullet list items.
    if (/^\s*[-*]\s/.test(line)) {
      const group: string[] = [];
      while (i < lines.length && /^\s*[-*]\s/.test(lines[i])) {
        group.push(lines[i].replace(/^\s*[-*]\s+/, ""));
        i++;
      }
      nodes.push(
        <ul key={nodes.length}>
          {group.map((item, gi) => (
            <li key={gi}>
              <InlineFormat text={item} />
            </li>
          ))}
        </ul>
      );
      continue;
    }

    // Numbered list items.
    if (/^\s*\d+\.\s/.test(line)) {
      const group: string[] = [];
      while (i < lines.length && /^\s*\d+\.\s/.test(lines[i])) {
        group.push(lines[i].replace(/^\s*\d+\.\s+/, ""));
        i++;
      }
      nodes.push(
        <ol key={nodes.length}>
          {group.map((item, gi) => (
            <li key={gi}>
              <InlineFormat text={item} />
            </li>
          ))}
        </ol>
      );
      continue;
    }

    // Blockquote.
    if (line.startsWith("> ")) {
      const group: string[] = [];
      while (i < lines.length && lines[i].startsWith("> ")) {
        group.push(lines[i].replace(/^>\s?/, ""));
        i++;
      }
      nodes.push(
        <blockquote key={nodes.length}>
          {group.map((item, gi) => (
            <p key={gi}>
              <InlineFormat text={item} />
            </p>
          ))}
        </blockquote>
      );
      continue;
    }

    // Empty line → spacer.
    if (line.trim() === "") {
      nodes.push(<div key={nodes.length} className="report-space" />);
      i++;
      continue;
    }

    // Regular paragraph.
    nodes.push(
      <p key={nodes.length}>
        <InlineFormat text={line} />
      </p>
    );
    i++;
  }

  return <div className="report-text">{nodes}</div>;
}

/** Split a markdown table row on `|`, trimming each cell. */
function splitTableRow(row: string): string[] {
  const cells = row.split("|").map((c) => c.trim());
  // Drop leading empty cell (before first |) and trailing empty cell (after last |)
  if (cells.length > 1 && cells[0] === "") cells.shift();
  if (cells.length > 1 && cells[cells.length - 1] === "") cells.pop();
  return cells;
}

/** Render bold, italic, and inline code within a text string. */
function InlineFormat({ text }: { text: string }) {
  // Order: code first (to avoid matching ` inside bold), then bold, then italic.
  const parts = splitByPattern(text, /(`[^`]+`)/g);
  return (
    <>
      {parts.map((part, i) => {
        if (part.startsWith("`") && part.endsWith("`")) {
          return <code key={i}>{part.slice(1, -1)}</code>;
        }
        // Bold + italic (***)
        const boldItalicParts = splitByPattern(part, /(\*\*\*[^*]+\*\*\*)/g);
        return boldItalicParts.map((bi, j) => {
          if (bi.startsWith("***") && bi.endsWith("***")) {
            return (
              <strong key={`${i}-${j}`}>
                <em>{bi.slice(3, -3)}</em>
              </strong>
            );
          }
          // Bold (**)
          const boldParts = splitByPattern(bi, /(\*\*[^*]+\*\*)/g);
          return boldParts.map((bp, k) => {
            if (bp.startsWith("**") && bp.endsWith("**")) {
              return <strong key={`${i}-${j}-${k}`}>{bp.slice(2, -2)}</strong>;
            }
            // Italic (*)
            const italicParts = splitByPattern(bp, /(\*[^*]+\*)/g);
            return italicParts.map((ip, l) => {
              if (ip.startsWith("*") && ip.endsWith("*") && ip.length > 2) {
                return <em key={`${i}-${j}-${k}-${l}`}>{ip.slice(1, -1)}</em>;
              }
              return <span key={`${i}-${j}-${k}-${l}`}>{ip}</span>;
            });
          }).flat();
        }).flat();
      })}
    </>
  );
}

function splitByPattern(text: string, pattern: RegExp): string[] {
  const result: string[] = [];
  let last = 0;
  let match: RegExpExecArray | null;
  const regex = new RegExp(pattern.source, pattern.flags);
  while ((match = regex.exec(text)) !== null) {
    if (match.index > last) {
      result.push(text.slice(last, match.index));
    }
    result.push(match[0]);
    last = match.index + match[0].length;
  }
  if (last < text.length) {
    result.push(text.slice(last));
  }
  return result;
}
