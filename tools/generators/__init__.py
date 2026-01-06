# -*- coding: utf-8 -*-
"""生成器工具模块。

提供各种文档生成工具：
- ResumeGenerator: 简历生成器（Word），支持多 Agent 优化
- ResumeOptimizer: LLM 简历内容优化器（单 Agent 模式）
- ResumeEnhancer: 本地简历增强器（无需 LLM）

多 Agent 架构（位于 agents/ 模块）：
- ContentAgent: 内容优化专家
- LayoutAgent: 布局编排专家
- ResumeAgentOrchestrator: 多 Agent 协调器
"""
from .resume import ResumeGenerator
from .resume_optimizer import ResumeOptimizer
from .enhancer import ResumeEnhancer

__all__ = [
    # 主要工具
    "ResumeGenerator",
    # 优化器
    "ResumeOptimizer",
    # 增强器
    "ResumeEnhancer",
]
