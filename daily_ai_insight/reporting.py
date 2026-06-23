from __future__ import annotations

import json

from .llm import DeepSeekClient
from .models import EventItem, RankedEvent, SourceProfile, StructuredNewsItem, VisualizationData


def generate_report(
    *,
    structured: list[StructuredNewsItem],
    events: list[EventItem],
    ranked_events: list[RankedEvent],
    source_profiles: list[SourceProfile],
    visualization_data: VisualizationData,
    llm: DeepSeekClient | None,
    mock_llm: bool = False,
) -> str:
    if mock_llm or llm is None:
        return _mock_report(
            structured=structured,
            events=events,
            ranked_events=ranked_events,
            source_profiles=source_profiles,
            visualization_data=visualization_data,
        )

    payload = {
        "structured_news": [item.model_dump(mode="json") for item in structured],
        "events": [event.model_dump(mode="json") for event in events],
        "ranked_events": [event.model_dump(mode="json") for event in ranked_events],
        "source_profiles": [profile.model_dump(mode="json") for profile in source_profiles],
        "visualization_data": visualization_data.model_dump(mode="json"),
    }
    return llm.complete_text(
        system=_REPORT_SYSTEM,
        user=json.dumps(payload, ensure_ascii=False),
    )


_REPORT_SYSTEM = """
You are the daily-report-generation module for the Daily AI Insight Engine.
Write a professional Chinese report in Markdown.

Required sections:
1. 今日概览
2. 今日 AI 领域 Top 3-5 热点事件
3. 重要事件深度总结
4. 趋势判断
5. 风险与机会提示
6. 可视化说明
7. 数据与方法说明

Rules:
- Use only provided structured news, events, ranking, source profiles, and visualization data.
- Every Top event must cite event_id or related news_id/source evidence.
- Do not invent facts, dates, URLs, companies, policy details, or funding amounts.
- Trend judgments must be supported by structured fields, key facts, or multiple events.
- Mention uncertainty when evidence is weak or source coverage is limited.
"""


def _mock_report(
    *,
    structured: list[StructuredNewsItem],
    events: list[EventItem],
    ranked_events: list[RankedEvent],
    source_profiles: list[SourceProfile],
    visualization_data: VisualizationData,
) -> str:
    top = ranked_events[:5]
    lines = [
        "# Daily AI Insight Report",
        "",
        "## 今日概览",
        "",
        f"本次报告基于 {len(structured)} 条结构化 AI 信息、{len(events)} 个聚类事件生成。"
        "以下结论仅来自已清洗和结构化的数据。",
        "",
        "## 今日 AI 领域 Top 3-5 热点事件",
        "",
    ]
    event_by_id = {event.event_id: event for event in events}
    for ranked in top:
        event = event_by_id.get(ranked.event_id)
        related = ", ".join(event.related_news_ids if event else [])
        lines.extend(
            [
                f"### {ranked.rank}. {ranked.event_name}",
                "",
                f"- 事件 ID：`{ranked.event_id}`",
                f"- 相关新闻 ID：`{related}`",
                f"- 重要性评分：{ranked.final_importance_score}",
                f"- 为什么重要：{ranked.ranking_reason}",
                f"- 证据：{'; '.join(ranked.supporting_evidence) or '无'}",
                "",
            ]
        )

    lines.extend(
        [
            "## 重要事件深度总结",
            "",
            "当前为 mock/report fallback 输出。正式运行应使用 DeepSeek 根据结构化事件生成更完整分析。"
            "本节不引入结构化数据之外的新事实。",
            "",
            "## 趋势判断",
            "",
            f"- 事件类型分布：{visualization_data.event_type_distribution}",
            f"- 行业领域分布：{visualization_data.industry_area_distribution}",
            "",
            "## 风险与机会提示",
            "",
            f"- 风险/机会矩阵来自 {len(visualization_data.risk_opportunity_matrix)} 个事件。",
            "",
            "## 可视化说明",
            "",
            "前端通过 React + D3 读取 `frontend/public/data/latest.json` 渲染图表。",
            "",
            "## 数据与方法说明",
            "",
            f"- 数据源评估记录数：{len(source_profiles)}",
            "- 流程：raw -> cleaned -> structured -> clustered -> scored -> report -> quality check。",
            "- 限制：mock 输出只用于开发验证，正式报告需使用 DeepSeek LLM 生成并质检。",
        ]
    )
    return "\n".join(lines) + "\n"

