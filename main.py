#!/usr/bin/env python3
"""
MatrixOne CDC 测试工具
支持多种CDC场景的自动化测试
"""

import argparse
from src.core.test_runner import TestRunner
from src.core.config_loader import ConfigLoader
from colorama import Fore, Style, init

init(autoreset=True)


def list_scenarios():
    """列出所有可用的测试场景"""
    loader = ConfigLoader()
    scenarios = loader.list_scenarios()
    
    print(f"\n{Fore.CYAN}可用的CDC测试场景:{Style.RESET_ALL}\n")
    for scenario in scenarios:
        print(f"  • {Fore.GREEN}{scenario['file']}{Style.RESET_ALL}")
        print(f"    名称: {scenario['name']}")
        print(f"    类型: {scenario['type']}\n")


def run_test(scenario: str, testcase: str = "common_tests.yaml", test_group: str = "basic"):
    """运行指定场景的测试"""
    try:
        runner = TestRunner(scenario)
        results = runner.run_tests(testcase, test_group)
        
        # 返回退出码
        failed = sum(1 for r in results if r['status'] == 'FAIL')
        return 0 if failed == 0 else 1
    
    except Exception as e:
        print(f"{Fore.RED}错误: {str(e)}{Style.RESET_ALL}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description='MatrixOne CDC 测试工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 列出所有场景
  python main.py --list
  
  # 运行MO到MO的基础测试
  python main.py --scenario mo_to_mo --group basic
  
  # 运行MO到MySQL的全文索引测试
  python main.py --scenario mo_to_mysql --group fulltext
  
  # 运行跨集群的分区表测试
  python main.py --scenario cross_cluster --group partition
        """
    )
    
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='列出所有可用的测试场景'
    )
    
    parser.add_argument(
        '--scenario', '-s',
        type=str,
        help='指定要运行的场景 (mo_to_mo, mo_to_mysql, cross_cluster)'
    )
    
    parser.add_argument(
        '--testcase', '-t',
        type=str,
        default='common_tests.yaml',
        help='指定测试用例文件 (默认: common_tests.yaml)'
    )
    
    parser.add_argument(
        '--group', '-g',
        type=str,
        default='basic',
        choices=['basic', 'fulltext', 'vector', 'partition'],
        help='指定测试组 (默认: basic)'
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_scenarios()
        return 0
    
    if args.scenario:
        return run_test(args.scenario, args.testcase, args.group)
    
    parser.print_help()
    return 0


if __name__ == '__main__':
    exit(main())
