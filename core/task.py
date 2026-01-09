# -*- coding: utf-8 -*-
"""通用任务定义。"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Task:
    """通用任务"""
    name: str                                    # 任务名称
    input_data: Any                              # 输入数据
    context: Dict[str, Any] = field(default_factory=dict)  # RAG 上下文
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskResult:
    """任务执行结果"""
    success: bool
    output: Any
    suggestions: List[str] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)
    error: Optional[str] = None

