# CDC 场景对比

## 四种 CDC 场景对比

| 特性 | MO to MO | MO to MySQL | Cross Cluster (CCPR) | Flink CDC |
|------|----------|-------------|---------------------|-----------|
| **源数据库** | MatrixOne | MatrixOne | MatrixOne | MySQL |
| **目标数据库** | MatrixOne | MySQL | MatrixOne | MatrixOne |
| **同步方式** | 直接CDC | 直接CDC | Publication/Subscription | Kafka消息队列 |
| **网络要求** | 同集群 | 跨数据库 | 跨集群 | 跨数据库 |
| **类型映射** | 不需要 | 需要 | 不需要 | 需要 |
| **中间件** | 无 | 无 | 无 | Kafka |
| **同步级别** | Table | Table | Account/Database/Table | Table |
| **配置复杂度** | 简单 | 中等 | 中等 | 复杂 |
| **适用场景** | 单集群内同步 | 迁移到MySQL | 跨集群备份/灾备 | MySQL迁移到MO |

## 场景选择指南

### 1. MO to MO
**适用场景**：
- 同一集群内的数据库间同步
- 开发测试环境
- 数据备份

**优势**：
- 配置简单
- 同步速度快
- 无需类型转换

**劣势**：
- 仅限单集群

### 2. MO to MySQL
**适用场景**：
- 数据迁移到 MySQL
- 与 MySQL 生态集成
- 兼容性测试

**优势**：
- 支持跨数据库
- 自动类型映射

**劣势**：
- 需要处理类型兼容性
- 部分 MO 特性不支持

### 3. Cross Cluster (CCPR)
**适用场景**：
- 跨集群数据同步
- 跨区域备份
- 灾备方案
- 读写分离

**优势**：
- 支持三种同步级别
- 自动管理 Publication/Subscription
- 状态监控完善
- 错误自动重试

**劣势**：
- 需要账户授权
- 网络延迟影响

### 4. Flink CDC
**适用场景**：
- MySQL 迁移到 MatrixOne
- 实时数据同步
- 数据集成

**优势**：
- 支持全量+增量同步
- 基于 binlog，实时性好
- 可扩展性强（Kafka）

**劣势**：
- 配置复杂
- 需要额外组件（Kafka）
- 资源消耗较大

## 性能对比

| 场景 | 同步延迟 | 吞吐量 | 资源消耗 |
|------|---------|--------|---------|
| MO to MO | 5-10s | 高 | 低 |
| MO to MySQL | 10-20s | 中 | 中 |
| Cross Cluster | 30-60s | 中 | 中 |
| Flink CDC | 10-30s | 高 | 高 |

## 配置复杂度对比

### MO to MO
```yaml
source:
  host: "localhost"
  port: 6001
target:
  host: "localhost"
  port: 6002
```
**复杂度**: ⭐

### MO to MySQL
```yaml
source:
  host: "localhost"
  port: 6001
target:
  type: "mysql"
  host: "localhost"
  port: 3306
cdc_config:
  type_mapping:
    enabled: true
```
**复杂度**: ⭐⭐

### Cross Cluster (CCPR)
```yaml
source:
  account: "account0"
  host: "cluster1.com"
target:
  account: "account1"
  host: "cluster2.com"
cdc_config:
  sync_level: "database"
  sync_interval: 60
```
**复杂度**: ⭐⭐⭐

### Flink CDC
```yaml
source:
  type: "mysql"
  host: "localhost"
target:
  type: "matrixone"
  host: "localhost"
flink_cdc:
  path: "~/code/flink-cdc"
  tables: ["table1", "table2"]
  topic: "cdc_topic"
  consumer_batch_size: 2000
```
**复杂度**: ⭐⭐⭐⭐

## 使用建议

### 开发测试
推荐：**MO to MO**
- 配置简单
- 快速验证

### 生产环境
推荐：**Cross Cluster (CCPR)**
- 功能完善
- 监控完善
- 错误处理好

### MySQL 迁移
推荐：**Flink CDC**
- 专为 MySQL 设计
- 全量+增量支持
- 实时性好

### 跨数据库集成
推荐：**MO to MySQL**
- 类型映射自动
- 兼容性好

## 测试建议

### 测试顺序
1. MO to MO（最简单）
2. MO to MySQL（中等）
3. Cross Cluster（复杂）
4. Flink CDC（最复杂）

### 数据量建议
- 快速测试：1000 条
- 常规测试：10000 条
- 性能测试：100000+ 条

### 测试重点

#### MO to MO
- 基础同步功能
- 性能测试

#### MO to MySQL
- 类型兼容性
- 数据一致性

#### Cross Cluster
- Publication/Subscription 管理
- 状态监控
- 错误恢复

#### Flink CDC
- Kafka 稳定性
- Producer/Consumer 状态
- 全量+增量同步

## 总结

选择合适的 CDC 场景取决于：
1. 源和目标数据库类型
2. 网络环境
3. 性能要求
4. 运维复杂度
5. 业务需求

测试工具支持所有四种场景，使用统一的测试用例，方便对比和验证。
