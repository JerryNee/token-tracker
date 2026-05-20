#!/bin/bash
# 一键初始化：登录 GitHub → 创建仓库 → 首次推送 → 安装定时同步
# 用法：bash setup.sh

set -e

GH="$HOME/bin/gh"
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_NAME="token-tracker"
PYTHON=$(which python3)

echo "========================================"
echo "  Token Tracker — 初始化脚本"
echo "========================================"
echo ""

# ── 1. 检查 gh ──
if [ ! -f "$GH" ]; then
    echo "❌ 找不到 gh CLI，请先运行：bash setup_gh.sh"
    exit 1
fi

# ── 2. GitHub 登录 ──
echo "▶ 步骤 1/5：GitHub 登录"
if ! "$GH" auth status &>/dev/null; then
    echo "  浏览器将打开，完成授权后返回此终端..."
    "$GH" auth login --web --git-protocol https
else
    echo "  已登录：$("$GH" auth status 2>&1 | grep 'Logged in' | head -1)"
fi

# ── 3. 初始化 git ──
echo ""
echo "▶ 步骤 2/5：初始化本地 git 仓库"
cd "$REPO_DIR"
if [ ! -d ".git" ]; then
    git init
    git add .
    git commit -m "init: token tracker"
    echo "  git 仓库已初始化"
else
    echo "  git 仓库已存在，跳过"
fi

# ── 4. 首次同步数据 ──
echo ""
echo "▶ 步骤 3/5：从本地会话提取历史数据"
"$PYTHON" -c "
import sys, json
sys.path.insert(0, '.')
from sync import load_known_uuids, parse_new_records, DATA_FILE
from pathlib import Path

DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
known = load_known_uuids()
records = parse_new_records(known)
with open(DATA_FILE, 'a') as f:
    for r in records:
        f.write(json.dumps(r) + '\n')
print(f'  已写入 {len(records)} 条记录到 data/requests.ndjson')
"

# 生成初始 README
"$PYTHON" report.py

git add data/requests.ndjson README.md
git diff --staged --quiet || git commit -m "data: initial sync"

# ── 5. 创建 GitHub 仓库 ──
echo ""
echo "▶ 步骤 4/5：创建 GitHub 仓库"
GITHUB_USER=$("$GH" api user --jq .login)
REMOTE_URL="https://github.com/$GITHUB_USER/$REPO_NAME.git"

if git remote get-url origin &>/dev/null; then
    echo "  remote 已存在：$(git remote get-url origin)"
else
    # 检查仓库是否已存在
    if "$GH" repo view "$GITHUB_USER/$REPO_NAME" &>/dev/null; then
        echo "  仓库 $GITHUB_USER/$REPO_NAME 已存在，直接关联"
    else
        "$GH" repo create "$REPO_NAME" --public --description "AI coding token usage tracker" --source . --remote origin
        echo "  仓库已创建：https://github.com/$GITHUB_USER/$REPO_NAME"
    fi
    git remote add origin "$REMOTE_URL" 2>/dev/null || true
fi

# ── 6. 推送 ──
echo ""
echo "▶ 步骤 5/5：推送到 GitHub"
git branch -M main
git push -u origin main

# ── 7. 安装定时任务 ──
echo ""
echo "▶ 附加：安装每日自动同步（macOS LaunchAgent）"
bash "$REPO_DIR/setup_auto_sync.sh"

echo ""
echo "========================================"
echo "  ✅ 全部完成！"
echo "  GitHub 仓库：https://github.com/$GITHUB_USER/$REPO_NAME"
echo "  每天 12:00 自动同步，也可随时手动运行："
echo "  python3 $REPO_DIR/sync.py"
echo "========================================"
