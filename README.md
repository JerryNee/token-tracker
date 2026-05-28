# Token Tracker

自动追踪 AI 编程工具的 token 用量与费用估算。

> 数据来源：Antigravity CLI、Claude Code
> 最后更新：2026-05-28 22:47 UTC | 数据范围：2026-05-19 ~ 2026-05-28

## 全量汇总

| 指标 | 数值 |
|------|------|
| 总对话数 | 2,674 |
| Input tokens | 136.1K |
| Output tokens | 1.72M |
| Cache 写入 | 13.85M |
| Cache 读取 | 410.28M |
| 总 tokens | 425.97M |
| **估算总费用** | **$862.61** |

## 按月统计

| 月份      | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用      |
| ------- | ------ | ------ | ------ | ------- | ------- | ---- | ------- |
| 2026-05 | 136.1K |  1.72M | 13.85M | 410.28M | 425.97M | 2674 | $862.56 |

## 按工具统计

| 工具              | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用      |
| --------------- | ------ | ------ | ------ | ------- | ------- | ---- | ------- |
| Claude Code     |  14.4K |  1.67M | 13.85M | 410.28M | 425.81M | 2446 | $861.97 |
| Antigravity CLI | 121.7K |  46.1K |      0 |       0 |  167.8K |  228 |   $0.59 |

## 按模型统计

| 模型                | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用      |
| ----------------- | ------ | ------ | ------ | ------- | ------- | ---- | ------- |
| claude-opus-4-7   |  12.1K |  1.33M |  8.39M | 380.14M | 389.86M | 1798 | $827.38 |
| claude-sonnet-4-6 |   2.2K | 338.7K |  5.46M |  30.14M |  35.94M |  648 |  $34.59 |
| gemini-3.5-flash  | 121.7K |  46.1K |      0 |       0 |  167.8K |  228 |   $0.59 |

## 按设备统计

| 设备                           | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用      |
| ---------------------------- | ------ | ------ | ------ | ------- | ------- | ---- | ------- |
| Jerrys-MacBook-Pro-403.local |  14.4K |  1.67M | 13.85M | 410.28M | 425.81M | 2446 | $861.97 |
| XR4Empathy                   | 121.7K |  46.1K |      0 |       0 |  167.8K |  228 |   $0.59 |

> 费用为估算值，基于 [Anthropic](https://www.anthropic.com/pricing) / [OpenAI](https://openai.com/api/pricing/) / [Google Gemini](https://ai.google.dev/pricing) 官方定价。
> 数据来源：`~/.claude/projects/` 会话文件及 `~/.tokentracker/tracker/`，由 sync.py 自动备份。
