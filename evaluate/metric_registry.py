"""
评测指标注册中心
提供指标的注册、获取和管理功能
"""
from typing import Dict, Type, List, Optional


class MetricRegistry:
    """评测指标注册中心"""
    
    def __init__(self):
        self._metrics: Dict[str, Type] = {}
        self._instances: Dict[str, object] = {}
    
    def register(self, metric_name: str, evaluator_class: Type):
        """
        注册评测器
        
        Args:
            metric_name: 指标名称
            evaluator_class: 评测器类
        """
        self._metrics[metric_name] = evaluator_class
        print(f"✅ 注册评测指标: {metric_name}")
    
    def get(self, metric_name: str) -> Optional[object]:
        """
        获取评测器实例（单例模式）
        
        Args:
            metric_name: 指标名称
            
        Returns:
            评测器实例，如果不存在返回None
        """
        if metric_name not in self._instances:
            if metric_name not in self._metrics:
                print(f"⚠️  未注册的评测指标: {metric_name}")
                return None
            
            # 创建实例（延迟初始化）
            evaluator_class = self._metrics[metric_name]
            self._instances[metric_name] = evaluator_class()
        
        return self._instances[metric_name]
    
    def list_all(self) -> List[str]:
        """
        列出所有已注册的指标
        
        Returns:
            指标名称列表
        """
        return list(self._metrics.keys())
    
    def initialize_all(self, prompt_service, llm_service, llm_config):
        """
        初始化所有评测器
        
        Args:
            prompt_service: Prompt模板服务
            llm_service: LLM服务
            llm_config: LLM配置
        """
        if not self._metrics:
            print("⚠️  警告: 没有已注册的评测器，请确保已导入 metric_evaluator 模块")
            return
        
        for metric_name, evaluator_class in self._metrics.items():
            self._instances[metric_name] = evaluator_class(
                prompt_service, llm_service, llm_config
            )
        print(f"✅ 初始化了 {len(self._instances)} 个评测器: {list(self._instances.keys())}")
    
    def has_metric(self, metric_name: str) -> bool:
        """
        检查指标是否已注册
        
        Args:
            metric_name: 指标名称
            
        Returns:
            是否已注册
        """
        return metric_name in self._metrics


# 全局注册中心实例
_global_registry = MetricRegistry()


def register_metric(metric_name: str):
    """
    装饰器：自动注册评测指标
    
    使用方式:
        @register_metric("accuracy")
        class AccuracyEvaluator(MetricEvaluator):
            ...
    
    Args:
        metric_name: 指标名称
    """
    def decorator(cls):
        _global_registry.register(metric_name, cls)
        cls.metric_name = metric_name
        return cls
    return decorator


def get_global_registry() -> MetricRegistry:
    """获取全局注册中心"""
    return _global_registry
