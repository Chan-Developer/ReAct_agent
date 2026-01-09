# -*- coding: utf-8 -*-
"""简历优化 Crew。

使用方式:
    from core import Orchestrator, Task
    from agents.crews.resume import ResumeCrew
    
    orchestrator = Orchestrator(llm)
    orchestrator.register(ResumeCrew)
    result = orchestrator.run(Task(name="resume", input_data=data))
"""

from .content_agent import ContentAgent
from .layout_agent import LayoutAgent
from .crew import ResumeCrew

__all__ = [
    "ContentAgent",
    "LayoutAgent",
    "ResumeCrew",
]

