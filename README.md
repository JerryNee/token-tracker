# Token Tracker

自动追踪 AI 编程工具的 token 用量与费用估算。

> 数据来源：Antigravity CLI、Claude Code
> 最后更新：2026-06-02 22:37 UTC | 数据范围：2026-05-19 ~ 2026-06-02

## 全量汇总

| 指标 | 数值 |
|------|------|
| 总对话数 | 4,147 |
| Input tokens | 804.0K |
| Output tokens | 2.83M |
| Cache 写入 | 18.83M |
| Cache 读取 | 548.28M |
| 总 tokens | 570.74M |
| **估算总费用** | **$1237.73** |

## 按月统计

| 月份      | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用       |
| ------- | ------ | ------ | ------ | ------- | ------- | ---- | -------- |
| 2026-06 |  76.4K | 367.9K |  2.00M |  12.54M |  14.98M |  102 |   $84.96 |
| 2026-05 | 727.6K |  2.46M | 16.84M | 535.74M | 555.76M | 4045 | $1152.69 |

## 按工具统计

| 工具              | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用       |
| --------------- | ------ | ------ | ------ | ------- | ------- | ---- | -------- |
| Claude Code     |  91.7K |  2.61M | 18.83M | 548.28M | 569.81M | 3036 | $1233.79 |
| Antigravity CLI | 712.4K | 224.4K |      0 |       0 |  936.7K | 1111 |    $3.86 |

## 按模型统计

| 模型                | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用       |
| ----------------- | ------ | ------ | ------ | ------- | ------- | ---- | -------- |
| claude-opus-4-7   |  13.0K |  1.93M | 11.98M | 506.42M | 520.34M | 2296 | $1128.76 |
| claude-opus-4-8   |  76.4K | 340.9K |  1.40M |  11.71M |  13.52M |   92 |   $70.44 |
| claude-sonnet-4-6 |   2.2K | 338.7K |  5.46M |  30.14M |  35.94M |  648 |   $34.59 |
| gemini-3.5-flash  | 462.4K | 174.5K |      0 |       0 |  636.9K |  757 |    $2.25 |
| claude-opus-4.6   |  22.1K |   8.0K |      0 |       0 |   30.1K |   52 |    $0.93 |
| gemini-3.1-pro    | 193.2K |  29.0K |      0 |       0 |  222.1K |  230 |    $0.38 |
| claude-sonnet-4.6 |  34.7K |  12.9K |      0 |       0 |   47.7K |   72 |    $0.30 |

## 按设备统计

| 设备                           | Input  | Output | CacheW | CacheR  | Total   | 对话数  | 费用       |
| ---------------------------- | ------ | ------ | ------ | ------- | ------- | ---- | -------- |
| Jerrys-MacBook-Pro-403.local |  91.7K |  2.61M | 18.83M | 548.28M | 569.81M | 3036 | $1233.79 |
| XR4Empathy                   | 712.4K | 224.4K |      0 |       0 |  936.7K | 1111 |    $3.86 |

> 费用为估算值，基于 [Anthropic](https://www.anthropic.com/pricing) / [OpenAI](https://openai.com/api/pricing/) / [Google Gemini](https://ai.google.dev/pricing) 官方定价。
> 数据来源：`~/.claude/projects/` 会话文件及 `~/.tokentracker/tracker/`，由 sync.py 自动备份。
