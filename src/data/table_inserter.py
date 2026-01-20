"""
表数据插入器 - 批量插入测试数据
"""

import pymysql
from typing import Dict, Any, List
from .data_generator import DataGenerator
from ..schema.table_definitions import TABLE_SCHEMAS


class TableInserter:
    """表数据插入器"""
    
    def __init__(self, connection, batch_size: int = 1000):
        self.conn = connection
        self.batch_size = batch_size
        self.generator = DataGenerator()
    
    def insert_base_table(self, count: int, table_name: str = 'cdc_test_base'):
        """插入基础表数据"""
        print(f"正在向 {table_name} 插入 {count} 条数据...")
        
        inserted = 0
        while inserted < count:
            batch = min(self.batch_size, count - inserted)
            rows = [self.generator.generate_base_table_row() for _ in range(batch)]
            self._batch_insert_base(table_name, rows)
            inserted += batch
            if inserted % 10000 == 0:
                print(f"  已插入 {inserted}/{count} 条")
        
        print(f"✓ 完成插入 {count} 条数据到 {table_name}")
    
    def _batch_insert_base(self, table_name: str, rows: List[Dict[str, Any]]):
        """批量插入基础表"""
        if not rows:
            return
        
        columns = list(rows[0].keys())
        placeholders = ', '.join(['%s'] * len(columns))
        columns_str = ', '.join(columns)
        
        sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        
        with self.conn.cursor() as cursor:
            for row in rows:
                values = tuple(row[col] for col in columns)
                cursor.execute(sql, values)
            self.conn.commit()
    
    def insert_composite_pk_table(self, count: int, table_name: str = 'cdc_test_composite_pk'):
        """插入复合主键表数据"""
        print(f"正在向 {table_name} 插入 {count} 条数据...")
        
        sql = f"""
        INSERT INTO {table_name} (pk1, pk2, col_data, col_int, col_datetime)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        inserted = 0
        with self.conn.cursor() as cursor:
            while inserted < count:
                batch = min(self.batch_size, count - inserted)
                for i in range(batch):
                    pk1 = inserted + i + 1
                    pk2 = self.generator.generate_varchar(50)
                    col_data = self.generator.generate_varchar(255)
                    col_int = self.generator.generate_int()
                    col_datetime = self.generator.generate_datetime()
                    
                    cursor.execute(sql, (pk1, pk2, col_data, col_int, col_datetime))
                
                self.conn.commit()
                inserted += batch
                if inserted % 10000 == 0:
                    print(f"  已插入 {inserted}/{count} 条")
        
        print(f"✓ 完成插入 {count} 条数据到 {table_name}")
    
    def insert_fulltext_table(self, count: int, table_name: str = 'cdc_test_fulltext'):
        """插入全文索引表数据"""
        print(f"正在向 {table_name} 插入 {count} 条数据...")
        
        sql = f"""
        INSERT INTO {table_name} (title, content, description)
        VALUES (%s, %s, %s)
        """
        
        inserted = 0
        with self.conn.cursor() as cursor:
            while inserted < count:
                batch = min(self.batch_size, count - inserted)
                for _ in range(batch):
                    title = self.generator.generate_varchar(255)
                    content = self.generator.generate_text(500, 2000)
                    description = self.generator.generate_text(100, 500)
                    
                    cursor.execute(sql, (title, content, description))
                
                self.conn.commit()
                inserted += batch
                if inserted % 5000 == 0:
                    print(f"  已插入 {inserted}/{count} 条")
        
        print(f"✓ 完成插入 {count} 条数据到 {table_name}")
    
    def insert_vector_index_table(self, count: int, table_name: str = 'cdc_test_vector_index'):
        """插入向量索引表数据"""
        print(f"正在向 {table_name} 插入 {count} 条数据...")
        
        sql = f"""
        INSERT INTO {table_name} (name, embedding, metadata)
        VALUES (%s, %s, %s)
        """
        
        inserted = 0
        with self.conn.cursor() as cursor:
            while inserted < count:
                batch = min(self.batch_size, count - inserted)
                for _ in range(batch):
                    name = self.generator.generate_varchar(100)
                    embedding = self.generator.generate_vector(128)
                    metadata = self.generator.generate_json()
                    
                    cursor.execute(sql, (name, embedding, metadata))
                
                self.conn.commit()
                inserted += batch
                if inserted % 5000 == 0:
                    print(f"  已插入 {inserted}/{count} 条")
        
        print(f"✓ 完成插入 {count} 条数据到 {table_name}")
    
    def insert_partition_range_table(self, count: int, table_name: str = 'cdc_test_partition_range'):
        """插入Range分区表数据"""
        print(f"正在向 {table_name} 插入 {count} 条数据...")
        
        sql = f"""
        INSERT INTO {table_name} (user_id, amount, order_date, status)
        VALUES (%s, %s, %s, %s)
        """
        
        statuses = ['pending', 'processing', 'completed', 'cancelled']
        inserted = 0
        
        with self.conn.cursor() as cursor:
            while inserted < count:
                batch = min(self.batch_size, count - inserted)
                for _ in range(batch):
                    user_id = self.generator.generate_int(unsigned=True) % 100000
                    amount = self.generator.generate_decimal(10, 2)
                    order_date = self.generator.generate_date(2020, 2024)
                    status = self.generator.generate_enum(statuses)
                    
                    cursor.execute(sql, (user_id, amount, order_date, status))
                
                self.conn.commit()
                inserted += batch
                if inserted % 10000 == 0:
                    print(f"  已插入 {inserted}/{count} 条")
        
        print(f"✓ 完成插入 {count} 条数据到 {table_name}")
    
    def insert_partition_hash_table(self, count: int, table_name: str = 'cdc_test_partition_hash'):
        """插入Hash分区表数据"""
        print(f"正在向 {table_name} 插入 {count} 条数据...")
        
        sql = f"""
        INSERT INTO {table_name} (user_id, username, email)
        VALUES (%s, %s, %s)
        """
        
        inserted = 0
        with self.conn.cursor() as cursor:
            while inserted < count:
                batch = min(self.batch_size, count - inserted)
                for i in range(batch):
                    user_id = inserted + i + 1
                    username = f"user_{user_id}"
                    email = f"user{user_id}@example.com"
                    
                    cursor.execute(sql, (user_id, username, email))
                
                self.conn.commit()
                inserted += batch
                if inserted % 10000 == 0:
                    print(f"  已插入 {inserted}/{count} 条")
        
        print(f"✓ 完成插入 {count} 条数据到 {table_name}")
    
    def insert_partition_list_table(self, count: int, table_name: str = 'cdc_test_partition_list'):
        """插入List分区表数据"""
        print(f"正在向 {table_name} 插入 {count} 条数据...")
        
        sql = f"""
        INSERT INTO {table_name} (region, city, population, data)
        VALUES (%s, %s, %s, %s)
        """
        
        regions = {
            'Beijing': ['Beijing', 'Chaoyang', 'Haidian'],
            'Shanghai': ['Shanghai', 'Pudong', 'Minhang'],
            'Guangdong': ['Guangzhou', 'Shenzhen', 'Dongguan'],
            'Sichuan': ['Chengdu', 'Mianyang', 'Deyang']
        }
        
        inserted = 0
        with self.conn.cursor() as cursor:
            while inserted < count:
                batch = min(self.batch_size, count - inserted)
                for _ in range(batch):
                    region = self.generator.generate_enum(list(regions.keys()))
                    city = self.generator.generate_enum(regions[region])
                    population = self.generator.generate_int(unsigned=True) % 10000000
                    data = self.generator.generate_varchar(255)
                    
                    cursor.execute(sql, (region, city, population, data))
                
                self.conn.commit()
                inserted += batch
                if inserted % 10000 == 0:
                    print(f"  已插入 {inserted}/{count} 条")
        
        print(f"✓ 完成插入 {count} 条数据到 {table_name}")
