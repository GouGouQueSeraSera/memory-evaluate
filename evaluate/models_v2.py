"""
记忆评测系统数据模型 V2
基于新的评测系统架构设计
"""
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime


# ==================== 基础数据结构 ====================

class Message(BaseModel):
    """对话消息"""
    message_id: str = Field(alias="messageId")
    role: str  # user 或 assistant
    content: str
    chat_time: str = Field(alias="chatTime")
    
    class Config:
        populate_by_name = True


class Memory(BaseModel):
    """记忆对象"""
    memory_id: str = Field(alias="memoryId")
    content: str
    meta_data: Dict[str, Any] = Field(default_factory=dict, alias="metaData")
    
    class Config:
        populate_by_name = True


class Evidence(BaseModel):
    """证据对象"""
    message_ids: List[str] = Field(default_factory=list, alias="messageIds")
    memory_ids: List[str] = Field(default_factory=list, alias="memoryIds")
    
    class Config:
        populate_by_name = True


class QA(BaseModel):
    """问答对"""
    question: str
    answer: str
    evidence: Dict[str, List[Evidence]] = Field(default_factory=dict)


class Session(BaseModel):
    """会话对象"""
    session_id: str = Field(alias="sessionId")
    memories: List[Memory] = Field(default_factory=list)
    conversation: List[Message] = Field(default_factory=list)
    
    class Config:
        populate_by_name = True


# ==================== 评测数据项 ====================

class EvaluationDataItem(BaseModel):
    """评测数据项"""
    item_id: str = Field(default="", alias="itemId")  # 数据项ID
    item_name: str = Field(default="", alias="itemName")  # 数据项名称
    qa: List[QA] = Field(default_factory=list)
    sessions: List[Session] = Field(default_factory=list)
    
    class Config:
        populate_by_name = True


# ==================== 评测用例 ====================

class DialogueExtractionCase(BaseModel):
    """记忆提取评测用例"""
    case_id: str
    session_id: str
    conversation: List[Message]  # 原始对话
    expected_memories: List[Memory]  # 预期记忆
    actual_memories: Optional[List[Memory]] = None  # 实际提取的记忆


class MemoryWriteRecallCase(BaseModel):
    """记忆写入+召回评测用例"""
    case_id: str
    session_id: str
    question: str
    answer: str
    expected_memory_ids: List[str]  # 预期召回的记忆ID
    memories_to_write: List[Memory]  # 需要写入的记忆
    actual_recalled_memory_ids: Optional[List[str]] = None  # 实际召回的记忆ID
    actual_recalled_memories_obj: Optional[List[Memory]] = None  # 实际召回的记忆对象（用于详细展示）


class ConversationWriteRecallCase(BaseModel):
    """对话写入+召回评测用例"""
    case_id: str
    session_id: str
    question: str
    answer: str
    conversation: List[Message]  # 原始对话
    expected_memory_ids: List[str]  # 预期召回的记忆ID（从evidence获取）
    all_memories: List[Memory]  # 该session的所有记忆
    actual_recalled_memories: Optional[List[Memory]] = None  # 实际召回的记忆


# ==================== 评测结果 ====================

class MemoryMatch(BaseModel):
    """记忆匹配详情"""
    expected_memory_id: Optional[str] = None
    expected_content: Optional[str] = None
    actual_memory_id: Optional[str] = None
    actual_content: Optional[str] = None
    match_status: str  # matched, missing, extra
    similarity_score: Optional[float] = None


class MetricResult(BaseModel):
    """单个指标结果"""
    metric_name: str  # 指标名称
    metric_value: float  # 指标值
    passed: bool  # 是否通过
    reason: str = ""  # 评测原因（详细说明）
    details: Dict[str, Any] = Field(default_factory=dict)  # 额外的详细信息


class ScenarioDetails(BaseModel):
    """场景特定详情（基类）"""
    pass


class DialogueExtractionDetails(ScenarioDetails):
    """记忆提取场景详情"""
    conversation: List[Message]  # 原始对话
    expected_memories: List[Memory]  # 预期记忆
    actual_memories: List[Memory]  # 实际提取的记忆
    memory_matches: List[MemoryMatch] = Field(default_factory=list)  # 记忆匹配情况


class MemoryWriteRecallDetails(ScenarioDetails):
    """记忆写入+召回场景详情"""
    question: str
    answer: str
    written_memories: List[Memory]  # 写入的记忆
    expected_memory_ids: List[str]  # 预期召回的记忆ID
    actual_recalled_memories: List[Memory]  # 实际召回的记忆
    memory_matches: List[MemoryMatch] = Field(default_factory=list)  # 记忆匹配情况


class ConversationWriteRecallDetails(ScenarioDetails):
    """对话写入+召回场景详情"""
    question: str
    answer: str
    conversation: List[Message]  # 原始对话
    expected_memory_ids: List[str]  # 预期召回的记忆ID
    actual_recalled_memories: List[Memory]  # 实际召回的记忆
    all_memories: List[Memory]  # 所有记忆
    memory_matches: List[MemoryMatch] = Field(default_factory=list)  # 记忆匹配情况


class CaseResult(BaseModel):
    """单个用例评测结果"""
    case_id: str
    case_type: str  # dialogue_extraction, memory_write_recall, conversation_write_recall
    metrics: List[MetricResult] = Field(default_factory=list)
    scenario_details: Optional[Dict[str, Any]] = None  # 场景特定详情
    

class EvaluationReport(BaseModel):
    """评测报告"""
    report_id: str
    report_name: str
    case_results: List[CaseResult] = Field(default_factory=list)
    summary: Dict[str, Any] = Field(default_factory=dict)  # 汇总信息
    create_time: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


# ==================== LLM配置 ====================

class LLMConfig(BaseModel):
    """LLM配置"""
    api_key: str = Field(alias="apiKey")
    base_url: str = Field(alias="baseUrl")
    model_name: str = Field(alias="modelName")
    temperature: float = 0.7
    max_output_tokens: int = Field(default=1000, alias="maxOutputTokens")
    log_requests: bool = Field(default=False, alias="logRequests")
    timeout: int = 60000
    
    class Config:
        populate_by_name = True


class EvaluationConfig(BaseModel):
    """评测配置"""
    llm: LLMConfig
    prompts: Dict[str, str] = Field(default_factory=dict)
