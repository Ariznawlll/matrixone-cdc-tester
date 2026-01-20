# MatrixOne CDC 测试工具架构文档

## 概述

本文档详细说明 MatrixOne CDC 测试工具的架构设计、核心组件和工作流程。

## 设计目标

1. **统一测试用例** - 同一套测试用例适用于所有CDC场景
2. **场景自动适配** - 根据配置自动选择对应的适配器
3. **全类型覆盖** - 覆盖所有 MatrixOne 数据类型和约束
4. **灵活可扩展** - 易于添加新场景、新类型、新测试用例

## 架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户层                                   │
├─────────────────────────────────────────────────────────────────┤
│  main.py                    generate_data.py                     │
│  (测试执行)                  (数据生成)                          │
└────────────────┬────────────────────────────┬────────────────────┘
                 │                            │
                 ▼                            ▼
┌─────────────────────────────────┐  ┌──────────────────────────┐
│      核心引擎层                  │  │     数据生成层            │
├─────────────────────────────────┤  ├──────────────────────────┤
│  TestRunner                     │  │  DataGenerator           │
│  - 加载配置                      │  │  - 生成各类型数据         │
│  - 选择适配器                    │  │  - 支持所有MO类型         │
│  - 执行测试用例                  │  │                          │
│  - 生成报告                      │  │  TableInserter           │
│                                 │  │  - 批量插入               │
│  ConfigLoader                   │  │  - 支持所有表类型         │
│  - 加载场景配置                  │  │                          │
│  - 加载测试用例                  │  │                          │
└────────────┬────────────────────┘  └──────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      适配器层 (Adapter Pattern)                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  BaseAdapter (抽象基类)                                          │
│  ├─ connect()           - 建立连接                              │
│  ├─ disconnect()        - 断开连接                              │
│  ├─ setup_cdc()         - 配置CDC                               │
│  ├─ teardown_cdc()      - 清理CDC                               │
│  ├─ execute_on_source() - 源库操作                              │
│  ├─ execute_on_target() - 目标库操作                            │
│  └─ validate_sync()     - 验证同步                              │
│                                                                  │
├──────────────────┬──────────────────┬──────────────────────────┤
│                  │                  │                          │
│  MoToMoAdapter   │ MoToMysqlAdapter │ CrossClusterAdapter      │
│  (单集群内CDC)    │ (跨数据库CDC)     │ (跨集群CCPR)             │
│                  │                  │                          │
│  - 标准CDC配置    │ - 类型映射        │ - Publication管理        │
│  - 同步验证       │ - 兼容性处理      │ - Subscription管理       │
│                  │                  │ - 状态监控               │
└──────────────────┴──────────────────┴──────────────────────────┘
             │                  │                  │
             ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                         数据库层                                 │
├─────────────────────────────────────────────────────────────────┤
│  MatrixOne (源)    MatrixOne (目标)    MySQL (目标)              │
└─────────────────────────────────────────────────────────────────┘
```

## 核心组件

### 1. 测试引擎 (TestRunner)

**职责**：
- 加载场景配置和测试用例
- 根据场景类型创建对应的适配器
- 执行测试用例并收集结果
- 生成测试报告

**关键方法**：
```python
class TestRunner:
    def __init__(self, scenario: str)
    def run_tests(self, testcase_file: str, test_group: str)
    def _run_single_test(self, test_case: Dict)
    def _execute_step(self, step: Dict, table: str)
    def _print_summary()
```

### 2. 适配器层 (Adapters)

#### BaseAdapter (抽象基类)

定义所有适配器必须实现的接口：

```python
class BaseAdapter(ABC):
    @abstractmethod
    def connect()
    
    @abstractmethod
    def disconnect()
    
    @abstractmethod
    def setup_cdc()
    
    @abstractmethod
    def teardown_cdc()
    
    @abstractmethod
    def execute_on_source(sql: str, params: tuple)
    
    @abstractmethod
    def execute_on_target(sql: str, params: tuple)
    
    @abstractmethod
    def validate_sync(table: str, timeout: int)
```

#### MoToMoAdapter (单集群CDC)

**特点**：
- 源和目标都是 MatrixOne
- 使用标准的 CDC 配置
- 简单的同步验证

**使用场景**：
- 同一集群内的数据库间同步
- 开发测试环境

#### MoToMysqlAdapter (跨数据库CDC)

**特点**：
- 源是 MatrixOne，目标是 MySQL
- 需要处理类型映射
- 兼容性验证

**使用场景**：
- 数据迁移到 MySQL
- 与 MySQL 生态集成

#### CrossClusterAdapter (跨集群CCPR)

**特点**：
- 基于 MatrixOne CCPR 功能
- Publication/Subscription 管理
- 支持三种同步级别（Account/Database/Table）
- 状态监控和错误处理

**关键实现**：
```python
class CrossClusterAdapter(BaseAdapter):
    def setup_cdc(self):
        # 1. 创建 Publication
        self._create_publication(sync_level)
        
        # 2. 创建 Subscription
        self._create_subscription(sync_level, sync_interval)
    
    def teardown_cdc(self):
        # 1. 删除 Subscription
        # 2. 删除 Publication
    
    def check_subscription_status(self):
        # 查询 SHOW CCPR SUBSCRIPTION
```

### 3. 数据生成层

#### DataGenerator

**职责**：生成各种数据类型的随机测试数据

**支持的类型**：
- 整数类型：TINYINT, SMALLINT, INT, BIGINT (含 UNSIGNED)
- 小数类型：DECIMAL, FLOAT, DOUBLE
- 字符串类型：CHAR, VARCHAR, TEXT, ENUM
- 二进制类型：BINARY, VARBINARY, BLOB, BIT
- 日期时间：TIME, DATE, DATETIME, TIMESTAMP, YEAR
- 特殊类型：BOOL, JSON, VECTOR

**关键方法**：
```python
class DataGenerator:
    def generate_tinyint(unsigned: bool)
    def generate_varchar(max_length: int)
    def generate_json()
    def generate_vector(dimension: int)
    def generate_base_table_row()
```

#### TableInserter

**职责**：批量插入测试数据到各种表

**支持的表类型**：
- 基础表
- 复合主键表
- 全文索引表
- 向量索引表
- 分区表（Range/Hash/List）

**关键方法**：
```python
class TableInserter:
    def insert_base_table(count: int, table_name: str)
    def insert_composite_pk_table(count: int)
    def insert_fulltext_table(count: int)
    def insert_vector_index_table(count: int)
    def insert_partition_range_table(count: int)
```

### 4. 表结构定义

#### TableDefinitions

**职责**：定义所有测试表的结构

**表分组**：
```python
TABLE_GROUPS = {
    'basic': ['base', 'composite_pk'],
    'fulltext': ['fulltext'],
    'vector': ['vector_index'],
    'partition': ['partition_range', 'partition_hash', 'partition_list']
}
```

**基础表结构**：
```sql
CREATE TABLE cdc_test_base (
    -- 主键
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    
    -- 整数类型 (8种)
    col_tinyint TINYINT NOT NULL DEFAULT 0,
    col_smallint SMALLINT,
    col_int INT,
    col_bigint BIGINT,
    col_tinyint_unsigned TINYINT UNSIGNED,
    col_smallint_unsigned SMALLINT UNSIGNED,
    col_int_unsigned INT UNSIGNED,
    col_bigint_unsigned BIGINT UNSIGNED,
    
    -- 小数类型 (3种)
    col_decimal DECIMAL(10, 2) DEFAULT 0.00,
    col_float FLOAT,
    col_double DOUBLE,
    
    -- 位类型
    col_bit BIT(8),
    
    -- 字符串类型 (4种)
    col_char CHAR(50),
    col_varchar VARCHAR(255) NOT NULL DEFAULT '',
    col_text TEXT,
    col_enum ENUM('A', 'B', 'C', 'D') DEFAULT 'A',
    
    -- 二进制类型 (3种)
    col_binary BINARY(16),
    col_varbinary VARBINARY(255),
    col_blob BLOB,
    
    -- JSON类型
    col_json JSON,
    
    -- 日期时间类型 (5种)
    col_time TIME,
    col_date DATE,
    col_datetime DATETIME DEFAULT CURRENT_TIMESTAMP,
    col_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    col_year YEAR,
    
    -- 布尔类型
    col_bool BOOL DEFAULT FALSE,
    
    -- 向量类型
    col_vector VECF32(512),
    
    -- 索引列
    idx_col1 INT,
    idx_col2 VARCHAR(100),
    unique_col VARCHAR(100),
    
    -- 索引定义
    INDEX idx_single (idx_col1),
    INDEX idx_composite (idx_col1, idx_col2),
    UNIQUE INDEX idx_unique (unique_col)
)
```

## 工作流程

### 数据生成流程

```
用户执行 generate_data.py
    ↓
ConfigLoader 加载配置
    ↓
连接数据库
    ↓
根据 table_group 选择表
    ↓
创建表结构 (TableDefinitions)
    ↓
DataGenerator 生成数据
    ↓
TableInserter 批量插入
    ↓
完成
```

### 测试执行流程

```
用户执行 main.py
    ↓
ConfigLoader 加载场景配置和测试用例
    ↓
TestRunner 创建对应的 Adapter
    ↓
Adapter.connect() - 建立连接
    ↓
Adapter.setup_cdc() - 配置CDC
    ↓
根据 test_group 筛选测试用例
    ↓
循环执行每个测试用例:
    ├─ 执行测试步骤
    ├─ 验证同步结果
    └─ 记录测试结果
    ↓
Adapter.teardown_cdc() - 清理CDC
    ↓
Adapter.disconnect() - 断开连接
    ↓
生成测试报告
```

### 跨集群CDC (CCPR) 流程

```
用户执行 main.py --scenario cross_cluster
    ↓
CrossClusterAdapter 初始化
    ↓
连接上游和下游集群
    ↓
在上游创建 Publication:
    CREATE PUBLICATION pub_name DATABASE db_name ACCOUNT target_account
    ↓
在下游创建 Subscription:
    CREATE DATABASE db_name 
    FROM 'connection_string' 
    PUBLICATION pub_name 
    SYNC INTERVAL 60
    ↓
执行测试用例
    ↓
验证同步状态:
    - 检查行数
    - 检查数据一致性
    - 查询 SHOW CCPR SUBSCRIPTION
    ↓
清理:
    - DROP CCPR SUBSCRIPTION
    - DROP PUBLICATION
```

## 配置文件结构

### 场景配置 (scenarios/*.yaml)

```yaml
scenario_name: "场景名称"
scenario_type: "mo_to_mo | mo_to_mysql | cross_cluster"

source:
  host: "主机"
  port: 端口
  user: "用户"
  password: "密码"
  database: "数据库"
  account: "账户"  # CCPR专用

target:
  host: "主机"
  port: 端口
  user: "用户"
  password: "密码"
  database: "数据库"
  account: "账户"  # CCPR专用

cdc_config:
  sync_level: "database"  # CCPR: account/database/table
  sync_interval: 60       # CCPR: 同步间隔（秒）
  
validation:
  check_interval: 10      # 检查间隔（秒）
  max_wait_time: 180      # 最大等待时间（秒）
```

### 测试用例配置 (testcases/*.yaml)

```yaml
test_suite:
  name: "测试套件名称"
  description: "描述"

test_groups:
  basic:
    - "TC001"
    - "TC002"
  partition:
    - "TC008"

test_cases:
  - id: "TC001"
    name: "测试名称"
    description: "描述"
    table: "表名"
    steps:
      - action: "validate_sync"
        timeout: 120
      - action: "update"
        sql: "UPDATE ..."
```

## 扩展指南

### 添加新的CDC场景

1. 创建配置文件：`config/scenarios/new_scenario.yaml`
2. 创建适配器：`src/adapters/new_scenario_adapter.py`
3. 继承 `BaseAdapter` 并实现所有抽象方法
4. 在 `TestRunner.ADAPTER_MAP` 注册

```python
class NewScenarioAdapter(BaseAdapter):
    def connect(self):
        # 实现连接逻辑
        pass
    
    def setup_cdc(self):
        # 实现CDC配置
        pass
    
    # ... 实现其他方法
```

### 添加新的数据类型

1. 在 `DataGenerator` 添加生成方法
2. 在 `TableDefinitions` 更新表结构
3. 在 `TableInserter` 更新插入逻辑

### 添加新的测试用例

在测试用例文件中添加：

```yaml
test_cases:
  - id: "TC_NEW"
    name: "新测试"
    table: "表名"
    steps:
      - action: "自定义动作"
        参数: 值
```

在 `TestRunner._execute_step()` 中处理新动作。

## 最佳实践

1. **数据量控制**
   - 快速测试：100-1000 条
   - 常规测试：1000-10000 条
   - 性能测试：100000+ 条

2. **测试分组**
   - 基础测试优先
   - 全文索引单独测试
   - 分区表单独测试

3. **错误处理**
   - 使用 try-finally 确保清理
   - 记录详细的错误信息
   - 提供恢复建议

4. **性能优化**
   - 批量插入数据
   - 合理设置同步间隔
   - 并行执行独立测试

## 总结

本测试工具通过适配器模式实现了统一的测试框架，支持多种CDC场景。核心设计理念是：

- **统一接口** - 所有场景使用相同的测试用例
- **灵活配置** - 通过YAML配置文件控制行为
- **易于扩展** - 添加新场景只需实现适配器
- **全面覆盖** - 覆盖所有数据类型和约束

这使得测试工作更加高效、可维护和可扩展。
