# -*- coding: utf-8 -*-
"""核心基础设施模块。

提供框架的基础组件：
- Task/TaskResult: 通用任务定义
- Orchestrator: 通用协调器
- BaseKnowledgeBase: 知识库接口
- Message/Conversation: 消息管理
- Parser: 工具调用解析
"""
# 任务
from .task import Task, TaskResult

# 协调器
from .orchestrator import Orchestrator

# 知识库
from .knowledge import BaseKnowledgeBase, Document, SearchResult

# 消息管理
from .message import Message, Role, Conversation

# 解析器
from .parser import ToolCall, parse_tool_calls

__all__ = [
    # 任务
    "Task",
    "TaskResult",
    # 协调器
    "Orchestrator",
    # 知识库
    "BaseKnowledgeBase",
    "Document",
    "SearchResult",
    # 消息
    "Message",
    "Role",
    "Conversation",
    # 解析
    "ToolCall",
    "parse_tool_calls",
]
