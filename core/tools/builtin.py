# -*- coding: utf-8 -*-
"""常用内置工具集合。

后续扩展的新工具也建议放在本文件，或在本包新建子模块。"""
from __future__ import annotations

import re
from .base import BaseTool

__all__ = [
    "Calculator",
    "Search",
    "FileOperations",
]


class Calculator(BaseTool):
    """执行简单数学表达式计算。"""

    def __init__(self) -> None:
        super().__init__(
            name="calculator",
            description="执行数学计算",
            parameters={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式"
                    }
                },
                "required": ["expression"],
            },
        )

    def execute(self, expression: str):  # type: ignore[override]
        if re.match(r"^[0-9+\-*/().\s]+$", expression):
            try:
                result = eval(expression)
            except Exception as exc:  # pragma: no cover
                return f"错误：表达式计算失败 => {exc}"
            return f"{expression} = {result}"
        return "错误：表达式包含不安全字符"


class Search(BaseTool):
    """离线演示搜索工具（示例）。"""

    _mock_results: dict[str, str] = {
        "python": "Python 是一种编程语言。",
        "ai": "人工智能相关信息。",
        "天气": "今天天气晴朗。",
    }

    def __init__(self) -> None:
        super().__init__(
            name="search",
            description="搜索信息",
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

    def execute(self, query: str):  # type: ignore[override]
        return self._mock_results.get(query.lower(), f"未找到关于 '{query}' 的信息")


class FileOperations(BaseTool):
    """文件读写演示工具。"""

    def __init__(self) -> None:
        super().__init__(
            name="fileOperations",
            description="文件操作（仅演示，不执行真实 IO）",
            parameters={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "description": "操作类型：read / write",
                    },
                    "filepath": {
                        "type": "string",
                        "description": "文件路径",
                    },
                },
                "required": ["operation", "filepath"],
            },
        )

    def execute(self, operation: str, filepath: str):  # type: ignore[override]
        return f"模拟 {operation} 操作文件：{filepath}"
