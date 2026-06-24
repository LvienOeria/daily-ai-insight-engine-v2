# 前端与可视化

## 技术栈

- React 18
- Vite 6
- pnpm
- D3.js 7
- lucide-react（图标）

## 角色

前端仅为展示层。Python 脚本产出所有权威数据工件。React 应用读取 `frontend/public/data/latest.json` 并渲染仪表盘。不调用 LLM、不创建事实、不修改排名。

## 仪表盘视图

- **Overview**：指标行、环形图（来源类型、事件类型）、风险/机会矩阵、Top 5 事件
- **Events**：可搜索的完整事件列表，含评分维度分解、证据、来源链接
- **Analysis**：报告正文，7 个章节渲染为结构化卡片
- **Sources**：源评估表格，含层级、状态、条目数
- **Quality**：质量检查结果，含通过/未通过、问题列表

## 图表

| 图表 | 类型 | 说明 |
|:---|:---|:---|
| 来源类型分布 | D3 环形图 | 研究 vs 媒体 vs 社区 |
| 事件类型分布 | D3 环形图 | 聚类类别 |
| 风险/机会矩阵 | D3 散点图 | 颜色按事件类型，大小按置信度，支持缩放/平移 |

## 数据契约

管线写入一个文件供前端消费：

```text
frontend/public/data/latest.json
```

## 仓库规则

- 提交源文件和 `pnpm-lock.yaml`
- 不提交 `node_modules/` 或 `dist/`
