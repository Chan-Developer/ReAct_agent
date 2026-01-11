# -*- coding: utf-8 -*-
"""Agent 工具模块。

将专家 Agent 包装为 Tool，供 ReactAgent 调用。
保留 Agent 内部的 Think-Execute-Reflect 完整流程。

使用方式:
    from tools.agent_wrappers import ContentOptimizerTool, LayoutDesignerTool, StyleSelectorTool
    
    tools = [
        ContentOptimizerTool(llm),
        StyleSelectorTool(llm),  # 新增：模板选择
        LayoutDesignerTool(llm),
        ResumeGenerator(output_dir="./output"),
    ]
    agent = ReactAgent(llm=llm, tools=tools)
"""
from .content_optimizer import ContentOptimizerTool
from .layout_designer import LayoutDesignerTool
from .style_selector import StyleSelectorTool

__all__ = [
    "ContentOptimizerTool",
    "LayoutDesignerTool",
    "StyleSelectorTool",
]
