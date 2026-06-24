---
name: daily-report-generation
description: "Use when: generating the final Chinese Daily AI Insight report from structured news, clustered events, ranked events, evidence, trends, risks, opportunities, and visualization data."
---

# Daily Report Generation Skill

## Purpose

Generate a readable Chinese AI daily insight report from structured and verified data.

The report must be evidence-based, not a free-form essay.

## When To Use

Use after:

- Raw news has been cleaned
- News items have been structured
- Events have been clustered
- Important events have been ranked
- Visualization statistics are available or planned

## Inputs

Use these inputs when available:

- Cleaned news dataset
- Structured news dataset
- Clustered event dataset
- Ranked event dataset
- Data source notes
- Schema notes
- Visualization data
- Known limitations

## Required Report Structure

Generate the report in Chinese with the following sections:

1. 今日概览
   - Summarize the overall state of today's AI information flow.
   - Keep it concise and evidence-based.

2. 今日 AI 领域 Top 3-5 热点事件
   For each event, include:
   - 事件名称
   - 事件摘要
   - 涉及主体
   - 相关新闻 ID 或来源
   - 为什么重要
   - 可能影响
   - 证据

3. 重要事件深度总结
   - Select 1-2 key events.
   - Explain background, short-term impact, and longer-term implications.
   - Do not introduce facts outside the dataset.

4. 趋势判断
   Cover relevant directions:
   - 技术趋势
   - 应用趋势
   - 政策/监管趋势
   - 资本/商业趋势

   Each trend must be supported by structured fields, key facts, or multiple events.

5. 风险与机会提示
   - Use risk_tags and opportunity_tags.
   - Link each risk or opportunity to evidence.
   - Avoid unsupported investment advice.

6. 可视化说明
   - Explain what each chart shows.
   - Chart conclusions must match structured data.

7. 数据与方法说明
   - Briefly explain data sources, schema, AI usage, and limitations.

## Writing Rules

- Write in clear professional Chinese.
- Use analytical language, not marketing language.
- Avoid vague claims such as "AI is developing rapidly" unless supported by specific evidence.
- Do not overstate a single news item as a broad trend.
- Do not invent external context.
- Mention uncertainty when evidence is limited.
- Prefer concrete event-based analysis over generic commentary.

## Evidence Rules

Every major claim should be traceable to at least one of:

- related_news_ids
- source names
- key_facts
- event evidence
- structured tags
- visualization statistics

Top events must include related news IDs or source references.

Trend judgments should be supported by:

- multiple related events, or
- one highly authoritative source with explicit evidence

## Output Quality Criteria

The report should answer:

- What happened today?
- Which events matter most?
- Why do they matter?
- What trends can be reasonably inferred?
- What risks and opportunities are visible?
- What data and method support these conclusions?

## Common Failure Modes To Avoid

- Listing news without analysis
- Writing only summaries
- Making broad claims without evidence
- Mixing unrelated events
- Ignoring source limitations
- Creating visual conclusions not supported by data
- Omitting data source and method explanation
