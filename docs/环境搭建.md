# 环境搭建

## 仓库管理

将生成的数据集和报告纳入版本控制以确保可复现性。切勿提交 `.env`、缓存、虚拟环境或 `node_modules/`。

## API 密钥配置

从 `.env.example` 创建 `.env`：

```bash
cp .env.example .env
```

必需：

- `DEEPSEEK_API_KEY` — 用于 LLM 驱动的结构化抽取、聚类和报告生成

可选：

- `TAVILY_API_KEY` — 备用搜索后端

RSS 源、arXiv API 和直接 HTTP 抓取不需要 API 密钥。

## 当前 MVP 默认配置

位于 `config/defaults.json`：

- 报告窗口：3 天
- 时区：`Asia/Shanghai`
- LLM 提供商：DeepSeek API
- 抽取模型：`deepseek-v4-flash`
- 报告模型：`deepseek-v4-pro`
- 前端：React + Vite + pnpm + D3.js

## 数据源

`config/sources.json` 中配置了 4 个数据源：

| 源 | 方式 | 语言 |
|:---|:---|:---|
| arXiv AI Search | API | 英文 |
| 量子位 (qbitai.com) | 直连 HTTP 抓取 | 中文 |
| TechCrunch AI | RSS | 英文 |
| The Verge | RSS + AI 关键词过滤 | 英文 |

添加新的 RSS 源时，使用 `"access_method": "rss"` 并提供 `"endpoint_url"`。HTTP 抓取源使用 `"access_method": "direct_http"`。

## 前端

- Python 脚本负责数据采集、清洗、结构化、聚类、评分、报告和质量检查。
- React 应用仅为展示层，读取 `frontend/public/data/latest.json`。
- D3 图表展示来源分布、事件类型分布和风险/机会矩阵。
- 提交 `pnpm-lock.yaml`，不提交 `node_modules/`。

## 密钥处理

- 真实密钥仅存储在本地 `.env` 文件中。
- 切勿将 API 密钥粘贴到文档、源文件或已提交的数据集中。
