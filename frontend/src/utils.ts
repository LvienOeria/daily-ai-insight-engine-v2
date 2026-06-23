import type { DashboardData, EventItem, RankedEvent, StructuredNewsItem } from "./types";

export function getNewsById(items: StructuredNewsItem[]) {
  return new Map(items.map((item) => [item.news_id, item]));
}

export function getRankedByEventId(items: RankedEvent[]) {
  return new Map(items.map((item) => [item.event_id, item]));
}

export function getEventSources(event: EventItem, newsById: Map<string, StructuredNewsItem>) {
  return event.related_news_ids
    .map((newsId) => newsById.get(newsId))
    .filter((item): item is StructuredNewsItem => Boolean(item));
}

export interface ReportSection {
  title: string;
  body: string;
}

export function parseReportSections(markdown: string): ReportSection[] {
  const lines = markdown.split(/\r?\n/);
  const sections: ReportSection[] = [];
  let current: ReportSection | null = null;

  for (const line of lines) {
    const match = line.match(/^##\s+(.*)$/);
    if (match) {
      if (current) {
        current.body = current.body.trim();
        sections.push(current);
      }
      current = { title: match[1].replace(/^\d+\.\s*/, ""), body: "" };
      continue;
    }
    if (current) {
      current.body += `${line}\n`;
    }
  }
  if (current) {
    current.body = current.body.trim();
    sections.push(current);
  }
  return sections;
}

export function findReportSection(markdown: string, keyword: string): ReportSection | undefined {
  return parseReportSections(markdown).find((section) => section.title.includes(keyword));
}

export function buildDashboardSummary(data: DashboardData) {
  const topScore = data.ranked_events[0]?.final_importance_score ?? 0;
  const sourceCount = data.source_profiles.filter((source) => source.observed_item_count > 0).length;
  const highConfidence = data.events.filter((event) => event.confidence === "high").length;
  return { topScore, sourceCount, highConfidence };
}

