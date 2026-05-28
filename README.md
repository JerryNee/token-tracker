# Token Tracker

自动追踪 AI 编程工具的 token 用量与费用估算。

> 数据来源：Antigravity CLI、Claude Code
> 最后更新：2026-05-28 23:08 UTC | 数据范围：2026-05-19 ~ 2026-05-28

## 全量汇总

| 指标 | 数值 |
|------|------|
| 总对话数 | 3,101 |
| Input tokens | 405.2K |
| Output tokens | 1.80M |
| Cache 写入 | 13.93M |
| Cache 读取 | 411.82M |
| 总 tokens | 427.96M |
| **估算总费用** | **$868.04** |

## 按月统计

| 月份      | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用      |
| ------- | ------ | ------ | ------ | ------- | ------- | ---- | ------- |
| 2026-05 | 405.2K |  1.80M | 13.93M | 411.82M | 427.96M | 3101 | $867.99 |

## 按工具统计

| 工具              | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用      |
| --------------- | ------ | ------ | ------ | ------- | ------- | ---- | ------- |
| Claude Code     |  14.4K |  1.68M | 13.93M | 411.82M | 427.44M | 2466 | $866.73 |
| Antigravity CLI | 390.8K | 120.6K |      0 |       0 |  511.4K |  635 |   $1.26 |

## 按模型统计

| 模型                | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用      |
| ----------------- | ------ | ------ | ------ | ------- | ------- | ---- | ------- |
| claude-opus-4-7   |  12.2K |  1.34M |  8.47M | 381.67M | 391.50M | 1818 | $832.14 |
| claude-sonnet-4-6 |   2.2K | 338.7K |  5.46M |  30.14M |  35.94M |  648 |  $34.59 |
| gemini-3.5-flash  | 257.5K |  97.7K |      0 |       0 |  355.1K |  421 |   $1.26 |
| gemini-3.1-pro    | 105.8K |  12.4K |      0 |       0 |  118.3K |  142 | $0.0000 |
| claude-opus-4.6   |   7.1K |   3.3K |      0 |       0 |   10.4K |   28 | $0.0000 |
| claude-sonnet-4.6 |  20.4K |   7.2K |      0 |       0 |   27.6K |   44 | $0.0000 |

## 按设备统计

| 设备                           | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用      |
| ---------------------------- | ------ | ------ | ------ | ------- | ------- | ---- | ------- |
| Jerrys-MacBook-Pro-403.local |  14.4K |  1.68M | 13.93M | 411.82M | 427.44M | 2466 | $866.73 |
| XR4Empathy                   | 390.8K | 120.6K |      0 |       0 |  511.4K |  635 |   $1.26 |

> 费用为估算值，基于 [Anthropic](https://www.anthropic.com/pricing) / [OpenAI](https://openai.com/api/pricing/) / [Google Gemini](https://ai.google.dev/pricing) 官方定价。
> 数据来源：`~/.claude/projects/` 会话文件及 `~/.tokentracker/tracker/`，由 sync.py 自动备份。
