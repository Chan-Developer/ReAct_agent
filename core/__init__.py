# -*- coding: utf-8 -*-
"""核心基础设施模块。

提供框架的基础组件：
- Message/Conversation: 消息和对话管理
- Parser: 工具调用解析

注意：Agent 实现已移至 agents/ 模块。
"""
# 消息管理
from .message import Message, Role, Conversation

# 解析器
from .parser import ToolCall, parse_tool_calls

__all__ = [
    # 消息
    "Message",
    "Role",
    "Conversation",
    # 解析
    "ToolCall",
    "parse_tool_calls",
]
