# -*- coding: utf-8 -*-
"""Memory 模块。

提供 Agent 的记忆管理功能：
- 短期记忆 (ShortTermMemory): 基于 Redis，存储当前会话上下文
- 长期记忆 (LongTermMemory): 基于 Milvus 向量数据库，存储重要经验
- MemoryManager: 统一管理短期和长期记忆
"""
from .base import BaseMemory, MemoryItem, MemoryType
from .short_term import ShortTermMemory
from .long_term import LongTermMemory
from .manager import MemoryManager

__all__ = [
    "BaseMemory",
    "MemoryItem",
    "MemoryType",
    "ShortTermMemory",
    "LongTermMemory",
    "MemoryManager",
]
