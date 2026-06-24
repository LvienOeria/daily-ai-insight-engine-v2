from __future__ import annotations

import json

from .llm import DeepSeekClient
from .models import EventItem, RankedEvent, SourceProfile, StructuredNewsItem, VisualizationData
from .skill_loader import load_prompt


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
        system=load_prompt("daily-report-generation"),
        user=json.dumps(payload, ensure_ascii=False),
    )


def _mock_report(
    *,
    structured: list[StructuredNewsItem],
    events: list[EventItem],
    ranked_events: list[RankedEvent],
    source_profiles: list[SourceProfile],
    visualization_data: VisualizationData,
) -> str:
    from collections import Counter

    top5 = ranked_events[:5]
    event_by_id = {e.event_id: e for e in events}
    news_by_id = {n.news_id: n for n in structured}

    source_names = sorted({n.source for n in structured})
    type_counter = Counter(n.event_type for n in structured)
    area_counter = Counter(n.industry_area for n in structured)
    lang_counter = Counter(n.language for n in structured)
    tech_counter: Counter[str] = Counter()
    for n in structured:
        tech_counter.update(n.technologies)
    entity_counter: Counter[str] = Counter()
    for n in structured:
        entity_counter.update(n.entities)
    sentiment_counter = Counter(n.sentiment for n in structured)

    # --- 今日概览 ---
    type_summary = "、".join(f"{_etype_label(k)}{v}条" for k, v in type_counter.most_common(4))
    area_summary = "、".join(f"{_earea_label(k)}{v}条" for k, v in area_counter.most_common(4))
    top_entities = [e for e, _ in entity_counter.most_common(6)] if entity_counter else []
    top_techs = [t for t, _ in tech_counter.most_common(5)] if tech_counter else []

    overview = [
        f"本报告覆盖 **{len(structured)}** 条结构化 AI 新闻、**{len(events)}** 个聚类事件。",
        f"数据来自 {len(source_names)} 个来源（{_join_names(source_names[:5])}），"
        f"语言分布为 {_fmt_counter(lang_counter)}。",
    ]
    if top_entities:
        overview.append(
            f"高频实体包括 {_join_names(top_entities)}，集中体现了当前 AI 领域的核心参与者格局。"
        )
    if type_summary:
        overview.append(f"事件类型分布：{type_summary}。")
    if area_summary:
        overview.append(f"涉及行业领域：{area_summary}。")
    if top_techs:
        overview.append(f"主要技术方向：{_join_names(top_techs)}。")

    # --- Top 5 table ---
    top_rows: list[str] = [
        "| 排名 | 事件 | 类型 | 领域 | 评分 | 置信度 |",
        "|:---:|:---|:---|:---|:---:|:---:|",
    ]
    for r in top5:
        ev = event_by_id.get(r.event_id)
        etype = _etype_label(ev.event_type) if ev else "-"
        earea = _earea_label(ev.industry_area) if ev else "-"
        top_rows.append(
            f"| {r.rank} | {r.event_name[:80]} | {etype} | {earea} "
            f"| {r.final_importance_score} | {r.confidence} |"
        )

    # --- 深度总结 (per Top event) ---
    deep: list[str] = []
    for r in top5:
        ev = event_by_id.get(r.event_id)
        if ev is None:
            continue
        related_news = [news_by_id[nid] for nid in ev.related_news_ids if nid in news_by_id]
        src_list = sorted({n.source for n in related_news})

        deep.append(f"### {r.rank}. {ev.event_name}")
        deep.append("")
        deep.append(f"**来源**: {_join_names(src_list) if src_list else '未知'}  "
                     f"| **类型**: {_etype_label(ev.event_type)}  "
                     f"| **领域**: {_earea_label(ev.industry_area)}  "
                     f"| **评分**: {r.final_importance_score}")
        deep.append("")

        # Core topic as summary paragraph
        if ev.core_topic:
            deep.append(f"> {ev.core_topic}")
            deep.append("")

        # Key facts with evidence-indicator
        if ev.key_facts:
            deep.append("**关键事实**:")
            for f in ev.key_facts[:4]:
                deep.append(f"- {f}")
            deep.append("")

        # Why it matters
        if ev.why_it_matters:
            deep.append(f"**为什么重要**: {ev.why_it_matters}")
            deep.append("")

        # Entities & technologies
        if ev.main_entities:
            deep.append(f"**涉及主体**: {_join_names(ev.main_entities[:6])}")
        if ev.technologies:
            deep.append(f"**技术方向**: {_join_names(ev.technologies[:6])}")
        deep.append("")

        # Impact/risk/opportunity
        extras: list[str] = []
        if ev.impact_scope:
            extras.append(f"影响范围: {_join_names(ev.impact_scope)}")
        if ev.risk_tags and ev.risk_tags != ["none"]:
            extras.append(f"风险标签: {_join_names(ev.risk_tags)}")
        if ev.opportunity_tags and ev.opportunity_tags != ["none"]:
            extras.append(f"机会标签: {_join_names(ev.opportunity_tags)}")
        if extras:
            deep.append("  ".join(f"`{x}`" for x in extras))
            deep.append("")

        # Score breakdown table
        b = r.score_breakdown
        deep.append(
            f"| 影响范围 | 来源权威 | 新颖性 | 多源 | 技术影响 | 商业影响 | 风险 | 机会 | 时效 |\n"
            f"|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|\n"
            f"| {b.impact_scope} | {b.source_authority} | {b.novelty} | {b.multi_source_support} "
            f"| {b.technical_impact} | {b.business_impact} | {b.risk_level} | {b.opportunity_level} | {b.recency} |"
        )
        deep.append("")

    # --- 趋势判断 ---
    trends: list[str] = []
    # Tech trends
    tech_items = [
        n for n in structured
        if n.technologies and n.technologies != ["none"]
    ]
    if tech_items:
        trends.append("**技术趋势**:")
        for tech, cnt in tech_counter.most_common(4):
            example = next((n for n in tech_items if tech in n.technologies), None)
            snippet = _trim_title(example.title) if example else ""
            trends.append(f"- **{tech}**（{cnt} 条）: {snippet}")
        trends.append("")

    # Industry trends
    area_items_by_area: dict[str, list[StructuredNewsItem]] = {}
    for n in structured:
        area_items_by_area.setdefault(n.industry_area, []).append(n)
    if len(area_items_by_area) >= 2:
        trends.append("**行业趋势**:")
        for area, cnt in area_counter.most_common(4):
            trends.append(f"- **{_earea_label(area)}**（{cnt} 条）占据主要份额，"
                          f"反映出该方向在当前时间窗口内的活跃度较高。")
        trends.append("")

    # Source diversity note
    if len(source_names) <= 2:
        trends.append(
            "**数据覆盖提示**: 当前数据来源较为集中（主要为 arXiv），"
            "趋势判断的普适性受限。建议在后续报告中增加产业媒体和官方来源的覆盖。"
        )
        trends.append("")

    # --- 风险与机会 ---
    risk_opp: list[str] = []
    # Collect all risk/opp from all events
    all_risks: dict[str, list[str]] = {}
    all_opps: dict[str, list[str]] = {}
    for ev in events:
        for tag in ev.risk_tags:
            if tag != "none":
                all_risks.setdefault(tag, []).append(ev.event_name)
        for tag in ev.opportunity_tags:
            if tag != "none":
                all_opps.setdefault(tag, []).append(ev.event_name)

    if all_risks:
        risk_opp.append("### 风险信号")
        risk_opp.append("")
        risk_opp.append("| 风险类型 | 涉及事件数 | 代表事件 |")
        risk_opp.append("|:---|:---:|:---|")
        for tag, ev_names in sorted(all_risks.items(), key=lambda x: -len(x[1])):
            risk_opp.append(f"| {_risk_label(tag)} | {len(ev_names)} | {ev_names[0][:60]} |")
        risk_opp.append("")

    if all_opps:
        risk_opp.append("### 机会信号")
        risk_opp.append("")
        risk_opp.append("| 机会类型 | 涉及事件数 | 代表事件 |")
        risk_opp.append("|:---|:---:|:---|")
        for tag, ev_names in sorted(all_opps.items(), key=lambda x: -len(x[1])):
            risk_opp.append(f"| {_opp_label(tag)} | {len(ev_names)} | {ev_names[0][:60]} |")
        risk_opp.append("")

    if not all_risks and not all_opps:
        risk_opp.append("当前数据窗口中未检测到明确的风险或机会标签。")

    # --- 可视化说明 ---
    vis_lines = [
        f"- 来源类型分布: {len(visualization_data.source_type_distribution)} 类",
        f"- 事件类型分布: {len(visualization_data.event_type_distribution)} 类",
        f"- 行业领域分布: {len(visualization_data.industry_area_distribution)} 个领域",
        f"- Top 事件评分对比: {len(visualization_data.top_event_scores)} 个事件",
        f"- 风险-机会矩阵: {len(visualization_data.risk_opportunity_matrix)} 个数据点",
    ]

    # --- 数据与方法 ---
    core_sources = [p for p in source_profiles if p.recommended_tier == "core"]
    aux_sources = [p for p in source_profiles if p.recommended_tier == "auxiliary"]
    method_lines = [
        f"- 评估数据源 {len(source_profiles)} 个（core {len(core_sources)}、auxiliary {len(aux_sources)}）",
        "- 流水线: raw → cleaned → structured → clustered → scored → report → quality check",
        "- 评分维度: 影响范围、来源权威、新颖性、多源支持、技术影响、商业影响、风险、机会、时效性",
        f"- 语言: {_fmt_counter(lang_counter)}",
        "- 局限: 本报告为 mock 模式生成，使用规则引擎而非 LLM；结论仅反映当前数据窗口内的结构化信息。",
    ]

    # --- Assemble ---
    return (
        "# Daily AI Insight Report\n\n"
        "## 今日概览\n\n"
        + "\n\n".join(overview) + "\n\n"
        "## 今日 AI 领域 Top 3-5 热点事件\n\n"
        + "\n".join(top_rows) + "\n\n"
        "## 重要事件深度总结\n\n"
        + "\n".join(deep) + "\n"
        "## 趋势判断\n\n"
        + "\n".join(trends) + "\n"
        "## 风险与机会提示\n\n"
        + "\n".join(risk_opp) + "\n"
        "## 可视化说明\n\n"
        + "\n".join(vis_lines) + "\n\n"
        "## 数据与方法说明\n\n"
        + "\n".join(method_lines) + "\n"
    )


# ---- label helpers ----

def _etype_label(v: str) -> str:
    _map: dict[str, str] = {
        "product_release": "产品发布",
        "model_release": "模型发布",
        "funding": "融资",
        "acquisition": "收购",
        "partnership": "合作",
        "regulation": "监管政策",
        "research": "学术研究",
        "open_source": "开源",
        "infrastructure": "基础设施",
        "security_risk": "安全风险",
        "business_update": "业务更新",
        "market_commentary": "市场评论",
        "other": "其他",
    }
    return _map.get(v, v)


def _earea_label(v: str) -> str:
    _map: dict[str, str] = {
        "foundation_model": "基础模型",
        "ai_agent": "AI Agent",
        "multimodal_ai": "多模态AI",
        "ai_infrastructure": "AI基础设施",
        "chip_compute": "芯片算力",
        "enterprise_ai": "企业AI",
        "consumer_ai": "消费AI",
        "developer_tools": "开发者工具",
        "ai_safety": "AI安全",
        "policy_regulation": "政策监管",
        "research": "研究",
        "capital_market": "资本市场",
        "other": "其他",
    }
    return _map.get(v, v)


def _risk_label(v: str) -> str:
    _map: dict[str, str] = {
        "privacy": "隐私",
        "copyright": "版权",
        "security": "安全",
        "compliance": "合规",
        "misinformation": "虚假信息",
        "job_displacement": "就业冲击",
        "market_bubble": "市场泡沫",
        "dependency_risk": "依赖风险",
        "model_safety": "模型安全",
    }
    return _map.get(v, v)


def _opp_label(v: str) -> str:
    _map: dict[str, str] = {
        "productivity": "生产力提升",
        "enterprise_adoption": "企业采纳",
        "developer_ecosystem": "开发生态",
        "cost_reduction": "成本降低",
        "new_market": "新市场",
        "open_source_growth": "开源增长",
        "ai_native_product": "AI原生应用",
        "infrastructure_growth": "基础设施增长",
        "research_breakthrough": "研究突破",
    }
    return _map.get(v, v)


def _join_names(names: list[str]) -> str:
    return "、".join(str(n) for n in names)


def _fmt_counter(c: Counter) -> str:
    return "、".join(f"{k} {v}条" for k, v in c.most_common())


def _trim_title(title: str, max_len: int = 80) -> str:
    return title if len(title) <= max_len else title[:max_len - 1] + "…"

