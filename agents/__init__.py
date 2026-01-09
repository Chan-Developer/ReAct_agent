# -*- coding: utf-8 -*-
"""Agent 模块。

Solo 模式（单 Agent）:
    from agents import ReactAgent
    agent = ReactAgent(llm, tools)
    agent.run("你的任务")
    
Crew 模式（多 Agent 团队）:
    from core import Orchestrator, Task
    from agents.crews import ResumeCrew
    
    orchestrator = Orchestrator(llm)
    orchestrator.register(ResumeCrew)
    result = orchestrator.run(Task(name="resume", input_data=data))
"""

# 基类
from .base import BaseLLMAgent

# Solo 模式
from .react_agent import ReactAgent, Agent

# Crew 基类
from .crews.base import BaseCrew

# Crew 实现
from .crews.resume.crew import ResumeCrew
from .crews.resume.content_agent import ContentAgent
from .crews.resume.layout_agent import LayoutAgent

__all__ = [
    # 基类
    "BaseLLMAgent",
    "BaseCrew",
    # Solo 模式
    "ReactAgent",
    "Agent",
    # Crews
    "ResumeCrew",
    "ContentAgent",
    "LayoutAgent",
]
