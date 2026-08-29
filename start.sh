#!/bin/bash
# 元素之诗QQ助手启动脚本

echo "=== 元素之诗QQ助手（官方API版） ==="
echo ""

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "错误：未找到 .env 文件"
    echo "请先复制 .env.example 并填写配置："
    echo "  cp .env.example .env"
    echo "  vim .env"
    exit 1
fi

# 检查依赖
echo "检查依赖..."
pip3 install -r requirements.txt -q

# 启动机器人
echo "启动机器人..."
python3 -m bot.main
