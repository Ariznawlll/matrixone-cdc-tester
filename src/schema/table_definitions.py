"""
MatrixOne CDC 测试表定义
覆盖所有数据类型和列约束
"""

# 基础表 - 覆盖所有数据类型和约束
BASE_TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS cdc_test_base (
    -- 整数类型
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    col_tinyint TINYINT NOT NULL DEFAULT 0,
    col_smallint SMALLINT,
    col_int INT,
    col_bigint BIGINT,
    col_tinyint_unsigned TINYINT UNSIGNED,
    col_smallint_unsigned SMALLINT UNSIGNED,
    col_int_unsigned INT UNSIGNED,
    col_bigint_unsigned BIGINT UNSIGNED,
    
    -- 小数类型
    col_decimal DECIMAL(10, 2) DEFAULT 0.00,
    col_float FLOAT,
    col_double DOUBLE,
    
    -- 位类型
    col_bit BIT(8),
    
    -- 字符串类型
    col_char CHAR(50),
    col_varchar VARCHAR(255) NOT NULL DEFAULT '',
    col_text TEXT,
    col_enum ENUM('A', 'B', 'C', 'D') DEFAULT 'A',
    
    -- 二进制类型
    col_binary BINARY(16),
    col_varbinary VARBINARY(255),
    col_blob BLOB,
    
    -- JSON类型
    col_json JSON,
    
    -- 日期时间类型
    col_time TIME,
    col_date DATE,
    col_datetime DATETIME DEFAULT CURRENT_TIMESTAMP,
    col_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    col_year YEAR,
    
    -- 布尔类型
    col_bool BOOL DEFAULT FALSE,
    
    -- 向量类型
    col_vector VECF32(3),
    
    -- 复合主键辅助列
    composite_key_part VARCHAR(50) NOT NULL DEFAULT 'default',
    
    -- 索引测试列
    idx_col1 INT,
    idx_col2 VARCHAR(100),
    unique_col VARCHAR(100),
    
    -- 创建索引
    INDEX idx_single (idx_col1),
    INDEX idx_composite (idx_col1, idx_col2),
    UNIQUE INDEX idx_unique (unique_col)
)
"""

# 复合主键表
COMPOSITE_PK_TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS cdc_test_composite_pk (
    pk1 INT NOT NULL,
    pk2 VARCHAR(50) NOT NULL,
    col_data VARCHAR(255),
    col_int INT,
    col_datetime DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (pk1, pk2),
    INDEX idx_data (col_data)
)
"""

# 全文索引表（单独测试）
FULLTEXT_TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS cdc_test_fulltext (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255),
    content TEXT,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FULLTEXT INDEX ft_title (title),
    FULLTEXT INDEX ft_content (content),
    FULLTEXT INDEX ft_composite (title, description)
)
"""

# 向量索引表（单独测试）
VECTOR_INDEX_TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS cdc_test_vector_index (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    embedding VECF32(128),
    metadata JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    VECTOR INDEX vec_idx (embedding)
)
"""

# 分区表 - Range分区
PARTITION_RANGE_TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS cdc_test_partition_range (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    amount DECIMAL(10, 2),
    order_date DATE NOT NULL,
    status VARCHAR(20),
    INDEX idx_user (user_id)
)
PARTITION BY RANGE (YEAR(order_date)) (
    PARTITION p2020 VALUES LESS THAN (2021),
    PARTITION p2021 VALUES LESS THAN (2022),
    PARTITION p2022 VALUES LESS THAN (2023),
    PARTITION p2023 VALUES LESS THAN (2024),
    PARTITION p2024 VALUES LESS THAN (2025),
    PARTITION p_future VALUES LESS THAN MAXVALUE
)
"""

# 分区表 - Hash分区
PARTITION_HASH_TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS cdc_test_partition_hash (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    username VARCHAR(100),
    email VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user (user_id)
)
PARTITION BY HASH(user_id)
PARTITIONS 4
"""

# 分区表 - List分区
PARTITION_LIST_TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS cdc_test_partition_list (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    region VARCHAR(50) NOT NULL,
    city VARCHAR(100),
    population INT,
    data VARCHAR(255),
    INDEX idx_region (region)
)
PARTITION BY LIST COLUMNS(region) (
    PARTITION p_north VALUES IN ('Beijing', 'Tianjin', 'Hebei'),
    PARTITION p_east VALUES IN ('Shanghai', 'Jiangsu', 'Zhejiang'),
    PARTITION p_south VALUES IN ('Guangdong', 'Fujian', 'Hainan'),
    PARTITION p_west VALUES IN ('Sichuan', 'Chongqing', 'Yunnan')
)
"""

# 所有表定义的映射
TABLE_SCHEMAS = {
    'base': BASE_TABLE_SCHEMA,
    'composite_pk': COMPOSITE_PK_TABLE_SCHEMA,
    'fulltext': FULLTEXT_TABLE_SCHEMA,
    'vector_index': VECTOR_INDEX_TABLE_SCHEMA,
    'partition_range': PARTITION_RANGE_TABLE_SCHEMA,
    'partition_hash': PARTITION_HASH_TABLE_SCHEMA,
    'partition_list': PARTITION_LIST_TABLE_SCHEMA
}

# 表分组 - 用于测试组织
TABLE_GROUPS = {
    'basic': ['base', 'composite_pk'],
    'fulltext': ['fulltext'],
    'vector': ['vector_index'],
    'partition': ['partition_range', 'partition_hash', 'partition_list']
}
