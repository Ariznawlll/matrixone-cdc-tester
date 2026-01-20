"""
Flink CDC 适配器 - MySQL 到 MO 通过 Flink CDC
使用 Kafka 作为消息队列
"""

import time
import subprocess
import pymysql
import os
from typing import Any, Dict, List
from .base_adapter import BaseAdapter


class FlinkCdcAdapter(BaseAdapter):
    """Flink CDC适配器 - MySQL到MO通过Kafka"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.producer_process = None
        self.consumer_process = None
        self.kafka_process = None
        self.flink_cdc_path = config.get('flink_cdc', {}).get('path', '../flink-cdc')
    
    def connect(self):
        """连接MySQL（源）和MatrixOne（目标）"""
        source_cfg = self.config['source']
        target_cfg = self.config['target']
        
        # 连接MySQL源
        self.source_conn = pymysql.connect(
            host=source_cfg['host'],
            port=source_cfg['port'],
            user=source_cfg['user'],
            password=source_cfg['password'],
            database=source_cfg['database'],
            charset='utf8mb4'
        )
        
        # 连接MatrixOne目标
        self.target_conn = pymysql.connect(
            host=target_cfg['host'],
            port=target_cfg['port'],
            user=target_cfg['user'],
            password=target_cfg['password'],
            database=target_cfg['database'],
            charset='utf8mb4'
        )
        
        print(f"✓ 已连接到MySQL源 ({source_cfg['host']}:{source_cfg['port']})")
        print(f"✓ 已连接到MO目标 ({target_cfg['host']}:{target_cfg['port']})")
    
    def disconnect(self):
        """断开连接"""
        if self.source_conn:
            self.source_conn.close()
        if self.target_conn:
            self.target_conn.close()
    
    def setup_cdc(self):
        """配置Flink CDC - 启动Kafka、Producer和Consumer"""
        flink_cfg = self.config.get('flink_cdc', {})
        source_cfg = self.config['source']
        
        database = source_cfg['database']
        tables = flink_cfg.get('tables', ['cdc_test_base'])
        topic = flink_cfg.get('topic', 'cdc_test_topic')
        consumer_batch_size = flink_cfg.get('consumer_batch_size', 2000)
        group = flink_cfg.get('group', 'cdc_test_group')
        
        print(f"\n配置Flink CDC:")
        print(f"  - 数据库: {database}")
        print(f"  - 表: {', '.join(tables)}")
        print(f"  - Kafka Topic: {topic}")
        print(f"  - Consumer Batch Size: {consumer_batch_size}")
        
        # 步骤1: 启动Kafka
        self._start_kafka()
        
        # 步骤2: 启动Producer
        self._start_producer(database, tables, topic)
        
        # 步骤3: 启动Consumer
        self._start_consumer(database, topic, consumer_batch_size, group)
        
        # 等待服务启动
        print("  等待Flink CDC服务启动...")
        time.sleep(10)
        
        print(f"✓ Flink CDC配置完成")
    
    def _start_kafka(self):
        """启动Kafka（使用docker-compose）"""
        try:
            print("  启动Kafka...")
            
            # 检查Kafka是否已经运行
            check_cmd = f"cd {self.flink_cdc_path} && docker-compose ps | grep kafka"
            result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
            
            if "Up" in result.stdout:
                print("  ✓ Kafka已在运行")
                return
            
            # 启动Kafka
            start_cmd = f"cd {self.flink_cdc_path} && docker-compose up -d"
            subprocess.run(start_cmd, shell=True, check=True)
            
            # 等待Kafka启动
            time.sleep(15)
            print("  ✓ Kafka已启动")
            
        except Exception as e:
            print(f"  ✗ 启动Kafka失败: {str(e)}")
            raise
    
    def _start_producer(self, database: str, tables: List[str], topic: str):
        """启动Producer"""
        try:
            print(f"  启动Producer (database={database}, tables={','.join(tables)}, topic={topic})...")
            
            tables_str = ','.join(tables)
            script_path = os.path.join(self.flink_cdc_path, 'scripts/producer-realtime.sh')
            
            cmd = [
                script_path,
                '--db', database,
                '--tables', tables_str,
                '--topic', topic
            ]
            
            # 启动Producer进程（后台运行）
            log_file = open('/tmp/flink_cdc_producer.log', 'w')
            self.producer_process = subprocess.Popen(
                cmd,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                cwd=self.flink_cdc_path
            )
            
            time.sleep(5)
            
            # 检查进程是否还在运行
            if self.producer_process.poll() is None:
                print(f"  ✓ Producer已启动 (PID: {self.producer_process.pid})")
            else:
                raise Exception("Producer启动后立即退出")
            
        except Exception as e:
            print(f"  ✗ 启动Producer失败: {str(e)}")
            raise
    
    def _start_consumer(self, database: str, topic: str, batch_size: int, group: str):
        """启动Consumer"""
        try:
            print(f"  启动Consumer (database={database}, topic={topic}, batch_size={batch_size})...")
            
            script_path = os.path.join(self.flink_cdc_path, 'scripts/consumer.sh')
            
            cmd = [
                script_path,
                '--db', database,
                '--consumer-batch-size', str(batch_size),
                '--topic', topic,
                '--group', group
            ]
            
            # 启动Consumer进程（后台运行）
            log_file = open('/tmp/flink_cdc_consumer.log', 'w')
            self.consumer_process = subprocess.Popen(
                cmd,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                cwd=self.flink_cdc_path
            )
            
            time.sleep(5)
            
            # 检查进程是否还在运行
            if self.consumer_process.poll() is None:
                print(f"  ✓ Consumer已启动 (PID: {self.consumer_process.pid})")
            else:
                raise Exception("Consumer启动后立即退出")
            
        except Exception as e:
            print(f"  ✗ 启动Consumer失败: {str(e)}")
            raise
    
    def teardown_cdc(self):
        """清理Flink CDC - 停止Producer、Consumer和Kafka"""
        print("\n清理Flink CDC:")
        
        # 停止Producer
        if self.producer_process:
            try:
                self.producer_process.terminate()
                self.producer_process.wait(timeout=10)
                print("  ✓ Producer已停止")
            except Exception as e:
                print(f"  ⚠ 停止Producer失败: {str(e)}")
                try:
                    self.producer_process.kill()
                except:
                    pass
        
        # 停止Consumer
        if self.consumer_process:
            try:
                self.consumer_process.terminate()
                self.consumer_process.wait(timeout=10)
                print("  ✓ Consumer已停止")
            except Exception as e:
                print(f"  ⚠ 停止Consumer失败: {str(e)}")
                try:
                    self.consumer_process.kill()
                except:
                    pass
        
        # 停止Kafka（可选）
        flink_cfg = self.config.get('flink_cdc', {})
        if flink_cfg.get('stop_kafka_on_teardown', False):
            try:
                stop_cmd = f"cd {self.flink_cdc_path} && docker-compose down"
                subprocess.run(stop_cmd, shell=True, check=True)
                print("  ✓ Kafka已停止")
            except Exception as e:
                print(f"  ⚠ 停止Kafka失败: {str(e)}")
    
    def execute_on_source(self, sql: str, params: tuple = None) -> Any:
        """在MySQL源执行SQL"""
        with self.source_conn.cursor() as cursor:
            cursor.execute(sql, params)
            self.source_conn.commit()
            return cursor.fetchall()
    
    def execute_on_target(self, sql: str, params: tuple = None) -> Any:
        """在MO目标执行SQL"""
        with self.target_conn.cursor() as cursor:
            cursor.execute(sql, params)
            self.target_conn.commit()
            return cursor.fetchall()
    
    def validate_sync(self, table: str, timeout: int = 120) -> bool:
        """验证Flink CDC数据同步"""
        check_interval = self.config['validation'].get('check_interval', 10)
        elapsed = 0
        
        print(f"  等待Flink CDC同步 (超时: {timeout}s)...")
        
        while elapsed < timeout:
            try:
                source_count = self.get_source_row_count(table)
                target_count = self.get_target_row_count(table)
                
                print(f"    MySQL源: {source_count} 行, MO目标: {target_count} 行 ({elapsed}s)")
                
                if source_count == target_count and source_count > 0:
                    print(f"  ✓ Flink CDC同步完成")
                    return True
            
            except Exception as e:
                print(f"    检查同步状态时出错: {str(e)}")
            
            time.sleep(check_interval)
            elapsed += check_interval
        
        return False
    
    def check_producer_status(self) -> bool:
        """检查Producer状态"""
        if self.producer_process:
            return self.producer_process.poll() is None
        return False
    
    def check_consumer_status(self) -> bool:
        """检查Consumer状态"""
        if self.consumer_process:
            return self.consumer_process.poll() is None
        return False
    
    def get_producer_log(self, lines: int = 50) -> str:
        """获取Producer日志"""
        try:
            with open('/tmp/flink_cdc_producer.log', 'r') as f:
                return ''.join(f.readlines()[-lines:])
        except:
            return "无法读取Producer日志"
    
    def get_consumer_log(self, lines: int = 50) -> str:
        """获取Consumer日志"""
        try:
            with open('/tmp/flink_cdc_consumer.log', 'r') as f:
                return ''.join(f.readlines()[-lines:])
        except:
            return "无法读取Consumer日志"
