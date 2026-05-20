#!/usr/bin/env python3
"""
同步 AI token 使用数据到 data/usage.ndjson，并推送到 GitHub。

数据源优先级：
  1. ~/.tokentracker/tracker/queue.jsonl  （TokenTracker，支持 16 个工具）
  2. ~/.claude/projects/                   （fallback，仅 Claude Code）

两个来源各自去重，合并后 push 到 GitHub，本地删文件也不丢历史。
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

REPO_DIR         = Path(__file__).parent
DATA_FILE        = REPO_DIR / "data" / "usage.ndjson"

# TokenTracker 数据目录
TT_QUEUE         = Path.home() / ".tokentracker" / "tracker" / "queue.jsonl"
TT_PROJECT_QUEUE = Path.home() / ".tokentracker" / "tracker" / "project.queue.jsonl"
TT_BIN           = Path.home() / "npm-global" / "bin" / "tokentracker-cli"

# Claude Code 原始会话目录（fallback）
CLAUDE_DIR       = Path.home() / ".claude" / "projects"


# ── 读取已有备份 → dict[(source, model, hour_start)] = record ──────────────
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


# ── 解析 TokenTracker queue.jsonl ─────────────────────────────────────────
def parse_tokentracker_queue(path: Path) -> list:
    """读取 queue.jsonl，按 (source, model, hour_start) 去重，只保留最新值。"""
    if not path.exists():
        return []

    latest: dict = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue

            source     = rec.get("source", "unknown")
            model      = rec.get("model", "unknown")
            hour_start = rec.get("hour_start", "")
            if not hour_start:
                continue

            # 跳过全零的撤回记录
            if (rec.get("input_tokens", 0) == 0
                    and rec.get("cached_input_tokens", 0) == 0
                    and rec.get("cache_creation_input_tokens", 0) == 0
                    and rec.get("output_tokens", 0) == 0):
                continue

            key = (source, model, hour_start)
            latest[key] = {
                "source":                      source,
                "model":                       model,
                "hour_start":                  hour_start,
                "input_tokens":                rec.get("input_tokens", 0),
                "cached_input_tokens":         rec.get("cached_input_tokens", 0),
                "cache_creation_input_tokens": rec.get("cache_creation_input_tokens", 0),
                "output_tokens":               rec.get("output_tokens", 0),
                "total_tokens":                rec.get("total_tokens", 0),
                "conversations":               rec.get("conversation_count", 0),
            }

    return list(latest.values())


# ── Claude Code fallback（直接读会话 jsonl）─────────────────────────────────
def project_slug_to_name(slug: str) -> str:
    path = slug.replace("-", "/").lstrip("/")
    home = str(Path.home()).lstrip("/")
    if path.startswith(home):
        path = "~" + path[len(home):]
    parts = path.split("/")
    return "/".join(parts[-2:]) if len(parts) > 2 else path


def parse_claude_sessions() -> list:
    """读取 Claude Code 原始会话，按 (claude-code, model, hour) 聚合。"""
    if not CLAUDE_DIR.exists():
        return []

    # buckets[(model, hour_start)] = {tokens...}
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
                            # 截断到小时
                            hour_start = ts.replace(minute=0, second=0, microsecond=0).strftime(
                                "%Y-%m-%dT%H:00:00.000Z"
                            )
                        except (ValueError, AttributeError):
                            continue

                        key = (model, hour_start)
                        b = buckets.setdefault(key, {
                            "source": "claude-code",
                            "model": model,
                            "hour_start": hour_start,
                            "input_tokens": 0,
                            "cached_input_tokens": 0,
                            "cache_creation_input_tokens": 0,
                            "output_tokens": 0,
                            "total_tokens": 0,
                            "conversations": 0,
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


# ── git push ──────────────────────────────────────────────────────────────
def git_push(new_count: int, updated_count: int):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    msg = f"sync: +{new_count} new, ~{updated_count} updated ({now})"
    cmds = [
        ["git", "pull", "--rebase"],
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


# ── main ──────────────────────────────────────────────────────────────────
def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始同步...")
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    # 1. 读取现有备份
    print("  读取已有备份...")
    existing = load_existing()
    print(f"  已有 {len(existing)} 条小时记录")

    # 2. 选择数据源
    if TT_QUEUE.exists():
        print(f"  数据源：TokenTracker ({TT_QUEUE})")
        # 先触发一次 tokentracker sync 拿最新数据
        if TT_BIN.exists():
            print("  运行 tokentracker sync...")
            subprocess.run([str(TT_BIN), "sync", "--auto"], capture_output=True, timeout=60)
        new_records = parse_tokentracker_queue(TT_QUEUE)
        # 也读 project queue
        new_records += parse_tokentracker_queue(TT_PROJECT_QUEUE)
        print(f"  从 TokenTracker 解析到 {len(new_records)} 条小时记录")
    else:
        print(f"  数据源：Claude Code 原始会话 ({CLAUDE_DIR})")
        new_records = parse_claude_sessions()
        print(f"  从会话文件解析到 {len(new_records)} 条小时记录")

    if not new_records:
        print("  没有新数据，退出。")
        return

    # 3. 合并（新数据覆盖同 key 的旧数据，保留孤立旧数据）
    new_count = updated_count = 0
    for rec in new_records:
        key = (rec["source"], rec["model"], rec["hour_start"])
        if key in existing:
            updated_count += 1
        else:
            new_count += 1
        existing[key] = rec

    print(f"  合并后共 {len(existing)} 条（新增 {new_count}，更新 {updated_count}）")

    # 4. 写回文件（按时间排序）
    sorted_records = sorted(existing.values(), key=lambda r: (r["hour_start"], r["source"], r["model"]))
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        for rec in sorted_records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    if new_count == 0 and updated_count == 0:
        print("  数据无变化，跳过推送。")
        return

    # 5. 推送
    print("  推送到 GitHub...")
    if git_push(new_count, updated_count):
        print("  推送成功！")
    else:
        print("  推送失败，请检查 git 配置。")
        sys.exit(1)


if __name__ == "__main__":
    main()
