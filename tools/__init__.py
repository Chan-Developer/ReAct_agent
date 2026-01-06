# -*- coding: utf-8 -*-
"""工具模块。

提供 Agent 可调用的各种工具。

模块结构:
    - base: 工具基类
    - registry: 工具注册器
    - builtin: 内置工具（计算器、搜索、文件操作等）
    - generators: 生成器工具（简历生成等）
"""
from .base import BaseTool, AsyncBaseTool
from .registry import ToolRegistry

# 内置工具
from .builtin import Calculator, Search, AddFile, ReadFile

# 生成器工具
from .generators import ResumeGenerator

__all__ = [
    # 基类
    "BaseTool",
    "AsyncBaseTool",
    "ToolRegistry",
    
    # 内置工具
    "Calculator",
    "Search",
    "AddFile",
    "ReadFile",
    
    # 生成器
    "ResumeGenerator",
]

