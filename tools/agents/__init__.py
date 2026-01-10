# -*- coding: utf-8 -*-
"""Agent 工具模块。

将专家 Agent 包装为 Tool，供 ReactAgent 调用。
保留 Agent 内部的 Think-Execute-Reflect 完整流程。

使用方式:
    from tools.agents import ContentOptimizerTool, LayoutDesignerTool
    
    tools = [
        ContentOptimizerTool(llm),
        LayoutDesignerTool(llm),
        ResumeGenerator(output_dir="./output"),
    ]
    agent = ReactAgent(llm=llm, tools=tools)
"""
from .content_optimizer import ContentOptimizerTool
from .layout_designer import LayoutDesignerTool

__all__ = [
    "ContentOptimizerTool",
    "LayoutDesignerTool",
]
