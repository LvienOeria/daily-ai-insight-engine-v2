# 核心流程

## 工作流概览

```text
1. 从 config/sources.json 加载数据源
2. 抓取各源（API / RSS / HTTP 抓取）
3. 评估源质量 → source_evaluation.json
4. 清洗与验证 → cleaned_news.json（去重、日期过滤、质量评分）
5. DeepSeek 结构化抽取 → structured_news.json（实体、事件类型、风险标签等）
6. DeepSeek 事件聚类 → clustered_events.json
7. 重要性评分 → importance_scores.json
8. 生成可视化数据 → visualization_data.json
9. DeepSeek 生成日报 → daily_ai_report.md
10. 质量检查 → quality_check.json
11. 导出前端数据 → frontend/public/data/latest.json
```

## 各步骤细节

### 1-2. 数据抓取

- **arXiv**：API 调用，查询 `cat:cs.AI OR cat:cs.CL OR cat:cs.LG`，最多 20 条结果
- **RSS**：`feedparser` 解析 XML，提取标题/摘要/日期/URL。The Verge 额外经过 AI 关键词过滤
- **HTTP 抓取**：取首页 → 提取文章链接 → 逐篇抓取 → 从 HTML 提取标题/摘要/日期

RSS 源使用文件缓存，有效期 1 小时，存储在 `data/cache/`。

### 3-4. 清洗

- 日期规范化至 `Asia/Shanghai` 时区
- 剔除 3 天报告窗口之外的条目
- 按 URL 去重
- 过滤缺失必填字段（标题、来源、发布时间）的条目
- 按 `published_at` 降序排列，截取前 `max_items` 条（默认 20）

### 5. 结构化抽取

DeepSeek（或 mock 关键词匹配）从每条清洗后新闻中抽取：

- 实体（entities）、技术（technologies）、事件类型（event_type）、行业领域（industry_area）
- 关键事实（key_facts）、情感（sentiment）、影响范围（impact_scope）
- 风险标签（risk_tags）、机会标签（opportunity_tags）、重要性评分（importance_score）、置信度（confidence）、证据（evidence）

批次大小：每次 API 调用 5 条。

### 6-7. 聚类与评分

DeepSeek 将相关新闻归类为事件。然后确定性评分模型对事件进行多维度排名：影响范围、来源权威性、新颖性、多源支持度、技术/商业影响、风险/机会水平、时效性。

### 8-9. 可视化与报告

从结构化条目和事件计算可视化数据。日报由 DeepSeek 以专业中文生成，包含 7 个规定章节。

### 10-11. 质量检查与导出

质量检查验证条目数量、字段完整度、证据可追溯性、报告章节完整性和文档存在性。所有工件导出至 `frontend/public/data/latest.json` 供 React 仪表盘使用。

## 运作原则

人定义规则，确定性处理保障稳定性，LLM 处理语义理解，质量检查在报告定稿前标记问题。
