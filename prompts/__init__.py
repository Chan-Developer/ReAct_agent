# -*- coding: utf-8 -*-
"""提示词模板模块。

集中管理所有 LLM 提示词模板。

模块结构：
    prompts/
    ├── __init__.py      # 模块入口
    ├── agent.py         # Agent 系统提示词
    └── resume.py        # 简历优化提示词
"""
from .agent import REACT_SYSTEM_PROMPT
from .resume import (
    RESUME_OPTIMIZER_SYSTEM_PROMPT,
    RESUME_OPTIMIZE_PROMPT,
    RESUME_SUMMARY_PROMPT,
    RESUME_EXPERIENCE_PROMPT,
)

__all__ = [
    # Agent
    "REACT_SYSTEM_PROMPT",
    # Resume
    "RESUME_OPTIMIZER_SYSTEM_PROMPT",
    "RESUME_OPTIMIZE_PROMPT",
    "RESUME_SUMMARY_PROMPT",
    "RESUME_EXPERIENCE_PROMPT",
]

