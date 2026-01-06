# -*- coding: utf-8 -*-
"""Agent 核心模块。

提供 Agent 框架的核心业务逻辑：
- Agent: 智能代理
- Message/Conversation: 消息管理
- Parser: 工具调用解析
"""
# 核心类
from .agent import Agent
from .message import Message, Role, Conversation

# 解析器
from .parser import ToolCall, parse_tool_calls

__all__ = [
    # 核心
    "Agent",
    "Message",
    "Role",
    "Conversation",
    "ToolCall",
    "parse_tool_calls",
]
