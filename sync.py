#!/usr/bin/env python3
"""
同步 Claude Code token 使用数据到 data/usage.ndjson，并推送到 GitHub。
直接读取 ~/.claude/projects/ 原始会话文件，按小时聚合后备份。
"""

import json
import subprocess
import sys
import socket
import platform
from pathlib import Path
from datetime import datetime

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
    # Claude Opus 4
    "claude-opus-4-8":   {"input": 15.00, "output": 75.00, "cache_write": 18.75, "cache_read": 1.50},
    "claude-opus-4-7":   {"input": 15.00, "output": 75.00, "cache_write": 18.75, "cache_read": 1.50},
    "claude-opus-4-6":   {"input": 15.00, "output": 75.00, "cache_write": 18.75, "cache_read": 1.50},
    "claude-opus-4-5":   {"input": 15.00, "output": 75.00, "cache_write": 18.75, "cache_read": 1.50},
    # Claude Sonnet 4
    "claude-sonnet-4-6": {"input":  3.00, "output": 15.00, "cache_write":  3.75, "cache_read": 0.30},
    "claude-sonnet-4-5": {"input":  3.00, "output": 15.00, "cache_write":  3.75, "cache_read": 0.30},
    # Claude Haiku 4
    "claude-haiku-4-5":  {"input":  0.80, "output":  4.00, "cache_write":  1.00, "cache_read": 0.08},
    # Gemini models
    "gemini-3.5-flash": {"input": 1.50, "output": 9.00,  "cache_write": 0.375,   "cache_read": 0.15},
    "gemini-3.1-pro":   {"input": 1.25, "output": 5.00,  "cache_write": 0.3125,  "cache_read": 0.125},
    "gemini-2.5-pro":   {"input": 1.25, "output": 5.00,  "cache_write": 0.3125,  "cache_read": 0.125},
    "gemini-2.5-flash": {"input": 0.30, "output": 2.50,  "cache_write": 0.075,   "cache_read": 0.03},
    "gemini-2.0-pro":   {"input": 1.25, "output": 5.00,  "cache_write": 0.3125,  "cache_read": 0.125},
    "gemini-2.0-flash": {"input": 0.075,"output": 0.30,  "cache_write": 0.01875, "cache_read": 0.01875},
}

def _normalize_model(model: str) -> str:
    """Normalize model name: replace dots between digits only when they appear
    at the end of the string (version suffix), e.g. claude-opus-4.6 → claude-opus-4-6.
    Leaves family-name dots like gemini-3.5-flash untouched.
    """
    import re
    return re.sub(r'(?<=\d)\.(?=\d+$)', '-', model)


def calc_cost(rec: dict) -> float:
    m = 1_000_000
    raw_model = rec.get("model", "")
    model = _normalize_model(raw_model)
    p = PRICING.get(model, {})
    if not p:
        for k, v in PRICING.items():
            if model.startswith(k) or k.startswith(model.split("-20")[0]):
                p = v; break
    return (
        rec.get("input_tokens", 0)                * p.get("input", 0)       / m +
        rec.get("output_tokens", 0)               * p.get("output", 0)      / m +
        rec.get("cache_creation_input_tokens", 0) * p.get("cache_write", 0) / m +
        rec.get("cached_input_tokens", 0)         * p.get("cache_read", 0)  / m
    )

def total_cost(records: dict) -> float:
    return sum(calc_cost(r) for r in records.values())

REPO_DIR   = Path(__file__).parent
DATA_FILE  = REPO_DIR / "data" / "usage.ndjson"
CLAUDE_DIR = Path.home() / ".claude" / "projects"
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
        subprocess.run("npx tokentracker-cli sync --auto", shell=True, capture_output=True, timeout=30)
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


# ── git commit + push（不含 pull）────────────────────────────────────────────
def git_commit_push(new_count: int, updated_count: int):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    msg = f"sync: +{new_count} new, ~{updated_count} updated ({now})"
    cmds = [
        ["git", "add", "data/usage.ndjson"],
        ["git", "commit", "-m", msg],
        ["git", "push"],
    ]
    for cmd in cmds:
        result = subprocess.run(cmd, cwd=REPO_DIR, capture_output=True)
        if result.returncode != 0:
            print(f"  命令失败: {' '.join(cmd)}")
            stderr = result.stderr.decode("utf-8", errors="ignore").strip()
            print(f"  {stderr}")
            return False
    return True


# ── main ──────────────────────────────────────────────────────────────────────
def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始同步...")
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    # 1. 先 pull（此时还没写任何文件，不会有 unstaged changes）
    print("  拉取远程最新...")
    pull = subprocess.run(["git", "pull", "--rebase"], cwd=REPO_DIR, capture_output=True)
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
    new_count = updated_count = 0
    device_drift = []  # (source, model, hour_start, old_device, new_device)
    for rec in new_records:
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
