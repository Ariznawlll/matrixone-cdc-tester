#!/usr/bin/env python3
"""
数据生成脚本 - 为CDC测试表生成数据
支持命令行控制数据量
"""

import argparse
import pymysql
import sys
from colorama import Fore, Style, init
from src.schema.table_definitions import TABLE_SCHEMAS, TABLE_GROUPS, INDEX_CREATION_SQLS
from src.data.table_inserter import TableInserter

init(autoreset=True)


def create_connection(host: str, port: int, user: str, password: str, database: str):
    """创建数据库连接"""
    try:
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4'
        )
        print(f"{Fore.GREEN}✓ 已连接到数据库 {host}:{port}/{database}{Style.RESET_ALL}")
        return conn
    except Exception as e:
        print(f"{Fore.RED}✗ 连接失败: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)


def create_tables(conn, table_group: str = 'basic'):
    """创建测试表"""
    print(f"\n{Fore.CYAN}创建测试表 (组: {table_group})...{Style.RESET_ALL}")
    
    tables = TABLE_GROUPS.get(table_group, [])
    if not tables:
        print(f"{Fore.RED}✗ 未知的表组: {table_group}{Style.RESET_ALL}")
        return False
    
    with conn.cursor() as cursor:
        for table_key in tables:
            schema = TABLE_SCHEMAS.get(table_key)
            if schema:
                try:
                    cursor.execute(schema)
                    conn.commit()
                    print(f"{Fore.GREEN}✓ 创建表: cdc_test_{table_key}{Style.RESET_ALL}")
                except pymysql.err.OperationalError as e:
                    # 检查是否是表已存在的错误
                    if 'already exists' in str(e).lower() or 'table' in str(e).lower() and 'exists' in str(e).lower():
                        print(f"{Fore.YELLOW}⚠ 表已存在: cdc_test_{table_key}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}✗ 创建表失败 (cdc_test_{table_key}): {str(e)}{Style.RESET_ALL}")
                        return False
                except Exception as e:
                    print(f"{Fore.RED}✗ 创建表失败 (cdc_test_{table_key}): {str(e)}{Style.RESET_ALL}")
                    return False
    
    return True


def generate_data(conn, table_group: str, count: int, batch_size: int = 1000):
    """生成测试数据"""
    print(f"\n{Fore.CYAN}生成测试数据 (每表 {count} 条)...{Style.RESET_ALL}\n")
    
    inserter = TableInserter(conn, batch_size)
    tables = TABLE_GROUPS.get(table_group, [])
    
    for table_key in tables:
        table_name = f"cdc_test_{table_key}"
        
        try:
            if table_key == 'base':
                inserter.insert_base_table(count, table_name)
            elif table_key == 'composite_pk':
                inserter.insert_composite_pk_table(count, table_name)
            elif table_key == 'fulltext':
                inserter.insert_fulltext_table(count, table_name)
            elif table_key == 'vector_index':
                inserter.insert_vector_index_table(count, table_name)
            elif table_key == 'partition_range':
                inserter.insert_partition_range_table(count, table_name)
            elif table_key == 'partition_hash':
                inserter.insert_partition_hash_table(count, table_name)
            elif table_key == 'partition_list':
                inserter.insert_partition_list_table(count, table_name)
        except Exception as e:
            print(f"{Fore.RED}✗ 插入数据失败 ({table_name}): {str(e)}{Style.RESET_ALL}")
            continue


def create_indexes(conn, table_group: str):
    """创建索引（数据插入后执行以提升性能）"""
    print(f"\n{Fore.CYAN}创建索引 (组: {table_group})...{Style.RESET_ALL}\n")
    
    tables = TABLE_GROUPS.get(table_group, [])
    index_created = False
    
    with conn.cursor() as cursor:
        for table_key in tables:
            if table_key in INDEX_CREATION_SQLS:
                index_sql = INDEX_CREATION_SQLS[table_key]
                try:
                    print(f"正在为 cdc_test_{table_key} 创建索引...")
                    cursor.execute(index_sql)
                    conn.commit()
                    print(f"{Fore.GREEN}✓ 索引创建成功: cdc_test_{table_key}{Style.RESET_ALL}")
                    index_created = True
                except Exception as e:
                    print(f"{Fore.RED}✗ 索引创建失败 (cdc_test_{table_key}): {str(e)}{Style.RESET_ALL}")
    
    if not index_created:
        print(f"{Fore.YELLOW}⚠ 该表组没有需要延迟创建的索引{Style.RESET_ALL}")



def main():
    parser = argparse.ArgumentParser(
        description='MatrixOne CDC 测试数据生成工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 生成基础表数据（1000条）
  python generate_data.py --host localhost --port 6001 --database test_db --count 1000
  
  # 生成全文索引表数据（500条），数据插入后创建索引
  python generate_data.py --host localhost --port 6001 --database test_db --group fulltext --count 500 --create-indexes
  
  # 生成分区表数据（10000条）
  python generate_data.py --host localhost --port 6001 --database test_db --group partition --count 10000
  
  # 只创建表结构，不插入数据
  python generate_data.py --host localhost --port 6001 --database test_db --create-only
  
  # 只创建索引（表和数据已存在）
  python generate_data.py --host localhost --port 6001 --database test_db --group fulltext --indexes-only

表组说明:
  basic     - 基础表和复合主键表（默认）
  fulltext  - 全文索引表（建议使用 --create-indexes）
  vector    - 向量索引表
  partition - 分区表（Range/Hash/List）

性能优化:
  对于大数据量插入，建议使用 --create-indexes 选项
  这样会先插入数据，然后再创建索引，可以显著提升插入速度
        """
    )
    
    # 数据库连接参数
    parser.add_argument('--host', default='localhost', help='数据库主机 (默认: localhost)')
    parser.add_argument('--port', type=int, default=6001, help='数据库端口 (默认: 6001)')
    parser.add_argument('--user', default='root', help='数据库用户 (默认: root)')
    parser.add_argument('--password', default='111', help='数据库密码 (默认: 111)')
    parser.add_argument('--database', required=True, help='数据库名称')
    
    # 数据生成参数
    parser.add_argument('--group', default='basic', 
                       choices=['basic', 'fulltext', 'vector', 'partition'],
                       help='表组 (默认: basic)')
    parser.add_argument('--count', type=int, default=1000, 
                       help='每个表生成的数据量 (默认: 1000)')
    parser.add_argument('--batch-size', type=int, default=1000,
                       help='批量插入大小 (默认: 1000)')
    parser.add_argument('--create-only', action='store_true',
                       help='只创建表结构，不插入数据')
    parser.add_argument('--create-indexes', action='store_true',
                       help='创建索引（在数据插入后执行，提升大数据量插入性能）')
    parser.add_argument('--indexes-only', action='store_true',
                       help='只创建索引，不创建表和插入数据')
    
    args = parser.parse_args()
    
    # 连接数据库
    conn = create_connection(args.host, args.port, args.user, args.password, args.database)
    
    try:
        # 只创建索引模式
        if args.indexes_only:
            create_indexes(conn, args.group)
            print(f"\n{Fore.GREEN}{'='*60}")
            print(f"✓ 索引创建完成!")
            print(f"{'='*60}{Style.RESET_ALL}\n")
            return 0
        
        # 创建表
        if not create_tables(conn, args.group):
            return 1
        
        # 生成数据
        if not args.create_only:
            generate_data(conn, args.group, args.count, args.batch_size)
            
            # 如果指定了 --create-indexes，在数据插入后创建索引
            if args.create_indexes:
                create_indexes(conn, args.group)
        
        print(f"\n{Fore.GREEN}{'='*60}")
        print(f"✓ 数据生成完成!")
        print(f"{'='*60}{Style.RESET_ALL}\n")
        
        return 0
    
    finally:
        conn.close()


if __name__ == '__main__':
    sys.exit(main())
