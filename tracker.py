#!/usr/bin/env python3
"""Token usage tracker for Claude Code and other AI coding tools."""

import json
import os
import sys
import argparse
import socket
import subprocess
import platform
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

def _canonical_device() -> str:
    """与 sync.py 保持一致：macOS 优先用 scutil LocalHostName（跨网络稳定）。"""
    if platform.system() == "Darwin":
        try:
            name = subprocess.check_output(
                ["scutil", "--get", "LocalHostName"],
                stderr=subprocess.DEVNULL, timeout=2,
            ).decode().strip()
            if name:
                return name + ".local"
        except (subprocess.SubprocessError, FileNotFoundError, OSError):
            pass
    h = socket.gethostname()
    if "MacBook" in h or h.startswith("Mac.") or h == "Mac":
        return "Jerrys-MacBook-Pro-403.local"
    if platform.system() == "Darwin":
        return "Jerrys-MacBook-Pro-403.local"
    return h


DEVICE = _canonical_device()

# ── Pricing (USD per 1M tokens) ──────────────────────────────────────────────
PRICING = {
    # Claude Opus 4
    "claude-opus-4-7":   {"input": 15.00, "output": 75.00, "cache_write": 18.75, "cache_read": 1.50},
    "claude-opus-4-6":   {"input": 15.00, "output": 75.00, "cache_write": 18.75, "cache_read": 1.50},
    "claude-opus-4-5":   {"input": 15.00, "output": 75.00, "cache_write": 18.75, "cache_read": 1.50},
    # Claude Sonnet 4
    "claude-sonnet-4-6": {"input":  3.00, "output": 15.00, "cache_write":  3.75, "cache_read": 0.30},
    "claude-sonnet-4-5": {"input":  3.00, "output": 15.00, "cache_write":  3.75, "cache_read": 0.30},
    # Claude Haiku 4
    "claude-haiku-4-5-20251001": {"input": 0.80, "output": 4.00, "cache_write": 1.00, "cache_read": 0.08},
    "claude-haiku-4-5": {"input": 0.80, "output": 4.00, "cache_write": 1.00, "cache_read": 0.08},
    # Gemini models
    "gemini-3.5-flash": {"input": 1.50, "output": 9.00,  "cache_write": 0.375,   "cache_read": 0.15},
    "gemini-3.1-pro":   {"input": 1.25, "output": 5.00,  "cache_write": 0.3125,  "cache_read": 0.125},
    "gemini-2.5-pro":   {"input": 1.25, "output": 5.00,  "cache_write": 0.3125,  "cache_read": 0.125},
    "gemini-2.5-flash": {"input": 0.30, "output": 2.50,  "cache_write": 0.075,   "cache_read": 0.03},
    "gemini-2.0-pro":   {"input": 1.25, "output": 5.00,  "cache_write": 0.3125,  "cache_read": 0.125},
    "gemini-2.0-flash": {"input": 0.075,"output": 0.30,  "cache_write": 0.01875, "cache_read": 0.01875},
}

import re as _re

def _normalize_model(model: str) -> str:
    """Normalize model name: replace dots between digits only when they appear
    at the end of the string (version suffix), e.g. claude-opus-4.6 → claude-opus-4-6.
    Leaves family-name dots like gemini-3.5-flash untouched.
    """
    return _re.sub(r'(?<=\d)\.(?=\d+$)', '-', model)


def get_price(model: str, kind: str) -> float:
    """Return price per 1M tokens for a model+kind, falling back to family match."""
    model = _normalize_model(model)
    if model in PRICING:
        return PRICING[model].get(kind, 0.0)
    # Fuzzy family match
    for key, prices in PRICING.items():
        if model.startswith(key) or key.startswith(model.split("-20")[0]):
            return prices.get(kind, 0.0)
    # Unknown model — return 0 rather than crash
    return 0.0


# ── Data structures ───────────────────────────────────────────────────────────
@dataclass
class UsageRecord:
    timestamp: datetime
    project: str
    session_id: str
    model: str
    device: str = "unknown"
    input_tokens: int = 0
    output_tokens: int = 0
    cache_write_tokens: int = 0
    cache_read_tokens: int = 0

    @property
    def cost(self) -> float:
        m = 1_000_000
        return (
            self.input_tokens      * get_price(self.model, "input")       / m +
            self.output_tokens     * get_price(self.model, "output")      / m +
            self.cache_write_tokens * get_price(self.model, "cache_write") / m +
            self.cache_read_tokens  * get_price(self.model, "cache_read")  / m
        )

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens + self.cache_write_tokens + self.cache_read_tokens


@dataclass
class AggRow:
    input_tokens: int = 0
    output_tokens: int = 0
    cache_write_tokens: int = 0
    cache_read_tokens: int = 0
    cost: float = 0.0
    requests: int = 0

    def add(self, rec: UsageRecord):
        self.input_tokens      += rec.input_tokens
        self.output_tokens     += rec.output_tokens
        self.cache_write_tokens += rec.cache_write_tokens
        self.cache_read_tokens  += rec.cache_read_tokens
        self.cost              += rec.cost
        self.requests          += 1

    @property
    def total_tokens(self):
        return self.input_tokens + self.output_tokens + self.cache_write_tokens + self.cache_read_tokens


# ── Claude Code parser ────────────────────────────────────────────────────────
CLAUDE_DIR = Path.home() / ".claude" / "projects"

def project_slug_to_name(slug: str) -> str:
    """Convert -Users-foo-bar-project to ~/bar/project."""
    path = slug.replace("-", "/").lstrip("/")
    home = str(Path.home()).lstrip("/")
    if path.startswith(home):
        path = "~" + path[len(home):]
    # Keep only last 2 components for readability
    parts = path.split("/")
    return "/".join(parts[-2:]) if len(parts) > 2 else path

TT_QUEUE   = Path.home() / ".tokentracker" / "tracker" / "queue.jsonl"

def parse_antigravity_sessions(since: Optional[datetime] = None) -> list[UsageRecord]:
    records: list[UsageRecord] = []
    if not TT_QUEUE.exists():
        return records

    try:
        with open(TT_QUEUE, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if rec.get("source") != "antigravity":
                    continue

                # Parse timestamp from hour_start
                hour_start = rec.get("hour_start")
                if not hour_start:
                    continue
                try:
                    ts = datetime.fromisoformat(hour_start.replace("Z", "+00:00"))
                except ValueError:
                    ts = datetime.now(timezone.utc)

                if since and ts < since:
                    continue

                # Check for zero tokens
                if (rec.get("input_tokens", 0) == 0
                        and rec.get("cached_input_tokens", 0) == 0
                        and rec.get("cache_creation_input_tokens", 0) == 0
                        and rec.get("output_tokens", 0) == 0):
                    continue

                urec = UsageRecord(
                    timestamp=ts,
                    project="Antigravity Workspace",
                    session_id="hourly-bucket",
                    model=rec.get("model", "unknown"),
                    device=rec.get("device", DEVICE),
                    input_tokens=rec.get("input_tokens", 0),
                    output_tokens=rec.get("output_tokens", 0),
                    cache_write_tokens=rec.get("cache_creation_input_tokens", 0),
                    cache_read_tokens=rec.get("cached_input_tokens", 0),
                )
                records.append(urec)
    except Exception as e:
        print(f"  解析 TokenTracker 队列时出错: {e}")

    return records


def parse_claude_sessions(since: Optional[datetime] = None) -> list[UsageRecord]:
    records: list[UsageRecord] = []
    if not CLAUDE_DIR.exists():
        return records

    seen_msg_ids: set = set()  # 按 message.id 去重

    for project_dir in CLAUDE_DIR.iterdir():
        if not project_dir.is_dir():
            continue
        project_name = project_slug_to_name(project_dir.name)
        for jsonl_file in project_dir.glob("*.jsonl"):
            session_id = jsonl_file.stem
            try:
                with open(jsonl_file, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            entry = json.loads(line)
                        except json.JSONDecodeError:
                            continue

                        msg = entry.get("message", {})
                        if msg.get("role") != "assistant":
                            continue
                        usage = msg.get("usage")
                        if not usage:
                            continue
                        model = msg.get("model", "unknown")
                        # 跳过无实际 token 的合成条目
                        if not model or model.startswith("<") or (
                            usage.get("input_tokens", 0) == 0
                            and usage.get("output_tokens", 0) == 0
                            and usage.get("cache_creation_input_tokens", 0) == 0
                            and usage.get("cache_read_input_tokens", 0) == 0
                        ):
                            continue

                        # 同一条消息可能在 JSONL 里出现多次，只取第一次
                        msg_id = msg.get("id")
                        if msg_id and msg_id in seen_msg_ids:
                            continue
                        if msg_id:
                            seen_msg_ids.add(msg_id)

                        ts_str = entry.get("timestamp")
                        if ts_str:
                            try:
                                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                            except ValueError:
                                ts = datetime.now(timezone.utc)
                        else:
                            ts = datetime.now(timezone.utc)

                        if since and ts < since:
                            continue

                        rec = UsageRecord(
                            timestamp=ts,
                            project=project_name,
                            session_id=session_id,
                            model=model,
                            device=DEVICE,
                            input_tokens=usage.get("input_tokens", 0),
                            output_tokens=usage.get("output_tokens", 0),
                            cache_write_tokens=usage.get("cache_creation_input_tokens", 0),
                            cache_read_tokens=usage.get("cache_read_input_tokens", 0),
                        )
                        records.append(rec)
            except (OSError, PermissionError):
                continue

    return records


# ── Display helpers ───────────────────────────────────────────────────────────
try:
    from rich.console import Console
    from rich.table import Table
    from rich import box
    HAS_RICH = True
    console = Console()
except ImportError:
    HAS_RICH = False

def fmt_tokens(n: int) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.2f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)

def fmt_cost(c: float) -> str:
    if c < 0.01:
        return f"${c:.4f}"
    return f"${c:.2f}"

def print_table_plain(title: str, headers: list[str], rows: list[list]):
    print(f"\n{'─'*60}")
    print(f"  {title}")
    print(f"{'─'*60}")
    widths = [max(len(str(r[i])) for r in ([headers] + rows)) for i in range(len(headers))]
    fmt = "  " + "  ".join(f"{{:<{w}}}" for w in widths)
    print(fmt.format(*headers))
    print("  " + "  ".join("─" * w for w in widths))
    for row in rows:
        print(fmt.format(*[str(x) for x in row]))

def print_table(title: str, headers: list[str], rows: list[list]):
    if not HAS_RICH:
        print_table_plain(title, headers, rows)
        return
    t = Table(title=title, box=box.SIMPLE_HEAD, show_edge=False)
    right_cols = {"Input", "Output", "CacheW", "CacheR", "Total", "Requests", "Cost"}
    for h in headers:
        t.add_column(h, justify="right" if h in right_cols else "left")
    for row in rows:
        t.add_row(*[str(x) for x in row])
    console.print(t)


# ── Views ─────────────────────────────────────────────────────────────────────
def view_daily(records: list[UsageRecord], days: int):
    agg: dict[str, AggRow] = defaultdict(AggRow)
    for r in records:
        day = r.timestamp.astimezone().strftime("%Y-%m-%d")
        agg[day].add(r)

    rows = []
    for day in sorted(agg.keys(), reverse=True)[:days]:
        a = agg[day]
        rows.append([day, fmt_tokens(a.input_tokens), fmt_tokens(a.output_tokens),
                     fmt_tokens(a.cache_write_tokens), fmt_tokens(a.cache_read_tokens),
                     fmt_tokens(a.total_tokens), a.requests, fmt_cost(a.cost)])

    print_table("Daily Usage", ["Date", "Input", "Output", "CacheW", "CacheR", "Total", "Requests", "Cost"], rows)


def view_projects(records: list[UsageRecord]):
    agg: dict[str, AggRow] = defaultdict(AggRow)
    for r in records:
        agg[r.project].add(r)

    rows = sorted(agg.items(), key=lambda x: x[1].cost, reverse=True)
    table_rows = [[p, fmt_tokens(a.input_tokens), fmt_tokens(a.output_tokens),
                   fmt_tokens(a.cache_write_tokens), fmt_tokens(a.cache_read_tokens),
                   fmt_tokens(a.total_tokens), a.requests, fmt_cost(a.cost)]
                  for p, a in rows]
    print_table("By Project", ["Project", "Input", "Output", "CacheW", "CacheR", "Total", "Requests", "Cost"], table_rows)


def view_models(records: list[UsageRecord]):
    agg: dict[str, AggRow] = defaultdict(AggRow)
    for r in records:
        agg[r.model].add(r)

    rows = sorted(agg.items(), key=lambda x: x[1].cost, reverse=True)
    table_rows = [[m, fmt_tokens(a.input_tokens), fmt_tokens(a.output_tokens),
                   fmt_tokens(a.cache_write_tokens), fmt_tokens(a.cache_read_tokens),
                   fmt_tokens(a.total_tokens), a.requests, fmt_cost(a.cost)]
                  for m, a in rows]
    print_table("By Model", ["Model", "Input", "Output", "CacheW", "CacheR", "Total", "Requests", "Cost"], table_rows)


def view_devices(records: list[UsageRecord]):
    agg: dict[str, AggRow] = defaultdict(AggRow)
    for r in records:
        agg[r.device].add(r)

    rows = sorted(agg.items(), key=lambda x: x[1].cost, reverse=True)
    table_rows = [[d, fmt_tokens(a.input_tokens), fmt_tokens(a.output_tokens),
                   fmt_tokens(a.cache_write_tokens), fmt_tokens(a.cache_read_tokens),
                   fmt_tokens(a.total_tokens), a.requests, fmt_cost(a.cost)]
                  for d, a in rows]
    print_table("By Device", ["Device", "Input", "Output", "CacheW", "CacheR", "Total", "Requests", "Cost"], table_rows)


def view_summary(records: list[UsageRecord]):
    total = AggRow()
    for r in records:
        total.add(r)

    print(f"\n  Total requests  : {total.requests:,}")
    print(f"  Input tokens    : {fmt_tokens(total.input_tokens)}")
    print(f"  Output tokens   : {fmt_tokens(total.output_tokens)}")
    print(f"  Cache write     : {fmt_tokens(total.cache_write_tokens)}")
    print(f"  Cache read      : {fmt_tokens(total.cache_read_tokens)}")
    print(f"  Total tokens    : {fmt_tokens(total.total_tokens)}")
    print(f"  Estimated cost  : {fmt_cost(total.cost)}")
    print()


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Track token usage across AI coding tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tracker.py                  # Last 7 days summary
  python tracker.py --days 30        # Last 30 days
  python tracker.py --today          # Today only
  python tracker.py --all            # All time
  python tracker.py --projects       # Break down by project
  python tracker.py --models         # Break down by model
  python tracker.py --projects --models --days 30
        """,
    )
    parser.add_argument("--days",     type=int, default=7,  help="Show last N days (default: 7)")
    parser.add_argument("--today",    action="store_true",  help="Today only")
    parser.add_argument("--all",      action="store_true",  help="All time (ignores --days)")
    parser.add_argument("--projects", action="store_true",  help="Show breakdown by project")
    parser.add_argument("--models",   action="store_true",  help="Show breakdown by model")
    parser.add_argument("--devices",  action="store_true",  help="Show breakdown by device")
    args = parser.parse_args()

    # Determine time window
    now = datetime.now(timezone.utc)
    if args.all:
        since = None
        window_label = "all time"
    elif args.today:
        local_today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        since = local_today.astimezone(timezone.utc)
        window_label = "today"
    else:
        since = now - timedelta(days=args.days)
        window_label = f"last {args.days} days"

    print(f"\n  AI Token Tracker — {window_label}")
    print(f"  Source: Claude Code ({CLAUDE_DIR}) & Antigravity ({TT_QUEUE if TT_QUEUE.exists() else 'not found'})")

    records = parse_claude_sessions(since=since)
    antigravity_records = parse_antigravity_sessions(since=since)
    records.extend(antigravity_records)

    if not records:
        print("\n  No usage data found for this period.\n")
        return

    view_summary(records)
    view_daily(records, days=9999 if args.all else (1 if args.today else args.days))

    if args.projects:
        view_projects(records)

    if args.models:
        view_models(records)

    if args.devices:
        view_devices(records)

    if not args.projects and not args.models and not args.devices:
        # Always show models in default view as a bonus
        view_models(records)


if __name__ == "__main__":
    main()
