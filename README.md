# Token Tracker

自动追踪 AI 编程工具的 token 用量与费用估算。

> 数据来源：Claude Code
> 最后更新：2026-05-20 01:08 UTC | 数据范围：2026-05-19 ~ 2026-05-20

## 全量汇总

| 指标 | 数值 |
|------|------|
| 总对话数 | 1,086 |
| Input tokens | 4.3K |
| Output tokens | 677.0K |
| Cache 写入 | 3.28M |
| Cache 读取 | 138.31M |
| 总 tokens | 142.27M |
| **估算总费用** | **$226.58** |

## 按月统计

| 月份      | Input | Output | CacheW | CacheR  | Total   | 对话数  | 费用      |
| ------- | ----- | ------ | ------ | ------- | ------- | ---- | ------- |
| 2026-05 |  4.3K | 677.0K |  3.28M | 138.31M | 142.27M | 1086 | $226.57 |

## 按工具统计

| 工具          | Input | Output | CacheW | CacheR  | Total   | 对话数  | 费用      |
| ----------- | ----- | ------ | ------ | ------- | ------- | ---- | ------- |
| Claude Code |  4.3K | 677.0K |  3.28M | 138.31M | 142.27M | 1086 | $226.57 |

## 按模型统计

| 模型                | Input | Output | CacheW | CacheR  | Total   | 对话数 | 费用      |
| ----------------- | ----- | ------ | ------ | ------- | ------- | --- | ------- |
| claude-opus-4-7   |  1.9K | 393.7K | 597.2K | 108.34M | 109.33M | 555 | $203.26 |
| claude-sonnet-4-6 |  2.4K | 283.3K |  2.69M |  29.97M |  32.94M | 531 |  $23.31 |

---

> 费用为估算值，基于 [Anthropic](https://www.anthropic.com/pricing) / [OpenAI](https://openai.com/api/pricing/) 官方定价。
> 数据通过 [TokenTracker](https://github.com/mm7894215/TokenTracker) 收集，由本项目 sync.py 定期备份到 GitHub。
