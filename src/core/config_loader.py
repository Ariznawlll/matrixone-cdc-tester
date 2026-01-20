import yaml
from pathlib import Path
from typing import Dict, Any


class ConfigLoader:
    """配置加载器"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
    
    def load_scenario(self, scenario_name: str) -> Dict[str, Any]:
        """加载场景配置"""
        scenario_file = self.config_dir / "scenarios" / f"{scenario_name}.yaml"
        
        if not scenario_file.exists():
            raise FileNotFoundError(f"场景配置文件不存在: {scenario_file}")
        
        with open(scenario_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        return config
    
    def load_testcases(self, testcase_file: str = "common_tests.yaml") -> Dict[str, Any]:
        """加载测试用例"""
        testcase_path = self.config_dir / "testcases" / testcase_file
        
        if not testcase_path.exists():
            raise FileNotFoundError(f"测试用例文件不存在: {testcase_path}")
        
        with open(testcase_path, 'r', encoding='utf-8') as f:
            testcases = yaml.safe_load(f)
        
        return testcases
    
    def list_scenarios(self):
        """列出所有可用场景"""
        scenario_dir = self.config_dir / "scenarios"
        scenarios = []
        
        for file in scenario_dir.glob("*.yaml"):
            with open(file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                scenarios.append({
                    'file': file.stem,
                    'name': config.get('scenario_name'),
                    'type': config.get('scenario_type')
                })
        
        return scenarios
