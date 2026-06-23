export type Confidence = "low" | "medium" | "high";

export interface DistributionDatum {
  name: string;
  count: number;
}

export interface TopEventScore {
  event_id: string;
  event_name: string;
  rank: number;
  score: number;
  confidence: Confidence;
}

export interface RiskOpportunityDatum {
  event_id: string;
  event_name: string;
  risk_level: number;
  opportunity_level: number;
  confidence: Confidence;
}

export interface VisualizationData {
  generated_at: string;
  source_type_distribution: DistributionDatum[];
  event_type_distribution: DistributionDatum[];
  industry_area_distribution: DistributionDatum[];
  technology_distribution: DistributionDatum[];
  top_event_scores: TopEventScore[];
  risk_opportunity_matrix: RiskOpportunityDatum[];
}

export interface SourceProfile {
  source_name: string;
  source_type: string;
  access_method: string;
  language: string;
  observed_item_count: number;
  fetch_status: string;
  recommended_tier: string;
  reason: string;
}

export interface EventItem {
  event_id: string;
  event_name: string;
  related_news_ids: string[];
  main_entities: string[];
  core_topic: string;
  event_type: string;
  industry_area: string;
  technologies: string[];
  key_facts: string[];
  evidence: string[];
  why_it_matters: string;
  impact_scope: string[];
  risk_tags: string[];
  opportunity_tags: string[];
  confidence: Confidence;
}

export interface StructuredNewsItem {
  news_id: string;
  title: string;
  source: string;
  source_type: string;
  published_at: string;
  language: string;
  url: string | null;
  entities: string[];
  technologies: string[];
  event_type: string;
  industry_area: string;
  key_facts: string[];
  summary: string;
  sentiment: string;
  impact_scope: string[];
  risk_tags: string[];
  opportunity_tags: string[];
  importance_score: number;
  confidence: Confidence;
  evidence: string[];
}

export interface RankedEvent {
  event_id: string;
  event_name: string;
  final_importance_score: number;
  rank: number;
  ranking_reason: string;
  supporting_evidence: string[];
  confidence: Confidence;
}

export interface QualityCheck {
  passed: boolean;
  requirement_check: Record<string, boolean>;
  missing_items: string[];
  weak_points: string[];
  unsupported_claims: string[];
  suspected_hallucinations: string[];
  data_quality_issues: string[];
  visualization_issues: string[];
  recommended_fixes: string[];
}

export interface DashboardData {
  generated_at: string;
  report: {
    timezone: string;
    window_days: number;
    markdown: string;
  };
  source_profiles: SourceProfile[];
  structured_news: StructuredNewsItem[];
  events: EventItem[];
  ranked_events: RankedEvent[];
  visualization_data: VisualizationData;
  quality_check: QualityCheck;
}
