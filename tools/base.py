# -*- coding: utf-8 -*-
"""工具基类模块。

定义所有工具的抽象基类。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseTool(ABC):
    """同步工具基类。
    
    所有具体工具都应继承此类并实现 execute 方法。
    
    Attributes:
        name: 工具名称（用于 LLM 调用）
        description: 工具描述
        parameters: 参数 schema（OpenAI 函数调用格式）
        
    Example:
        >>> class MyTool(BaseTool):
        ...     def __init__(self):
        ...         super().__init__(
        ...             name="my_tool",
        ...             description="我的工具",
        ...             parameters={
        ...                 "type": "object",
        ...                 "properties": {
        ...                     "param1": {"type": "string", "description": "参数1"}
        ...                 },
        ...                 "required": ["param1"]
        ...             }
        ...         )
        ...     
        ...     def execute(self, param1: str) -> str:
        ...         return f"处理: {param1}"
    """

    def __init__(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any] | None = None,
    ):
        """初始化工具。
        
        Args:
            name: 工具名称
            description: 工具描述
            parameters: 参数 schema
        """
        self.name = name
        self.description = description
        self.parameters = parameters or {
            "type": "object",
            "properties": {},
            "required": [],
        }

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """执行工具。
        
        子类必须实现此方法。
        
        Returns:
            工具执行结果
        """
        raise NotImplementedError

    def as_function_spec(self) -> Dict[str, Any]:
        """导出为 OpenAI functions 格式的 schema。
        
        Returns:
            OpenAI 函数调用格式的字典
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"


class AsyncBaseTool(BaseTool):
    """异步工具基类。
    
    适用于需要异步 IO 操作的工具。
    """

    @abstractmethod
    async def execute(self, *args, **kwargs) -> Any:
        """异步执行工具。"""
        raise NotImplementedError

