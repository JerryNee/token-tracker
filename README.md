# Token Tracker

自动追踪 AI 编程工具的 token 用量与费用估算。

> 数据来源：Antigravity CLI、Claude Code
> 最后更新：2026-05-29 21:26 UTC | 数据范围：2026-05-19 ~ 2026-05-29

## 全量汇总

| 指标 | 数值 |
|------|------|
| 总对话数 | 3,871 |
| Input tokens | 727.3K |
| Output tokens | 2.25M |
| Cache 写入 | 15.03M |
| Cache 读取 | 469.01M |
| 总 tokens | 487.01M |
| **估算总费用** | **$1002.71** |

## 按月统计

| 月份      | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用       |
| ------- | ------ | ------ | ------ | ------- | ------- | ---- | -------- |
| 2026-05 | 727.3K |  2.25M | 15.03M | 469.01M | 487.01M | 3871 | $1002.64 |

## 按工具统计

| 工具              | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用      |
| --------------- | ------ | ------ | ------ | ------- | ------- | ---- | ------- |
| Claude Code     |  14.9K |  2.02M | 15.03M | 469.01M | 486.08M | 2760 | $998.78 |
| Antigravity CLI | 712.4K | 224.4K |      0 |       0 |  936.7K | 1111 |   $3.86 |

## 按模型统计

| 模型                | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用      |
| ----------------- | ------ | ------ | ------ | ------- | ------- | ---- | ------- |
| claude-opus-4-7   |  12.6K |  1.68M |  9.57M | 438.87M | 450.13M | 2112 | $964.19 |
| claude-sonnet-4-6 |   2.2K | 338.7K |  5.46M |  30.14M |  35.94M |  648 |  $34.59 |
| gemini-3.5-flash  | 462.4K | 174.5K |      0 |       0 |  636.9K |  757 |   $2.25 |
| claude-opus-4.6   |  22.1K |   8.0K |      0 |       0 |   30.1K |   52 |   $0.93 |
| gemini-3.1-pro    | 193.2K |  29.0K |      0 |       0 |  222.1K |  230 |   $0.38 |
| claude-sonnet-4.6 |  34.7K |  12.9K |      0 |       0 |   47.7K |   72 |   $0.30 |

## 按设备统计

| 设备                           | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用      |
| ---------------------------- | ------ | ------ | ------ | ------- | ------- | ---- | ------- |
| Jerrys-MacBook-Pro-403.local |  14.9K |  2.02M | 15.03M | 469.01M | 486.08M | 2760 | $998.78 |
| XR4Empathy                   | 712.4K | 224.4K |      0 |       0 |  936.7K | 1111 |   $3.86 |

> 费用为估算值，基于 [Anthropic](https://www.anthropic.com/pricing) / [OpenAI](https://openai.com/api/pricing/) / [Google Gemini](https://ai.google.dev/pricing) 官方定价。
> 数据来源：`~/.claude/projects/` 会话文件及 `~/.tokentracker/tracker/`，由 sync.py 自动备份。
