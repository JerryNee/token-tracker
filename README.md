# Token Tracker

自动追踪 AI 编程工具的 token 用量与费用估算。

> 数据来源：Antigravity CLI、Claude Code
> 最后更新：2026-06-16 21:12 UTC | 数据范围：2026-05-19 ~ 2026-06-16

## 全量汇总

| 指标 | 数值 |
|------|------|
| 总对话数 | 5,207 |
| Input tokens | 1.06M |
| Output tokens | 4.77M |
| Cache 写入 | 27.60M |
| Cache 读取 | 779.24M |
| 总 tokens | 812.66M |
| **估算总费用** | **$1893.66** |

## 按月统计

| 月份      | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用       |
| ------- | ------ | ------ | ------ | ------- | ------- | ---- | -------- |
| 2026-06 | 325.1K |  2.30M | 10.77M | 243.50M | 256.89M | 1153 |  $740.85 |
| 2026-05 | 733.1K |  2.46M | 16.84M | 535.74M | 555.77M | 4054 | $1152.70 |

## 按工具统计

| 工具              | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用       |
| --------------- | ------ | ------ | ------ | ------- | ------- | ---- | -------- |
| Claude Code     | 197.0K |  4.51M | 27.60M | 779.24M | 811.55M | 3906 | $1889.37 |
| Antigravity CLI | 861.2K | 253.2K |      0 |       0 |   1.11M | 1301 |    $4.18 |

## 按模型统计

| 模型                | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用       |
| ----------------- | ------ | ------ | ------ | ------- | ------- | ---- | -------- |
| claude-opus-4-7   |  13.0K |  1.93M | 11.98M | 506.42M | 520.34M | 2296 | $1128.76 |
| claude-opus-4-8   | 181.7K |  2.25M | 10.17M | 242.67M | 255.27M |  962 |  $726.02 |
| claude-sonnet-4-6 |   2.2K | 338.7K |  5.46M |  30.14M |  35.94M |  648 |   $34.59 |
| gemini-3.5-flash  | 462.4K | 174.5K |      0 |       0 |  636.9K |  757 |    $2.25 |
| claude-opus-4.6   |  22.1K |   8.0K |      0 |       0 |   30.1K |   52 |    $0.93 |
| gemini-3.1-pro    | 342.0K |  57.8K |      0 |       0 |  399.8K |  420 |    $0.70 |
| claude-sonnet-4.6 |  34.7K |  12.9K |      0 |       0 |   47.7K |   72 |    $0.30 |

## 按设备统计

| 设备                           | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用       |
| ---------------------------- | ------ | ------ | ------ | ------- | ------- | ---- | -------- |
| Jerrys-MacBook-Pro-403.local | 197.0K |  4.51M | 27.60M | 779.24M | 811.55M | 3906 | $1889.37 |
| XR4Empathy                   | 861.2K | 253.2K |      0 |       0 |   1.11M | 1301 |    $4.18 |

> 费用为估算值，基于 [Anthropic](https://www.anthropic.com/pricing) / [OpenAI](https://openai.com/api/pricing/) / [Google Gemini](https://ai.google.dev/pricing) 官方定价。
> 数据来源：`~/.claude/projects/` 会话文件及 `~/.tokentracker/tracker/`，由 sync.py 自动备份。
