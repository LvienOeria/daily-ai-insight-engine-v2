# AI 使用方式、Prompt 设计与错误处理

## 目的

本文档说明 DeepSeek LLM 在每日 AI 洞察引擎中的使用方式。

## AI 使用

DeepSeek 用于管线的三个阶段：

1. **结构化抽取** — 从清洗后的新闻文本中抽取实体、技术、事件类型、关键事实、风险、机会和置信度。每次 API 调用批量处理 5 条。
2. **事件聚类** — 判断多条新闻是否描述同一事件。有充分支撑的单一新闻事件也允许。
3. **日报生成** — 将结构化事件数据转换为包含 7 个规定章节的专业中文分析报告。

DeepSeek 不用于：

- 数据采集（RSS、API、HTTP 抓取均为确定性处理）
- 字段验证（日期规范化、去重、必填字段检查均为程序化处理）
- 最终质量检查

## Prompt 设计

### 结构化 Prompt

- 仅返回有效 JSON
- 仅使用输入条目文本；不得编造公司、日期、URL、金额或事实
- 未知字段使用 `null`、`[]` 或 `other`
- 证据必须引用或紧密转述输入中的片段
- 事件类型和行业领域限定为固定枚举值
- 置信度：low / medium / high

### 聚类 Prompt

- 仅在描述同一具体事件时才进行分组
- 不得按宽泛主题、同一天、相同情感或相同公司但不同事实进行分组
- 每个事件必须包含证据和有效的 related_news_ids

### 报告 Prompt

- 生成包含 7 个章节的专业中文 Markdown
- 顶级事件必须引用 event_id 或 news_id
- 趋势必须有多个事件或关键事实支撑
- 风险/机会必须映射到结构化标签
- 不得编造事实或夸大弱证据

## 错误处理

### 数据错误

缺失字段、日期不一致、重复 → 在清洗步骤中以程序化方式处理。条目被丢弃或标记 `missing_fields`。

### LLM 输出错误

无效 JSON、缺失字段、无效枚举 → `_normalize_structured_record` 填充默认值，将无效值映射为 `other`，将分数限制在 1-5。若 JSON 完全无法解析，管线抛出 `LLMError`。

### 分析错误

质量检查捕获：缺乏支撑的论断、缺失报告章节、高重要性条目的证据为空、文档缺失。

## Mock 模式

`--mock-llm` 将所有 DeepSeek 调用替换为确定性的关键词匹配启发式规则。适用于开发和测试，无需 API 费用。质量低于真实 LLM 抽取。

## Skill 系统

3 个 DeepSeek 调用的 prompt 通过 skill 系统管理：

```
skills/
  news-structuring/prompt.txt      → 结构化抽取的 system prompt
  event-clustering/prompt.txt      → 事件聚类的 system prompt
  daily-report-generation/prompt.txt → 日报生成的 system prompt
```

`daily_ai_insight/skill_loader.py` 在运行时加载对应的 prompt 文件。修改 prompt 只需编辑 `prompt.txt`，无需改代码。3 个程序化 skill（数据源评估、重要性评分、质量检查）不需要 prompt，直接在代码中实现。

Prompt 均以中文编写，因为 DeepSeek 对中文指令的理解和执行更精准。
