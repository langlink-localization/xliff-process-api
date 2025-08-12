#!/bin/bash

# 启动脚本 - 用于快速启动API服务器

echo "XLIFF Process API Server 启动脚本"
echo "======================================"

# 检查Python版本
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then 
    echo "警告: Python版本需要 $required_version 或更高，当前版本为 $python_version"
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装/更新依赖
echo "安装依赖..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# 运行测试（可选）
if [ "$1" == "--test" ]; then
    echo "运行测试..."
    pytest tests/ -v
    if [ $? -ne 0 ]; then
        echo "测试失败！"
        exit 1
    fi
fi

# 启动服务器
echo "启动服务器..."
echo "API文档地址: http://localhost:8848/docs"
echo "健康检查: http://localhost:8848/health"
echo ""
python main.py