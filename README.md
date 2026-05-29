# Token Tracker

自动追踪 AI 编程工具的 token 用量与费用估算。

> 数据来源：Antigravity CLI、Claude Code
> 最后更新：2026-05-29 16:14 UTC | 数据范围：2026-05-19 ~ 2026-05-29

## 全量汇总

| 指标 | 数值 |
|------|------|
| 总对话数 | 3,245 |
| Input tokens | 406.3K |
| Output tokens | 1.98M |
| Cache 写入 | 14.74M |
| Cache 读取 | 443.45M |
| 总 tokens | 460.57M |
| **估算总费用** | **$944.77** |

## 按月统计

| 月份      | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用      |
| ------- | ------ | ------ | ------ | ------- | ------- | ---- | ------- |
| 2026-05 | 406.3K |  1.98M | 14.74M | 443.45M | 460.57M | 3245 | $944.71 |

## 按工具统计

| 工具              | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用      |
| --------------- | ------ | ------ | ------ | ------- | ------- | ---- | ------- |
| Claude Code     |  14.6K |  1.86M | 14.74M | 443.45M | 460.06M | 2607 | $942.73 |
| Antigravity CLI | 391.7K | 120.9K |      0 |       0 |  512.6K |  638 |   $1.98 |

## 按模型统计

| 模型                | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用      |
| ----------------- | ------ | ------ | ------ | ------- | ------- | ---- | ------- |
| claude-opus-4-7   |  12.4K |  1.52M |  9.28M | 413.31M | 424.12M | 1959 | $908.14 |
| claude-sonnet-4-6 |   2.2K | 338.7K |  5.46M |  30.14M |  35.94M |  648 |  $34.59 |
| gemini-3.5-flash  | 257.5K |  97.7K |      0 |       0 |  355.1K |  421 |   $1.26 |
| claude-opus-4.6   |   7.1K |   3.3K |      0 |       0 |   10.4K |   28 |   $0.35 |
| gemini-3.1-pro    | 105.8K |  12.4K |      0 |       0 |  118.3K |  142 |   $0.19 |
| claude-sonnet-4.6 |  21.2K |   7.5K |      0 |       0 |   28.8K |   47 |   $0.17 |

## 按设备统计

| 设备                           | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用      |
| ---------------------------- | ------ | ------ | ------ | ------- | ------- | ---- | ------- |
| Jerrys-MacBook-Pro-403.local |  14.6K |  1.86M | 14.74M | 443.45M | 460.06M | 2607 | $942.73 |
| XR4Empathy                   | 391.7K | 120.9K |      0 |       0 |  512.6K |  638 |   $1.98 |

> 费用为估算值，基于 [Anthropic](https://www.anthropic.com/pricing) / [OpenAI](https://openai.com/api/pricing/) / [Google Gemini](https://ai.google.dev/pricing) 官方定价。
> 数据来源：`~/.claude/projects/` 会话文件及 `~/.tokentracker/tracker/`，由 sync.py 自动备份。
