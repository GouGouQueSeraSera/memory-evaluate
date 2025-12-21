"""
场景配置工厂
使用工厂模式管理不同评测场景的配置
"""
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class ScenarioConfig:
    """场景配置"""
    scenario_name: str
    display_name: str
    case_key: str  # 在 all_cases 字典中的键名
    default_metrics: List[str]


class ScenarioFactory:
    """场景配置工厂"""
    
    # 场景配置注册表
    _SCENARIO_CONFIGS = {
        "dialogue_extraction": ScenarioConfig(
            scenario_name="dialogue_extraction",
            display_name="记忆提取评测",
            case_key="dialogue_extraction",
            default_metrics=["accuracy", "completeness"]
        ),
        "memory_write_recall": ScenarioConfig(
            scenario_name="memory_write_recall",
            display_name="记忆写入+召回评测",
            case_key="memory_write_recall",
            default_metrics=["recall_accuracy", "recall_completeness"]
        ),
        "conversation_write_recall": ScenarioConfig(
            scenario_name="conversation_write_recall",
            display_name="对话写入+召回评测",
            case_key="conversation_write_recall",
            default_metrics=["memory_duplication_effect", "memory_conflict_effect"]
        )
    }
    
    @classmethod
    def get_config(cls, scenario_name: str) -> ScenarioConfig:
        """
        获取场景配置
        
        Args:
            scenario_name: 场景名称
            
        Returns:
            场景配置对象
            
        Raises:
            ValueError: 如果场景名称不存在
        """
        config = cls._SCENARIO_CONFIGS.get(scenario_name)
        if not config:
            raise ValueError(f"未知的评测场景: {scenario_name}")
        return config
    
    @classmethod
    def get_all_scenario_names(cls) -> List[str]:
        """获取所有场景名称"""
        return list(cls._SCENARIO_CONFIGS.keys())
    
    @classmethod
    def get_all_configs(cls) -> Dict[str, ScenarioConfig]:
        """获取所有场景配置"""
        return cls._SCENARIO_CONFIGS.copy()
    
    @classmethod
    def get_scenarios_for_metrics(cls, metrics: List[str]) -> List[str]:
        """
        根据指标列表推断应该评测哪些场景
        
        Args:
            metrics: 指标列表
            
        Returns:
            场景名称列表
        """
        scenarios = []
        for scenario_name, config in cls._SCENARIO_CONFIGS.items():
            # 如果场景的任何默认指标在用户指定的指标中，就包含该场景
            if any(metric in metrics for metric in config.default_metrics):
                scenarios.append(scenario_name)
        return scenarios
    
    @classmethod
    def filter_metrics_for_scenario(cls, scenario_name: str, metrics: List[str]) -> List[str]:
        """
        过滤出场景支持的指标
        
        Args:
            scenario_name: 场景名称
            metrics: 指标列表
            
        Returns:
            该场景支持的指标列表
        """
        config = cls.get_config(scenario_name)
        # 返回用户指定的指标中，该场景支持的那些
        return [m for m in metrics if m in config.default_metrics]
