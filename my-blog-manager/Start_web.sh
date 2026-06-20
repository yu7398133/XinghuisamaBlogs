#!/bin/bash
# ==================================================
# 星辉云端·控制台 - Web 模式启动脚本
# 适用于 Linux / NAS / Docker 等环境
# ==================================================

cd "$(dirname "$0")"

echo "🌟 星辉云端·控制台 (Web 模式)"
echo ""

# 检查 Python
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ 未找到 Python，请先安装 Python 3.10+"
    exit 1
fi

echo "✅ Python: $($PYTHON_CMD --version)"

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 未找到 Node.js，请先安装 Node.js 18+"
    exit 1
fi

echo "✅ Node.js: $(node --version)"
echo ""

# 启动
$PYTHON_CMD start_web.py
