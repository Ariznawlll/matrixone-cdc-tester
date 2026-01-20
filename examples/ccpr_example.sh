#!/bin/bash
# MatrixOne 跨集群CDC (CCPR) 完整测试示例

set -e

echo "=========================================="
echo "MatrixOne CCPR 测试示例"
echo "=========================================="

# 配置
UPSTREAM_HOST="localhost"
UPSTREAM_PORT=6001
DOWNSTREAM_HOST="localhost"
DOWNSTREAM_PORT=6002
DATABASE="test_db"

echo ""
echo "步骤1: 在上游集群生成测试数据"
echo "----------------------------------------"
python generate_data.py \
  --host $UPSTREAM_HOST \
  --port $UPSTREAM_PORT \
  --database $DATABASE \
  --group basic \
  --count 1000

echo ""
echo "步骤2: 运行跨集群CDC基础测试"
echo "----------------------------------------"
python main.py --scenario cross_cluster --group basic

echo ""
echo "步骤3: 生成分区表数据"
echo "----------------------------------------"
python generate_data.py \
  --host $UPSTREAM_HOST \
  --port $UPSTREAM_PORT \
  --database $DATABASE \
  --group partition \
  --count 5000

echo ""
echo "步骤4: 运行分区表测试"
echo "----------------------------------------"
python main.py --scenario cross_cluster --group partition

echo ""
echo "=========================================="
echo "测试完成！"
echo "=========================================="
echo ""
echo "查看下游集群订阅状态："
echo "  mysql -h $DOWNSTREAM_HOST -P $DOWNSTREAM_PORT -u root -p"
echo "  > SHOW CCPR SUBSCRIPTIONS;"
echo ""
