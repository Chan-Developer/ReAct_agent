# -*- coding: utf-8 -*-
"""Crew 模块。

通用框架：
- BaseCrew: Crew 基类

已实现的团队：
- ResumeCrew: 简历优化

扩展方式：继承 BaseCrew，实现 _init_agents() 和 _execute()
"""

# 基类
from .base import BaseCrew

# 简历 Crew
from .resume import ResumeCrew, ContentAgent, LayoutAgent

__all__ = [
    "BaseCrew",
    "ResumeCrew",
    "ContentAgent",
    "LayoutAgent",
]

