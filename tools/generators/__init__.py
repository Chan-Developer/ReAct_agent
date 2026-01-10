# -*- coding: utf-8 -*-
"""生成器工具模块。

提供文档生成工具：
- ResumeGenerator: 简历生成器（Word）

内容优化由 Agent 工具处理（位于 tools/agents/）：
- ContentOptimizerTool: 内容优化（包装 ContentAgent）
- LayoutDesignerTool: 布局设计（包装 LayoutAgent）
"""
from .resume import ResumeGenerator

__all__ = [
    "ResumeGenerator",
]
