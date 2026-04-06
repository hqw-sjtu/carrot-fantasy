#!/bin/bash
# 保卫萝卜 - 一键安装运行脚本

echo "🎮 保卫萝卜 安装中..."

# 检测Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装Python"
    exit 1
fi

# 安装依赖
echo "📦 安装依赖..."
pip install -r requirements.txt

# 运行游戏
echo "🎮 启动游戏..."
cd src
python3 main.py