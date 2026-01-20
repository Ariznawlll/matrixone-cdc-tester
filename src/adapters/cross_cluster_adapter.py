import time
import pymysql
from typing import Any, Dict
from .base_adapter import BaseAdapter


class CrossClusterAdapter(BaseAdapter):
    """跨集群CDC适配器 - 基于MatrixOne CCPR"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.publication_name = None
        self.subscription_name = None
    
    def connect(self):
        """连接不同集群的MatrixOne"""
        source_cfg = self.config['source']
        target_cfg = self.config['target']
        
        # 连接上游集群（Publication端）
        self.source_conn = pymysql.connect(
            host=source_cfg['host'],
            port=source_cfg['port'],
            user=source_cfg['user'],
            password=source_cfg['password'],
            database=source_cfg.get('database', 'mysql'),
            charset='utf8mb4'
        )
        
        # 连接下游集群（Subscription端）
        self.target_conn = pymysql.connect(
            host=target_cfg['host'],
            port=target_cfg['port'],
            user=target_cfg['user'],
            password=target_cfg['password'],
            database=target_cfg.get('database', 'mysql'),
            charset='utf8mb4'
        )
        
        source_account = source_cfg.get('account', 'sys')
        target_account = target_cfg.get('account', 'sys')
        print(f"✓ 已连接到上游集群 {source_account}@{source_cfg['host']}:{source_cfg['port']}")
        print(f"✓ 已连接到下游集群 {target_account}@{target_cfg['host']}:{target_cfg['port']}")
    
    def disconnect(self):
        """断开连接"""
        if self.source_conn:
            self.source_conn.close()
        if self.target_conn:
            self.target_conn.close()
    
    def setup_cdc(self):
        """配置跨集群CDC - 创建Publication和Subscription"""
        cdc_cfg = self.config['cdc_config']
        source_cfg = self.config['source']
        target_cfg = self.config['target']
        
        sync_level = cdc_cfg.get('sync_level', 'database')
        sync_interval = cdc_cfg.get('sync_interval', 60)
        
        # 生成唯一的Publication和Subscription名称
        timestamp = int(time.time())
        self.publication_name = f"pub_test_{timestamp}"
        self.subscription_name = f"sub_test_{timestamp}"
        
        print(f"\n配置跨集群CDC:")
        print(f"  - 同步级别: {sync_level}")
        print(f"  - 同步间隔: {sync_interval}秒")
        
        # 步骤1: 在上游创建Publication
        self._create_publication(sync_level)
        
        # 步骤2: 在下游创建Subscription
        self._create_subscription(sync_level, sync_interval)
        
        print(f"✓ 跨集群CDC配置完成")
    
    def _create_publication(self, sync_level: str):
        """在上游集群创建Publication"""
        source_cfg = self.config['source']
        target_cfg = self.config['target']
        target_account = target_cfg.get('account', 'sys')
        
        try:
            with self.source_conn.cursor() as cursor:
                if sync_level == 'database':
                    database = source_cfg.get('database', 'test_db')
                    sql = f"CREATE PUBLICATION {self.publication_name} DATABASE {database} ACCOUNT {target_account}"
                    cursor.execute(sql)
                    print(f"  ✓ 创建Publication: {self.publication_name} (DATABASE {database})")
                
                elif sync_level == 'table':
                    database = source_cfg.get('database', 'test_db')
                    table = source_cfg.get('table', 'cdc_test_base')
                    sql = f"CREATE PUBLICATION {self.publication_name} DATABASE {database} TABLE {table} ACCOUNT {target_account}"
                    cursor.execute(sql)
                    print(f"  ✓ 创建Publication: {self.publication_name} (TABLE {database}.{table})")
                
                elif sync_level == 'account':
                    sql = f"CREATE PUBLICATION {self.publication_name} ACCOUNT {target_account}"
                    cursor.execute(sql)
                    print(f"  ✓ 创建Publication: {self.publication_name} (ACCOUNT级别)")
                
                self.source_conn.commit()
        
        except Exception as e:
            print(f"  ✗ 创建Publication失败: {str(e)}")
            raise
    
    def _create_subscription(self, sync_level: str, sync_interval: int):
        """在下游集群创建Subscription"""
        source_cfg = self.config['source']
        target_cfg = self.config['target']
        
        # 构建连接字符串
        source_account = source_cfg.get('account', 'sys')
        source_user = source_cfg.get('user', 'root')
        source_password = source_cfg.get('password', '111')
        source_host = source_cfg['host']
        source_port = source_cfg['port']
        
        conn_str = f"mysql://{source_account}#{source_user}:{source_password}@{source_host}:{source_port}"
        
        try:
            with self.target_conn.cursor() as cursor:
                if sync_level == 'database':
                    database = target_cfg.get('database', 'test_db')
                    sql = f"""
                    CREATE DATABASE IF NOT EXISTS {database}
                    FROM '{conn_str}'
                    PUBLICATION {self.publication_name}
                    SYNC INTERVAL {sync_interval}
                    """
                    cursor.execute(sql)
                    self.subscription_name = database
                    print(f"  ✓ 创建Subscription: {database} (DATABASE级别)")
                
                elif sync_level == 'table':
                    database = target_cfg.get('database', 'test_db')
                    table = target_cfg.get('table', 'cdc_test_base')
                    sql = f"""
                    CREATE TABLE IF NOT EXISTS {database}.{table}
                    FROM '{conn_str}'
                    PUBLICATION {self.publication_name}
                    SYNC INTERVAL {sync_interval}
                    """
                    cursor.execute(sql)
                    self.subscription_name = f"{database}.{table}"
                    print(f"  ✓ 创建Subscription: {database}.{table} (TABLE级别)")
                
                self.target_conn.commit()
        
        except Exception as e:
            print(f"  ✗ 创建Subscription失败: {str(e)}")
            raise
    
    def teardown_cdc(self):
        """清理CDC配置 - 删除Subscription和Publication"""
        print("\n清理跨集群CDC配置:")
        
        # 步骤1: 删除Subscription
        if self.subscription_name:
            try:
                with self.target_conn.cursor() as cursor:
                    sql = f"DROP CCPR SUBSCRIPTION {self.subscription_name}"
                    cursor.execute(sql)
                    self.target_conn.commit()
                    print(f"  ✓ 删除Subscription: {self.subscription_name}")
            except Exception as e:
                print(f"  ⚠ 删除Subscription失败: {str(e)}")
        
        # 步骤2: 删除Publication
        if self.publication_name:
            try:
                with self.source_conn.cursor() as cursor:
                    sql = f"DROP PUBLICATION {self.publication_name}"
                    cursor.execute(sql)
                    self.source_conn.commit()
                    print(f"  ✓ 删除Publication: {self.publication_name}")
            except Exception as e:
                print(f"  ⚠ 删除Publication失败: {str(e)}")
    
    def execute_on_source(self, sql: str, params: tuple = None) -> Any:
        """在源集群执行SQL"""
        with self.source_conn.cursor() as cursor:
            cursor.execute(sql, params)
            self.source_conn.commit()
            return cursor.fetchall()
    
    def execute_on_target(self, sql: str, params: tuple = None) -> Any:
        """在目标集群执行SQL"""
        with self.target_conn.cursor() as cursor:
            cursor.execute(sql, params)
            self.target_conn.commit()
            return cursor.fetchall()
    
    def validate_sync(self, table: str, timeout: int = 120) -> bool:
        """验证跨集群数据同步"""
        check_interval = self.config['validation'].get('check_interval', 10)
        elapsed = 0
        
        print(f"  等待数据同步 (超时: {timeout}s)...")
        
        while elapsed < timeout:
            try:
                source_count = self.get_source_row_count(table)
                target_count = self.get_target_row_count(table)
                
                print(f"    源: {source_count} 行, 目标: {target_count} 行 ({elapsed}s)")
                
                if source_count == target_count and source_count > 0:
                    print(f"  ✓ 数据同步完成")
                    return True
            
            except Exception as e:
                print(f"    检查同步状态时出错: {str(e)}")
            
            time.sleep(check_interval)
            elapsed += check_interval
        
        return False
    
    def check_subscription_status(self) -> Dict[str, Any]:
        """检查Subscription状态"""
        try:
            with self.target_conn.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = f"SHOW CCPR SUBSCRIPTION {self.subscription_name}"
                cursor.execute(sql)
                result = cursor.fetchone()
                return result if result else {}
        except Exception as e:
            print(f"  ⚠ 查询Subscription状态失败: {str(e)}")
            return {}
