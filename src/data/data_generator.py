"""
数据生成器 - 为测试表生成随机数据
"""

import random
import string
import json
from datetime import datetime, timedelta, date, time
from typing import List, Dict, Any


class DataGenerator:
    """测试数据生成器"""
    
    def __init__(self, seed: int = None):
        if seed:
            random.seed(seed)
    
    # ========== 基础类型生成 ==========
    
    def generate_tinyint(self, unsigned: bool = False) -> int:
        """生成TINYINT"""
        return random.randint(0 if unsigned else -128, 255 if unsigned else 127)
    
    def generate_smallint(self, unsigned: bool = False) -> int:
        """生成SMALLINT"""
        return random.randint(0 if unsigned else -32768, 65535 if unsigned else 32767)
    
    def generate_int(self, unsigned: bool = False) -> int:
        """生成INT"""
        max_val = 4294967295 if unsigned else 2147483647
        min_val = 0 if unsigned else -2147483648
        return random.randint(min_val, max_val)
    
    def generate_bigint(self, unsigned: bool = False) -> int:
        """生成BIGINT"""
        if unsigned:
            return random.randint(0, 18446744073709551615)
        return random.randint(-9223372036854775808, 9223372036854775807)
    
    def generate_decimal(self, precision: int = 10, scale: int = 2) -> float:
        """生成DECIMAL"""
        max_val = 10 ** (precision - scale) - 1
        return round(random.uniform(-max_val, max_val), scale)
    
    def generate_float(self) -> float:
        """生成FLOAT"""
        return round(random.uniform(-1000000, 1000000), 2)
    
    def generate_double(self) -> float:
        """生成DOUBLE"""
        return round(random.uniform(-1000000000, 1000000000), 4)
    
    def generate_bit(self, length: int = 8) -> int:
        """生成BIT"""
        return random.randint(0, (1 << length) - 1)
    
    # ========== 字符串类型生成 ==========
    
    def generate_char(self, length: int = 50) -> str:
        """生成CHAR"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def generate_varchar(self, max_length: int = 255) -> str:
        """生成VARCHAR"""
        length = random.randint(1, max_length)
        return ''.join(random.choices(string.ascii_letters + string.digits + ' ', k=length))
    
    def generate_text(self, min_length: int = 100, max_length: int = 1000) -> str:
        """生成TEXT"""
        length = random.randint(min_length, max_length)
        words = ['Lorem', 'ipsum', 'dolor', 'sit', 'amet', 'consectetur', 
                 'adipiscing', 'elit', 'sed', 'do', 'eiusmod', 'tempor']
        return ' '.join(random.choices(words, k=length // 6))
    
    def generate_enum(self, values: List[str]) -> str:
        """生成ENUM"""
        return random.choice(values)
    
    # ========== 二进制类型生成 ==========
    
    def generate_binary(self, length: int = 16) -> bytes:
        """生成BINARY"""
        return bytes([random.randint(0, 255) for _ in range(length)])
    
    def generate_varbinary(self, max_length: int = 255) -> bytes:
        """生成VARBINARY"""
        length = random.randint(1, max_length)
        return bytes([random.randint(0, 255) for _ in range(length)])
    
    def generate_blob(self, max_length: int = 1000) -> bytes:
        """生成BLOB"""
        length = random.randint(100, max_length)
        return bytes([random.randint(0, 255) for _ in range(length)])
    
    # ========== JSON类型生成 ==========
    
    def generate_json(self) -> str:
        """生成JSON"""
        data = {
            'id': random.randint(1, 10000),
            'name': self.generate_varchar(20),
            'tags': [self.generate_varchar(10) for _ in range(random.randint(1, 5))],
            'metadata': {
                'created': datetime.now().isoformat(),
                'score': round(random.uniform(0, 100), 2)
            }
        }
        return json.dumps(data)
    
    # ========== 日期时间类型生成 ==========
    
    def generate_time(self) -> time:
        """生成TIME"""
        return time(random.randint(0, 23), random.randint(0, 59), random.randint(0, 59))
    
    def generate_date(self, start_year: int = 2020, end_year: int = 2025) -> date:
        """生成DATE"""
        start = date(start_year, 1, 1)
        end = date(end_year, 12, 31)
        delta = end - start
        random_days = random.randint(0, delta.days)
        return start + timedelta(days=random_days)
    
    def generate_datetime(self, start_year: int = 2020) -> datetime:
        """生成DATETIME"""
        start = datetime(start_year, 1, 1)
        end = datetime.now()
        delta = end - start
        random_seconds = random.randint(0, int(delta.total_seconds()))
        return start + timedelta(seconds=random_seconds)
    
    def generate_timestamp(self) -> datetime:
        """生成TIMESTAMP"""
        return self.generate_datetime()
    
    def generate_year(self) -> int:
        """生成YEAR"""
        return random.randint(1901, 2155)
    
    # ========== 其他类型生成 ==========
    
    def generate_bool(self) -> bool:
        """生成BOOL"""
        return random.choice([True, False])
    
    def generate_vector(self, dimension: int = 3) -> str:
        """生成VECTOR"""
        vector = [round(random.uniform(-1, 1), 6) for _ in range(dimension)]
        return json.dumps(vector)
    
    # ========== 表数据生成 ==========
    
    def generate_base_table_row(self) -> Dict[str, Any]:
        """生成基础表的一行数据"""
        return {
            'col_tinyint': self.generate_tinyint(),
            'col_smallint': self.generate_smallint(),
            'col_int': self.generate_int(),
            'col_bigint': self.generate_bigint(),
            'col_tinyint_unsigned': self.generate_tinyint(unsigned=True),
            'col_smallint_unsigned': self.generate_smallint(unsigned=True),
            'col_int_unsigned': self.generate_int(unsigned=True),
            'col_bigint_unsigned': self.generate_bigint(unsigned=True),
            'col_decimal': self.generate_decimal(),
            'col_float': self.generate_float(),
            'col_double': self.generate_double(),
            'col_bit': self.generate_bit(),
            'col_char': self.generate_char(50),
            'col_varchar': self.generate_varchar(255),
            'col_text': self.generate_text(),
            'col_enum': self.generate_enum(['A', 'B', 'C', 'D']),
            'col_binary': self.generate_binary(16),
            'col_varbinary': self.generate_varbinary(255),
            'col_blob': self.generate_blob(),
            'col_json': self.generate_json(),
            'col_time': self.generate_time(),
            'col_date': self.generate_date(),
            'col_datetime': self.generate_datetime(),
            'col_year': self.generate_year(),
            'col_bool': self.generate_bool(),
            'col_vector': self.generate_vector(3),
            'composite_key_part': self.generate_varchar(50),
            'idx_col1': self.generate_int(),
            'idx_col2': self.generate_varchar(100),
            'unique_col': self.generate_varchar(100)
        }
