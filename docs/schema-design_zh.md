# Schema 设计

## 目的

本文档说明每日 AI 洞察引擎使用的结构化数据模型。

该 Schema 旨在支持：

- 超越摘要的结构化抽取
- 事件聚类
- 重要性评分
- 趋势分析
- 风险与机会检测
- 可视化
- 证据可追溯性

## 设计原则

Schema 将原始新闻记录、结构化新闻记录和事件级记录分开。

这种分离避免了将原始源差异与下游分析逻辑混在一起。

## 原始新闻条目（RawNewsItem）

原始条目对不同 API、RSS 源和静态手动输入的数据进行规范化。

字段定义：

```json
{
  "news_id": "唯一标识符",
  "title": "标题",
  "url": "原始链接",
  "source": "来源名称",
  "source_type": "来源类型（research/official/media/community 等）",
  "published_at": "发布时间（ISO 8601）",
  "language": "语言（zh/en/mixed）",
  "summary": "摘要",
  "content": "正文",
  "collected_at": "采集时间",
  "raw_provider": "原始提供商名称",
  "raw_payload": {},
  "missing_fields": [],
  "quality_score": 0
}
```

## 结构化新闻条目（StructuredNewsItem）

结构化条目在清洗和 LLM 抽取后生成。

字段定义：

```json
{
  "news_id": "关联的原始条目 ID",
  "title": "标题",
  "source": "来源",
  "source_type": "来源类型",
  "published_at": "发布时间",
  "language": "语言",
  "url": "链接",
  "entities": ["涉及的实体（公司/机构/人物）"],
  "technologies": ["涉及的技术"],
  "event_type": "事件类型（枚举值）",
  "industry_area": "行业领域（枚举值）",
  "key_facts": ["关键事实列表"],
  "summary": "摘要",
  "sentiment": "情感倾向",
  "impact_scope": ["影响范围"],
  "risk_tags": ["风险标签"],
  "opportunity_tags": ["机会标签"],
  "importance_score": 1,
  "confidence": "置信度",
  "evidence": ["证据片段"]
}
```

## 事件条目（EventItem）

事件将相关新闻归类为分析单元。

字段定义：

```json
{
  "event_id": "事件唯一标识符",
  "event_name": "事件名称",
  "related_news_ids": ["关联的新闻 ID 列表"],
  "main_entities": ["主要涉及实体"],
  "core_topic": "核心主题",
  "event_type": "事件类型",
  "industry_area": "行业领域",
  "technologies": ["技术方向"],
  "key_facts": ["关键事实"],
  "evidence": ["证据"],
  "why_it_matters": "重要性说明",
  "impact_scope": ["影响范围"],
  "risk_tags": ["风险标签"],
  "opportunity_tags": ["机会标签"],
  "confidence": "置信度",
  "published_at": "最早关联新闻的发布时间"
}
```

## 字段设计理由

- `entities`：支持公司、机构和人物追踪。
- `technologies`：支持技术趋势可视化。
- `event_type`：支持事件类别统计。
- `industry_area`：支持领域级趋势分析。
- `key_facts`：确保报告论断有据可依。
- `risk_tags`：支持风险预警。
- `opportunity_tags`：支持机会分析。
- `importance_score`：支持顶级事件排名。
- `confidence`：标记不确定的抽取结果。
- `evidence`：支持可追溯性和幻觉检查。

## 枚举策略

尽可能使用固定的枚举值。这可以提高一致性和可视化质量。

摘要、证据和分析类字段允许使用自由文本，但分类字段应当受到约束。

## 校验要求

在报告中使用结构化数据之前，必须满足：

- 必填字段必须存在。
- 枚举值必须有效。
- 分数必须在有效范围内。
- 重要事件应有证据支撑。
- 低置信度数据不应在顶级事件分析中过度使用。
