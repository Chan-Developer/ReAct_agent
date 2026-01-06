# -*- coding: utf-8 -*-
"""搜索工具。"""
from __future__ import annotations

from typing import ClassVar, Dict

from ..base import BaseTool


class Search(BaseTool):
    """搜索工具（演示用）。
    
    这是一个离线演示搜索工具，返回预设的模拟结果。
    实际使用时应替换为真实的搜索 API。
    
    Example:
        >>> search = Search()
        >>> search.execute(query="python")
        'Python 是一种编程语言。'
    """

    # 模拟搜索结果
    MOCK_RESULTS: ClassVar[Dict[str, str]] = {
        "python": "Python 是一种通用编程语言，以简洁易读著称。",
        "ai": "人工智能(AI)是计算机科学的一个分支，致力于创建智能机器。",
        "天气": "今天天气晴朗，温度适宜。",
        "机器学习": "机器学习是人工智能的一个子领域，让计算机从数据中学习。",
    }

    def __init__(self) -> None:
        super().__init__(
            name="search",
            description="搜索信息（演示用，返回预设结果）",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词",
                    }
                },
                "required": ["query"],
            },
        )

    def execute(self, query: str) -> str:
        """执行搜索。
        
        Args:
            query: 搜索关键词
            
        Returns:
            搜索结果或未找到提示
        """
        result = self.MOCK_RESULTS.get(query.lower())
        if result:
            return result
        return f"未找到关于 '{query}' 的信息"

