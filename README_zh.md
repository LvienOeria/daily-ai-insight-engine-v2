# 每日 AI 洞察引擎（Daily AI Insight Engine）

可复现的 AI 新闻情报 MVP 工作流：

```text
候选源 → 源评估 → 原始新闻 → 清洗后新闻 → 结构化抽取
→ 事件聚类 → 重要性评分 → 日报 → React/D3 仪表盘 → 质量检查
```

## 运行环境

Python：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
```

前端：

```bash
cd frontend
pnpm install
```

需要 Node.js 20 或更新版本。本工作区已验证通过 Node 22.22.2。

## 配置

复制 `.env.example` 为 `.env`，仅在其中填入本地密钥。

真实 LLM 运行需要：

```text
DEEPSEEK_API_KEY
```

默认值：

- LLM 提供商：DeepSeek
- LLM 模型：`deepseek-v4-flash`（用于抽取和报告生成）
- 报告窗口：最近 3 天
- 时区：`Asia/Shanghai`
- 前端数据文件：`frontend/public/data/latest.json`

## 运行

开发模式（不调用 LLM）：

```bash
.venv/bin/python -m daily_ai_insight run --mock-llm
```

真实 LLM 运行：

```bash
.venv/bin/python -m daily_ai_insight run
```

启动仪表盘：

```bash
cd frontend
pnpm dev
```

## 中文网络搜索兼容

中文 DeepSeek 网络搜索限定于以下站点：

- 量子位：`qbitai.com`
- 机器之心：`jiqizhixin.com`
- 知乎：`zhihu.com`

当前实现通过 MCP 搜索服务进行中文源抓取。当 MCP 不可用时，回退至静态观测文件：

```text
data/manual/chinese_websearch_observations.json
```

搜索结果需通过白名单和必填字段校验后才进入主数据集。

## 验证

```bash
.venv/bin/python -m pytest
.venv/bin/ruff check daily_ai_insight tests
cd frontend && pnpm build
```
