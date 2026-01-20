# MatrixOne CDC 测试工具 - 文件清单

## 项目文件结构

```
matrixone-cdc-tester/
│
├── 📄 主要文件
│   ├── main.py                     # 测试执行入口
│   ├── generate_data.py            # 数据生成入口
│   ├── requirements.txt            # Python依赖
│   ├── .gitignore                  # Git忽略配置
│   └── .editorconfig               # 编辑器配置
│
├── 📚 文档 (5个)
│   ├── README.md                   # 主文档（完整介绍）
│   ├── QUICK_START.md              # 快速开始指南
│   ├── PROJECT_SUMMARY.md          # 项目总结
│   ├── FILE_MANIFEST.md            # 文件清单（本文件）
│   └── docs/
│       ├── ARCHITECTURE.md         # 架构设计文档
│       └── CCPR_SETUP_GUIDE.md     # CCPR配置指南
│
├── ⚙️ 配置文件 (5个)
│   └── config/
│       ├── scenarios/              # CDC场景配置
│       │   ├── mo_to_mo.yaml       # MO到MO场景
│       │   ├── mo_to_mysql.yaml    # MO到MySQL场景
│       │   └── cross_cluster.yaml  # 跨集群场景
│       └── testcases/              # 测试用例
│           ├── common_tests.yaml   # 通用测试用例
│           └── cross_cluster_tests.yaml  # CCPR专用测试
│
├── 🔧 源代码 (16个Python文件)
│   └── src/
│       ├── __init__.py
│       ├── adapters/               # 场景适配器 (5个文件)
│       │   ├── __init__.py
│       │   ├── base_adapter.py     # 抽象基类
│       │   ├── mo_to_mo_adapter.py # MO到MO适配器
│       │   ├── mo_to_mysql_adapter.py  # MO到MySQL适配器
│       │   └── cross_cluster_adapter.py  # 跨集群适配器
│       ├── core/                   # 核心引擎 (3个文件)
│       │   ├── __init__.py
│       │   ├── test_runner.py      # 测试执行引擎
│       │   └── config_loader.py    # 配置加载器
│       ├── data/                   # 数据生成 (3个文件)
│       │   ├── __init__.py
│       │   ├── data_generator.py   # 数据生成器
│       │   └── table_inserter.py   # 批量插入器
│       └── schema/                 # 表结构 (2个文件)
│           ├── __init__.py
│           └── table_definitions.py  # 表结构定义
│
├── 📝 示例和脚本 (3个)
│   ├── examples/
│   │   ├── ccpr_example.sh         # CCPR完整示例脚本
│   │   └── custom_test.yaml        # 自定义测试示例
│   └── scripts/
│       └── setup_test_env.sh       # 环境初始化脚本
│
└── 📖 参考文档 (1个)
    └── development document/
        └── Cross-Cluster Replication  # MatrixOne CCPR官方文档
```

## 文件统计

| 类型 | 数量 | 说明 |
|------|------|------|
| Python文件 | 16 | 核心代码 |
| YAML配置 | 5 | 场景和测试配置 |
| Markdown文档 | 6 | 各类文档 |
| Shell脚本 | 2 | 自动化脚本 |
| 配置文件 | 3 | .gitignore, requirements.txt, .editorconfig |
| **总计** | **32** | **所有文件** |

## 核心文件说明

### 入口文件

#### main.py (测试执行入口)
```bash
# 功能：执行CDC测试
python main.py --scenario cross_cluster --group basic
```

**主要功能**：
- 列出所有可用场景
- 执行指定场景的测试
- 生成测试报告

#### generate_data.py (数据生成入口)
```bash
# 功能：生成测试数据
python generate_data.py --database test_db --group basic --count 1000
```

**主要功能**：
- 创建测试表结构
- 生成随机测试数据
- 批量插入数据

### 核心模块

#### src/core/test_runner.py (测试引擎)
**职责**：
- 加载配置和测试用例
- 创建适配器
- 执行测试
- 生成报告

**关键类**：`TestRunner`

#### src/adapters/base_adapter.py (适配器基类)
**职责**：
- 定义适配器接口
- 提供通用方法

**关键类**：`BaseAdapter` (抽象基类)

#### src/adapters/cross_cluster_adapter.py (跨集群适配器)
**职责**：
- 实现CCPR功能
- Publication/Subscription管理
- 状态监控

**关键类**：`CrossClusterAdapter`

#### src/data/data_generator.py (数据生成器)
**职责**：
- 生成30+种数据类型
- 随机但合理的数据

**关键类**：`DataGenerator`

#### src/schema/table_definitions.py (表结构定义)
**职责**：
- 定义7种测试表
- 覆盖所有数据类型和约束

**关键常量**：
- `TABLE_SCHEMAS` - 表结构字典
- `TABLE_GROUPS` - 表分组

### 配置文件

#### config/scenarios/cross_cluster.yaml (跨集群场景配置)
```yaml
source:          # 上游集群配置
target:          # 下游集群配置
cdc_config:      # CDC配置
validation:      # 验证配置
```

#### config/testcases/common_tests.yaml (通用测试用例)
```yaml
test_suite:      # 测试套件信息
test_groups:     # 测试分组
test_cases:      # 测试用例列表
```

### 文档文件

#### README.md (主文档)
- 完整的项目介绍
- 详细的使用说明
- 架构设计概述
- 扩展指南

#### QUICK_START.md (快速开始)
- 5分钟快速上手
- 常用命令
- 快速参考

#### docs/ARCHITECTURE.md (架构文档)
- 详细的架构设计
- 组件说明
- 工作流程
- 扩展指南

#### docs/CCPR_SETUP_GUIDE.md (CCPR配置指南)
- CCPR详细配置
- 使用场景
- 监控和调试
- 故障排查

#### PROJECT_SUMMARY.md (项目总结)
- 项目概述
- 核心特性
- 技术实现
- 最佳实践

## 代码行数统计

| 模块 | 文件数 | 估计行数 |
|------|--------|---------|
| 适配器层 | 5 | ~800 |
| 核心引擎 | 3 | ~400 |
| 数据生成 | 3 | ~600 |
| 表结构定义 | 2 | ~400 |
| 入口文件 | 2 | ~400 |
| **总计** | **15** | **~2600** |

## 依赖关系

```
main.py
  └── TestRunner (src/core/test_runner.py)
      ├── ConfigLoader (src/core/config_loader.py)
      └── Adapters (src/adapters/)
          ├── BaseAdapter
          ├── MoToMoAdapter
          ├── MoToMysqlAdapter
          └── CrossClusterAdapter

generate_data.py
  ├── TableDefinitions (src/schema/table_definitions.py)
  ├── DataGenerator (src/data/data_generator.py)
  └── TableInserter (src/data/table_inserter.py)
```

## 配置依赖

```
TestRunner
  ├── 读取: config/scenarios/*.yaml
  └── 读取: config/testcases/*.yaml

DataGenerator
  └── 使用: src/schema/table_definitions.py
```

## 使用流程

### 1. 数据生成流程
```
generate_data.py
  → ConfigLoader
  → 连接数据库
  → TableDefinitions (创建表)
  → DataGenerator (生成数据)
  → TableInserter (插入数据)
```

### 2. 测试执行流程
```
main.py
  → TestRunner
  → ConfigLoader (加载配置)
  → 创建 Adapter
  → 执行测试用例
  → 生成报告
```

## 快速导航

### 想要快速开始？
👉 阅读 [QUICK_START.md](QUICK_START.md)

### 想要了解架构？
👉 阅读 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

### 想要配置CCPR？
👉 阅读 [docs/CCPR_SETUP_GUIDE.md](docs/CCPR_SETUP_GUIDE.md)

### 想要了解项目全貌？
👉 阅读 [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

### 想要查看完整文档？
👉 阅读 [README.md](README.md)

## 文件用途速查

| 文件 | 用途 | 何时使用 |
|------|------|---------|
| main.py | 执行测试 | 运行CDC测试时 |
| generate_data.py | 生成数据 | 准备测试数据时 |
| config/scenarios/*.yaml | 场景配置 | 配置CDC场景时 |
| config/testcases/*.yaml | 测试用例 | 定义测试用例时 |
| src/adapters/*.py | 适配器实现 | 添加新场景时 |
| src/data/*.py | 数据生成 | 添加新数据类型时 |
| src/schema/*.py | 表结构 | 添加新表时 |
| docs/*.md | 文档 | 学习和参考时 |
| examples/*.sh | 示例脚本 | 快速演示时 |

## 版本信息

- **版本**: 1.0.0
- **创建日期**: 2025-01-19
- **文件总数**: 32
- **代码行数**: ~2600
- **文档页数**: ~50

---

**提示**: 本文件清单会随项目更新而更新。
