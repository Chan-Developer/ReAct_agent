# -*- coding: utf-8 -*-
"""Agent 模块。

Solo 模式（单 Agent）:
    from agents import ReactAgent
    agent = ReactAgent(llm, tools)
    agent.run("你的任务")

Workflow 模式（专家流水线）:
    from workflows import ResumePipeline
    
    pipeline = ResumePipeline(llm)
    result = pipeline.run(input_data=data, job_description="...")
"""

# 基类
from .base import BaseLLMAgent

# Solo 模式
from .react_agent import ReactAgent, Agent

# 专家 Agent（供 Workflow 使用）
from .crews.resume.content_agent import ContentAgent
from .crews.resume.layout_agent import LayoutAgent

__all__ = [
    # 基类
    "BaseLLMAgent",
    # Solo 模式
    "ReactAgent",
    "Agent",
    # 专家 Agent
    "ContentAgent",
    "LayoutAgent",
]
