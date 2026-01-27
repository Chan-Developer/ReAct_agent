# -*- coding: utf-8 -*-
"""Memory 基类和数据结构定义。"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import hashlib
import json


class MemoryType(str, Enum):
    """记忆类型"""
    CONVERSATION = "conversation"  # 对话记录
    TASK = "task"                  # 任务执行记录
    KNOWLEDGE = "knowledge"        # 学到的知识
    EXPERIENCE = "experience"      # 经验总结
    USER_PREFERENCE = "user_pref"  # 用户偏好


@dataclass
class MemoryItem:
    """记忆项"""
    content: str                              # 记忆内容
    memory_type: MemoryType                   # 记忆类型
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    importance: float = 0.5                   # 重要性 0-1
    session_id: Optional[str] = None          # 会话 ID
    
    def __post_init__(self):
        if isinstance(self.memory_type, str):
            self.memory_type = MemoryType(self.memory_type)
    
    @property
    def id(self) -> str:
        """生成唯一 ID"""
        data = f"{self.content}:{self.timestamp.isoformat()}:{self.memory_type.value}"
        return hashlib.md5(data.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        """转为字典"""
        return {
            "id": self.id,
            "content": self.content,
            "memory_type": self.memory_type.value,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "importance": self.importance,
            "session_id": self.session_id,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryItem":
        """从字典创建"""
        return cls(
            content=data["content"],
            memory_type=MemoryType(data["memory_type"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {}),
            importance=data.get("importance", 0.5),
            session_id=data.get("session_id"),
        )
    
    def to_json(self) -> str:
        """转为 JSON 字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False)
    
    @classmethod
    def from_json(cls, json_str: str) -> "MemoryItem":
        """从 JSON 字符串创建"""
        return cls.from_dict(json.loads(json_str))


@dataclass
class MemorySearchResult:
    """记忆检索结果"""
    item: MemoryItem
    score: float = 0.0  # 相关性得分
    source: str = ""    # 来源 (short_term / long_term)


class BaseMemory(ABC):
    """记忆存储基类"""
    
    @abstractmethod
    def add(self, item: MemoryItem) -> bool:
        """添加记忆"""
        pass
    
    @abstractmethod
    def get(self, memory_id: str) -> Optional[MemoryItem]:
        """获取指定记忆"""
        pass
    
    @abstractmethod
    def search(
        self, 
        query: str, 
        top_k: int = 5,
        memory_type: Optional[MemoryType] = None,
    ) -> List[MemorySearchResult]:
        """检索相关记忆"""
        pass
    
    @abstractmethod
    def delete(self, memory_id: str) -> bool:
        """删除记忆"""
        pass
    
    @abstractmethod
    def clear(self, session_id: Optional[str] = None) -> int:
        """清空记忆，返回删除数量"""
        pass
    
    @abstractmethod
    def count(self) -> int:
        """获取记忆数量"""
        pass
