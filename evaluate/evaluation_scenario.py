"""
评测场景基类和具体实现
使用策略模式 + 模板方法模式实现
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from models_v2 import (
    CaseResult, MetricResult, MemoryMatch,
    DialogueExtractionDetails, MemoryWriteRecallDetails, ConversationWriteRecallDetails
)
from memory_system_interface import MemorySystemInterface
from metric_registry import MetricRegistry


class EvaluationScenario(ABC):
    """评测场景抽象基类"""
    
    def __init__(
        self,
        memory_system: MemorySystemInterface,
        metric_registry: MetricRegistry
    ):
        self.memory_system = memory_system
        self.metric_registry = metric_registry
    
    @property
    @abstractmethod
    def scenario_name(self) -> str:
        """场景名称"""
        pass
    
    @property
    @abstractmethod
    def supported_metrics(self) -> List[str]:
        """支持的评测指标"""
        pass
    
    def execute(self, case, metrics: List[str] = None) -> CaseResult:
        """
        执行评测（模板方法）
        
        这是一个模板方法，定义了评测的标准流程：
        0. 清理会话（避免数据污染）
        1. 准备数据
        2. 运行记忆系统
        3. 评测指标
        4. 收集场景详情
        
        Args:
            case: 评测用例
            metrics: 要评测的指标列表，默认使用场景支持的所有指标
            
        Returns:
            评测结果
        """
        # 0. 清理会话，避免不同用例之间的数据污染
        self.memory_system.clear_session(case.session_id)
        
        # 1. 准备数据
        self._prepare_data(case)
        
        # 2. 运行记忆系统
        self._run_system(case)
        
        # 3. 评测指标
        if metrics is None:
            metrics = self.supported_metrics
        
        metric_results = self._evaluate_metrics(case, metrics)
        
        # 4. 收集场景详情
        scenario_details = self._collect_scenario_details(case)
        
        # 5. 生成结果
        return CaseResult(
            case_id=case.case_id,
            case_type=self.scenario_name,
            metrics=metric_results,
            scenario_details=scenario_details
        )
    
    @abstractmethod
    def _prepare_data(self, case):
        """准备评测数据（钩子方法）"""
        pass
    
    @abstractmethod
    def _run_system(self, case):
        """运行记忆系统（钩子方法）"""
        pass
    
    @abstractmethod
    def _evaluate_metrics(self, case, metrics: List[str]) -> List[MetricResult]:
        """评测指标（钩子方法，不同场景的评测逻辑不同）"""
        pass
    
    @abstractmethod
    def _collect_scenario_details(self, case) -> Dict[str, Any]:
        """收集场景特定详情（钩子方法）"""
        pass
    
    def _compute_memory_matches(self, expected_memories, actual_memories) -> List[MemoryMatch]:
        """计算记忆匹配情况"""
        matches = []
        expected_dict = {m.memory_id: m for m in expected_memories}
        actual_dict = {m.memory_id: m for m in actual_memories}
        
        # 匹配的记忆
        for mem_id in expected_dict:
            if mem_id in actual_dict:
                matches.append(MemoryMatch(
                    expected_memory_id=mem_id,
                    expected_content=expected_dict[mem_id].content,
                    actual_memory_id=mem_id,
                    actual_content=actual_dict[mem_id].content,
                    match_status="matched",
                    similarity_score=1.0
                ))
            else:
                matches.append(MemoryMatch(
                    expected_memory_id=mem_id,
                    expected_content=expected_dict[mem_id].content,
                    match_status="missing"
                ))
        
        # 额外的记忆
        for mem_id in actual_dict:
            if mem_id not in expected_dict:
                matches.append(MemoryMatch(
                    actual_memory_id=mem_id,
                    actual_content=actual_dict[mem_id].content,
                    match_status="extra"
                ))
        
        return matches


class DialogueExtractionScenario(EvaluationScenario):
    """记忆提取评测场景"""
    
    @property
    def scenario_name(self) -> str:
        return "dialogue_extraction"
    
    @property
    def supported_metrics(self) -> List[str]:
        return ["accuracy", "completeness"]
    
    def _prepare_data(self, case):
        """准备数据：无需特殊准备"""
    
    def _run_system(self, case):
        """运行系统：调用记忆提取"""
        actual_memories = self.memory_system.extract_memories(
            case.conversation,
            case.session_id
        )
        case.actual_memories = actual_memories

    def _evaluate_metrics(self, case, metrics: List[str]) -> List[MetricResult]:
        """评测指标：accuracy 和 completeness"""
        results = []
        
        for metric_name in metrics:
            if metric_name not in self.supported_metrics:
                print(f"  ⚠️  场景 {self.scenario_name} 不支持指标 {metric_name}")
                continue
            
            evaluator = self.metric_registry.get(metric_name)
            if not evaluator:
                continue
            
            result = evaluator.evaluate(
                case.expected_memories,
                case.actual_memories
            )
            results.append(result)

        return results
    
    def _collect_scenario_details(self, case) -> Dict[str, Any]:
        """收集记忆提取场景详情"""
        memory_matches = self._compute_memory_matches(
            case.expected_memories,
            case.actual_memories or []
        )
        
        details = DialogueExtractionDetails(
            conversation=case.conversation,
            expected_memories=case.expected_memories,
            actual_memories=case.actual_memories or [],
            memory_matches=memory_matches
        )
        return details.model_dump()


class MemoryWriteRecallScenario(EvaluationScenario):
    """记忆写入+召回评测场景"""
    
    @property
    def scenario_name(self) -> str:
        return "memory_write_recall"
    
    @property
    def supported_metrics(self) -> List[str]:
        return ["recall_accuracy", "recall_completeness"]
    
    def _prepare_data(self, case):
        """准备数据：写入记忆"""
        self.memory_system.write_memories(
            case.memories_to_write,
            case.session_id
        )
    
    def _run_system(self, case):
        """运行系统：召回记忆"""
        recalled = self.memory_system.recall_memories(
            case.question,
            case.session_id
        )
        # MemoryWriteRecallCase 使用 actual_recalled_memory_ids (ID列表)
        case.actual_recalled_memory_ids = [m.memory_id for m in recalled]
        case.actual_recalled_memories_obj = recalled  # 保存完整的记忆对象

    def _evaluate_metrics(self, case, metrics: List[str]) -> List[MetricResult]:
        """评测指标：recall_accuracy 和 recall_completeness"""
        results = []
        
        # 获取预期和实际的记忆对象
        expected_memories = [
            m for m in case.memories_to_write
            if m.memory_id in case.expected_memory_ids
        ]
        actual_memories = getattr(case, 'actual_recalled_memories_obj', [])
        
        for metric_name in metrics:
            if metric_name not in self.supported_metrics:
                print(f"  ⚠️  场景 {self.scenario_name} 不支持指标 {metric_name}")
                continue
            
            evaluator = self.metric_registry.get(metric_name)
            if not evaluator:
                continue
            
            # 传递记忆对象而不ID
            result = evaluator.evaluate(expected_memories, actual_memories)
            results.append(result)

        return results
    
    def _collect_scenario_details(self, case) -> Dict[str, Any]:
        """收集记忆写入+召回场景详情"""
        # 获取实际召回的记忆对象
        actual_recalled_memories = [
            m for m in case.memories_to_write
            if m.memory_id in (case.actual_recalled_memory_ids or [])
        ]
        
        # 获取预期召回的记忆对象
        expected_memories = [
            m for m in case.memories_to_write
            if m.memory_id in case.expected_memory_ids
        ]
        
        memory_matches = self._compute_memory_matches(
            expected_memories,
            actual_recalled_memories
        )
        
        details = MemoryWriteRecallDetails(
            question=case.question,
            answer=case.answer,
            written_memories=case.memories_to_write,
            expected_memory_ids=case.expected_memory_ids,
            actual_recalled_memories=actual_recalled_memories,
            memory_matches=memory_matches
        )
        return details.model_dump()


class ConversationWriteRecallScenario(EvaluationScenario):
    """对话写入+召回评测场景"""
    
    @property
    def scenario_name(self) -> str:
        return "conversation_write_recall"
    
    @property
    def supported_metrics(self) -> List[str]:
        return ["memory_duplication_effect", "memory_conflict_effect"]
    
    def _prepare_data(self, case):
        """准备数据：提取并写入记忆"""
        extracted = self.memory_system.extract_and_write_memories(
            case.conversation,
            case.session_id
        )
        print(f"  - 提取并写入{len(extracted)}条记忆")
    
    def _run_system(self, case):
        """运行系统：召回记忆"""
        recalled = self.memory_system.recall_memories(
            case.question,
            case.session_id
        )
        case.actual_recalled_memories = recalled

    def _evaluate_metrics(self, case, metrics: List[str]) -> List[MetricResult]:
        """评测指标：memory_duplication_effect 和 memory_conflict_effect"""
        results = []
        
        for metric_name in metrics:
            if metric_name not in self.supported_metrics:
                print(f"  ⚠️  场景 {self.scenario_name} 不支持指标 {metric_name}")
                continue
            
            evaluator = self.metric_registry.get(metric_name)
            if not evaluator:
                continue
            
            result = evaluator.evaluate(case.actual_recalled_memories)
            results.append(result)

        return results
    
    def _collect_scenario_details(self, case) -> Dict[str, Any]:
        """收集对话写入+召回场景详情"""
        # 获取预期召回的记忆对象
        expected_memories = [
            m for m in case.all_memories
            if m.memory_id in case.expected_memory_ids
        ]
        
        memory_matches = self._compute_memory_matches(
            expected_memories,
            case.actual_recalled_memories or []
        )
        
        details = ConversationWriteRecallDetails(
            question=case.question,
            answer=case.answer,
            conversation=case.conversation,
            expected_memory_ids=case.expected_memory_ids,
            actual_recalled_memories=case.actual_recalled_memories or [],
            all_memories=case.all_memories,
            memory_matches=memory_matches
        )
        return details.model_dump()
