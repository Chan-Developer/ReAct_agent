# -*- coding: utf-8 -*-
"""通用知识库接口。"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Document:
    """知识文档"""
    text: str
    source: str = ""
    category: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchResult:
    """检索结果"""
    text: str
    score: float
    source: str = ""
    category: str = ""


class BaseKnowledgeBase(ABC):
    """知识库抽象基类"""
    
    @abstractmethod
    def add(self, documents: List[Document]) -> int:
        """添加文档，返回添加数量"""
        pass
    
    @abstractmethod
    def search(
        self,
        query: str,
        top_k: int = 5,
        category: Optional[str] = None,
    ) -> List[SearchResult]:
        """检索相关文档"""
        pass
    
    def retrieve_context(self, query: str, top_k: int = 3) -> List[str]:
        """便捷方法：检索并返回文本列表"""
        results = self.search(query, top_k=top_k)
        return [r.text for r in results]

