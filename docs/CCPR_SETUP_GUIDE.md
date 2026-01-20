# MatrixOne 跨集群CDC (CCPR) 测试指南

## 概述

本指南介绍如何使用测试工具进行 MatrixOne 跨集群复制 (Cross-Cluster Replication, CCPR) 的测试。

## 前置条件

### 1. 环境准备

需要准备两个 MatrixOne 集群：

- **上游集群（Publication端）**：数据源集群
- **下游集群（Subscription端）**：数据目标集群

### 2. 账户配置

在上游集群创建账户并授权：

```sql
-- 在上游集群执行
-- 创建账户（如果不存在）
CREATE ACCOUNT IF NOT EXISTS account0 ADMIN_NAME 'admin' IDENTIFIED BY 'password';
CREATE ACCOUNT IF NOT EXISTS account1 ADMIN_NAME 'admin' IDENTIFIED BY 'password';

-- 使用account0登录，创建测试数据库
CREATE DATABASE test_db;
```

## 快速开始

### 步骤1: 生成测试数据

在上游集群生成测试数据：

```bash
# 连接到上游集群，生成基础表数据
python generate_data.py \
  --host localhost \
  --port 6001 \
  --database test_db \
  --group basic \
  --count 1000

# 生成分区表数据
python generate_data.py \
  --host localhost \
  --port 6001 \
  --database test_db \
  --group partition \
  --count 5000
```

### 步骤2: 配置跨集群场景

编辑 `config/scenarios/cross_cluster.yaml`：

```yaml
# 上游集群配置
source:
  host: "localhost"
  port: 6001
  user: "root"
  password: "111"
  account: "account0"  # 上游账户
  database: "test_db"

# 下游集群配置
target:
  host: "localhost"
  port: 6002
  user: "root"
  password: "111"
  account: "account1"  # 下游账户（需要被上游授权）
  database: "test_db"

# CDC配置
cdc_config:
  sync_level: "database"  # account, database, table
  sync_interval: 60       # 同步间隔（秒）
```

### 步骤3: 运行测试

```bash
# 运行基础测试
python main.py --scenario cross_cluster --group basic

# 运行分区表测试
python main.py --scenario cross_cluster --group partition

# 使用跨集群专用测试用例
python main.py --scenario cross_cluster --testcase cross_cluster_tests.yaml
```

## 同步级别说明

### 1. Database级别同步

复制整个数据库下的所有表：

```yaml
cdc_config:
  sync_level: "database"
```

**适用场景**：
- 需要同步整个数据库
- 数据库中的表结构相对稳定

### 2. Table级别同步

只复制指定的单张表：

```yaml
cdc_config:
  sync_level: "table"

source:
  database: "test_db"
  table: "cdc_test_base"  # 指定表名

target:
  database: "test_db"
  table: "cdc_test_base"
```

**适用场景**：
- 只需要同步特定表
- 需要精细控制同步范围

### 3. Account级别同步

复制整个账户下的所有数据库和表：

```yaml
cdc_config:
  sync_level: "account"
```

**适用场景**：
- 需要完整的账户级别备份
- 跨集群的灾备场景

## 测试场景

### 基础同步测试

测试基本的数据同步功能：

```bash
python main.py --scenario cross_cluster --group basic
```

包含的测试：
- 基础表数据同步
- UPDATE操作同步
- DELETE操作同步
- 复合主键表同步
- 索引数据一致性

### 分区表测试

测试分区表的跨集群同步：

```bash
python main.py --scenario cross_cluster --group partition
```

包含的测试：
- Range分区表同步
- Hash分区表同步
- List分区表同步

### 全文索引测试

测试全文索引表的同步（耗时较长）：

```bash
python main.py --scenario cross_cluster --group fulltext
```

### 向量索引测试

测试向量索引表的同步：

```bash
python main.py --scenario cross_cluster --group vector
```

## 监控和调试

### 查看Subscription状态

在下游集群执行：

```sql
-- 查看所有订阅
SHOW CCPR SUBSCRIPTIONS;

-- 查看特定订阅详情
SHOW CCPR SUBSCRIPTION test_db;
```

### 状态字段说明

| 状态值 | 说明 |
|--------|------|
| 0 | running - 正常运行 |
| 1 | error - 出现错误 |
| 2 | pause - 已暂停 |
| 3 | dropped - 已删除 |

### 处理同步错误

如果订阅状态为 error (1)：

1. 查看错误信息：
```sql
SHOW CCPR SUBSCRIPTION test_db;
```

2. 检查 `error_message` 字段

3. 解决问题后恢复订阅：
```sql
RESUME CCPR SUBSCRIPTION test_db;
```

### 暂停和恢复订阅

```sql
-- 暂停订阅
PAUSE CCPR SUBSCRIPTION test_db;

-- 恢复订阅
RESUME CCPR SUBSCRIPTION test_db;
```

## 性能调优

### 调整同步间隔

根据业务需求调整 `sync_interval`：

```yaml
cdc_config:
  sync_interval: 30  # 更频繁的同步（30秒）
  # sync_interval: 300  # 较低频率的同步（5分钟）
```

**建议**：
- 实时性要求高：30-60秒
- 批量同步场景：120-300秒
- 最小值建议不低于30秒

### 批量数据生成

生成大量数据进行性能测试：

```bash
# 生成10万条数据
python generate_data.py \
  --host localhost \
  --port 6001 \
  --database test_db \
  --group basic \
  --count 100000 \
  --batch-size 5000
```

## 常见问题

### Q1: 同步延迟较大

**可能原因**：
- 上游集群负载高
- 网络延迟
- sync_interval 设置过长

**解决方法**：
- 检查上游集群性能
- 优化网络连接
- 调整 sync_interval 参数

### Q2: Subscription创建失败

**可能原因**：
- 下游账户未被上游授权
- Publication不存在
- 连接字符串错误

**解决方法**：
- 确认上游已创建Publication并授权
- 检查连接参数是否正确
- 查看错误日志

### Q3: 数据不一致

**可能原因**：
- 同步尚未完成
- 存在同步错误

**解决方法**：
- 等待足够的同步时间
- 检查Subscription状态
- 查看error_message

## 清理测试环境

测试完成后清理：

```sql
-- 在下游集群删除订阅
DROP CCPR SUBSCRIPTION test_db;

-- 在上游集群删除Publication
DROP PUBLICATION pub_test_xxx;

-- 删除测试数据库（可选）
DROP DATABASE test_db;
```

## 参考资料

- [MatrixOne CCPR 官方文档](../development%20document/Cross-Cluster%20Replication)
- [测试工具 README](../README.md)
