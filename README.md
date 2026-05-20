# Token Tracker

自动追踪 AI 编程工具的 token 用量与费用估算。

> 数据来源：Claude Code、claude
> 最后更新：2026-05-20 05:39 UTC | 数据范围：2026-05-19 ~ 2026-05-20

## 全量汇总

| 指标 | 数值 |
|------|------|
| 总对话数 | 1,434 |
| Input tokens | 9.2K |
| Output tokens | 1.10M |
| Cache 写入 | 6.48M |
| Cache 读取 | 324.63M |
| 总 tokens | 332.22M |
| **估算总费用** | **$521.63** |

## 按月统计

| 月份      | Input | Output | CacheW | CacheR  | Total   | 对话数  | 费用      |
| ------- | ----- | ------ | ------ | ------- | ------- | ---- | ------- |
| 2026-05 |  9.2K |  1.10M |  6.48M | 324.63M | 332.22M | 1434 | $521.61 |

## 按工具统计

| 工具          | Input | Output | CacheW | CacheR  | Total   | 对话数  | 费用      |
| ----------- | ----- | ------ | ------ | ------- | ------- | ---- | ------- |
| claude      |  4.9K | 421.5K |  3.20M | 185.93M | 189.56M |  344 | $294.88 |
| Claude Code |  4.3K | 678.9K |  3.29M | 138.70M | 142.67M | 1090 | $226.73 |

## 按模型统计

| 模型                | Input | Output | CacheW | CacheR  | Total   | 对话数 | 费用      |
| ----------------- | ----- | ------ | ------ | ------- | ------- | --- | ------- |
| claude-opus-4-7   |  5.2K | 631.5K |  1.30M | 271.63M | 273.57M | 899 | $479.24 |
| claude-sonnet-4-6 |  4.0K | 469.0K |  5.18M |  53.00M |  58.65M | 535 |  $42.37 |

---

> 费用为估算值，基于 [Anthropic](https://www.anthropic.com/pricing) / [OpenAI](https://openai.com/api/pricing/) 官方定价。
> 数据通过 [TokenTracker](https://github.com/mm7894215/TokenTracker) 收集，由本项目 sync.py 定期备份到 GitHub。
