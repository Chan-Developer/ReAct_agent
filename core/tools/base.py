# -*- coding: utf-8 -*-
"""基础 Tool 抽象类。
所有具体工具都应继承自 BaseTool / AsyncBaseTool。
"""
from __future__ import annotations

from abc import ABC, abstractmethod

__all__ = [
    "BaseTool",
    "AsyncBaseTool",
]


class BaseTool(ABC):
    """同步工具基类。"""

    def __init__(self, name: str, parameters: dict, description: str):
        self.name = name
        self.parameters = parameters
        self.description = description

    @abstractmethod
    def execute(self, *args, **kwargs):  # noqa: D401,E501
        """执行工具。
        子类实现具体逻辑。"""
        raise NotImplementedError

    # ---------------------------------------------------------------------
    # OpenAI 兼容
    # ---------------------------------------------------------------------
    def as_function_spec(self) -> dict:  # noqa: D401
        """以 OpenAI `functions` 字段所需格式导出工具 schema。"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }


class AsyncBaseTool(BaseTool):
    """异步工具基类。适用于需要 IO 等异步操作的工具。"""

    @abstractmethod
    async def execute(self, *args, **kwargs):
        raise NotImplementedError
