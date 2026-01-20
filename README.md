# MatrixOne CDC 测试工具

一个统一的 MatrixOne CDC 测试框架，支持多种 CDC 场景的自动化测试，覆盖所有 MatrixOne 数据类型和约束。

## 特性

✨ **统一测试用例** - 同一套测试用例适用于所有CDC场景  
🔄 **自动场景切换** - 根据配置自动选择对应的适配器  
📊 **详细测试报告** - 彩色输出，清晰的测试结果  
⚙️ **灵活配置** - YAML配置文件，易于维护和扩展  
🎯 **全类型覆盖** - 覆盖所有 MatrixOne 数据类型和列约束  
📈 **可控数据量** - 命令行控制测试数据生成量

## 支持的场景

1. **MO to MO** - MatrixOne 到 MatrixOne 的 CDC（单集群内）
2. **MO to MySQL** - MatrixOne 到 MySQL 的 CDC（含类型映射）
3. **Cross Cluster (CCPR)** - 跨集群的 CDC（基于 MatrixOne CCPR 功能）
4. **Flink CDC** - MySQL 到 MatrixOne 的 CDC（通过 Flink CDC + Kafka）

## 架构设计

### 核心组件

```
┌─────────────────────────────────────────────────────────────┐
│                      测试框架                                │
├─────────────────────────────────────────────────────────────┤
│  main.py (入口)                                              │
│  generate_data.py (数据生成)                                 │
├─────────────────────────────────────────────────────────────┤
│  TestRunner (测试引擎)                                       │
│    ├─ 加载配置                                               │
│    ├─ 选择适配器                                             │
│    ├─ 执行测试用例                                           │
│    └─ 生成报告                                               │
├─────────────────────────────────────────────────────────────┤
│  适配器层 (Adapter Pattern)                                  │
│    ├─ BaseAdapter (基类)                                     │
│    ├─ MoToMoAdapter (单集群)                                 │
│    ├─ MoToMysqlAdapter (跨数据库)                            │
│    ├─ CrossClusterAdapter (跨集群CCPR)                       │
│    └─ FlinkCdcAdapter (Flink CDC)                            │
├─────────────────────────────────────────────────────────────┤
│  数据层                                                      │
│    ├─ DataGenerator (数据生成器)                             │
│    ├─ TableInserter (批量插入)                               │
│    └─ TableDefinitions (表结构定义)                          │
└─────────────────────────────────────────────────────────────┘
```

### 表结构设计

工具提供了7种测试表，覆盖所有MatrixOne数据类型和约束：

1. **cdc_test_base** - 基础表
   - 覆盖所有数据类型（30+种）
   - 单列主键、索引、唯一索引
   
2. **cdc_test_composite_pk** - 复合主键表
   - 测试复合主键的同步

3. **cdc_test_fulltext** - 全文索引表
   - 单独测试（耗时较长）

4. **cdc_test_vector_index** - 向量索引表
   - 测试向量类型和向量索引

5. **cdc_test_partition_range** - Range分区表
6. **cdc_test_partition_hash** - Hash分区表
7. **cdc_test_partition_list** - List分区表

## 覆盖的数据类型

### 整数类型
- TINYINT / TINYINT UNSIGNED
- SMALLINT / SMALLINT UNSIGNED
- INT / INT UNSIGNED
- BIGINT / BIGINT UNSIGNED

### 小数类型
- DECIMAL
- FLOAT
- DOUBLE

### 字符串类型
- CHAR
- VARCHAR
- TEXT
- ENUM

### 二进制类型
- BINARY
- VARBINARY
- BLOB
- BIT

### 日期时间类型
- TIME
- DATE
- DATETIME
- TIMESTAMP
- YEAR

### 其他类型
- BOOL
- JSON
- VECTOR (VECF32)

## 覆盖的列约束

- ✅ 单列主键 (PRIMARY KEY)
- ✅ 复合主键 (COMPOSITE PRIMARY KEY)
- ✅ 单列索引 (INDEX)
- ✅ 复合索引 (COMPOSITE INDEX)
- ✅ 唯一索引 (UNIQUE INDEX)
- ✅ 全文索引 (FULLTEXT INDEX)
- ✅ 向量索引 (VECTOR INDEX)
- ✅ NOT NULL 约束
- ✅ DEFAULT 约束
- ✅ AUTO_INCREMENT

## 测试表分组

### 基础表组 (basic)
- `cdc_test_base` - 覆盖所有数据类型和基础约束
- `cdc_test_composite_pk` - 复合主键表

### 全文索引组 (fulltext)
- `cdc_test_fulltext` - 全文索引表（单独测试，较耗时）

### 向量索引组 (vector)
- `cdc_test_vector_index` - 向量索引表

### 分区表组 (partition)
- `cdc_test_partition_range` - Range 分区表
- `cdc_test_partition_hash` - Hash 分区表
- `cdc_test_partition_list` - List 分区表

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置数据库连接

编辑 `config/scenarios/` 目录下的配置文件：

```yaml
# config/scenarios/mo_to_mo.yaml
source:
  host: "localhost"
  port: 6001
  user: "root"
  password: "111"
  database: "source_db"

target:
  host: "localhost"
  port: 6002
  user: "root"
  password: "111"
  database: "target_db"
```

### 3. 生成测试数据

```bash
# 生成基础表数据（1000条）并创建向量索引
python generate_data.py --host localhost --port 6001 --database source_db --group basic --count 1000 --create-indexes

# 生成全文索引表数据（500条）并创建全文索引
python generate_data.py --host localhost --port 6001 --database source_db --group fulltext --count 500 --create-indexes

# 生成向量索引表数据（1000条）并创建向量索引
python generate_data.py --host localhost --port 6001 --database source_db --group vector --count 1000 --create-indexes

# 生成分区表数据（10000条）
python generate_data.py --host localhost --port 6001 --database source_db --group partition --count 10000
```

> **性能提示**: 对于大数据量（>10000条），建议使用 `--create-indexes` 参数，先插入数据再创建索引，可显著提升插入速度。

### 4. 配置并启动 CDC

根据你的场景配置 MatrixOne CDC 任务（参考 MatrixOne CDC 文档）

### 5. 运行测试

```bash
# 列出所有可用场景
python main.py --list

# 运行 MO to MO 基础测试
python main.py --scenario mo_to_mo --group basic

# 运行 MO to MySQL 全文索引测试
python main.py --scenario mo_to_mysql --group fulltext

# 运行跨集群分区表测试
python main.py --scenario cross_cluster --group partition

# 运行 Flink CDC 测试
python main.py --scenario flink_cdc --group basic
```

## Flink CDC (MySQL to MO) 快速开始

Flink CDC 通过 Kafka 实现 MySQL 到 MatrixOne 的数据同步：

### 1. 克隆 Flink CDC 代码库

```bash
cd ~/code
git clone git@github.com:matrixorigin/flink-cdc.git
```

### 2. 配置 Flink CDC 路径

编辑 `config/scenarios/flink_cdc.yaml`：

```yaml
flink_cdc:
  path: "~/code/flink-cdc"  # 修改为你的实际路径
  tables:
    - "cdc_test_base"
  topic: "cdc_test_topic"
  consumer_batch_size: 2000
```

### 3. 在 MySQL 生成测试数据

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

### 4. 在 MO 创建表结构

```bash
python generate_data.py \
  --host localhost \
  --port 6001 \
  --database test_db \
  --group basic \
  --create-only
```

### 5. 运行 Flink CDC 测试

```bash
# 运行基础测试（会自动启动 Kafka、Producer、Consumer）
python main.py --scenario flink_cdc --group basic

# 使用 Flink CDC 专用测试用例
python main.py --scenario flink_cdc --testcase flink_cdc_tests.yaml
```

### 6. 监控同步状态

```bash
# 查看 Producer 日志
tail -f /tmp/flink_cdc_producer.log

# 查看 Consumer 日志
tail -f /tmp/flink_cdc_consumer.log

# 查看 Kafka 状态
cd ~/code/flink-cdc && docker-compose ps
```

详细的 Flink CDC 配置和使用指南请参考：[docs/FLINK_CDC_GUIDE.md](docs/FLINK_CDC_GUIDE.md)

## 跨集群CDC (CCPR) 快速开始

跨集群CDC使用MatrixOne的CCPR功能，配置流程略有不同：

### 1. 准备两个集群

- **上游集群**：localhost:6001
- **下游集群**：localhost:6002

### 2. 在上游集群创建账户和数据

```sql
-- 连接到上游集群 (localhost:6001)
-- 创建账户
CREATE ACCOUNT IF NOT EXISTS account0 ADMIN_NAME 'admin' IDENTIFIED BY 'password';
CREATE ACCOUNT IF NOT EXISTS account1 ADMIN_NAME 'admin' IDENTIFIED BY 'password';

-- 使用 account0 登录，创建数据库
CREATE DATABASE test_db;
```

### 3. 生成测试数据

```bash
# 在上游集群生成数据
python generate_data.py \
  --host localhost \
  --port 6001 \
  --database test_db \
  --group basic \
  --count 1000
```

### 4. 配置跨集群场景

编辑 `config/scenarios/cross_cluster.yaml`：

```yaml
source:
  host: "localhost"
  port: 6001
  account: "account0"  # 上游账户
  database: "test_db"

target:
  host: "localhost"
  port: 6002
  account: "account1"  # 下游账户（需要被授权）
  database: "test_db"

cdc_config:
  sync_level: "database"  # account, database, table
  sync_interval: 60       # 同步间隔（秒）
```

### 5. 运行跨集群测试

```bash
# 运行基础测试
python main.py --scenario cross_cluster --group basic

# 使用CCPR专用测试用例
python main.py --scenario cross_cluster --testcase cross_cluster_tests.yaml
```

### 6. 监控同步状态

在下游集群执行：

```sql
-- 查看所有订阅
SHOW CCPR SUBSCRIPTIONS;

-- 查看特定订阅详情
SHOW CCPR SUBSCRIPTION test_db;
```

详细的CCPR配置和使用指南请参考：[docs/CCPR_SETUP_GUIDE.md](docs/CCPR_SETUP_GUIDE.md)

## 完整工作流示例

```bash
# 1. 在源库生成测试数据
python generate_data.py --host localhost --port 6001 --database source_db --group basic --count 1000

# 2. 配置并启动 CDC（手动操作）

# 3. 运行 CDC 测试
python main.py --scenario mo_to_mo --group basic

# 4. 测试其他表组
python generate_data.py --host localhost --port 6001 --database source_db --group partition --count 5000
python main.py --scenario mo_to_mo --group partition
```

## 项目结构

```
matrixone-cdc-tester/
├── config/
│   ├── scenarios/              # CDC场景配置
│   │   ├── mo_to_mo.yaml
│   │   ├── mo_to_mysql.yaml
│   │   └── cross_cluster.yaml
│   └── testcases/              # 测试用例定义
│       └── common_tests.yaml
├── src/
│   ├── adapters/               # 场景适配器
│   │   ├── base_adapter.py
│   │   ├── mo_to_mo_adapter.py
│   │   ├── mo_to_mysql_adapter.py
│   │   └── cross_cluster_adapter.py
│   ├── core/                   # 核心引擎
│   │   ├── test_runner.py
│   │   └── config_loader.py
│   ├── schema/                 # 表结构定义
│   │   └── table_definitions.py
│   └── data/                   # 数据生成
│       ├── data_generator.py
│       └── table_inserter.py
├── main.py                     # 测试入口
├── generate_data.py            # 数据生成入口
└── requirements.txt
```

## 数据生成工具详解

### 命令行参数

```bash
python generate_data.py [OPTIONS]

必需参数:
  --database DB_NAME          数据库名称

可选参数:
  --host HOST                 数据库主机 (默认: localhost)
  --port PORT                 数据库端口 (默认: 6001)
  --user USER                 数据库用户 (默认: root)
  --password PASSWORD         数据库密码 (默认: 111)
  --group GROUP               表组 (basic/fulltext/vector/partition, 默认: basic)
  --count COUNT               每表数据量 (默认: 1000)
  --batch-size SIZE           批量插入大小 (默认: 1000)
  --create-only               只创建表结构，不插入数据
  --create-indexes            数据插入后创建索引（提升大数据量插入性能）
  --indexes-only              只创建索引，不创建表和插入数据
```

### 使用示例

```bash
# 只创建表结构
python generate_data.py --database test_db --group basic --create-only

# 生成小批量数据用于快速测试
python generate_data.py --database test_db --group basic --count 100

# 生成大批量数据用于性能测试（推荐使用 --create-indexes）
python generate_data.py --database test_db --group basic --count 100000 --batch-size 5000 --create-indexes

# 分步执行：先插入数据，后创建索引
python generate_data.py --database test_db --group basic --count 100000
python generate_data.py --database test_db --group basic --indexes-only

# 生成所有表组的数据
for group in basic fulltext vector partition; do
  python generate_data.py --database test_db --group $group --count 1000 --create-indexes
done
```

### 索引创建优化

为了提升大数据量插入性能，工具支持延迟创建索引：

- **basic 组**: 为 `cdc_test_base` 表的 `col_vector` 列创建向量索引（IVFFlat）
- **fulltext 组**: 为 `cdc_test_fulltext` 表创建3个全文索引
- **vector 组**: 为 `cdc_test_vector_index` 表的 `embedding` 列创建向量索引（IVFFlat）
- **partition 组**: 无延迟索引

**性能对比**（以10万条数据为例）：
- 不使用 `--create-indexes`: 插入时维护索引，较慢
- 使用 `--create-indexes`: 先插入数据再创建索引，速度提升 2-5 倍

## 测试用例说明

### 基础测试组 (basic)
- TC001: 基础表数据同步测试
- TC002: UPDATE 操作测试
- TC003: DELETE 操作测试
- TC004: 复合主键表同步测试
- TC005: 索引数据一致性测试

### 全文索引测试组 (fulltext)
- TC006: 全文索引表同步测试

### 向量索引测试组 (vector)
- TC007: 向量索引表同步测试

### 分区表测试组 (partition)
- TC008: Range 分区表同步测试
- TC009: Hash 分区表同步测试
- TC010: List 分区表同步测试

## 工作原理

### 适配器模式

每种 CDC 场景都有对应的适配器，实现统一的接口：

- `connect()` - 建立数据库连接
- `setup_cdc()` - 配置 CDC 任务
- `execute_on_source()` - 在源库执行操作
- `execute_on_target()` - 在目标库执行操作
- `validate_sync()` - 验证数据同步
- `teardown_cdc()` - 清理 CDC 配置

### 测试流程

1. 加载场景配置
2. 创建对应的适配器
3. 建立数据库连接
4. 配置 CDC 任务
5. 根据测试组筛选测试用例
6. 执行测试用例
7. 验证同步结果
8. 生成测试报告
9. 清理环境

## 扩展指南

### 添加新的数据类型

1. 在 `src/data/data_generator.py` 添加生成方法
2. 在 `src/schema/table_definitions.py` 更新表结构
3. 在 `src/data/table_inserter.py` 更新插入逻辑

### 添加新的测试场景

1. 在 `config/scenarios/` 创建新的配置文件
2. 在 `src/adapters/` 创建新的适配器类
3. 在 `TestRunner.ADAPTER_MAP` 注册新适配器

### 添加新的测试用例

在 `config/testcases/common_tests.yaml` 添加：

```yaml
test_cases:
  - id: "TC011"
    name: "自定义测试"
    description: "测试描述"
    table: "cdc_test_base"
    steps:
      - action: "update"
        sql: "UPDATE cdc_test_base SET col_int = 999 WHERE id = 1"
      - action: "validate_sync"
        timeout: 60
```

## 注意事项

- ⚠️ 全文索引测试较耗时，建议单独运行
- ⚠️ 向量索引需要 MatrixOne 支持 VECF32 类型
- ⚠️ 分区表测试需要确保 CDC 支持分区表同步
- ⚠️ 测试前请备份重要数据
- ⚠️ 根据实际的 MatrixOne CDC 语法调整配置

## 性能建议

- 基础测试：1000-10000 条数据
- 性能测试：100000+ 条数据
- 全文索引：建议 500-5000 条数据
- 向量索引：建议 1000-10000 条数据
- 批量插入大小：1000-5000 条/批

## License

MIT
