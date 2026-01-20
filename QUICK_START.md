# MatrixOne CDC 测试工具 - 快速开始

## 5分钟快速上手

### 1. 安装依赖

```bash
cd matrixone-cdc-tester
pip install -r requirements.txt
```

### 2. 选择你的场景

#### 场景A: MO to MO (单集群内CDC)

```bash
# 1. 配置连接
vim config/scenarios/mo_to_mo.yaml

# 2. 生成数据
python generate_data.py --host localhost --port 6001 --database source_db --count 1000

# 3. 运行测试
python main.py --scenario mo_to_mo --group basic
```

#### 场景B: MO to MySQL

```bash
# 1. 配置连接
vim config/scenarios/mo_to_mysql.yaml

# 2. 生成数据
python generate_data.py --host localhost --port 6001 --database source_db --count 1000

# 3. 运行测试
python main.py --scenario mo_to_mysql --group basic
```

#### 场景C: 跨集群CDC (CCPR) ⭐推荐

```bash
# 1. 在上游集群创建账户
mysql -h localhost -P 6001 -u root -p
> CREATE ACCOUNT account0 ADMIN_NAME 'admin' IDENTIFIED BY 'password';
> CREATE ACCOUNT account1 ADMIN_NAME 'admin' IDENTIFIED BY 'password';
> CREATE DATABASE test_db;

# 2. 配置连接
vim config/scenarios/cross_cluster.yaml

# 3. 生成数据
python generate_data.py --host localhost --port 6001 --database test_db --count 1000

# 4. 运行测试
python main.py --scenario cross_cluster --group basic

# 5. 查看同步状态（在下游集群）
mysql -h localhost -P 6002 -u root -p
> SHOW CCPR SUBSCRIPTIONS;
```

## 常用命令

### 数据生成

```bash
# 基础表（1000条）
python generate_data.py --database test_db --group basic --count 1000

# 分区表（10000条）
python generate_data.py --database test_db --group partition --count 10000

# 全文索引表（500条，较慢）
python generate_data.py --database test_db --group fulltext --count 500

# 向量索引表（1000条）
python generate_data.py --database test_db --group vector --count 1000

# 只创建表结构，不插入数据
python generate_data.py --database test_db --group basic --create-only
```

### 运行测试

```bash
# 列出所有场景
python main.py --list

# 运行基础测试
python main.py --scenario cross_cluster --group basic

# 运行分区表测试
python main.py --scenario cross_cluster --group partition

# 运行全文索引测试
python main.py --scenario cross_cluster --group fulltext

# 使用自定义测试用例
python main.py --scenario cross_cluster --testcase cross_cluster_tests.yaml
```

## 测试表说明

| 表组 | 表名 | 说明 | 推荐数据量 |
|------|------|------|-----------|
| basic | cdc_test_base | 覆盖所有数据类型 | 1000-10000 |
| basic | cdc_test_composite_pk | 复合主键表 | 1000-10000 |
| fulltext | cdc_test_fulltext | 全文索引表 | 500-5000 |
| vector | cdc_test_vector_index | 向量索引表 | 1000-10000 |
| partition | cdc_test_partition_range | Range分区表 | 5000-50000 |
| partition | cdc_test_partition_hash | Hash分区表 | 5000-50000 |
| partition | cdc_test_partition_list | List分区表 | 5000-50000 |

## 覆盖的数据类型（30+种）

### 整数类型（8种）
- TINYINT, SMALLINT, INT, BIGINT
- TINYINT UNSIGNED, SMALLINT UNSIGNED, INT UNSIGNED, BIGINT UNSIGNED

### 小数类型（3种）
- DECIMAL, FLOAT, DOUBLE

### 字符串类型（4种）
- CHAR, VARCHAR, TEXT, ENUM

### 二进制类型（4种）
- BINARY, VARBINARY, BLOB, BIT

### 日期时间类型（5种）
- TIME, DATE, DATETIME, TIMESTAMP, YEAR

### 其他类型（3种）
- BOOL, JSON, VECTOR

## 覆盖的约束

- ✅ 单列主键 (PRIMARY KEY)
- ✅ 复合主键 (COMPOSITE PRIMARY KEY)
- ✅ 单列索引 (INDEX)
- ✅ 复合索引 (COMPOSITE INDEX)
- ✅ 唯一索引 (UNIQUE INDEX)
- ✅ 全文索引 (FULLTEXT INDEX)
- ✅ 向量索引 (VECTOR INDEX)
- ✅ NOT NULL
- ✅ DEFAULT
- ✅ AUTO_INCREMENT

## 跨集群CDC (CCPR) 特别说明

### 同步级别

```yaml
# Database级别 - 同步整个数据库
cdc_config:
  sync_level: "database"

# Table级别 - 只同步指定表
cdc_config:
  sync_level: "table"
source:
  table: "cdc_test_base"
target:
  table: "cdc_test_base"

# Account级别 - 同步整个账户
cdc_config:
  sync_level: "account"
```

### 监控命令

```sql
-- 查看所有订阅
SHOW CCPR SUBSCRIPTIONS;

-- 查看特定订阅
SHOW CCPR SUBSCRIPTION test_db;

-- 暂停订阅
PAUSE CCPR SUBSCRIPTION test_db;

-- 恢复订阅
RESUME CCPR SUBSCRIPTION test_db;

-- 删除订阅
DROP CCPR SUBSCRIPTION test_db;
```

### 状态说明

| 状态值 | 状态名 | 说明 |
|--------|--------|------|
| 0 | running | 正常运行 |
| 1 | error | 出现错误 |
| 2 | pause | 已暂停 |
| 3 | dropped | 已删除 |

## 完整示例：跨集群CDC测试

```bash
#!/bin/bash

# 步骤1: 在上游生成基础表数据
python generate_data.py \
  --host localhost \
  --port 6001 \
  --database test_db \
  --group basic \
  --count 1000

# 步骤2: 运行基础测试
python main.py --scenario cross_cluster --group basic

# 步骤3: 生成分区表数据
python generate_data.py \
  --host localhost \
  --port 6001 \
  --database test_db \
  --group partition \
  --count 5000

# 步骤4: 运行分区表测试
python main.py --scenario cross_cluster --group partition

# 步骤5: 查看结果
echo "测试完成！查看下游集群订阅状态："
mysql -h localhost -P 6002 -u root -p -e "SHOW CCPR SUBSCRIPTIONS;"
```

或者直接运行示例脚本：

```bash
chmod +x examples/ccpr_example.sh
./examples/ccpr_example.sh
```

## 故障排查

### 问题1: 连接失败

```bash
# 检查数据库是否运行
mysql -h localhost -P 6001 -u root -p

# 检查配置文件
cat config/scenarios/cross_cluster.yaml
```

### 问题2: 同步超时

```yaml
# 增加超时时间
validation:
  max_wait_time: 300  # 增加到5分钟
```

### 问题3: Subscription创建失败

```sql
-- 检查上游是否创建了Publication
-- 在上游集群执行
SHOW PUBLICATIONS;

-- 检查账户是否被授权
-- 确认Publication的ACCOUNT字段包含下游账户
```

### 问题4: 数据不一致

```bash
# 等待更长时间让同步完成
# 检查Subscription状态
mysql -h localhost -P 6002 -u root -p
> SHOW CCPR SUBSCRIPTION test_db;
> -- 查看 state 和 error_message 字段
```

## 性能建议

| 场景 | 推荐数据量 | 批量大小 | 同步间隔 |
|------|-----------|---------|---------|
| 快速测试 | 100-1000 | 1000 | 30s |
| 常规测试 | 1000-10000 | 1000 | 60s |
| 性能测试 | 100000+ | 5000 | 120s |
| 全文索引 | 500-5000 | 500 | 60s |

## 下一步

- 📖 阅读完整文档：[README.md](README.md)
- 🏗️ 了解架构设计：[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- 🔄 CCPR详细指南：[docs/CCPR_SETUP_GUIDE.md](docs/CCPR_SETUP_GUIDE.md)
- 📝 查看开发文档：[development document/Cross-Cluster Replication](development%20document/Cross-Cluster%20Replication)

## 获取帮助

```bash
# 查看命令帮助
python main.py --help
python generate_data.py --help

# 列出所有场景
python main.py --list
```

祝测试顺利！🚀
