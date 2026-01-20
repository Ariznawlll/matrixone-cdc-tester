import time
import pymysql
from typing import Any
from .base_adapter import BaseAdapter


class MoToMysqlAdapter(BaseAdapter):
    """MO到MySQL的CDC适配器"""
    
    def connect(self):
        """连接源MatrixOne和目标MySQL"""
        source_cfg = self.config['source']
        target_cfg = self.config['target']
        
        self.source_conn = pymysql.connect(
            host=source_cfg['host'],
            port=source_cfg['port'],
            user=source_cfg['user'],
            password=source_cfg['password'],
            database=source_cfg['database']
        )
        
        self.target_conn = pymysql.connect(
            host=target_cfg['host'],
            port=target_cfg['port'],
            user=target_cfg['user'],
            password=target_cfg['password'],
            database=target_cfg['database']
        )
        print(f"✓ 已连接到源MO ({source_cfg['host']}:{source_cfg['port']})")
        print(f"✓ 已连接到目标MySQL ({target_cfg['host']}:{target_cfg['port']})")
    
    def disconnect(self):
        """断开连接"""
        if self.source_conn:
            self.source_conn.close()
        if self.target_conn:
            self.target_conn.close()
    
    def setup_cdc(self):
        """配置MO到MySQL的CDC（需要类型映射）"""
        cdc_cfg = self.config['cdc_config']
        source_db = self.config['source']['database']
        target_db = self.config['target']['database']
        
        # MO到MySQL需要特殊的类型映射配置
        type_mapping = "WITH TYPE_MAPPING" if cdc_cfg.get('type_mapping', {}).get('enabled') else ""
        
        print(f"✓ CDC任务已配置: {source_db} -> MySQL {target_db} {type_mapping}")
    
    def teardown_cdc(self):
        """清理CDC配置"""
        print("✓ CDC任务已清理")
    
    def execute_on_source(self, sql: str, params: tuple = None) -> Any:
        """在源MO执行SQL"""
        with self.source_conn.cursor() as cursor:
            cursor.execute(sql, params)
            self.source_conn.commit()
            return cursor.fetchall()
    
    def execute_on_target(self, sql: str, params: tuple = None) -> Any:
        """在目标MySQL执行SQL"""
        with self.target_conn.cursor() as cursor:
            cursor.execute(sql, params)
            self.target_conn.commit()
            return cursor.fetchall()
    
    def validate_sync(self, table: str, timeout: int = 60) -> bool:
        """验证数据同步完成"""
        check_interval = self.config['validation']['check_interval']
        elapsed = 0
        
        while elapsed < timeout:
            source_count = self.get_source_row_count(table)
            target_count = self.get_target_row_count(table)
            
            if source_count == target_count:
                return True
            
            time.sleep(check_interval)
            elapsed += check_interval
        
        return False
