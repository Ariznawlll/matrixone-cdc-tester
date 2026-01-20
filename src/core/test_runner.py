from typing import Dict, Any, List
from ..adapters.base_adapter import BaseAdapter
from ..adapters.mo_to_mo_adapter import MoToMoAdapter
from ..adapters.mo_to_mysql_adapter import MoToMysqlAdapter
from ..adapters.cross_cluster_adapter import CrossClusterAdapter
from ..adapters.flink_cdc_adapter import FlinkCdcAdapter
from .config_loader import ConfigLoader
from colorama import Fore, Style, init
import time

init(autoreset=True)


class TestRunner:
    """测试执行引擎"""
    
    ADAPTER_MAP = {
        'mo_to_mo': MoToMoAdapter,
        'mo_to_mysql': MoToMysqlAdapter,
        'cross_cluster': CrossClusterAdapter,
        'flink_cdc': FlinkCdcAdapter
    }
    
    def __init__(self, scenario: str):
        self.config_loader = ConfigLoader()
        self.scenario_config = self.config_loader.load_scenario(scenario)
        self.adapter = self._create_adapter()
        self.results = []
    
    def _create_adapter(self) -> BaseAdapter:
        """根据场景类型创建对应的适配器"""
        scenario_type = self.scenario_config['scenario_type']
        adapter_class = self.ADAPTER_MAP.get(scenario_type)
        
        if not adapter_class:
            raise ValueError(f"不支持的场景类型: {scenario_type}")
        
        return adapter_class(self.scenario_config)
    
    def run_tests(self, testcase_file: str = "common_tests.yaml", test_group: str = "basic"):
        """运行测试用例"""
        testcases = self.config_loader.load_testcases(testcase_file)
        
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"场景: {self.scenario_config['scenario_name']}")
        print(f"测试套件: {testcases['test_suite']['name']}")
        print(f"测试组: {test_group}")
        print(f"{'='*60}{Style.RESET_ALL}\n")
        
        try:
            self.adapter.connect()
            self.adapter.setup_cdc()
            
            # 根据测试组筛选测试用例
            test_ids = testcases.get('test_groups', {}).get(test_group, [])
            if not test_ids:
                print(f"{Fore.YELLOW}⚠ 未找到测试组 '{test_group}'，运行所有测试{Style.RESET_ALL}")
                test_cases = testcases['test_cases']
            else:
                test_cases = [tc for tc in testcases['test_cases'] if tc['id'] in test_ids]
            
            for test_case in test_cases:
                result = self._run_single_test(test_case)
                self.results.append(result)
            
        finally:
            self.adapter.teardown_cdc()
            self.adapter.disconnect()
        
        self._print_summary()
        return self.results
    
    def _run_single_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """运行单个测试用例"""
        test_id = test_case['id']
        test_name = test_case['name']
        table = test_case.get('table', '')
        
        print(f"{Fore.YELLOW}[{test_id}] {test_name}{Style.RESET_ALL}")
        if table:
            print(f"  表: {table}")
        
        start_time = time.time()
        
        try:
            for step in test_case['steps']:
                self._execute_step(step, table)
            
            elapsed = time.time() - start_time
            print(f"{Fore.GREEN}✓ 通过 ({elapsed:.2f}s){Style.RESET_ALL}\n")
            return {'id': test_id, 'name': test_name, 'status': 'PASS', 'time': elapsed}
        
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"{Fore.RED}✗ 失败: {str(e)} ({elapsed:.2f}s){Style.RESET_ALL}\n")
            return {'id': test_id, 'name': test_name, 'status': 'FAIL', 'error': str(e), 'time': elapsed}
    
    def _execute_step(self, step: Dict[str, Any], table: str = None):
        """执行测试步骤"""
        action = step['action']
        
        if action == 'validate_sync':
            timeout = step.get('timeout', 60)
            if not self.adapter.validate_sync(table, timeout):
                raise AssertionError(f"数据同步超时 (>{timeout}s)")
        
        elif action == 'update':
            sql = step.get('sql')
            if sql:
                self.adapter.execute_on_source(sql)
                print(f"  执行UPDATE: {sql[:50]}...")
        
        elif action == 'delete':
            sql = step.get('sql')
            if sql:
                self.adapter.execute_on_source(sql)
                print(f"  执行DELETE: {sql[:50]}...")
        
        elif action == 'validate_index_query':
            sql = step.get('sql')
            if sql:
                source_result = self.adapter.execute_on_source(sql)
                time.sleep(5)  # 等待同步
                target_result = self.adapter.execute_on_target(sql)
                if source_result != target_result:
                    raise AssertionError("索引查询结果不一致")
                print(f"  索引查询验证通过")
    
    def _print_summary(self):
        """打印测试摘要"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r['status'] == 'PASS')
        failed = total - passed
        total_time = sum(r.get('time', 0) for r in self.results)
        
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"测试摘要")
        print(f"{'='*60}{Style.RESET_ALL}")
        print(f"总计: {total} | {Fore.GREEN}通过: {passed}{Style.RESET_ALL} | {Fore.RED}失败: {failed}{Style.RESET_ALL}")
        print(f"总耗时: {total_time:.2f}s")
