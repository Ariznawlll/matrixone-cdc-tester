# Flink CDC (MySQL to MO) 测试指南

## 概述

本指南介绍如何使用测试工具进行 Flink CDC（MySQL 到 MatrixOne）的测试。Flink CDC 通过 Kafka 消息队列实现 MySQL 到 MatrixOne 的数据同步。

## 架构说明

```
MySQL (源)
    ↓
Producer (读取MySQL binlog)
    ↓
Kafka (消息队列)
    ↓
Consumer (写入MO)
    ↓
MatrixOne (目标)
```

## 前置条件

### 1. 环境准备

需要准备以下环境：

- **MySQL 数据库**：作为数据源
- **MatrixOne 数据库**：作为数据目标
- **Docker**：用于运行 Kafka
- **Flink CDC 代码库**：从 GitHub 克隆

### 2. 克隆 Flink CDC 代码库

```bash
cd ~/code
git clone git@github.com:matrixorigin/flink-cdc.git
```

### 3. 数据库准备

在 MySQL 和 MatrixOne 中创建相同的数据库和表：

```sql
-- 在 MySQL 和 MO 中都执行
CREATE DATABASE test_db;
USE test_db;

-- 创建测试表（使用数据生成工具）
```

## 快速开始

### 步骤1: 配置 Flink CDC 路径

编辑 `config/scenarios/flink_cdc.yaml`：

```yaml
flink_cdc:
  # 指定 Flink CDC 代码库路径
  path: "~/code/flink-cdc"  # 修改为你的实际路径
  
  # 要同步的表
  tables:
    - "cdc_test_base"
    - "cdc_test_composite_pk"
  
  # Kafka 主题名
  topic: "cdc_test_topic"
  
  # Consumer 批量大小
  consumer_batch_size: 2000
  
  # Consumer 组名
  group: "cdc_test_group"
```

### 步骤2: 在 MySQL 生成测试数据

```bash
# 在 MySQL 中生成测试数据
python generate_data.py \
  --host localhost \
  --port 3306 \
  --user root \
  --password password \
  --database test_db \
  --group basic \
  --count 1000
```

### 步骤3: 在 MO 创建相同的表结构

```bash
# 只创建表结构，不插入数据
python generate_data.py \
  --host localhost \
  --port 6001 \
  --user root \
  --password 111 \
  --database test_db \
  --group basic \
  --create-only
```

### 步骤4: 运行 Flink CDC 测试

```bash
# 运行基础测试
python main.py --scenario flink_cdc --group basic

# 使用 Flink CDC 专用测试用例
python main.py --scenario flink_cdc --testcase flink_cdc_tests.yaml
```

## 工作流程

### 自动化流程

测试工具会自动执行以下步骤：

1. **启动 Kafka**
   ```bash
   cd flink-cdc && docker-compose up -d
   ```

2. **启动 Producer**
   ```bash
   ./scripts/producer-realtime.sh \
     --db test_db \
     --tables cdc_test_base,cdc_test_composite_pk \
     --topic cdc_test_topic
   ```

3. **启动 Consumer**
   ```bash
   ./scripts/consumer.sh \
     --db test_db \
     --consumer-batch-size 2000 \
     --topic cdc_test_topic \
     --group cdc_test_group
   ```

4. **执行测试用例**
   - 验证全量数据同步
   - 测试增量数据同步（INSERT/UPDATE/DELETE）
   - 检查同步状态

5. **清理环境**
   - 停止 Producer
   - 停止 Consumer
   - 可选：停止 Kafka

### 手动测试流程

如果需要手动测试，可以按照以下步骤：

#### 1. 启动 Kafka

```bash
cd ~/code/flink-cdc
docker-compose up -d

# 检查 Kafka 状态
docker-compose ps
```

#### 2. 启动 Producer

```bash
cd ~/code/flink-cdc
./scripts/producer-realtime.sh \
  --db test_db \
  --tables cdc_test_base \
  --topic t1
```

#### 3. 启动 Consumer

```bash
cd ~/code/flink-cdc
./scripts/consumer.sh \
  --db test_db \
  --consumer-batch-size 2000 \
  --topic t1 \
  --group group-1
```

#### 4. 插入测试数据

在 MySQL 中插入数据：

```sql
-- 使用 INSERT
INSERT INTO cdc_test_base (col_varchar, col_int) VALUES ('test', 123);

-- 或使用 LOAD DATA
LOAD DATA LOCAL INFILE '/path/to/data.csv' 
INTO TABLE cdc_test_base 
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n';
```

#### 5. 验证同步

在 MatrixOne 中查询：

```sql
SELECT COUNT(*) FROM cdc_test_base;
SELECT * FROM cdc_test_base ORDER BY id DESC LIMIT 10;
```

## 配置说明

### 场景配置参数

```yaml
# MySQL 源配置
source:
  type: "mysql"
  host: "localhost"
  port: 3306
  user: "root"
  password: "password"
  database: "test_db"

# MatrixOne 目标配置
target:
  type: "matrixone"
  host: "localhost"
  port: 6001
  user: "root"
  password: "111"
  database: "test_db"

# Flink CDC 配置
flink_cdc:
  path: "~/code/flink-cdc"           # Flink CDC 代码库路径
  tables:                             # 要同步的表列表
    - "cdc_test_base"
    - "cdc_test_composite_pk"
  topic: "cdc_test_topic"             # Kafka 主题名
  consumer_batch_size: 2000           # Consumer 批量大小
  group: "cdc_test_group"             # Consumer 组名
  stop_kafka_on_teardown: false       # 测试完成后是否停止 Kafka
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| path | Flink CDC 代码库路径 | ../flink-cdc |
| tables | 要同步的表列表 | ["cdc_test_base"] |
| topic | Kafka 主题名 | cdc_test_topic |
| consumer_batch_size | Consumer 批量大小 | 2000 |
| group | Consumer 组名 | cdc_test_group |
| stop_kafka_on_teardown | 测试后停止 Kafka | false |

## 测试场景

### 1. 全量同步测试

测试 MySQL 中已有数据的全量同步：

```bash
# 先在 MySQL 生成数据
python generate_data.py --host localhost --port 3306 --database test_db --count 1000

# 在 MO 创建表结构
python generate_data.py --host localhost --port 6001 --database test_db --create-only

# 运行测试
python main.py --scenario flink_cdc --group basic
```

### 2. 增量同步测试

测试 MySQL 新增数据的增量同步：

```bash
# 运行增量测试
python main.py --scenario flink_cdc --group incremental
```

测试会自动：
- 在 MySQL 插入新数据
- 更新已有数据
- 删除部分数据
- 验证 MO 中的数据一致性

### 3. 性能测试

测试大批量数据的同步性能：

```bash
# 生成大量数据
python generate_data.py --host localhost --port 3306 --database test_db --count 100000

# 运行性能测试
python main.py --scenario flink_cdc --group basic
```

## 监控和调试

### 查看日志

测试工具会将 Producer 和 Consumer 的日志保存到：

```bash
# Producer 日志
tail -f /tmp/flink_cdc_producer.log

# Consumer 日志
tail -f /tmp/flink_cdc_consumer.log
```

### 检查 Kafka 状态

```bash
cd ~/code/flink-cdc
docker-compose ps

# 查看 Kafka 日志
docker-compose logs kafka
```

### 检查进程状态

```bash
# 查看 Producer 进程
ps aux | grep producer-realtime

# 查看 Consumer 进程
ps aux | grep consumer
```

### 查看 Kafka 主题

```bash
cd ~/code/flink-cdc

# 列出所有主题
docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:9092

# 查看主题详情
docker-compose exec kafka kafka-topics --describe --topic cdc_test_topic --bootstrap-server localhost:9092

# 查看主题消息
docker-compose exec kafka kafka-console-consumer --topic cdc_test_topic --from-beginning --bootstrap-server localhost:9092
```

## 故障排查

### 问题1: Kafka 启动失败

**可能原因**：
- Docker 未运行
- 端口被占用
- docker-compose.yml 配置错误

**解决方法**：
```bash
# 检查 Docker 状态
docker ps

# 检查端口占用
lsof -i :9092

# 重启 Kafka
cd ~/code/flink-cdc
docker-compose down
docker-compose up -d
```

### 问题2: Producer 启动失败

**可能原因**：
- MySQL 连接失败
- 表不存在
- Binlog 未开启

**解决方法**：
```bash
# 检查 MySQL 连接
mysql -h localhost -P 3306 -u root -p

# 检查 Binlog 是否开启
mysql> SHOW VARIABLES LIKE 'log_bin';

# 查看 Producer 日志
tail -f /tmp/flink_cdc_producer.log
```

### 问题3: Consumer 启动失败

**可能原因**：
- MatrixOne 连接失败
- Kafka 连接失败
- 表不存在

**解决方法**：
```bash
# 检查 MO 连接
mysql -h localhost -P 6001 -u root -p

# 检查 Kafka 连接
cd ~/code/flink-cdc
docker-compose ps

# 查看 Consumer 日志
tail -f /tmp/flink_cdc_consumer.log
```

### 问题4: 数据不同步

**可能原因**：
- Producer/Consumer 未运行
- Kafka 消息堆积
- 网络问题

**解决方法**：
```bash
# 检查进程状态
ps aux | grep -E "producer|consumer"

# 检查 Kafka 消息
cd ~/code/flink-cdc
docker-compose exec kafka kafka-consumer-groups --describe --group cdc_test_group --bootstrap-server localhost:9092

# 重启 Producer 和 Consumer
# 测试工具会自动重启
```

## 性能调优

### 1. 调整 Consumer 批量大小

```yaml
flink_cdc:
  consumer_batch_size: 5000  # 增加批量大小以提高吞吐量
```

### 2. 调整 Kafka 配置

编辑 `flink-cdc/docker-compose.yml`：

```yaml
environment:
  KAFKA_NUM_PARTITIONS: 3  # 增加分区数
  KAFKA_DEFAULT_REPLICATION_FACTOR: 1
```

### 3. 并行消费

启动多个 Consumer 实例（使用相同的 group）：

```bash
# Consumer 1
./scripts/consumer.sh --db test_db --topic t1 --group group-1

# Consumer 2
./scripts/consumer.sh --db test_db --topic t1 --group group-1
```

## 清理环境

### 测试完成后清理

```bash
# 停止 Producer 和 Consumer（测试工具会自动停止）

# 停止 Kafka
cd ~/code/flink-cdc
docker-compose down

# 删除测试数据
mysql -h localhost -P 3306 -u root -p -e "DROP DATABASE test_db;"
mysql -h localhost -P 6001 -u root -p111 -e "DROP DATABASE test_db;"
```

## 最佳实践

1. **数据量建议**
   - 快速测试：1000-10000 条
   - 性能测试：100000+ 条

2. **批量大小建议**
   - 小数据量：1000-2000
   - 大数据量：5000-10000

3. **测试顺序**
   - 先测试全量同步
   - 再测试增量同步
   - 最后测试性能

4. **监控建议**
   - 定期检查 Producer/Consumer 状态
   - 监控 Kafka 消息堆积
   - 关注同步延迟

## 参考资料

- [Flink CDC GitHub](https://github.com/matrixorigin/flink-cdc)
- [测试工具 README](../README.md)
- [架构文档](ARCHITECTURE.md)
