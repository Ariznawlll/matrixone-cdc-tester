# MatrixOne CDC 测试工具 - 使用检查清单

## 📋 快速检查清单

使用本工具前，请按照此清单逐项检查。

---

## 1️⃣ 环境准备

### Python环境
-  Python 3.7+ 已安装
-  pip 已安装并可用
-  虚拟环境已创建（推荐）

```bash
# 检查Python版本
python --version  # 应该 >= 3.7

# 创建虚拟环境（可选但推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 依赖安装
-  requirements.txt 中的依赖已安装

```bash
cd matrixone-cdc-tester
pip install -r requirements.txt
```

---

## 2️⃣ 数据库准备

### MO to MO 场景
-  源MatrixOne实例运行中
-  目标MatrixOne实例运行中
-  可以连接到两个实例
-  已创建测试数据库

```bash
# 测试连接
mysql -h localhost -P 6001 -u root -p
mysql -h localhost -P 6002 -u root -p
```

### MO to MySQL 场景
-  源MatrixOne实例运行中
-  目标MySQL实例运行中
-  可以连接到两个实例
-  已创建测试数据库

### Cross Cluster (CCPR) 场景
-  上游MatrixOne集群运行中
-  下游MatrixOne集群运行中
-  已创建上游账户 (account0)
-  已创建下游账户 (account1)
-  上游已创建测试数据库
-  网络连通性正常

```sql
-- 在上游集群执行
CREATE ACCOUNT IF NOT EXISTS account0 ADMIN_NAME 'admin' IDENTIFIED BY 'password';
CREATE ACCOUNT IF NOT EXISTS account1 ADMIN_NAME 'admin' IDENTIFIED BY 'password';
CREATE DATABASE test_db;
```

---

## 3️⃣ 配置文件

### 场景配置
-  已选择场景配置文件
-  数据库连接信息已更新
-  账户信息已配置（CCPR场景）
-  同步参数已设置

```bash
# 编辑配置文件
vim config/scenarios/cross_cluster.yaml
```

**必须配置的字段**：
-  source.host
-  source.port
-  source.user
-  source.password
-  source.database
-  target.host
-  target.port
-  target.user
-  target.password
-  target.database

**CCPR额外字段**：
-  source.account
-  target.account
-  cdc_config.sync_level
-  cdc_config.sync_interval

---

## 4️⃣ 数据生成

### 选择表组
-  已确定要测试的表组
  -  basic - 基础表和复合主键表
  -  fulltext - 全文索引表
  -  vector - 向量索引表
  -  partition - 分区表

### 确定数据量
-  已确定每表数据量
  -  快速测试: 100-1000
  -  常规测试: 1000-10000
  -  性能测试: 100000+

### 执行数据生成
-  数据生成命令已准备
-  数据已成功生成
-  数据已验证

```bash
# 示例命令
python generate_data.py \
  --host localhost \
  --port 6001 \
  --database test_db \
  --group basic \
  --count 1000
```

---

## 5️⃣ CDC配置

### MO to MO / MO to MySQL
-  CDC任务已手动配置
-  CDC任务运行正常
-  可以看到数据同步

### Cross Cluster (CCPR)
-  工具会自动创建Publication
-  工具会自动创建Subscription
-  无需手动配置CDC

---

## 6️⃣ 测试执行

### 测试前检查
-  配置文件正确
-  数据已生成
-  CDC已配置（非CCPR场景）
-  数据库连接正常

### 执行测试
-  测试命令已准备
-  测试组已选择

```bash
# 列出所有场景
python main.py --list

# 执行测试
python main.py --scenario cross_cluster --group basic
```

### 测试中监控
-  观察测试输出
-  检查错误信息
-  监控同步进度

---

## 7️⃣ 结果验证

### 测试报告
-  查看测试摘要
-  检查通过/失败数量
-  查看失败原因

### 数据验证
-  源库数据正确
-  目标库数据正确
-  数据一致性验证

```sql
-- 检查行数
SELECT COUNT(*) FROM cdc_test_base;

-- 检查数据
SELECT * FROM cdc_test_base LIMIT 10;
```

### CCPR状态检查
-  Subscription状态正常
-  无错误信息
-  同步延迟可接受

```sql
-- 在下游集群执行
SHOW CCPR SUBSCRIPTIONS;
SHOW CCPR SUBSCRIPTION test_db;
```

---

## 8️⃣ 清理工作

### 测试数据清理
-  决定是否保留测试数据
-  删除不需要的数据

```sql
-- 删除测试数据库（可选）
DROP DATABASE test_db;
```

### CDC清理
-  CCPR: 工具会自动清理
-  其他场景: 手动清理CDC任务

### 环境清理
-  退出虚拟环境（如果使用）
-  关闭数据库连接

---

## 🔍 故障排查检查清单

### 连接失败
-  检查主机地址
-  检查端口号
-  检查用户名密码
-  检查网络连通性
-  检查防火墙设置

### 数据生成失败
-  检查数据库连接
-  检查数据库权限
-  检查磁盘空间
-  检查表是否已存在

### 测试失败
-  检查配置文件
-  检查CDC状态
-  检查同步延迟
-  查看错误日志

### CCPR问题
-  检查账户是否创建
-  检查账户是否授权
-  检查Publication是否存在
-  检查Subscription状态
-  查看error_message字段

---

## 📊 性能检查清单

### 数据生成性能
-  批量大小合理 (1000-5000)
-  生成速度正常
-  无内存问题

### 测试执行性能
-  同步延迟可接受
-  测试时间合理
-  资源使用正常

### 优化建议
-  调整批量大小
-  调整同步间隔
-  调整数据量
-  使用表分组

---

## 📝 文档检查清单

### 使用前阅读
-  README.md - 了解项目
-  QUICK_START.md - 快速上手
-  场景配置文件 - 了解配置

### 深入学习
-  docs/ARCHITECTURE.md - 了解架构
-  docs/CCPR_SETUP_GUIDE.md - CCPR详细配置
-  PROJECT_SUMMARY.md - 项目总结

### 参考资料
-  FILE_MANIFEST.md - 文件清单
-  COMPLETION_REPORT.md - 完成报告
-  development document/ - 官方文档

---

## ✅ 完整工作流检查

### 第一次使用
1. [ ] 安装依赖
2. [ ] 准备数据库
3. [ ] 配置场景
4. [ ] 生成数据
5. [ ] 配置CDC（非CCPR）
6. [ ] 执行测试
7. [ ] 验证结果
8. [ ] 清理环境

### 日常使用
1. [ ] 检查配置
2. [ ] 生成数据
3. [ ] 执行测试
4. [ ] 验证结果

### 问题排查
1. [ ] 查看错误信息
2. [ ] 检查配置
3. [ ] 检查连接
4. [ ] 查看文档
5. [ ] 尝试解决方案

---

## 🎯 测试场景检查

### 基础测试 (basic)
-  数据已生成 (1000条)
-  测试已执行
-  结果已验证
-  基础表同步正常
-  复合主键表同步正常

### 全文索引测试 (fulltext)
-  数据已生成 (500-5000条)
-  测试已执行
-  结果已验证
-  全文索引同步正常

### 向量索引测试 (vector)
-  数据已生成 (1000条)
-  测试已执行
-  结果已验证
-  向量数据同步正常

### 分区表测试 (partition)
-  数据已生成 (5000-10000条)
-  测试已执行
-  结果已验证
-  Range分区同步正常
-  Hash分区同步正常
-  List分区同步正常

---

## 📞 获取帮助

### 命令行帮助
```bash
python main.py --help
python generate_data.py --help
python main.py --list
```

### 文档帮助
- README.md - 完整文档
- QUICK_START.md - 快速开始
- docs/ - 详细文档

### 常见问题
- 查看 docs/CCPR_SETUP_GUIDE.md 的"常见问题"部分
- 查看 COMPLETION_REPORT.md 的"已知限制"部分

---

## ✨ 最佳实践检查

### 数据量
-  快速测试: 100-1000条
-  常规测试: 1000-10000条
-  性能测试: 100000+条
-  全文索引: 500-5000条

### 测试顺序
-  1. 基础表测试
-  2. 分区表测试
-  3. 向量索引测试
-  4. 全文索引测试（最后）

### 监控
-  定期检查Subscription状态
-  监控同步延迟
-  关注错误日志
-  验证数据一致性

---

## 🎉 完成确认

全部检查完成后，你应该能够：

- ✅ 成功安装和配置工具
- ✅ 生成测试数据
- ✅ 执行CDC测试
- ✅ 验证测试结果
- ✅ 处理常见问题

**祝测试顺利！** 🚀

---

**版本**: 1.0.0  
**最后更新**: 2025-01-19
