"""
Memory-Evaluate: 记忆系统评测框架 V2 (Python版本)
"""

__version__ = "2.0.0"
__author__ = "wangjiajun05"

# 导入配置相关
from .config_loader import ConfigLoader

# 导入服务
from .llm_service import LLMService
from .prompt_service import PromptTemplateService

# 导入数据模型
from .models_v2 import (
    Message,
    Memory,
    DialogueExtractionCase,
    MemoryWriteRecallCase,
    ConversationWriteRecallCase,
    MetricResult,
    CaseResult,
    EvaluationReport,
    EvaluationDataItem,
    LLMConfig,
    EvaluationConfig,
    Session
)

# 导入评测器（会自动注册）
from .metric_evaluator import (
    MetricEvaluator,
    AccuracyEvaluator,
    CompletenessEvaluator,
    MemoryDuplicationEvaluator,
    MemoryConflictEvaluator,
    RecallAccuracyEvaluator,
    RecallCompletenessEvaluator
)

# 导入注册中心
from .metric_registry import MetricRegistry, register_metric, get_global_registry

# 导入场景
from .evaluation_scenario import (
    EvaluationScenario,
    DialogueExtractionScenario,
    MemoryWriteRecallScenario,
    ConversationWriteRecallScenario
)

# 导入评测引擎
from .evaluation_engine import EvaluationEngine

# 导入用例加载器
from .case_loader import CaseLoader

# 导入记忆系统接口
from .memory_system_interface import MemorySystemInterface, MockMemorySystem

__all__ = [
    # Services
    'ConfigLoader',
    'LLMService',
    'PromptTemplateService',
    
    # Models
    'Message',
    'Memory',
    'DialogueExtractionCase',
    'MemoryWriteRecallCase',
    'ConversationWriteRecallCase',
    'MetricResult',
    'CaseResult',
    'EvaluationReport',
    'EvaluationDataItem',
    'LLMConfig',
    'EvaluationConfig',
    'Session',
    
    # Evaluators
    'MetricEvaluator',
    'AccuracyEvaluator',
    'CompletenessEvaluator',
    'MemoryDuplicationEvaluator',
    'MemoryConflictEvaluator',
    'RecallAccuracyEvaluator',
    'RecallCompletenessEvaluator',
    
    # Registry
    'MetricRegistry',
    'register_metric',
    'get_global_registry',
    
    # Scenarios
    'EvaluationScenario',
    'DialogueExtractionScenario',
    'MemoryWriteRecallScenario',
    'ConversationWriteRecallScenario',
    
    # Engine
    'EvaluationEngine',
    
    # Loader
    'CaseLoader',
    
    # Interface
    'MemorySystemInterface',
    'MockMemorySystem',
    'EvaluationReport',
]
