#!/bin/bash
# 设置 macOS LaunchAgent，每天自动同步 token 数据到 GitHub。
# 用法：bash setup_auto_sync.sh

set -e

PLIST_DIR="$HOME/Library/LaunchAgents"
PLIST_FILE="$PLIST_DIR/com.token-tracker.sync.plist"
PYTHON=$(which python3)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"

mkdir -p "$PLIST_DIR" "$LOG_DIR"

cat > "$PLIST_FILE" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.token-tracker.sync</string>

  <key>ProgramArguments</key>
  <array>
    <string>$PYTHON</string>
    <string>$SCRIPT_DIR/sync.py</string>
  </array>

  <!-- 每天 12:00 运行 -->
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>   <integer>12</integer>
    <key>Minute</key> <integer>0</integer>
  </dict>

  <key>StandardOutPath</key>
  <string>$LOG_DIR/sync.log</string>
  <key>StandardErrorPath</key>
  <string>$LOG_DIR/sync.err</string>

  <!-- 登录后才运行 -->
  <key>RunAtLoad</key>
  <false/>
</dict>
</plist>
EOF

# 加载（如已存在则先卸载）
launchctl unload "$PLIST_FILE" 2>/dev/null || true
launchctl load "$PLIST_FILE"

echo "✓ LaunchAgent 已安装：每天 12:00 自动同步"
echo "  配置文件：$PLIST_FILE"
echo "  日志目录：$LOG_DIR"
echo ""
echo "手动立即同步：python3 $SCRIPT_DIR/sync.py"
echo "卸载自动同步：launchctl unload $PLIST_FILE"
