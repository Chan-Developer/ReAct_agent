# -*- coding: utf-8 -*-
"""工具注册器模块。

管理工具的注册、查询和获取。
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Type

from .base import BaseTool


class ToolRegistry:
    """工具注册器。
    
    集中管理所有可用工具，支持动态注册和查询。
    
    Example:
        >>> registry = ToolRegistry()
        >>> registry.register(Calculator())
        >>> registry.register_tools([Search(), AddFile()])
        >>> 
        >>> tool = registry.get("calculator")
        >>> result = tool.execute(expression="1+1")
    """

    def __init__(self):
        """初始化注册器。"""
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """注册单个工具。
        
        Args:
            tool: 工具实例
            
        Raises:
            ValueError: 工具名称已存在
        """
        if tool.name in self._tools:
            raise ValueError(f"工具 '{tool.name}' 已注册")
        self._tools[tool.name] = tool

    def register_tools(self, tools: Iterable[BaseTool]) -> None:
        """批量注册工具。
        
        Args:
            tools: 工具实例列表
        """
        for tool in tools:
            self.register(tool)

    def unregister(self, name: str) -> bool:
        """注销工具。
        
        Args:
            name: 工具名称
            
        Returns:
            是否成功注销
        """
        if name in self._tools:
            del self._tools[name]
            return True
        return False

    def get(self, name: str) -> Optional[BaseTool]:
        """获取工具。
        
        Args:
            name: 工具名称
            
        Returns:
            工具实例，如果不存在则返回 None
        """
        return self._tools.get(name)

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """获取工具（别名）。"""
        return self.get(name)

    def get_all(self) -> List[BaseTool]:
        """获取所有已注册的工具。"""
        return list(self._tools.values())

    def get_all_tools(self) -> List[BaseTool]:
        """获取所有工具（别名）。"""
        return self.get_all()

    def get_names(self) -> List[str]:
        """获取所有工具名称。"""
        return list(self._tools.keys())

    def get_tool_names(self) -> List[str]:
        """获取所有工具名称（别名）。"""
        return self.get_names()

    def has(self, name: str) -> bool:
        """检查工具是否已注册。"""
        return name in self._tools

    def clear(self) -> None:
        """清空所有工具。"""
        self._tools.clear()

    def as_function_specs(self) -> List[Dict]:
        """导出所有工具的 OpenAI 函数规范。"""
        return [tool.as_function_spec() for tool in self._tools.values()]

    def __len__(self) -> int:
        return len(self._tools)

    def __contains__(self, name: str) -> bool:
        return name in self._tools

    def __iter__(self):
        return iter(self._tools.values())

    def __repr__(self) -> str:
        return f"ToolRegistry(tools={list(self._tools.keys())})"

