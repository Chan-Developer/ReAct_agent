# -*- coding: utf-8 -*-
"""存储层模块。

提供各种存储后端的客户端封装，包括：
- 向量数据库（Milvus）
- 其他存储服务...
"""
from .milvus import MilvusClient

__all__ = [
    "MilvusClient",
]

