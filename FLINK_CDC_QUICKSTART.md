# Flink CDC 快速开始

## 5分钟快速上手 Flink CDC

### 前置条件

- ✅ MySQL 数据库运行中
- ✅ MatrixOne 数据库运行中
- ✅ Docker 已安装
- ✅ Flink CDC 代码库已克隆

### 步骤1: 克隆 Flink CDC 代码库

```bash
cd ~/code
git clone git@github.com:matrixorigin/flink-cdc.git
```

### 步骤2: 配置路径

编辑 `config/scenarios/flink_cdc.yaml`：

```yaml
flink_cdc:
  path: "~/code/flink-cdc"  # 修改为你的实际路径
```

### 步骤3: 在 MySQL 生成数据

```bash
python generate_data.py \
  --host localhost \
  --port 3306 \
  --user root \
  --password password \
  --database test_db \
  --group basic \
  --count 1000
```

### 步骤4: 在 MO 创建表结构

```bash
python generate_data.py \
  --host localhost \
  --port 6001 \
  --database test_db \
  --group basic \
  --create-only
```

### 步骤5: 运行测试

```bash
# 自动启动 Kafka、Producer、Consumer 并运行测试
python main.py --scenario flink_cdc --group basic
```

## 工作原理

```
MySQL (源数据)
    ↓
Producer (读取 binlog)
    ↓
Kafka (消息队列)
    ↓
Consumer (写入 MO)
    ↓
MatrixOne (目标数据)
```

## 测试内容

测试工具会自动：

1. ✅ 启动 Kafka (docker-compose)
2. ✅ 启动 Producer (读取 MySQL binlog)
3. ✅ 启动 Consumer (写入 MatrixOne)
4. ✅ 验证全量数据同步
5. ✅ 测试增量数据同步
6. ✅ 停止 Producer 和 Consumer

## 监控

### 查看日志

```bash
# Producer 日志
tail -f /tmp/flink_cdc_producer.log

# Consumer 日志
tail -f /tmp/flink_cdc_consumer.log
```

### 查看 Kafka 状态

```bash
cd ~/code/flink-cdc
docker-compose ps
```

### 查看数据同步

```sql
-- 在 MySQL 查询
mysql -h localhost -P 3306 -u root -p
> SELECT COUNT(*) FROM test_db.cdc_test_base;

-- 在 MO 查询
mysql -h localhost -P 6001 -u root -p111
> SELECT COUNT(*) FROM test_db.cdc_test_base;
```

## 手动测试

如果需要手动控制，可以分步执行：

### 1. 启动 Kafka

```bash
cd ~/code/flink-cdc
docker-compose up -d
```

### 2. 启动 Producer

```bash
./scripts/producer-realtime.sh \
  --db test_db \
  --tables cdc_test_base \
  --topic t1
```

### 3. 启动 Consumer

```bash
./scripts/consumer.sh \
  --db test_db \
  --consumer-batch-size 2000 \
  --topic t1 \
  --group group-1
```

### 4. 插入测试数据

```sql
-- 在 MySQL 中
INSERT INTO test_db.cdc_test_base (col_varchar, col_int) 
VALUES ('manual_test', 999);
```

### 5. 验证同步

```sql
-- 在 MO 中查询
SELECT * FROM test_db.cdc_test_base 
WHERE col_varchar = 'manual_test';
```

## 故障排查

### Kafka 启动失败

```bash
# 检查 Docker
docker ps

# 重启 Kafka
cd ~/code/flink-cdc
docker-compose down
docker-compose up -d
```

### Producer 启动失败

```bash
# 查看日志
tail -f /tmp/flink_cdc_producer.log

# 检查 MySQL binlog
mysql> SHOW VARIABLES LIKE 'log_bin';
```

### Consumer 启动失败

```bash
# 查看日志
tail -f /tmp/flink_cdc_consumer.log

# 检查 MO 连接
mysql -h localhost -P 6001 -u root -p111
```

### 数据不同步

```bash
# 检查进程
ps aux | grep -E "producer|consumer"

# 检查 Kafka 消息
cd ~/code/flink-cdc
docker-compose exec kafka kafka-console-consumer \
  --topic t1 \
  --from-beginning \
  --bootstrap-server localhost:9092
```

## 清理环境

```bash
# 停止 Kafka
cd ~/code/flink-cdc
docker-compose down

# 删除测试数据
mysql -h localhost -P 3306 -u root -p -e "DROP DATABASE test_db;"
mysql -h localhost -P 6001 -u root -p111 -e "DROP DATABASE test_db;"
```

## 完整示例脚本

```bash
# 运行完整示例
chmod +x examples/flink_cdc_example.sh
./examples/flink_cdc_example.sh
```

## 下一步

- 📖 阅读详细文档：[docs/FLINK_CDC_GUIDE.md](docs/FLINK_CDC_GUIDE.md)
- 🔧 查看配置说明：[config/scenarios/flink_cdc.yaml](config/scenarios/flink_cdc.yaml)
- 📝 查看测试用例：[config/testcases/flink_cdc_tests.yaml](config/testcases/flink_cdc_tests.yaml)

祝测试顺利！🚀
