# Token Tracker

自动追踪 AI 编程工具的 token 用量与费用估算。

> 数据来源：Antigravity CLI、Claude Code
> 最后更新：2026-05-27 06:21 UTC | 数据范围：2026-05-19 ~ 2026-05-27

## 全量汇总

| 指标 | 数值 |
|------|------|
| 总对话数 | 2,584 |
| Input tokens | 137.7K |
| Output tokens | 1.67M |
| Cache 写入 | 14.21M |
| Cache 读取 | 462.35M |
| 总 tokens | 478.37M |
| **估算总费用** | **$909.96** |

## 按月统计

| 月份      | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用      |
| ------- | ------ | ------ | ------ | ------- | ------- | ---- | ------- |
| 2026-05 | 137.7K |  1.67M | 14.21M | 462.35M | 478.37M | 2584 | $909.91 |

## 按工具统计

| 工具              | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用      |
| --------------- | ------ | ------ | ------ | ------- | ------- | ---- | ------- |
| Claude Code     |  16.0K |  1.63M | 14.21M | 462.35M | 478.20M | 2356 | $909.31 |
| Antigravity CLI | 121.7K |  46.1K |      0 |       0 |  167.8K |  228 |   $0.59 |

## 按模型统计

| 模型                | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用      |
| ----------------- | ------ | ------ | ------ | ------- | ------- | ---- | ------- |
| claude-opus-4-7   |  13.5K |  1.21M |  7.69M | 420.58M | 429.49M | 1708 | $866.17 |
| claude-sonnet-4-6 |   2.6K | 411.8K |  6.52M |  41.77M |  48.70M |  648 |  $43.15 |
| gemini-3.5-flash  | 121.7K |  46.1K |      0 |       0 |  167.8K |  228 |   $0.59 |

## 按设备统计

| 设备                           | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用      |
| ---------------------------- | ------ | ------ | ------ | ------- | ------- | ---- | ------- |
| Jerrys-MacBook-Pro-403.local |  16.0K |  1.63M | 14.21M | 462.35M | 478.20M | 2356 | $909.31 |
| XR4Empathy                   | 121.7K |  46.1K |      0 |       0 |  167.8K |  228 |   $0.59 |

> 费用为估算值，基于 [Anthropic](https://www.anthropic.com/pricing) / [OpenAI](https://openai.com/api/pricing/) / [Google Gemini](https://ai.google.dev/pricing) 官方定价。
> 数据来源：`~/.claude/projects/` 会话文件及 `~/.tokentracker/tracker/`，由 sync.py 自动备份。
