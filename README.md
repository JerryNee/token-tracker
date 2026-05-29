# Token Tracker

自动追踪 AI 编程工具的 token 用量与费用估算。

> 数据来源：Antigravity CLI、Claude Code
> 最后更新：2026-05-29 21:23 UTC | 数据范围：2026-05-19 ~ 2026-05-29

## 全量汇总

| 指标 | 数值 |
|------|------|
| 总对话数 | 3,725 |
| Input tokens | 727.0K |
| Output tokens | 2.09M |
| Cache 写入 | 14.74M |
| Cache 读取 | 444.16M |
| 总 tokens | 461.72M |
| **估算总费用** | **$948.04** |

## 按月统计

| 月份      | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用      |
| ------- | ------ | ------ | ------ | ------- | ------- | ---- | ------- |
| 2026-05 | 727.0K |  2.09M | 14.74M | 444.16M | 461.72M | 3725 | $947.98 |

## 按工具统计

| 工具              | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用      |
| --------------- | ------ | ------ | ------ | ------- | ------- | ---- | ------- |
| Claude Code     |  14.6K |  1.86M | 14.74M | 444.16M | 460.78M | 2614 | $944.11 |
| Antigravity CLI | 712.4K | 224.4K |      0 |       0 |  936.7K | 1111 |   $3.86 |

## 按模型统计

| 模型                | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用      |
| ----------------- | ------ | ------ | ------ | ------- | ------- | ---- | ------- |
| claude-opus-4-7   |  12.4K |  1.52M |  9.28M | 414.02M | 424.84M | 1966 | $909.53 |
| claude-sonnet-4-6 |   2.2K | 338.7K |  5.46M |  30.14M |  35.94M |  648 |  $34.59 |
| gemini-3.5-flash  | 462.4K | 174.5K |      0 |       0 |  636.9K |  757 |   $2.25 |
| claude-opus-4.6   |  22.1K |   8.0K |      0 |       0 |   30.1K |   52 |   $0.93 |
| gemini-3.1-pro    | 193.2K |  29.0K |      0 |       0 |  222.1K |  230 |   $0.38 |
| claude-sonnet-4.6 |  34.7K |  12.9K |      0 |       0 |   47.7K |   72 |   $0.30 |

## 按设备统计

| 设备                           | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用      |
| ---------------------------- | ------ | ------ | ------ | ------- | ------- | ---- | ------- |
| Jerrys-MacBook-Pro-403.local |  14.6K |  1.86M | 14.74M | 444.16M | 460.78M | 2614 | $944.11 |
| XR4Empathy                   | 712.4K | 224.4K |      0 |       0 |  936.7K | 1111 |   $3.86 |

> 费用为估算值，基于 [Anthropic](https://www.anthropic.com/pricing) / [OpenAI](https://openai.com/api/pricing/) / [Google Gemini](https://ai.google.dev/pricing) 官方定价。
> 数据来源：`~/.claude/projects/` 会话文件及 `~/.tokentracker/tracker/`，由 sync.py 自动备份。
