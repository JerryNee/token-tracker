# Token Tracker

自动追踪 AI 编程工具的 token 用量与费用估算。

> 数据来源：Antigravity CLI、Claude Code
> 最后更新：2026-06-03 22:53 UTC | 数据范围：2026-05-19 ~ 2026-06-03

## 全量汇总

| 指标 | 数值 |
|------|------|
| 总对话数 | 4,459 |
| Input tokens | 952.9K |
| Output tokens | 3.43M |
| Cache 写入 | 23.06M |
| Cache 读取 | 643.36M |
| 总 tokens | 670.79M |
| **估算总费用** | **$1503.18** |

## 按月统计

| 月份      | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用       |
| ------- | ------ | ------ | ------ | ------- | ------- | ---- | -------- |
| 2026-06 | 219.8K | 963.3K |  6.22M | 107.62M | 115.02M |  405 |  $350.38 |
| 2026-05 | 733.1K |  2.46M | 16.84M | 535.74M | 555.77M | 4054 | $1152.70 |

## 按工具统计

| 工具              | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用       |
| --------------- | ------ | ------ | ------ | ------- | ------- | ---- | -------- |
| Claude Code     | 122.5K |  3.18M | 23.06M | 643.36M | 669.71M | 3199 | $1498.97 |
| Antigravity CLI | 830.4K | 248.4K |      0 |       0 |   1.08M | 1260 |    $4.12 |

## 按模型统计

| 模型                | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用       |
| ----------------- | ------ | ------ | ------ | ------- | ------- | ---- | -------- |
| claude-opus-4-7   |  13.0K |  1.93M | 11.98M | 506.42M | 520.34M | 2296 | $1128.76 |
| claude-opus-4-8   | 107.2K | 913.1K |  5.62M | 106.79M | 113.43M |  255 |  $335.62 |
| claude-sonnet-4-6 |   2.2K | 338.7K |  5.46M |  30.14M |  35.94M |  648 |   $34.59 |
| gemini-3.5-flash  | 462.4K | 174.5K |      0 |       0 |  636.9K |  757 |    $2.25 |
| claude-opus-4.6   |  22.1K |   8.0K |      0 |       0 |   30.1K |   52 |    $0.93 |
| gemini-3.1-pro    | 311.2K |  53.0K |      0 |       0 |  364.2K |  379 |    $0.64 |
| claude-sonnet-4.6 |  34.7K |  12.9K |      0 |       0 |   47.7K |   72 |    $0.30 |

## 按设备统计

| 设备                           | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用       |
| ---------------------------- | ------ | ------ | ------ | ------- | ------- | ---- | -------- |
| Jerrys-MacBook-Pro-403.local | 122.5K |  3.18M | 23.06M | 643.36M | 669.71M | 3199 | $1498.97 |
| XR4Empathy                   | 830.4K | 248.4K |      0 |       0 |   1.08M | 1260 |    $4.12 |

> 费用为估算值，基于 [Anthropic](https://www.anthropic.com/pricing) / [OpenAI](https://openai.com/api/pricing/) / [Google Gemini](https://ai.google.dev/pricing) 官方定价。
> 数据来源：`~/.claude/projects/` 会话文件及 `~/.tokentracker/tracker/`，由 sync.py 自动备份。
