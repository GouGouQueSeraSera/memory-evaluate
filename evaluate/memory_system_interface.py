"""
记忆系统能力接口
定义记忆系统需要提供的4种基础能力
"""
from abc import ABC, abstractmethod
from typing import List, Dict
from models_v2 import Message, Memory


class MemorySystemInterface(ABC):
    """记忆系统接口"""
    
    @abstractmethod
    def extract_memories(self, conversation: List[Message], session_id: str) -> List[Memory]:
        """
        能力1: 纯记忆提取
        从对话中提取记忆，不写入存储
        
        Args:
            conversation: 对话消息列表
            session_id: 会话ID
            
        Returns:
            提取的记忆列表
        """
        pass
    
    @abstractmethod
    def recall_memories(self, query: str, session_id: str, top_k: int = 10) -> List[Memory]:
        """
        能力2: 记忆召回
        根据查询召回相关记忆
        
        Args:
            query: 查询问题
            session_id: 会话ID
            top_k: 召回数量
            
        Returns:
            召回的记忆列表
        """
        pass
    
    @abstractmethod
    def write_memories(self, memories: List[Memory], session_id: str) -> bool:
        """
        能力3: 记忆直接写入
        将记忆直接写入存储
        
        Args:
            memories: 要写入的记忆列表
            session_id: 会话ID
            
        Returns:
            是否写入成功
        """
        pass
    
    @abstractmethod
    def extract_and_write_memories(self, conversation: List[Message], session_id: str) -> List[Memory]:
        """
        能力4: 记忆提取和写入
        从对话中提取记忆并写入存储
        
        Args:
            conversation: 对话消息列表
            session_id: 会话ID
            
        Returns:
            提取并写入的记忆列表
        """
        pass
    
    @abstractmethod
    def clear_session(self, session_id: str) -> bool:
        """
        清空会话记忆（用于测试）
        
        Args:
            session_id: 会话ID
            
        Returns:
            是否清空成功
        """
        pass


class MockMemorySystem(MemorySystemInterface):
    """
    Mock记忆系统实现
    用于本地测试和演示
    """
    
    def __init__(self):
        # 内存存储
        self.memory_storage: Dict[str, List[Memory]] = {}
        
    def extract_memories(self, conversation: List[Message], session_id: str) -> List[Memory]:
        """
        Mock实现：简单规则提取记忆
        - 从用户消息中提取包含"我"、"喜欢"、"叫"等关键词的内容
        """
        import re
        import uuid
        
        memories = []
        
        for msg in conversation:
            if msg.role == "user":
                content = msg.content
                
                # 规则1: 提取姓名
                name_match = re.search(r'我[叫是](.{2,10})', content)
                if name_match:
                    name = name_match.group(1).strip()
                    memory = Memory(
                        memory_id=f"mem_{uuid.uuid4().hex[:8]}",
                        content=f"用户叫{name}",
                        meta_data={"source": "name_extraction", "message_id": msg.message_id}
                    )
                    memories.append(memory)
                
                # 规则2: 提取喜好
                like_match = re.search(r'(我|用户).*?喜欢(.{2,20})', content)
                if like_match:
                    hobby = like_match.group(2).strip()
                    memory = Memory(
                        memory_id=f"mem_{uuid.uuid4().hex[:8]}",
                        content=f"用户喜欢{hobby}",
                        meta_data={"source": "hobby_extraction", "message_id": msg.message_id}
                    )
                    memories.append(memory)
                
                # 规则3: 提取居住地
                live_match = re.search(r'(我|用户).*?住在(.{2,10})', content)
                if live_match:
                    location = live_match.group(2).strip()
                    memory = Memory(
                        memory_id=f"mem_{uuid.uuid4().hex[:8]}",
                        content=f"用户住在{location}",
                        meta_data={"source": "location_extraction", "message_id": msg.message_id}
                    )
                    memories.append(memory)
        
        return memories
    
    def recall_memories(self, query: str, session_id: str, top_k: int = 10) -> List[Memory]:
        """
        Mock实现：简单关键词匹配召回
        """
        if session_id not in self.memory_storage:
            return []
        
        all_memories = self.memory_storage[session_id]
        
        # 简单的关键词匹配
        query_keywords = set(query)
        scored_memories = []
        
        for memory in all_memories:
            # 计算匹配分数（简单字符重叠）
            memory_chars = set(memory.content)
            overlap = len(query_keywords & memory_chars)
            if overlap > 0:
                scored_memories.append((memory, overlap))
        
        # 按分数排序
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        
        # 返回top_k
        return [mem for mem, _ in scored_memories[:top_k]]
    
    def write_memories(self, memories: List[Memory], session_id: str) -> bool:
        """
        Mock实现：写入内存存储
        """
        if session_id not in self.memory_storage:
            self.memory_storage[session_id] = []
        
        self.memory_storage[session_id].extend(memories)
        return True
    
    def extract_and_write_memories(self, conversation: List[Message], session_id: str) -> List[Memory]:
        """
        Mock实现：提取并写入
        """
        memories = self.extract_memories(conversation, session_id)
        self.write_memories(memories, session_id)
        return memories
    
    def clear_session(self, session_id: str) -> bool:
        """
        清空会话记忆
        """
        if session_id in self.memory_storage:
            del self.memory_storage[session_id]
        return True
