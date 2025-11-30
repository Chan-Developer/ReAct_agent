# -*- coding: utf-8 -*-
"""工具注册器 - 实现工具的动态注入和管理。

使用方式:
    1. 装饰器注册:
        @tool_registry.register
        class MyTool(BaseTool):
            pass
    
    2. 手动注册:
        tool_registry.register_tool(MyTool())
    
    3. 批量注册:
        tool_registry.register_tools([tool1, tool2, tool3])
"""
from __future__ import annotations

from typing import Dict, List, Optional
from .tools.base import BaseTool

__all__ = ["ToolRegistry", "tool_registry"]


class ToolRegistry:
    """工具注册中心，负责工具的注册、查询和管理。"""

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool_class_or_instance):
        """
        注册工具，支持类或实例。
        
        可以作为装饰器使用:
            @registry.register
            class MyTool(BaseTool):
                pass
        
        或直接调用:
            registry.register(MyTool())
        """
        # 如果是类，实例化它
        if isinstance(tool_class_or_instance, type):
            tool = tool_class_or_instance()
        else:
            tool = tool_class_or_instance
        
        if not isinstance(tool, BaseTool):
            raise TypeError(f"工具必须继承自 BaseTool，但得到了 {type(tool)}")
        
        self._tools[tool.name] = tool
        return tool_class_or_instance  # 返回原对象，支持装饰器链

    def register_tool(self, tool: BaseTool):
        """手动注册单个工具实例。"""
        if not isinstance(tool, BaseTool):
            raise TypeError(f"工具必须继承自 BaseTool，但得到了 {type(tool)}")
        self._tools[tool.name] = tool

    def register_tools(self, tools: List[BaseTool]):
        """批量注册工具列表。"""
        for tool in tools:
            self.register_tool(tool)

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """根据名称获取工具。"""
        return self._tools.get(name)

    def get_all_tools(self) -> List[BaseTool]:
        """获取所有已注册的工具。"""
        return list(self._tools.values())

    def get_tools_spec(self) -> List[dict]:
        """
        获取所有工具的 OpenAI Function Calling 规范。
        
        返回格式:
            [
                {
                    "type": "function",
                    "function": {
                        "name": "calculator",
                        "description": "执行数学计算",
                        "parameters": {...}
                    }
                },
                ...
            ]
        """
        return [
            {
                "type": "function",
                "function": tool.as_function_spec()
            }
            for tool in self._tools.values()
        ]

    def unregister(self, tool_name: str):
        """注销工具。"""
        if tool_name in self._tools:
            del self._tools[tool_name]

    def clear(self):
        """清空所有注册的工具。"""
        self._tools.clear()

    def __len__(self):
        """返回已注册工具的数量。"""
        return len(self._tools)

    def __contains__(self, tool_name: str):
        """检查工具是否已注册。"""
        return tool_name in self._tools

    def __repr__(self):
        tool_names = list(self._tools.keys())
        return f"ToolRegistry(tools={tool_names})"


# 全局单例注册器
tool_registry = ToolRegistry()

