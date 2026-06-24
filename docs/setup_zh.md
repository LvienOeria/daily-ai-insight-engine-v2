# 环境搭建

## 仓库管理

本项目已初始化为 Git 仓库。

作为可复现的 MVP，应将生成的数据集、结构化输出、报告、可视化结果和文档纳入版本控制。切勿提交本地密钥、缓存、虚拟环境或机器特定文件。

## API 密钥配置

从 `.env.example` 创建本地 `.env` 文件：

```bash
cp .env.example .env
```

只填入源评估后选定的 MVP 所需密钥。

### 当前必需

MVP 使用 DeepSeek 作为本地 LLM 脚本引擎。

必须配置的本地值：

- `DEEPSEEK_API_KEY`

已配置的默认值：

- `LLM_PROVIDER=deepseek`
- `DEEPSEEK_BASE_URL=https://api.deepseek.com`
- `DEEPSEEK_MODEL=deepseek-v4-flash`
- `DEEPSEEK_REPORT_MODEL=deepseek-v4-flash`
- `REPORT_TIMEZONE=Asia/Shanghai`
- `REPORT_WINDOW_DAYS=3`

DeepSeek API 兼容 OpenAI 协议，因此本地脚本可以直接使用 OpenAI SDK 配合 DeepSeek 的 base URL。

### 可选的配置

- `NEWS_API_KEY` 或 `GNEWS_API_KEY`：如果选定的数据采集路径依赖新闻聚合 API。
- `GITHUB_TOKEN`：如果使用 GitHub 仓库、发布或 Issue 时，未认证的速率限制过低。
- `SERPAPI_API_KEY` 或 `TAVILY_API_KEY`：用于基于搜索的采集，但除非源评估确认其必要性，否则应视为辅助或未来阶段方案。

RSS 源、arXiv 和 Hacker News 的公开 API 通常不需要 API 密钥。

## 当前 MVP 默认设置

当前默认运行时设置也记录在 `config/defaults.json` 中。

- 报告时间窗口：最近 3 天
- 报告时区：`Asia/Shanghai`
- LLM 提供商：DeepSeek API
- LLM 执行模式：本地脚本
- 数据源策略：先尝试抓取候选源，评估实际数据质量后再选择核心源
- 中文源兼容路径：DeepSeek 网络搜索 + MCP，限定于量子位、机器之心和知乎
- 前端：React + Vite + pnpm
- 可视化：D3.js

## 实施前需确认的配置

在编写工作流代码之前，确认或记录：

- 经过抓取尝试后的数据源组合。例如：官方 AI 公司博客、arXiv、Hacker News、选定的 RSS 源。
- 中文网络搜索的查询模板和各站点的结果上限。
- 原始数据、清洗数据、结构化数据、聚类事件、排名、可视化、报告和质量检查的输出路径。
- 是否应将生成的公开新闻数据集纳入版本控制以确保可复现性。

## 前端与可视化

MVP 前端使用 React、Vite、pnpm 和 D3.js。

实施规则：

- 使用 Node.js 20 或更新版本。注意系统自带的 Node.js 可能版本过低，本工作区已使用 nvm 安装了 Node 22.22.2。
- Python 脚本负责数据采集、清洗、结构化、事件聚类、重要性评分、报告生成和质量检查。
- React 应用仅为展示层。它不得生成事实、调用 LLM 或更改排名。
- D3 图表必须从结构化 JSON 文件读取数据，主要是 `frontend/public/data/latest.json`。
- 仪表盘应通过 `news_id`、`event_id`、来源名称、关键事实或证据摘要来展示顶级事件、趋势、风险和机会的证据可追溯性。
- 提交前端源码和 `pnpm-lock.yaml`。不要提交 `node_modules/`。
- 不要用前端美化来替代可复现的数据工件。

## 中文网络搜索约束

中文网络搜索是一条兼容性路径，而非绕过源评估的捷径。

实施规则：

- 仅对量子位（`qbitai.com`）、机器之心（`jiqizhixin.com`）和知乎（`zhihu.com`）的白名单页面使用 DeepSeek 网络搜索。
- 在清洗和验证之前，将搜索观测结果单独存储。
- 仅当结果包含标题、来源/站点、发布日期或可追溯的可见日期、URL 以及摘要/正文时才接受进入主数据集。
- 默认将知乎视为社区信号。除非具体条目完整、可追溯且有事实依据，否则不应将其作为顶级事件的主要证据。
- 在源评估备注中记录被拒绝或隔离的搜索结果，以说明源选择的权衡。

## 密钥处理规则

- 不要将真实 API 密钥粘贴到 AGENTS.md、文档、源文件、报告或已提交的数据集中。
- 仅在本地 `.env` 文件或操作系统密钥管理器中存储真实密钥。
- 如果原始提供商载荷中包含凭据，保存前应移除或脱敏该凭据。
