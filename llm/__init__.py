# -*- coding: utf-8 -*-
"""LLM 接口模块。

提供统一的 LLM 接口抽象和多种实现。

支持的 LLM:
    - VllmLLM: 本地 vLLM 服务
    - ModelScopeOpenAI: ModelScope 云平台
"""
from .base import BaseLLM, LLMResponse, LLMProtocol
from .vllm import VllmLLM
from .modelscope import ModelScopeOpenAI

__all__ = [
    # 基础类型
    "BaseLLM",
    "LLMResponse",
    "LLMProtocol",
    # 实现类
    "VllmLLM",
    "ModelScopeOpenAI",
]

