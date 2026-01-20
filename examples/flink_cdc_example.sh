#!/bin/bash
# Flink CDC (MySQL to MO) 完整测试示例

set -e

echo "=========================================="
echo "Flink CDC 测试示例"
echo "=========================================="

# 配置
MYSQL_HOST="localhost"
MYSQL_PORT=3306
MYSQL_USER="root"
MYSQL_PASSWORD="password"
MO_HOST="localhost"
MO_PORT=6001
MO_USER="root"
MO_PASSWORD="111"
DATABASE="test_db"

echo ""
echo "步骤1: 在MySQL生成测试数据"
echo "----------------------------------------"
python generate_data.py \
  --host $MYSQL_HOST \
  --port $MYSQL_PORT \
  --user $MYSQL_USER \
  --password $MYSQL_PASSWORD \
  --database $DATABASE \
  --group basic \
  --count 1000

echo ""
echo "步骤2: 在MO创建表结构"
echo "----------------------------------------"
python generate_data.py \
  --host $MO_HOST \
  --port $MO_PORT \
  --user $MO_USER \
  --password $MO_PASSWORD \
  --database $DATABASE \
  --group basic \
  --create-only

echo ""
echo "步骤3: 运行Flink CDC基础测试"
echo "----------------------------------------"
python main.py --scenario flink_cdc --group basic

echo ""
echo "步骤4: 测试增量同步"
echo "----------------------------------------"
echo "在MySQL插入新数据..."
mysql -h $MYSQL_HOST -P $MYSQL_PORT -u $MYSQL_USER -p$MYSQL_PASSWORD $DATABASE <<EOF
INSERT INTO cdc_test_base (col_varchar, col_int) VALUES ('incremental_test', 12345);
EOF

echo "等待同步..."
sleep 10

echo "验证MO中的数据..."
mysql -h $MO_HOST -P $MO_PORT -u $MO_USER -p$MO_PASSWORD $DATABASE <<EOF
SELECT COUNT(*) as total_rows FROM cdc_test_base;
SELECT * FROM cdc_test_base WHERE col_varchar = 'incremental_test';
EOF

echo ""
echo "=========================================="
echo "测试完成！"
echo "=========================================="
echo ""
echo "查看Flink CDC日志："
echo "  Producer: tail -f /tmp/flink_cdc_producer.log"
echo "  Consumer: tail -f /tmp/flink_cdc_consumer.log"
echo ""
echo "查看Kafka状态："
echo "  cd ~/code/flink-cdc && docker-compose ps"
echo ""
