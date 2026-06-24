# 每日 AI 洞察引擎

可复现的 AI 新闻情报 MVP 工作流：

```text
抓取（RSS + HTTP + API）→ 清洗 → 结构化抽取（DeepSeek）
→ 事件聚类 → 重要性评分 → 日报 → React/D3 仪表盘 → 质量检查
```

## 数据源

| 源 | 方式 | 语言 | 覆盖范围 |
|:---|:---|:---|:---|
| arXiv | API | 英文 | AI/ML/CL 研究预印本 |
| 量子位 (qbitai.com) | HTTP 抓取（全文提取） | 中文 | 中国 AI 产业与技术报道 |
| TechCrunch AI | RSS | 英文 | 创业融资、产品发布 |
| The Verge | RSS + AI 关键词过滤 | 英文 | 消费科技与 AI 报道 |
| 36氪 | RSS + AI 关键词过滤 | 中文 | 创业、科技与 AI 商业化报道 |

## 运行环境

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
cd frontend && pnpm install
```

需要 Node.js 20+，已验证 Node 22.22.2。

## 配置

复制 `.env.example` 为 `.env`，设置：

```text
DEEPSEEK_API_KEY=sk-...
```

默认值：
- LLM：DeepSeek（抽取用 `deepseek-v4-flash`，报告用 `deepseek-v4-pro`）
- 报告窗口：最近 3 天
- 时区：`Asia/Shanghai`
- RSS 缓存：1 小时
- 每源最多 6 条，全局最多 20 条

## 运行

```bash
.venv/bin/python -m daily_ai_insight run          # 正式运行
.venv/bin/python -m daily_ai_insight run --mock-llm  # 开发模式
cd frontend && pnpm dev                            # 启动仪表盘
```

## 管线流程

```
sources.json → 抓取 → source_evaluation.json
    → raw_news.json → 清洗 → cleaned_news.json
    → 结构化（DeepSeek）→ structured_news.json
    → 聚类（DeepSeek）→ clustered_events.json
    → 评分 → importance_scores.json
    → 可视化 → visualization_data.json
    → 报告（DeepSeek）→ daily_ai_report.md
    → 质量检查 → quality_check.json
    → frontend/public/data/latest.json
```
