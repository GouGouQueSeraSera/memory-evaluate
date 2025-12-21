"""
评测引擎
负责执行评测的核心逻辑，返回评测结果
"""
from typing import List
from models_v2 import CaseResult
from memory_system_interface import MemorySystemInterface
from llm_service import LLMService
from prompt_service import PromptTemplateService

# 重要：先导入评测器以触发注册
import metric_evaluator

from metric_registry import get_global_registry
from evaluation_scenario import (
    DialogueExtractionScenario,
    MemoryWriteRecallScenario,
    ConversationWriteRecallScenario
)


class EvaluationEngine:
    """
    评测引擎
    
    职责：
    - 初始化评测环境（指标注册中心、场景注册中心）
    - 执行评测并返回结果
    - 不负责报告生成（由ReportGenerator负责）
    """
    
    def __init__(
        self,
        memory_system: MemorySystemInterface,
        prompt_service: PromptTemplateService,
        llm_service: LLMService,
        llm_config
    ):
        self.memory_system = memory_system
        self.prompt_service = prompt_service
        self.llm_service = llm_service
        self.llm_config = llm_config
        
        # 初始化指标注册中心
        self.metric_registry = get_global_registry()
        self.metric_registry.initialize_all(prompt_service, llm_service, llm_config)
        
        # 初始化场景注册中心
        self.scenario_registry = {
            "dialogue_extraction": DialogueExtractionScenario(
                memory_system, self.metric_registry
            ),
            "memory_write_recall": MemoryWriteRecallScenario(
                memory_system, self.metric_registry
            ),
            "conversation_write_recall": ConversationWriteRecallScenario(
                memory_system, self.metric_registry
            )
        }
    
    def evaluate(
        self,
        scenario_name: str,
        cases: List,
        metrics: List[str] = None
    ) -> List[CaseResult]:
        """
        统一的评测接口
        
        Args:
            scenario_name: 场景名称 (dialogue_extraction, memory_write_recall, conversation_write_recall)
            cases: 评测用例列表
            metrics: 要评测的指标列表，默认使用场景支持的所有指标
        
        Returns:
            评测结果列表
        """
        # 获取场景
        scenario = self.scenario_registry.get(scenario_name)
        if not scenario:
            raise ValueError(f"未知的评测场景: {scenario_name}")
        
        # 执行评测
        results = []
        for case in cases:
            result = scenario.execute(case, metrics)
            results.append(result)
        
        return results
    
