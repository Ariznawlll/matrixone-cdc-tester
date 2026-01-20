#!/bin/bash
# 测试环境初始化脚本

echo "初始化 MatrixOne CDC 测试环境..."

# 创建源数据库
echo "创建源数据库..."
mysql -h localhost -P 6001 -u root -p111 -e "CREATE DATABASE IF NOT EXISTS source_db;"

# 创建目标数据库
echo "创建目标数据库..."
mysql -h localhost -P 6002 -u root -p111 -e "CREATE DATABASE IF NOT EXISTS target_db;"

echo "✓ 测试环境初始化完成"
