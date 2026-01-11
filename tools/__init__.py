# -*- coding: utf-8 -*-
"""工具模块。

提供 Agent 可调用的各种工具。

模块结构:
    - base: 工具基类
    - registry: 工具注册器
    - builtin: 内置工具（计算器、搜索、文件操作等）
    - generators: 生成器工具（简历生成、分页优化等）
    - agents: Agent 包装工具（将专家 Agent 包装为 Tool）
    - templates: 模板系统（模板配置、注册表）

注意：向量数据库客户端已移至 storage 模块，请使用:
    from storage import MilvusClient
"""
from .base import BaseTool, AsyncBaseTool
from .registry import ToolRegistry

# 内置工具
from .builtin import Calculator, Search, AddFile, ReadFile

# 生成器工具
from .generators import ResumeGenerator, ContentEstimator, LayoutOptimizer, PageSplitter

# Agent 包装工具（用于多智能体协作）
from .agent_wrappers import ContentOptimizerTool, LayoutDesignerTool, StyleSelectorTool

# 模板系统
from .templates import TemplateRegistry, TemplateConfig, get_registry

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
    "ContentEstimator",
    "LayoutOptimizer",
    "PageSplitter",
    
    # Agent 工具（多智能体）
    "ContentOptimizerTool",
    "LayoutDesignerTool",
    "StyleSelectorTool",
    
    # 模板系统
    "TemplateRegistry",
    "TemplateConfig",
    "get_registry",
]

