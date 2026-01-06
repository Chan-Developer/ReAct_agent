# -*- coding: utf-8 -*-
"""Crew 模块。

包含各种多 Agent 团队：
- resume: 简历优化 Crew（ContentAgent + LayoutAgent）
- (未来可扩展) code_review: 代码审查 Crew
- (未来可扩展) data_analysis: 数据分析 Crew
"""

from .resume import (
    ContentAgent,
    LayoutAgent,
    ResumeOrchestrator,
)

__all__ = [
    # 简历 Crew
    "ContentAgent",
    "LayoutAgent",
    "ResumeOrchestrator",
]

