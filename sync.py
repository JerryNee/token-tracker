#!/usr/bin/env python3
"""
同步本地 Claude Code 会话数据到 data/requests.ndjson，并推送到 GitHub。

每次运行只追加新记录（按 UUID 去重），不会覆盖已有数据。
就算本地会话被删除，GitHub 上的历史数据依然完整。
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

CLAUDE_DIR = Path.home() / ".claude" / "projects"
REPO_DIR   = Path(__file__).parent
DATA_FILE  = REPO_DIR / "data" / "requests.ndjson"


def project_slug_to_name(slug: str) -> str:
    path = slug.replace("-", "/").lstrip("/")
    home = str(Path.home()).lstrip("/")
    if path.startswith(home):
        path = "~" + path[len(home):]
    parts = path.split("/")
    return "/".join(parts[-2:]) if len(parts) > 2 else path


def load_known_uuids() -> set:
    if not DATA_FILE.exists():
        return set()
    uuids = set()
    with open(DATA_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                uuids.add(json.loads(line)["uuid"])
            except (json.JSONDecodeError, KeyError):
                continue
    return uuids


def parse_new_records(known_uuids: set) -> list:
    new_records = []

    if not CLAUDE_DIR.exists():
        print(f"  找不到 Claude 数据目录: {CLAUDE_DIR}")
        return new_records

    for project_dir in CLAUDE_DIR.iterdir():
        if not project_dir.is_dir():
            continue
        project_name = project_slug_to_name(project_dir.name)

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

                        uuid = entry.get("uuid")
                        if not uuid or uuid in known_uuids:
                            continue

                        msg = entry.get("message", {})
                        if msg.get("role") != "assistant":
                            continue
                        usage = msg.get("usage")
                        if not usage:
                            continue

                        ts_str = entry.get("timestamp", "")
                        try:
                            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                            date = ts.astimezone().strftime("%Y-%m-%d")
                        except (ValueError, AttributeError):
                            date = datetime.now().strftime("%Y-%m-%d")

                        rec = {
                            "uuid":               uuid,
                            "date":               date,
                            "project":            project_name,
                            "model":              msg.get("model", "unknown"),
                            "input_tokens":       usage.get("input_tokens", 0),
                            "output_tokens":      usage.get("output_tokens", 0),
                            "cache_write_tokens": usage.get("cache_creation_input_tokens", 0),
                            "cache_read_tokens":  usage.get("cache_read_input_tokens", 0),
                        }
                        new_records.append(rec)
                        known_uuids.add(uuid)

            except (OSError, PermissionError):
                continue

    return new_records


def git_push(new_count: int):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    cmds = [
        ["git", "add", "data/requests.ndjson"],
        ["git", "commit", "-m", f"sync: +{new_count} records ({now})"],
        ["git", "push"],
    ]
    for cmd in cmds:
        result = subprocess.run(cmd, cwd=REPO_DIR, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  命令失败: {' '.join(cmd)}")
            print(f"  {result.stderr.strip()}")
            return False
    return True


def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始同步...")

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    print("  读取已有记录...")
    known_uuids = load_known_uuids()
    print(f"  已有 {len(known_uuids)} 条记录")

    print("  扫描本地会话...")
    new_records = parse_new_records(known_uuids)
    print(f"  发现 {len(new_records)} 条新记录")

    if not new_records:
        print("  没有新数据，退出。")
        return

    with open(DATA_FILE, "a", encoding="utf-8") as f:
        for rec in new_records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"  已写入 {DATA_FILE.name}")

    print("  推送到 GitHub...")
    if git_push(len(new_records)):
        print("  推送成功！")
    else:
        print("  推送失败，请检查 git 配置。")
        sys.exit(1)


if __name__ == "__main__":
    main()
