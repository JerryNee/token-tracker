#!/usr/bin/env python3
"""
同步 Claude Code token 使用数据到 data/usage.ndjson，并推送到 GitHub。
直接读取 ~/.claude/projects/ 原始会话文件，按小时聚合后备份。
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

REPO_DIR   = Path(__file__).parent
DATA_FILE  = REPO_DIR / "data" / "usage.ndjson"
CLAUDE_DIR = Path.home() / ".claude" / "projects"


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
                key = (rec["source"], rec["model"], rec["hour_start"])
                existing[key] = rec
            except (json.JSONDecodeError, KeyError):
                continue
    return existing


# ── 解析 Claude Code 会话文件 ─────────────────────────────────────────────────
def parse_claude_sessions() -> list:
    if not CLAUDE_DIR.exists():
        print(f"  找不到 Claude 数据目录: {CLAUDE_DIR}")
        return []

    buckets: dict = {}

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
        result = subprocess.run(cmd, cwd=REPO_DIR, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  命令失败: {' '.join(cmd)}")
            print(f"  {result.stderr.strip()}")
            return False
    return True


# ── main ──────────────────────────────────────────────────────────────────────
def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始同步...")
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    # 1. 先 pull（此时还没写任何文件，不会有 unstaged changes）
    print("  拉取远程最新...")
    pull = subprocess.run(["git", "pull", "--rebase"], cwd=REPO_DIR, capture_output=True, text=True)
    if pull.returncode != 0:
        print(f"  pull 失败: {pull.stderr.strip()}")
        sys.exit(1)

    # 2. 读取备份（pull 后的最新状态）
    print("  读取已有备份...")
    existing = load_existing()
    print(f"  已有 {len(existing)} 条小时记录")

    # 3. 扫描本地会话
    print("  扫描 Claude Code 会话...")
    new_records = parse_claude_sessions()
    print(f"  解析到 {len(new_records)} 条小时记录")

    if not new_records:
        print("  没有数据，退出。")
        return

    # 4. 合并
    new_count = updated_count = 0
    for rec in new_records:
        key = (rec["source"], rec["model"], rec["hour_start"])
        if key in existing:
            updated_count += 1
        else:
            new_count += 1
        existing[key] = rec

    print(f"  合并后共 {len(existing)} 条（新增 {new_count}，更新 {updated_count}）")

    # 5. 写文件
    sorted_records = sorted(existing.values(), key=lambda r: (r["hour_start"], r["source"], r["model"]))
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
