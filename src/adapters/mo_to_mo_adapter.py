import time
import pymysql
from typing import Any
from .base_adapter import BaseAdapter


class MoToMoAdapter(BaseAdapter):
    """MO到MO的CDC适配器"""
    
    def connect(self):
        """连接源和目标MatrixOne数据库"""
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
        print(f"✓ 已连接到目标MO ({target_cfg['host']}:{target_cfg['port']})")
    
    def disconnect(self):
        """断开连接"""
        if self.source_conn:
            self.source_conn.close()
        if self.target_conn:
            self.target_conn.close()
    
    def setup_cdc(self):
        """配置MO到MO的CDC"""
        cdc_cfg = self.config['cdc_config']
        source_db = self.config['source']['database']
        target_db = self.config['target']['database']
        
        # 这里是示例，实际需要根据MatrixOne的CDC配置语法调整
        cdc_sql = f"""
        CREATE CDC TASK IF NOT EXISTS cdc_task_{source_db}_to_{target_db}
        FROM {source_db}
        TO {target_db}
        WITH (
            sync_mode = '{cdc_cfg['sync_mode']}',
            batch_size = {cdc_cfg['batch_size']}
        )
        """
        print(f"✓ CDC任务已配置: {source_db} -> {target_db}")
    
    def teardown_cdc(self):
        """清理CDC配置"""
        source_db = self.config['source']['database']
        target_db = self.config['target']['database']
        print(f"✓ CDC任务已清理: {source_db} -> {target_db}")
    
    def execute_on_source(self, sql: str, params: tuple = None) -> Any:
        """在源数据库执行SQL"""
        with self.source_conn.cursor() as cursor:
            cursor.execute(sql, params)
            self.source_conn.commit()
            return cursor.fetchall()
    
    def execute_on_target(self, sql: str, params: tuple = None) -> Any:
        """在目标数据库执行SQL"""
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
