# -*- coding: utf-8 -*-
"""自定义异常。"""
from typing import Any, Optional


class AgentBaseException(Exception):
    """Agent 基础异常"""
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.details = details


# LLM 异常
class LLMException(AgentBaseException):
    """LLM 相关异常"""
    pass


# 工具异常
class ToolException(AgentBaseException):
    """工具相关异常"""
    pass


class ToolNotFoundError(ToolException):
    """工具未找到"""
    def __init__(self, name: str, available: list):
        super().__init__(f"工具 '{name}' 未找到", {"available": available})


class ToolExecutionError(ToolException):
    """工具执行错误"""
    def __init__(self, name: str, error: Exception):
        super().__init__(f"工具 '{name}' 执行失败: {error}")


# 解析异常
class ParseException(AgentBaseException):
    """解析异常"""
    pass


# 运行时异常
class AgentRuntimeError(AgentBaseException):
    """Agent 运行时错误"""
    pass


class MaxRoundsExceededError(AgentRuntimeError):
    """超过最大迭代次数"""
    def __init__(self, max_rounds: int):
        super().__init__(f"达到最大迭代次数 ({max_rounds})")
