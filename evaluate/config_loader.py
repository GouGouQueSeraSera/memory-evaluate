"""
配置加载器
"""
import yaml
from pathlib import Path
from typing import Dict, Any
from models_v2 import EvaluationConfig, LLMConfig


class ConfigLoader:
    """配置加载器"""
    
    @staticmethod
    def load_from_file(file_path: str) -> EvaluationConfig:
        """从文件加载配置"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"配置文件不存在: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return ConfigLoader._parse_config(data)
    
    @staticmethod
    def load_default() -> EvaluationConfig:
        """加载默认配置（config.yaml）"""
        # config.yaml 在 data/ 目录下
        config_path = Path(__file__).parent.parent / "data" / "config.yaml"
        return ConfigLoader.load_from_file(str(config_path))
    
    @staticmethod
    def _parse_config(data: Dict[str, Any]) -> EvaluationConfig:
        """解析配置数据"""
        llm_data = data.get('llm', {})
        llm_config = LLMConfig(
            api_key=llm_data.get('apiKey', ''),
            base_url=llm_data.get('baseUrl', ''),
            model_name=llm_data.get('modelName', 'qwen-max'),
            temperature=llm_data.get('temperature', 0.7),
            max_output_tokens=llm_data.get('maxOutputTokens', 1000),
            log_requests=llm_data.get('logRequests', False),
            timeout=llm_data.get('timeout', 60000)
        )
        
        prompts = data.get('prompts', {})
        
        return EvaluationConfig(
            llm=llm_config,
            prompts=prompts
        )
