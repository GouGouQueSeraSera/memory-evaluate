"""
评测用例加载器
从评测数据项生成不同场景的评测用例
"""
from typing import List
from models_v2 import (
    EvaluationDataItem,
    DialogueExtractionCase,
    MemoryWriteRecallCase,
    ConversationWriteRecallCase
)


class CaseLoader:
    """评测用例加载器"""
    
    @staticmethod
    def load_dialogue_extraction_cases(data_item: EvaluationDataItem) -> List[DialogueExtractionCase]:
        """
        加载记忆提取评测用例
        每个session生成一个用例
        
        Args:
            data_item: 评测数据项
            
        Returns:
            记忆提取评测用例列表
        """
        cases = []
        
        for idx, session in enumerate(data_item.sessions):
            case = DialogueExtractionCase(
                case_id=f"{data_item.item_id}_dialogue_extraction_{idx}",
                session_id=session.session_id,
                conversation=session.conversation,
                expected_memories=session.memories
            )
            cases.append(case)
        
        return cases
    
    @staticmethod
    def load_memory_write_recall_cases(data_item: EvaluationDataItem) -> List[MemoryWriteRecallCase]:
        """
        加载记忆写入+召回评测用例
        每个QA对生成一个用例
        
        Args:
            data_item: 评测数据项
            
        Returns:
            记忆写入+召回评测用例列表
        """
        cases = []
        
        # 构建session_id到memories的映射
        session_memories = {
            session.session_id: session.memories
            for session in data_item.sessions
        }
        
        for idx, qa in enumerate(data_item.qa):
            # 从evidence中提取预期召回的记忆ID
            expected_memory_ids = []
            memories_to_write = []
            
            for session_id, evidences in qa.evidence.items():
                for evidence in evidences:
                    expected_memory_ids.extend(evidence.memory_ids)
                
                # 获取该session的所有记忆用于写入
                if session_id in session_memories:
                    memories_to_write.extend(session_memories[session_id])
            
            case = MemoryWriteRecallCase(
                case_id=f"{data_item.item_id}_memory_write_recall_{idx}",
                session_id=list(qa.evidence.keys())[0] if qa.evidence else "default",
                question=qa.question,
                answer=qa.answer,
                expected_memory_ids=expected_memory_ids,
                memories_to_write=memories_to_write
            )
            cases.append(case)
        
        return cases
    
    @staticmethod
    def load_conversation_write_recall_cases(data_item: EvaluationDataItem) -> List[ConversationWriteRecallCase]:
        """
        加载对话写入+召回评测用例
        每个QA对生成一个用例
        
        Args:
            data_item: 评测数据项
            
        Returns:
            对话写入+召回评测用例列表
        """
        cases = []
        
        # 构建session_id到conversation和memories的映射
        session_data = {
            session.session_id: {
                "conversation": session.conversation,
                "memories": session.memories
            }
            for session in data_item.sessions
        }
        
        for idx, qa in enumerate(data_item.qa):
            # 从evidence中提取预期召回的记忆ID
            expected_memory_ids = []
            conversation = []
            all_memories = []
            session_id = "default"
            
            for sid, evidences in qa.evidence.items():
                session_id = sid
                for evidence in evidences:
                    expected_memory_ids.extend(evidence.memory_ids)
                
                # 获取该session的对话和记忆
                if sid in session_data:
                    conversation = session_data[sid]["conversation"]
                    all_memories = session_data[sid]["memories"]
            
            case = ConversationWriteRecallCase(
                case_id=f"{data_item.item_id}_conversation_write_recall_{idx}",
                session_id=session_id,
                question=qa.question,
                answer=qa.answer,
                conversation=conversation,
                expected_memory_ids=expected_memory_ids,
                all_memories=all_memories
            )
            cases.append(case)
        
        return cases
    
    @staticmethod
    def load_all_cases(data_item: EvaluationDataItem) -> dict:
        """
        加载所有类型的评测用例
        
        Args:
            data_item: 评测数据项
            
        Returns:
            包含所有类型用例的字典
        """
        return {
            "dialogue_extraction": CaseLoader.load_dialogue_extraction_cases(data_item),
            "memory_write_recall": CaseLoader.load_memory_write_recall_cases(data_item),
            "conversation_write_recall": CaseLoader.load_conversation_write_recall_cases(data_item)
        }
