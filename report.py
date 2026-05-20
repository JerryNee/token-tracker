#!/usr/bin/env python3
"""
从 data/usage.ndjson 生成 README.md 报告。
在 GitHub Actions 里自动运行，也可本地执行。
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

REPO_DIR  = Path(__file__).parent
DATA_FILE = REPO_DIR / "data" / "usage.ndjson"

# ── 定价（USD / 1M tokens）──────────────────────────────────────────────────
PRICING = {
    "claude-opus-4-7":           {"input": 15.00, "output": 75.00, "cache_write": 18.75, "cache_read": 1.50},
    "claude-opus-4-5":           {"input": 15.00, "output": 75.00, "cache_write": 18.75, "cache_read": 1.50},
    "claude-sonnet-4-6":         {"input":  3.00, "output": 15.00, "cache_write":  3.75, "cache_read": 0.30},
    "claude-sonnet-4-5":         {"input":  3.00, "output": 15.00, "cache_write":  3.75, "cache_read": 0.30},
    "claude-haiku-4-5-20251001": {"input":  0.80, "output":  4.00, "cache_write":  1.00, "cache_read": 0.08},
    "claude-haiku-4-5":          {"input":  0.80, "output":  4.00, "cache_write":  1.00, "cache_read": 0.08},
    # Cursor / GPT 系列（粗略估算）
    "gpt-4o":                    {"input":  2.50, "output": 10.00, "cache_write":  0.00, "cache_read": 1.25},
    "gpt-4o-mini":               {"input":  0.15, "output":  0.60, "cache_write":  0.00, "cache_read": 0.075},
    "gpt-4.1":                   {"input":  2.00, "output":  8.00, "cache_write":  0.00, "cache_read": 0.50},
    "gpt-4.1-mini":              {"input":  0.40, "output":  1.60, "cache_write":  0.00, "cache_read": 0.10},
    "o3":                        {"input": 10.00, "output": 40.00, "cache_write":  0.00, "cache_read": 2.50},
    "o4-mini":                   {"input":  1.10, "output":  4.40, "cache_write":  0.00, "cache_read": 0.275},
}

# 工具来源的中文名
SOURCE_NAMES = {
    "claude-code":  "Claude Code",
    "cursor":       "Cursor",
    "copilot":      "GitHub Copilot",
    "gemini":       "Gemini CLI",
    "codex":        "Codex CLI",
    "every-code":   "Every Code",
    "opencode":     "OpenCode",
    "kiro":         "Kiro",
    "kimi":         "Kimi Code",
    "hermes":       "Hermes",
}


def get_price(model: str, kind: str) -> float:
    if model in PRICING:
        return PRICING[model].get(kind, 0.0)
    for key, prices in PRICING.items():
        if model.startswith(key.split("-20")[0]):
            return prices.get(kind, 0.0)
    return 0.0


def calc_cost(rec: dict) -> float:
    m = 1_000_000
    model = rec["model"]
    return (
        rec.get("input_tokens", 0)                * get_price(model, "input")       / m +
        rec.get("output_tokens", 0)               * get_price(model, "output")      / m +
        rec.get("cache_creation_input_tokens", 0) * get_price(model, "cache_write") / m +
        rec.get("cached_input_tokens", 0)         * get_price(model, "cache_read")  / m
    )


def fmt_tokens(n: int) -> str:
    if n >= 1_000_000: return f"{n/1_000_000:.2f}M"
    if n >= 1_000:     return f"{n/1_000:.1f}K"
    return str(n)


def fmt_cost(c: float) -> str:
    return f"${c:.2f}" if c >= 0.01 else f"${c:.4f}"


def source_display(source: str) -> str:
    return SOURCE_NAMES.get(source, source)


def load_records() -> list:
    if not DATA_FILE.exists():
        return []
    records = []
    with open(DATA_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


def make_table(headers: list, rows: list) -> str:
    widths = [max(len(str(r[i])) for r in ([headers] + rows)) for i in range(len(headers))]
    sep    = "| " + " | ".join("-" * w for w in widths) + " |"
    header = "| " + " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers)) + " |"
    lines  = [header, sep]
    for row in rows:
        cells = []
        for i, v in enumerate(row):
            s = str(v)
            # 数字右对齐，文字左对齐
            if i == 0:
                cells.append(s.ljust(widths[i]))
            else:
                cells.append(s.rjust(widths[i]))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def generate_readme(records: list) -> str:
    if not records:
        return "# Token Tracker\n\n暂无数据。\n"

    # ── 全量汇总 ──
    total_input = total_output = total_cw = total_cr = total_cost = total_conv = 0
    for r in records:
        total_input  += r.get("input_tokens", 0)
        total_output += r.get("output_tokens", 0)
        total_cw     += r.get("cache_creation_input_tokens", 0)
        total_cr     += r.get("cached_input_tokens", 0)
        total_cost   += calc_cost(r)
        total_conv   += r.get("conversations", 0)
    total_tokens = total_input + total_output + total_cw + total_cr

    # ── 按月汇总 ──
    monthly = defaultdict(lambda: defaultdict(int))
    for r in records:
        m = r["hour_start"][:7]
        monthly[m]["input"]  += r.get("input_tokens", 0)
        monthly[m]["output"] += r.get("output_tokens", 0)
        monthly[m]["cw"]     += r.get("cache_creation_input_tokens", 0)
        monthly[m]["cr"]     += r.get("cached_input_tokens", 0)
        monthly[m]["conv"]   += r.get("conversations", 0)
        monthly[m]["cost_x1000"] += int(calc_cost(r) * 1000)  # 避免浮点累加误差

    monthly_rows = []
    for month in sorted(monthly.keys(), reverse=True):
        a = monthly[month]
        t = a["input"] + a["output"] + a["cw"] + a["cr"]
        cost = a["cost_x1000"] / 1000
        monthly_rows.append([month, fmt_tokens(a["input"]), fmt_tokens(a["output"]),
                              fmt_tokens(a["cw"]), fmt_tokens(a["cr"]),
                              fmt_tokens(t), a["conv"], fmt_cost(cost)])

    # ── 按工具来源汇总 ──
    by_source = defaultdict(lambda: defaultdict(int))
    for r in records:
        s = by_source[source_display(r["source"])]
        s["input"]  += r.get("input_tokens", 0)
        s["output"] += r.get("output_tokens", 0)
        s["cw"]     += r.get("cache_creation_input_tokens", 0)
        s["cr"]     += r.get("cached_input_tokens", 0)
        s["conv"]   += r.get("conversations", 0)
        s["cost_x1000"] += int(calc_cost(r) * 1000)

    source_rows = sorted(by_source.items(), key=lambda x: x[1]["cost_x1000"], reverse=True)
    source_table = [
        [name, fmt_tokens(a["input"]), fmt_tokens(a["output"]),
         fmt_tokens(a["cw"]), fmt_tokens(a["cr"]),
         fmt_tokens(a["input"]+a["output"]+a["cw"]+a["cr"]),
         a["conv"], fmt_cost(a["cost_x1000"]/1000)]
        for name, a in source_rows
    ]

    # ── 按模型汇总 ──
    by_model = defaultdict(lambda: defaultdict(int))
    for r in records:
        m = by_model[r["model"]]
        m["input"]  += r.get("input_tokens", 0)
        m["output"] += r.get("output_tokens", 0)
        m["cw"]     += r.get("cache_creation_input_tokens", 0)
        m["cr"]     += r.get("cached_input_tokens", 0)
        m["conv"]   += r.get("conversations", 0)
        m["cost_x1000"] += int(calc_cost(r) * 1000)

    model_rows = sorted(by_model.items(), key=lambda x: x[1]["cost_x1000"], reverse=True)
    model_table = [
        [m, fmt_tokens(a["input"]), fmt_tokens(a["output"]),
         fmt_tokens(a["cw"]), fmt_tokens(a["cr"]),
         fmt_tokens(a["input"]+a["output"]+a["cw"]+a["cr"]),
         a["conv"], fmt_cost(a["cost_x1000"]/1000)]
        for m, a in model_rows
    ]

    headers = ["Input", "Output", "CacheW", "CacheR", "Total", "对话数", "费用"]
    date_range  = f"{records[0]['hour_start'][:10]} ~ {records[-1]['hour_start'][:10]}"
    updated_at  = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    sources_str = "、".join(sorted({source_display(r["source"]) for r in records}))

    return f"""# Token Tracker

自动追踪 AI 编程工具的 token 用量与费用估算。

> 数据来源：{sources_str}
> 最后更新：{updated_at} | 数据范围：{date_range}

## 全量汇总

| 指标 | 数值 |
|------|------|
| 总对话数 | {total_conv:,} |
| Input tokens | {fmt_tokens(total_input)} |
| Output tokens | {fmt_tokens(total_output)} |
| Cache 写入 | {fmt_tokens(total_cw)} |
| Cache 读取 | {fmt_tokens(total_cr)} |
| 总 tokens | {fmt_tokens(total_tokens)} |
| **估算总费用** | **{fmt_cost(total_cost)}** |

## 按月统计

{make_table(["月份"] + headers, monthly_rows)}

## 按工具统计

{make_table(["工具"] + headers, source_table)}

## 按模型统计

{make_table(["模型"] + headers, model_table)}

---

> 费用为估算值，基于 [Anthropic](https://www.anthropic.com/pricing) / [OpenAI](https://openai.com/api/pricing/) 官方定价。
> 数据来源：`~/.claude/projects/` 会话文件，由 sync.py 每日自动备份。
"""


def main():
    print("读取数据...")
    records = load_records()
    print(f"  共 {len(records)} 条小时记录")

    print("生成 README.md...")
    readme = generate_readme(records)

    readme_path = REPO_DIR / "README.md"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme)
    print(f"  已写入 {readme_path}")


if __name__ == "__main__":
    main()
