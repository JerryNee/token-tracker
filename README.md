# Token Tracker

自动追踪 AI 编程工具的 token 用量与费用估算。

> 数据来源：Antigravity CLI、Claude Code
> 最后更新：2026-05-24 08:29 UTC | 数据范围：2026-05-19 ~ 2026-05-24

## 全量汇总

| 指标 | 数值 |
|------|------|
| 总对话数 | 2,618 |
| Input tokens | 231.7K |
| Output tokens | 1.61M |
| Cache 写入 | 13.80M |
| Cache 读取 | 447.99M |
| 总 tokens | 463.63M |
| **估算总费用** | **$873.73** |

## 按月统计

| 月份      | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用      |
| ------- | ------ | ------ | ------ | ------- | ------- | ---- | ------- |
| 2026-05 | 231.7K |  1.61M | 13.80M | 447.99M | 463.63M | 2618 | $873.69 |

## 按工具统计

| 工具              | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用      |
| --------------- | ------ | ------ | ------ | ------- | ------- | ---- | ------- |
| Claude Code     |  15.8K |  1.52M | 13.80M | 447.99M | 463.33M | 2213 | $872.63 |
| Antigravity CLI | 215.9K |  81.5K |      0 |       0 |  297.4K |  405 |   $1.05 |

## 按模型统计

| 模型                | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用      |
| ----------------- | ------ | ------ | ------ | ------- | ------- | ---- | ------- |
| claude-opus-4-7   |  13.2K |  1.11M |  7.28M | 406.22M | 414.62M | 1565 | $829.49 |
| claude-sonnet-4-6 |   2.6K | 411.8K |  6.52M |  41.77M |  48.70M |  648 |  $43.15 |
| gemini-3.5-flash  | 215.9K |  81.5K |      0 |       0 |  297.4K |  405 |   $1.05 |

## 按设备统计

| 设备                           | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用      |
| ---------------------------- | ------ | ------ | ------ | ------- | ------- | ---- | ------- |
| Jerrys-MacBook-Pro-403.local | 110.0K |  1.56M | 13.80M | 447.99M | 463.46M | 2390 | $873.09 |
| XR4Empathy                   | 121.7K |  46.1K |      0 |       0 |  167.8K |  228 |   $0.59 |

> 费用为估算值，基于 [Anthropic](https://www.anthropic.com/pricing) / [OpenAI](https://openai.com/api/pricing/) / [Google Gemini](https://ai.google.dev/pricing) 官方定价。
> 数据来源：`~/.claude/projects/` 会话文件及 `~/.tokentracker/tracker/`，由 sync.py 自动备份。
