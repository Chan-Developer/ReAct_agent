# -*- coding: utf-8 -*-
"""生成器工具模块。

提供文档生成工具：
- ResumeGenerator: 简历生成器（Word）
- ContentEstimator: 内容空间估算
- LayoutOptimizer: 布局优化（自动分页）
- PageSplitter: 页面拆分

内容优化由 Agent 工具处理（位于 tools/agent_wrappers/）：
- ContentOptimizerTool: 内容优化（包装 ContentAgent）
- LayoutDesignerTool: 布局设计（包装 LayoutAgent）
- StyleSelectorTool: 模板选择
"""
from .resume import ResumeGenerator
from .pagination import ContentEstimator, LayoutOptimizer, PageSplitter

__all__ = [
    "ResumeGenerator",
    "ContentEstimator",
    "LayoutOptimizer",
    "PageSplitter",
]
