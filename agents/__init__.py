# -*- coding: utf-8 -*-
"""Agent 模块。

包含所有 Agent 实现：

Solo 模式（单 Agent）:
    from agents import ReactAgent
    
Crew 模式（多 Agent 团队）:
    from agents.crews.resume import ResumeOrchestrator
    from agents.crews import ContentAgent, LayoutAgent

目录结构:
    agents/
    ├── base.py            # Agent 基类
    ├── react_agent.py     # Solo 模式
    └── crews/             # 多 Agent 团队
        └── resume/        # 简历 Crew
"""

# 基类
from .base import BaseLLMAgent

# Solo 模式
from .react_agent import ReactAgent, Agent  # Agent 是别名

# Crew 模式（简化导入）
from .crews.resume import (
    ContentAgent,
    LayoutAgent,
    ResumeOrchestrator,
)

# 向后兼容
ResumeAgentOrchestrator = ResumeOrchestrator

__all__ = [
    # 基类
    "BaseLLMAgent",
    # Solo 模式
    "ReactAgent",
    "Agent",
    # Crew 模式
    "ContentAgent",
    "LayoutAgent",
    "ResumeOrchestrator",
    "ResumeAgentOrchestrator",  # 向后兼容
]
