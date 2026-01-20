from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseAdapter(ABC):
    """CDC场景适配器基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.source_conn = None
        self.target_conn = None
    
    @abstractmethod
    def connect(self):
        """建立源和目标数据库连接"""
        pass
    
    @abstractmethod
    def disconnect(self):
        """断开连接"""
        pass
    
    @abstractmethod
    def setup_cdc(self):
        """配置CDC同步"""
        pass
    
    @abstractmethod
    def teardown_cdc(self):
        """清理CDC配置"""
        pass
    
    @abstractmethod
    def execute_on_source(self, sql: str, params: tuple = None) -> Any:
        """在源数据库执行SQL"""
        pass
    
    @abstractmethod
    def execute_on_target(self, sql: str, params: tuple = None) -> Any:
        """在目标数据库执行SQL"""
        pass
    
    @abstractmethod
    def validate_sync(self, table: str, timeout: int = 60) -> bool:
        """验证数据同步完成"""
        pass
    
    def get_source_row_count(self, table: str) -> int:
        """获取源表行数"""
        result = self.execute_on_source(f"SELECT COUNT(*) FROM {table}")
        return result[0][0] if result else 0
    
    def get_target_row_count(self, table: str) -> int:
        """获取目标表行数"""
        result = self.execute_on_target(f"SELECT COUNT(*) FROM {table}")
        return result[0][0] if result else 0
    
    def compare_data(self, table: str, where_clause: str = None) -> bool:
        """比较源和目标数据"""
        where = f" WHERE {where_clause}" if where_clause else ""
        source_data = self.execute_on_source(f"SELECT * FROM {table}{where} ORDER BY id")
        target_data = self.execute_on_target(f"SELECT * FROM {table}{where} ORDER BY id")
        return source_data == target_data
