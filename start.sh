#!/bin/bash

# 金融数据智能查询助手 - 启动脚本

echo "=============================================="
echo "   FinQuery - 金融数据智能查询助手"
echo "=============================================="
echo ""

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python3，请先安装 Python3"
    exit 1
fi

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 检查是否需要安装依赖
if [ ! -f ".deps_installed" ]; then
    echo "首次运行，正在安装依赖..."
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        touch .deps_installed
        echo "依赖安装完成！"
    else
        echo "依赖安装失败，请手动运行: pip install -r requirements.txt"
        exit 1
    fi
fi

# 检查 .env 文件
if [ ! -f "src/.env" ]; then
    echo "警告: 未找到 src/.env 文件"
    echo "请创建 src/.env 并添加: DEEPSEEK_API_KEY=your_api_key"
    exit 1
fi

echo ""
echo "正在启动服务..."
echo "Web 界面地址: http://localhost:5000"
echo ""
echo "按 Ctrl+C 停止服务"
echo "=============================================="
echo ""

# 启动 Flask 服务
cd src
python3 ../backend/app.py
