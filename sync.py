#!/usr/bin/env python3
"""
同步 Claude Code / Codex / Antigravity token 使用数据到 data/usage.ndjson，并推送到 GitHub。
直接读取本地会话文件，按小时聚合后备份。
"""

import json
import subprocess
import sys
import socket
import platform
import os
from pathlib import Path
from datetime import datetime, timezone
import re as _re

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def _canonical_device() -> str:
    """Hostname 在不同网络下会变 (Mac.mshome.net, wirelessprv-…illinois.edu, …)，
    导致同小时桶按 device 拆成两条 → 双重计数。
    优先用 macOS 的 LocalHostName（与网络无关），兜底再用 hostname 关键词匹配。"""
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

PRICING = {
    # Claude Fable 5
    "claude-fable-5":   {"input": 10.00, "output": 50.00, "cache_write": 12.50, "cache_read": 1.00},
    # Claude Opus 4
    "claude-opus-4-8":   {"input":  5.00, "output": 25.00, "cache_write":  6.25, "cache_read": 0.50},
    "claude-opus-4-7":   {"input":  5.00, "output": 25.00, "cache_write":  6.25, "cache_read": 0.50},
    "claude-opus-4-6":   {"input":  5.00, "output": 25.00, "cache_write":  6.25, "cache_read": 0.50},
    "claude-opus-4-5":   {"input":  5.00, "output": 25.00, "cache_write":  6.25, "cache_read": 0.50},
    # Claude Sonnet 4
    "claude-sonnet-4-6": {"input":  3.00, "output": 15.00, "cache_write":  3.75, "cache_read": 0.30},
    "claude-sonnet-4-5": {"input":  3.00, "output": 15.00, "cache_write":  3.75, "cache_read": 0.30},
    # Claude Sonnet 5 — 引导价 $2/$10（至 2026-08-31），2026-09-01 起标准价 $3/$15。
    # 同一 model ID 分段计价示例：值为按 from 升序的档位列表，见 _price_row()。
    "claude-sonnet-5": [
        {"from": "2026-01-01", "input":  2.00, "output": 10.00, "cache_write":  2.50, "cache_read": 0.20},
        {"from": "2026-09-01", "input":  3.00, "output": 15.00, "cache_write":  3.75, "cache_read": 0.30},
    ],
    # Claude Haiku 4
    "claude-haiku-4-5":  {"input":  1.00, "output":  5.00, "cache_write":  1.25, "cache_read": 0.10},
    # OpenAI models
    "gpt-5.6-sol":       {"input":  5.00, "output": 30.00, "cache_write": 6.25,  "cache_read": 0.50},
    "gpt-5.6-terra":     {"input":  2.50, "output": 15.00, "cache_write": 3.125, "cache_read": 0.25},
    "gpt-5.6-luna":      {"input":  1.00, "output":  6.00, "cache_write": 1.25,  "cache_read": 0.10},
    "gpt-5.5":           {"input":  5.00, "output": 30.00, "cache_write": 0.00, "cache_read": 0.50},
    "gpt-5.4":           {"input":  2.50, "output": 15.00, "cache_write": 0.00, "cache_read": 0.25},
    "gpt-5.4-mini":      {"input":  0.75, "output":  4.50, "cache_write": 0.00, "cache_read": 0.075},
    "gpt-4o":           {"input":  2.50, "output": 10.00, "cache_write": 0.00, "cache_read": 1.25},
    "gpt-4o-mini":      {"input":  0.15, "output":  0.60, "cache_write": 0.00, "cache_read": 0.075},
    "gpt-4.1":          {"input":  2.00, "output":  8.00, "cache_write": 0.00, "cache_read": 0.50},
    "gpt-4.1-mini":     {"input":  0.40, "output":  1.60, "cache_write": 0.00, "cache_read": 0.10},
    "o3":               {"input": 10.00, "output": 40.00, "cache_write": 0.00, "cache_read": 2.50},
    "o4-mini":          {"input":  1.10, "output":  4.40, "cache_write": 0.00, "cache_read": 0.275},
    # Gemini models
    "gemini-3.5-flash": {"input": 1.50, "output": 9.00,  "cache_write": 0.375,   "cache_read": 0.15},
    "gemini-3.1-pro":   {"input": 2.00, "output": 12.00, "cache_write": 0.50,    "cache_read": 0.20},
    "gemini-2.5-pro":   {"input": 1.25, "output": 10.00, "cache_write": 0.3125,  "cache_read": 0.125},
    "gemini-2.5-flash": {"input": 0.30, "output": 2.50,  "cache_write": 0.075,   "cache_read": 0.03},
    "gemini-2.0-pro":   {"input": 1.25, "output": 5.00,  "cache_write": 0.3125,  "cache_read": 0.125},
    "gemini-2.0-flash": {"input": 0.075,"output": 0.30,  "cache_write": 0.01875, "cache_read": 0.01875},
}

def _normalize_model(model: str) -> str:
    """Normalize model name: replace dots between digits only when they appear
    at the end of the string (version suffix), e.g. claude-opus-4.6 → claude-opus-4-6.
    Leaves OpenAI/Gemini dots like gpt-5.5 and gemini-3.5-flash untouched.
    """
    if not model.startswith("claude-"):
        return model
    return _re.sub(r'(?<=\d)\.(?=\d+$)', '-', model)


def _price_row(model: str, when=None) -> dict:
    """Resolve the price dict for `model` effective at `when`.

    PRICING[model] is either a flat dict (one price for all time) or a list of
    effective-dated tiers [{"from": "YYYY-MM-DD", ...}, ...]. For a list we pick
    the tier whose `from` is the latest date <= `when`. `when` accepts an ISO
    string (e.g. hour_start), a datetime, or None (→ latest/current price).
    """
    model = _normalize_model(model)
    entry = PRICING.get(model)
    if entry is None:
        for key, val in PRICING.items():
            if model.startswith(key) or key.startswith(model.split("-20")[0]):
                entry = val
                break
    if entry is None:
        return {}
    if isinstance(entry, dict):
        return entry
    if when is None:
        day = "9999-12-31"
    elif isinstance(when, str):
        day = when[:10]
    else:
        day = when.strftime("%Y-%m-%d")
    tiers = sorted(entry, key=lambda t: t.get("from", ""))
    chosen = tiers[0]
    for t in tiers:
        if t.get("from", "") <= day:
            chosen = t
        else:
            break
    return chosen


def get_price(model: str, kind: str, when=None) -> float:
    return _price_row(model, when).get(kind, 0.0)


def calc_cost(rec: dict) -> float:
    m = 1_000_000
    model = rec.get("model", "")
    when = rec.get("hour_start")
    return (
        rec.get("input_tokens", 0)                * get_price(model, "input",       when) / m +
        rec.get("output_tokens", 0)               * get_price(model, "output",      when) / m +
        rec.get("cache_creation_input_tokens", 0) * get_price(model, "cache_write", when) / m +
        rec.get("cached_input_tokens", 0)         * get_price(model, "cache_read",  when) / m
    )

def total_cost(records: dict) -> float:
    return sum(calc_cost(r) for r in records.values())

REPO_DIR   = Path(__file__).parent
DATA_FILE  = REPO_DIR / "data" / "usage.ndjson"
CLAUDE_DIR = Path.home() / ".claude" / "projects"
CODEX_DIR  = Path.home() / ".codex" / "sessions"
CODEX_CONFIG = Path.home() / ".codex" / "config.toml"
TT_QUEUE   = Path.home() / ".tokentracker" / "tracker" / "queue.jsonl"


# ── 读取已有备份 ──────────────────────────────────────────────────────────────
def load_existing() -> dict:
    existing = {}
    if not DATA_FILE.exists():
        return existing
    with open(DATA_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                # 早期 TokenTracker 集成阶段，claude-code 数据曾按 :30 分桶写入；
                # 当前 sync 始终用 :00，两者并存会双重计数 — 仅对 claude-code 丢弃 :30。
                # antigravity 的 :30 来自 TT_QUEUE 原文，是独立桶，必须保留。
                if rec.get("source") == "claude-code" and rec.get("hour_start", "")[14:16] != "00":
                    continue
                key = (rec["source"], rec["model"], rec["hour_start"], rec.get("device", "unknown"))
                existing[key] = rec
            except (json.JSONDecodeError, KeyError):
                continue
    return existing


# ── 解析 Antigravity 会话文件 (通过 TokenTracker) ─────────────────────────────
def parse_antigravity_sessions() -> list:
    if not TT_QUEUE.exists():
        print(f"  找不到 TokenTracker 队列数据: {TT_QUEUE}")
        return []

    print("  运行 TokenTracker sync...")
    try:
        if platform.system() == "Windows":
            # Windows 下 shell=True 会派生 cmd.exe，Python 的 timeout 只能杀死 cmd 而残留 node 子进程
            # 使用 taskkill /T 可以强制结束整个进程树，避免挂起和文件锁占用
            p = subprocess.Popen("npx tokentracker-cli sync --auto", shell=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            try:
                p.wait(timeout=30)
            except subprocess.TimeoutExpired:
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print("  TokenTracker sync 超时，已强制终止进程树。")
        else:
            subprocess.run(["npx", "-y", "tokentracker-cli", "sync", "--auto"], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30)
    except Exception as e:
        print(f"  TokenTracker sync 失败: {e}")

    records = []
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
                
                # 过滤出 source 为 antigravity 的记录
                if rec.get("source") != "antigravity":
                    continue
                
                # 跳过无 tokens 的记录
                if (rec.get("input_tokens", 0) == 0
                        and rec.get("cached_input_tokens", 0) == 0
                        and rec.get("cache_creation_input_tokens", 0) == 0
                        and rec.get("output_tokens", 0) == 0):
                    continue
                
                mapped = {
                    "source":                      "antigravity",
                    "model":                       rec.get("model", "unknown"),
                    "hour_start":                  rec.get("hour_start"),
                    "device":                      DEVICE,
                    "input_tokens":                rec.get("input_tokens", 0),
                    "cached_input_tokens":         rec.get("cached_input_tokens", 0),
                    "cache_creation_input_tokens": rec.get("cache_creation_input_tokens", 0),
                    "output_tokens":               rec.get("output_tokens", 0),
                    "total_tokens":                rec.get("total_tokens", 0),
                    "conversations":               rec.get("conversation_count", 0),
                }
                records.append(mapped)
    except Exception as e:
        print(f"  解析 TokenTracker 队列时出错: {e}")

    return records


# ── 解析 Claude Code 会话文件 ─────────────────────────────────────────────────
def parse_claude_sessions() -> list:
    if not CLAUDE_DIR.exists():
        print(f"  找不到 Claude 数据目录: {CLAUDE_DIR}")
        return []

    buckets: dict = {}
    seen_msg_ids: set = set()  # 按 message.id 去重，避免重复计数

    for project_dir in CLAUDE_DIR.iterdir():
        if not project_dir.is_dir():
            continue
        for jsonl_file in project_dir.glob("*.jsonl"):
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
                        if not model or model.startswith("<"):
                            continue

                        # 同一条消息在 JSONL 里可能出现多次，只取第一次
                        msg_id = msg.get("id")
                        if msg_id and msg_id in seen_msg_ids:
                            continue
                        if msg_id:
                            seen_msg_ids.add(msg_id)

                        ts_str = entry.get("timestamp", "")
                        try:
                            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                            hour_start = ts.replace(minute=0, second=0, microsecond=0).strftime(
                                "%Y-%m-%dT%H:00:00.000Z"
                            )
                        except (ValueError, AttributeError):
                            continue

                        key = (model, hour_start)
                        b = buckets.setdefault(key, {
                            "source":                      "claude-code",
                            "model":                       model,
                            "hour_start":                  hour_start,
                            "device":                      DEVICE,
                            "input_tokens":                0,
                            "cached_input_tokens":         0,
                            "cache_creation_input_tokens": 0,
                            "output_tokens":               0,
                            "total_tokens":                0,
                            "conversations":               0,
                        })
                        b["input_tokens"]                += usage.get("input_tokens", 0)
                        b["cached_input_tokens"]         += usage.get("cache_read_input_tokens", 0)
                        b["cache_creation_input_tokens"] += usage.get("cache_creation_input_tokens", 0)
                        b["output_tokens"]               += usage.get("output_tokens", 0)
                        b["conversations"]               += 1
                        b["total_tokens"] = (
                            b["input_tokens"] + b["cached_input_tokens"]
                            + b["cache_creation_input_tokens"] + b["output_tokens"]
                        )
            except (OSError, PermissionError):
                continue

    return list(buckets.values())


# ── 解析 Codex 会话文件 ───────────────────────────────────────────────────────
def _int_token(value) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _codex_default_model() -> str:
    if not CODEX_CONFIG.exists():
        return "codex-openai"
    try:
        with open(CODEX_CONFIG, encoding="utf-8") as f:
            for line in f:
                m = _re.match(r'^\s*model\s*=\s*["\']([^"\']+)["\']', line)
                if m:
                    return m.group(1)
    except OSError:
        pass
    return "codex-openai"


def _codex_usage_parts(usage: dict):
    input_total = _int_token(usage.get("input_tokens"))
    cached = _int_token(usage.get("cached_input_tokens"))
    output = _int_token(usage.get("output_tokens"))
    total = _int_token(usage.get("total_tokens"))

    if input_total or cached or output:
        # OpenAI reports cached_input_tokens as a subset of input_tokens.
        # Store only the uncached part in input_tokens to keep totals exact.
        uncached_input = max(input_total - cached, 0)
        return uncached_input, cached, 0, output

    # Older/imported Codex records can expose only total_tokens. Preserve that
    # usage in the schema even though input/output split is unavailable.
    if total:
        return total, 0, 0, 0

    return None


def parse_codex_sessions() -> list:
    if not CODEX_DIR.exists():
        print(f"  找不到 Codex 数据目录: {CODEX_DIR}")
        return []

    buckets: dict = {}
    fallback_model = _codex_default_model()
    # 去重键不含时间戳：Codex resume/fork 会话会把整段历史回放进一个新 rollout 文件，
    # 每个 token_count 事件盖上 resume 时刻的新时间戳，但 last_token_usage / total_token_usage
    # 序列与原会话逐条相同。旧实现把 ts 放进去重键 → 回放副本 ts 不同 → 同一批用量被 resume
    # 次数倍计（实测虚增约 46%）。改用 (session_id, 累计 total, last total)：同一会话 cumulative
    # 单调递增，(cum,last) 逐轮唯一；last=0 的空事件贡献 0，重复丢弃无害。文件按名（内嵌 ISO
    # 时间）排序处理，令原始会话先于 resume 文件，事件归到最早出现的小时。
    seen_events: set[tuple[str, int, int]] = set()

    for jsonl_file in sorted(CODEX_DIR.rglob("*.jsonl")):
        session_id = jsonl_file.stem
        model = fallback_model
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

                    if entry.get("type") == "session_meta":
                        payload = entry.get("payload", {})
                        session_id = payload.get("id") or session_id
                        model = payload.get("model") or fallback_model
                        continue

                    payload = entry.get("payload", {})
                    if entry.get("type") != "event_msg" or payload.get("type") != "token_count":
                        continue

                    # Codex 有时会写 "info": null（只带 rate_limits 的事件）。
                    # payload.get("info", {}) 的默认值仅在键缺失时生效，值为 null 仍会拿到 None，
                    # 故用 `or {}` 兜底，避免下一行 None.get(...) 崩溃。
                    info = payload.get("info") or {}
                    usage = info.get("last_token_usage") or {}
                    parts = _codex_usage_parts(usage)
                    if not parts:
                        continue

                    ts_str = entry.get("timestamp", "")
                    try:
                        ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00")).astimezone(timezone.utc)
                        hour_start = ts.replace(minute=0, second=0, microsecond=0).strftime(
                            "%Y-%m-%dT%H:00:00.000Z"
                        )
                    except (ValueError, AttributeError):
                        continue

                    event_key = (
                        session_id,
                        _int_token((info.get("total_token_usage") or {}).get("total_tokens")),
                        _int_token(usage.get("total_tokens")),
                    )
                    if event_key in seen_events:
                        continue
                    seen_events.add(event_key)

                    input_tokens, cached_input_tokens, cache_creation_input_tokens, output_tokens = parts
                    key = (model, hour_start)
                    b = buckets.setdefault(key, {
                        "source":                      "codex",
                        "model":                       model,
                        "hour_start":                  hour_start,
                        "device":                      DEVICE,
                        "input_tokens":                0,
                        "cached_input_tokens":         0,
                        "cache_creation_input_tokens": 0,
                        "output_tokens":               0,
                        "total_tokens":                0,
                        "conversations":               0,
                    })
                    b["input_tokens"]                += input_tokens
                    b["cached_input_tokens"]         += cached_input_tokens
                    b["cache_creation_input_tokens"] += cache_creation_input_tokens
                    b["output_tokens"]               += output_tokens
                    b["conversations"]               += 1
                    b["total_tokens"] = (
                        b["input_tokens"] + b["cached_input_tokens"]
                        + b["cache_creation_input_tokens"] + b["output_tokens"]
                    )
        except (OSError, PermissionError):
            continue

    return list(buckets.values())


# ── git commit + push（不含 pull）────────────────────────────────────────────
def git_commit_push(new_count: int, updated_count: int):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    msg = f"sync: +{new_count} new, ~{updated_count} updated ({now})"

    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GIT_SSH_COMMAND"] = "ssh -o BatchMode=yes"

    add = subprocess.run(["git", "add", "data/usage.ndjson"], cwd=REPO_DIR, capture_output=True)
    if add.returncode != 0:
        print("  命令失败: git add data/usage.ndjson")
        print("  " + add.stderr.decode("utf-8", errors="ignore").strip())
        return False

    # 数据无变化时没有任何暂存内容，git commit 会以非零退出（nothing to commit）——这不是错误。
    if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=REPO_DIR).returncode == 0:
        print("  数据无变化，无需提交。")
        # 仍尝试 push，把历史上未推送的提交同步到远程（已最新则为空操作）。
        subprocess.run(["git", "push"], cwd=REPO_DIR, capture_output=True, env=env)
        return True

    for cmd in (["git", "commit", "-m", msg], ["git", "push"]):
        result = subprocess.run(cmd, cwd=REPO_DIR, capture_output=True, env=env)
        if result.returncode != 0:
            print(f"  命令失败: {' '.join(cmd)}")
            print("  " + result.stderr.decode("utf-8", errors="ignore").strip())
            return False
    return True


# ── 处理未提交改动（commit / stash 二选一）──────────────────────────────────
def has_uncommitted_changes() -> bool:
    """git pull --rebase 会被已跟踪文件的未提交改动（staged/unstaged）阻塞。
    未跟踪文件不阻塞，所以用 `git diff --quiet HEAD` 只检测已跟踪改动。"""
    return subprocess.run(["git", "diff", "--quiet", "HEAD"], cwd=REPO_DIR).returncode != 0


def handle_dirty_worktree() -> str:
    """让用户选择如何处理未提交改动；返回 'committed' / 'stashed'，取消则退出。"""
    status = subprocess.run(
        ["git", "status", "--short"], cwd=REPO_DIR, capture_output=True, text=True,
    ).stdout.rstrip()
    print("\n  ⚠️  检测到未提交改动，git pull --rebase 无法进行：")
    for line in status.splitlines():
        print(f"     {line}")
    print("\n  要怎么处理？")
    print("     [1] commit  — 提交这些改动（进入历史，随本次 sync 一起 push）")
    print("     [2] stash   — 先暂存，sync 跑完自动恢复（改动仍保持未提交）")
    print("     [其他] 取消")
    choice = input("  请选择 [1/2]: ").strip()

    if choice == "1":
        default_msg = f"chore: 本地改动（sync 前提交 {datetime.now().strftime('%Y-%m-%d %H:%M')}）"
        msg = input("  提交信息（直接回车用默认）: ").strip() or default_msg
        subprocess.run(["git", "add", "-u"], cwd=REPO_DIR)
        r = subprocess.run(["git", "commit", "-m", msg], cwd=REPO_DIR, capture_output=True)
        if r.returncode != 0:
            print("  commit 失败：")
            print("  " + r.stderr.decode("utf-8", errors="ignore").strip())
            sys.exit(1)
        print("  已提交，稍后随 sync 一起推送。")
        return "committed"

    if choice == "2":
        r = subprocess.run(
            ["git", "stash", "push", "-m", "sync.py auto-stash"],
            cwd=REPO_DIR, capture_output=True,
        )
        if r.returncode != 0:
            print("  stash 失败：")
            print("  " + r.stderr.decode("utf-8", errors="ignore").strip())
            sys.exit(1)
        print("  已暂存，sync 结束后会自动 git stash pop 恢复。")
        return "stashed"

    print("  已取消。")
    sys.exit(0)


# ── main ──────────────────────────────────────────────────────────────────────
def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始同步...")
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    # 0. 工作区若有未提交改动，先让用户选 commit 还是 stash（否则 pull --rebase 会中止）
    stashed = False
    if has_uncommitted_changes():
        stashed = handle_dirty_worktree() == "stashed"

    try:
        _do_sync()
    finally:
        if stashed:
            print("  恢复暂存改动 (git stash pop)...")
            r = subprocess.run(["git", "stash", "pop"], cwd=REPO_DIR, capture_output=True)
            if r.returncode != 0:
                print("  ⚠️  stash pop 失败或有冲突，请手动 `git stash list` 检查：")
                print("  " + r.stderr.decode("utf-8", errors="ignore").strip())
            else:
                print("  暂存改动已恢复。")


def _do_sync():
    # 1. 先 pull（此时工作区已干净，不会有 unstaged changes 阻塞 rebase）
    print("  拉取远程最新...")
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GIT_SSH_COMMAND"] = "ssh -o BatchMode=yes"
    pull = subprocess.run(["git", "pull", "--rebase"], cwd=REPO_DIR, capture_output=True, env=env)
    if pull.returncode != 0:
        stderr = pull.stderr.decode("utf-8", errors="ignore").strip()
        print(f"  pull 失败: {stderr}")
        sys.exit(1)

    # 2. 读取备份（pull 后的最新状态）
    print("  读取已有备份...")
    existing = load_existing()
    print(f"  已有 {len(existing)} 条小时记录")

    # 3. 扫描本地会话
    print("  扫描 Claude Code 会话...")
    new_records = parse_claude_sessions()
    print(f"  解析到 {len(new_records)} 条 Claude Code 小时记录")

    print("  扫描 Codex 会话...")
    codex_records = parse_codex_sessions()
    print(f"  解析到 {len(codex_records)} 条 Codex 小时记录")
    new_records.extend(codex_records)

    print("  扫描 Antigravity 会话...")
    antigravity_records = parse_antigravity_sessions()
    print(f"  解析到 {len(antigravity_records)} 条 Antigravity 小时记录")
    new_records.extend(antigravity_records)

    if not new_records:
        print("  没有数据，退出。")
        return

    # 4. 合并 + 检测同时段同 (source, model) 下出现新 device（hostname 漂移）
    cost_before = sum(calc_cost(r) for r in existing.values())
    existing_by_smh = {(k[0], k[1], k[2]): k[3] for k in existing.keys()}
    # (source, device, hour_start) -> model，用于检测 codex 模型重标导致的重复计数
    existing_by_sdh = {(k[0], r.get("device", "unknown"), k[2]): k[1]
                       for k, r in existing.items()}
    new_count = updated_count = 0
    device_drift = []  # (source, model, hour_start, old_device, new_device)
    model_relabel = []  # (source, hour_start, device, old_model, new_model)
    for rec in new_records:
        # Codex 会话文件不记录 model，模型名取自 ~/.codex/config.toml 的当前默认值。
        # 用户切换默认模型后，重新解析会把同一批旧会话按新模型重标（token 完全相同），
        # 而合并键含 model → 旧记录留存、又多出新模型副本 → 历史小时翻倍。
        # 若某 (source, device, hour) 已按别的模型记过，保留历史归属、丢弃重标副本。
        if rec["source"] == "codex":
            sdh = (rec["source"], rec.get("device", "unknown"), rec["hour_start"])
            prev_model = existing_by_sdh.get(sdh)
            if prev_model is not None and prev_model != rec["model"]:
                model_relabel.append((rec["source"], rec["hour_start"],
                                      rec.get("device", "unknown"), prev_model, rec["model"]))
                continue
        key = (rec["source"], rec["model"], rec["hour_start"], rec.get("device", "unknown"))
        smh = (rec["source"], rec["model"], rec["hour_start"])
        if smh in existing_by_smh and existing_by_smh[smh] != key[3]:
            device_drift.append((*smh, existing_by_smh[smh], key[3]))
        if key in existing:
            updated_count += 1
        else:
            new_count += 1
        existing[key] = rec

    print(f"  合并后共 {len(existing)} 条（新增 {new_count}，更新 {updated_count}）")

    # 提示：codex 历史小时被 config 新默认模型重标，已保留原归属避免重复计数
    if model_relabel:
        print(f"\n  ℹ️  codex 模型重标：{len(model_relabel)} 个历史小时按 config 新默认被重新归属，"
              f"已保留原模型避免翻倍：")
        for s, h, dev, old_m, new_m in model_relabel[:5]:
            print(f"     {s}@{h} [{dev}]  保留 {old_m}（忽略 {new_m}）")
        if len(model_relabel) > 5:
            print(f"     ... 还有 {len(model_relabel) - 5} 条")

    # 异常检测：device 漂移 — 同 (source, model, hour) 下出现两个 device
    if device_drift:
        print(f"\n  ⚠️  device 漂移检测到 {len(device_drift)} 条同时段桶被分配到新 device：")
        for s, m, h, old_dev, new_dev in device_drift[:5]:
            print(f"     {s}/{m}@{h}  {old_dev!r} → {new_dev!r}")
        if len(device_drift) > 5:
            print(f"     ... 还有 {len(device_drift)-5} 条")
        print(f"  本机 _canonical_device() = {DEVICE!r}")
        print(f"  这会让历史桶被双计数。检查 _canonical_device() 是否识别当前 hostname。中止。")
        sys.exit(2)

    # 异常检测：费用涨幅超过 20% 时警告
    cost_after = sum(calc_cost(r) for r in existing.values())
    if cost_before > 0:
        pct = (cost_after - cost_before) / cost_before * 100
        if pct > 20:
            print(f"\n  ⚠️  费用异常：${cost_before:.2f} → ${cost_after:.2f} (+{pct:.0f}%)")
            print("  可能存在重复计数，请检查后再推送。继续？[y/N] ", end="", flush=True)
            if input().strip().lower() != "y":
                print("  已取消。")
                sys.exit(0)

    # 5. 写文件
    sorted_records = sorted(existing.values(), key=lambda r: (r["hour_start"], r["source"], r["model"], r.get("device", "unknown")))
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        for rec in sorted_records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # 6. commit + push
    print("  推送到 GitHub...")
    if git_commit_push(new_count, updated_count):
        print("  推送成功！")
    else:
        print("  推送失败，请检查 git 配置。")
        sys.exit(1)


if __name__ == "__main__":
    main()
