# Token Tracker

自动追踪 AI 编程工具的 token 用量与费用估算。

> 数据来源：Antigravity CLI、Claude Code、claude
> 最后更新：2026-05-24 04:15 UTC | 数据范围：2026-05-19 ~ 2026-05-24

## 全量汇总

| 指标 | 数值 |
|------|------|
| 总对话数 | 2,864 |
| Input tokens | 234.6K |
| Output tokens | 1.82M |
| Cache 写入 | 15.50M |
| Cache 读取 | 555.40M |
| 总 tokens | 572.95M |
| **估算总费用** | **$1040.89** |

## 按月统计

| 月份      | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用       |
| ------- | ------ | ------ | ------ | ------- | ------- | ---- | -------- |
| 2026-05 | 234.6K |  1.82M | 15.50M | 555.40M | 572.95M | 2864 | $1040.83 |

## 按工具统计

| 工具              | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用      |
| --------------- | ------ | ------ | ------ | ------- | ------- | ---- | ------- |
| Claude Code     |  13.8K |  1.31M | 12.30M | 368.85M | 382.48M | 2112 | $744.25 |
| claude          |   4.9K | 421.9K |  3.20M | 186.55M | 190.17M |  347 | $295.53 |
| Antigravity CLI | 215.9K |  81.5K |      0 |       0 |  297.4K |  405 |   $1.05 |

## 按模型统计

| 模型                | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用      |
| ----------------- | ------ | ------ | ------ | ------- | ------- | ---- | ------- |
| claude-opus-4-7   |  14.9K |  1.21M |  7.55M | 502.38M | 511.15M | 1811 | $986.21 |
| claude-sonnet-4-6 |   3.8K | 522.7K |  7.96M |  53.02M |  61.50M |  648 |  $53.56 |
| gemini-3.5-flash  | 215.9K |  81.5K |      0 |       0 |  297.4K |  405 |   $1.05 |

## 按设备统计

| 设备         | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用       |
| ---------- | ------ | ------ | ------ | ------- | ------- | ---- | -------- |
| unknown    | 112.8K |  1.77M | 15.50M | 555.40M | 572.78M | 2636 | $1040.24 |
| XR4Empathy | 121.7K |  46.1K |      0 |       0 |  167.8K |  228 |    $0.59 |

> 费用为估算值，基于 [Anthropic](https://www.anthropic.com/pricing) / [OpenAI](https://openai.com/api/pricing/) / [Google Gemini](https://ai.google.dev/pricing) 官方定价。
> 数据来源：`~/.claude/projects/` 会话文件及 `~/.tokentracker/tracker/`，由 sync.py 自动备份。
