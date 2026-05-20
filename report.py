#!/usr/bin/env python3
"""
从 data/requests.ndjson 读取历史数据，生成 README.md。
在 GitHub Actions 里自动运行，也可以本地执行。
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

REPO_DIR  = Path(__file__).parent
DATA_FILE = REPO_DIR / "data" / "requests.ndjson"

PRICING = {
    "claude-opus-4-7":           {"input": 15.00, "output": 75.00, "cache_write": 18.75, "cache_read": 1.50},
    "claude-opus-4-5":           {"input": 15.00, "output": 75.00, "cache_write": 18.75, "cache_read": 1.50},
    "claude-sonnet-4-6":         {"input":  3.00, "output": 15.00, "cache_write":  3.75, "cache_read": 0.30},
    "claude-sonnet-4-5":         {"input":  3.00, "output": 15.00, "cache_write":  3.75, "cache_read": 0.30},
    "claude-haiku-4-5-20251001": {"input":  0.80, "output":  4.00, "cache_write":  1.00, "cache_read": 0.08},
    "claude-haiku-4-5":          {"input":  0.80, "output":  4.00, "cache_write":  1.00, "cache_read": 0.08},
}

def get_price(model, kind):
    if model in PRICING:
        return PRICING[model].get(kind, 0.0)
    for key, prices in PRICING.items():
        if model.startswith(key.split("-20")[0]):
            return prices.get(kind, 0.0)
    return 0.0

def calc_cost(rec):
    m = 1_000_000
    return (
        rec["input_tokens"]       * get_price(rec["model"], "input")       / m +
        rec["output_tokens"]      * get_price(rec["model"], "output")      / m +
        rec["cache_write_tokens"] * get_price(rec["model"], "cache_write") / m +
        rec["cache_read_tokens"]  * get_price(rec["model"], "cache_read")  / m
    )

def fmt_tokens(n):
    if n >= 1_000_000: return f"{n/1_000_000:.2f}M"
    if n >= 1_000:     return f"{n/1_000:.1f}K"
    return str(n)

def fmt_cost(c):
    return f"${c:.2f}" if c >= 0.01 else f"${c:.4f}"

def load_records():
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


def make_table(headers, rows):
    widths = [max(len(str(r[i])) for r in ([headers] + rows)) for i in range(len(headers))]
    sep    = "| " + " | ".join("-" * w for w in widths) + " |"
    header = "| " + " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers)) + " |"
    lines  = [header, sep]
    for row in rows:
        lines.append("| " + " | ".join(str(row[i]).rjust(widths[i]) for i in range(len(row))) + " |")
    return "\n".join(lines)


def generate_readme(records):
    if not records:
        return "# Token Tracker\n\n暂无数据。\n"

    # ── 全量汇总 ──
    total = {"input": 0, "output": 0, "cw": 0, "cr": 0, "cost": 0.0, "req": 0}
    for r in records:
        total["input"]  += r["input_tokens"]
        total["output"] += r["output_tokens"]
        total["cw"]     += r["cache_write_tokens"]
        total["cr"]     += r["cache_read_tokens"]
        total["cost"]   += calc_cost(r)
        total["req"]    += 1
    total_tokens = total["input"] + total["output"] + total["cw"] + total["cr"]

    # ── 按月汇总 ──
    monthly = defaultdict(lambda: {"input": 0, "output": 0, "cw": 0, "cr": 0, "cost": 0.0, "req": 0})
    for r in records:
        m = r["date"][:7]
        monthly[m]["input"]  += r["input_tokens"]
        monthly[m]["output"] += r["output_tokens"]
        monthly[m]["cw"]     += r["cache_write_tokens"]
        monthly[m]["cr"]     += r["cache_read_tokens"]
        monthly[m]["cost"]   += calc_cost(r)
        monthly[m]["req"]    += 1

    monthly_rows = []
    for month in sorted(monthly.keys(), reverse=True):
        a = monthly[month]
        t = a["input"] + a["output"] + a["cw"] + a["cr"]
        monthly_rows.append([month, fmt_tokens(a["input"]), fmt_tokens(a["output"]),
                              fmt_tokens(a["cw"]), fmt_tokens(a["cr"]),
                              fmt_tokens(t), a["req"], fmt_cost(a["cost"])])

    # ── 按项目汇总 ──
    by_proj = defaultdict(lambda: {"input": 0, "output": 0, "cw": 0, "cr": 0, "cost": 0.0, "req": 0})
    for r in records:
        p = by_proj[r["project"]]
        p["input"]  += r["input_tokens"]
        p["output"] += r["output_tokens"]
        p["cw"]     += r["cache_write_tokens"]
        p["cr"]     += r["cache_read_tokens"]
        p["cost"]   += calc_cost(r)
        p["req"]    += 1

    proj_rows = sorted(by_proj.items(), key=lambda x: x[1]["cost"], reverse=True)
    proj_table_rows = [
        [p, fmt_tokens(a["input"]), fmt_tokens(a["output"]),
         fmt_tokens(a["cw"]), fmt_tokens(a["cr"]),
         fmt_tokens(a["input"]+a["output"]+a["cw"]+a["cr"]),
         a["req"], fmt_cost(a["cost"])]
        for p, a in proj_rows
    ]

    # ── 按模型汇总 ──
    by_model = defaultdict(lambda: {"input": 0, "output": 0, "cw": 0, "cr": 0, "cost": 0.0, "req": 0})
    for r in records:
        m = by_model[r["model"]]
        m["input"]  += r["input_tokens"]
        m["output"] += r["output_tokens"]
        m["cw"]     += r["cache_write_tokens"]
        m["cr"]     += r["cache_read_tokens"]
        m["cost"]   += calc_cost(r)
        m["req"]    += 1

    model_rows = sorted(by_model.items(), key=lambda x: x[1]["cost"], reverse=True)
    model_table_rows = [
        [m, fmt_tokens(a["input"]), fmt_tokens(a["output"]),
         fmt_tokens(a["cw"]), fmt_tokens(a["cr"]),
         fmt_tokens(a["input"]+a["output"]+a["cw"]+a["cr"]),
         a["req"], fmt_cost(a["cost"])]
        for m, a in model_rows
    ]

    date_range = f"{min(r['date'] for r in records)} ~ {max(r['date'] for r in records)}"
    updated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    headers = ["Input", "Output", "CacheW", "CacheR", "Total", "请求数", "费用"]

    readme = f"""# Token Tracker

自动追踪 Claude Code 的 token 用量与费用估算。

> 最后更新：{updated_at} | 数据范围：{date_range}

## 全量汇总

| 指标 | 数值 |
|------|------|
| 总请求数 | {total["req"]:,} |
| Input tokens | {fmt_tokens(total["input"])} |
| Output tokens | {fmt_tokens(total["output"])} |
| Cache 写入 | {fmt_tokens(total["cw"])} |
| Cache 读取 | {fmt_tokens(total["cr"])} |
| 总 tokens | {fmt_tokens(total_tokens)} |
| **估算总费用** | **{fmt_cost(total["cost"])}** |

## 按月统计

{make_table(["月份"] + headers, monthly_rows)}

## 按项目统计

{make_table(["项目"] + headers, proj_table_rows)}

## 按模型统计

{make_table(["模型"] + headers, model_table_rows)}

---

> 费用为估算值，基于 [Anthropic 官方定价](https://www.anthropic.com/pricing)。
> 数据来源：本地 `~/.claude/projects/` 会话记录，通过 `sync.py` 定期同步。
"""
    return readme


def main():
    print("读取数据...")
    records = load_records()
    print(f"  共 {len(records)} 条记录")

    print("生成 README.md...")
    readme = generate_readme(records)

    readme_path = REPO_DIR / "README.md"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme)

    print(f"  已写入 {readme_path}")


if __name__ == "__main__":
    main()
