# Token Tracker

自动追踪 AI 编程工具的 token 用量与费用估算。

> 数据来源：Antigravity CLI、Claude Code、Codex
> 最后更新：2026-06-17 06:43 UTC | 数据范围：2026-05-19 ~ 2026-06-17

## 全量汇总

| 指标 | 数值 |
|------|------|
| 总对话数 | 5,628 |
| Input tokens | 4.83M |
| Output tokens | 5.02M |
| Cache 写入 | 29.87M |
| Cache 读取 | 847.43M |
| 总 tokens | 887.14M |
| **估算总费用** | **$2041.00** |

## 按月统计

| 月份      | Input | Output | CacheW | CacheR  | Total   | 对话数  | 费用       |
| ------- | ----- | ------ | ------ | ------- | ------- | ---- | -------- |
| 2026-06 | 3.69M |  2.56M | 13.03M | 311.69M | 330.97M | 1532 |  $886.16 |
| 2026-05 | 1.14M |  2.46M | 16.84M | 535.74M | 556.18M | 4096 | $1154.73 |

## 按工具统计

| 工具              | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用       |
| --------------- | ------ | ------ | ------ | ------- | ------- | ---- | -------- |
| Claude Code     | 204.7K |  4.61M | 29.87M | 819.30M | 853.98M | 3963 | $1999.05 |
| Codex           |  3.76M | 159.3K |      0 |  28.12M |  32.05M |  364 |   $37.66 |
| Antigravity CLI | 861.2K | 253.2K |      0 |       0 |   1.11M | 1301 |    $4.18 |

## 按模型统计

| 模型                | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用       |
| ----------------- | ------ | ------ | ------ | ------- | ------- | ---- | -------- |
| claude-opus-4-7   |  13.0K |  1.93M | 11.98M | 506.42M | 520.34M | 2296 | $1128.76 |
| claude-opus-4-8   | 189.5K |  2.34M | 12.43M | 282.74M | 297.70M | 1019 |  $835.70 |
| gpt-5.5           |  3.76M | 159.3K |      0 |  28.12M |  32.05M |  364 |   $37.66 |
| claude-sonnet-4-6 |   2.2K | 338.7K |  5.46M |  30.14M |  35.94M |  648 |   $34.59 |
| gemini-3.5-flash  | 462.4K | 174.5K |      0 |       0 |  636.9K |  757 |    $2.25 |
| claude-opus-4.6   |  22.1K |   8.0K |      0 |       0 |   30.1K |   52 |    $0.93 |
| gemini-3.1-pro    | 342.0K |  57.8K |      0 |       0 |  399.8K |  420 |    $0.70 |
| claude-sonnet-4.6 |  34.7K |  12.9K |      0 |       0 |   47.7K |   72 |    $0.30 |

## 按设备统计

| 设备                           | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用       |
| ---------------------------- | ------ | ------ | ------ | ------- | ------- | ---- | -------- |
| Jerrys-MacBook-Pro-403.local |  3.97M |  4.77M | 29.87M | 847.43M | 886.03M | 4327 | $2036.71 |
| XR4Empathy                   | 861.2K | 253.2K |      0 |       0 |   1.11M | 1301 |    $4.18 |

> 费用为估算值，基于 [Anthropic](https://www.anthropic.com/pricing) / [OpenAI](https://openai.com/api/pricing/) / [Google Gemini](https://ai.google.dev/pricing) 官方定价。
> 数据来源：`~/.claude/projects/`、`~/.codex/sessions/` 会话文件及 `~/.tokentracker/tracker/`，由 sync.py 自动备份。
