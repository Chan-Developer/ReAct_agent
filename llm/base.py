# -*- coding: utf-8 -*-
"""LLM 基础抽象模块。

定义 LLM 接口的抽象基类、协议和通用数据结构。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Generator, List, Optional, Protocol, runtime_checkable


@dataclass
class LLMResponse:
    """LLM 响应数据结构"""
    role: str = "assistant"
    content: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {"role": self.role}
        if self.content is not None:
            result["content"] = self.content
        if self.tool_calls:
            result["tool_calls"] = self.tool_calls
        return result


@runtime_checkable
class LLMProtocol(Protocol):
    """LLM 接口协议。
    
    用于类型检查，任何实现了 chat 方法的对象都可以作为 LLM 使用。
    这是一个结构化子类型（鸭子类型）的协议定义。
    
    Example:
        >>> def process(llm: LLMProtocol):
        ...     response = llm.chat([{"role": "user", "content": "Hello"}])
        ...     return response["content"]
    """
    
    def chat(
        self,
        messages: List[Dict[str, Any]],
        **kwargs,
    ) -> Dict[str, Any]:
        """发送对话请求。
        
        Args:
            messages: OpenAI 风格的消息列表
            **kwargs: 其他参数（temperature, max_tokens 等）
            
        Returns:
            响应消息字典，格式为 {"role": "assistant", "content": "..."}
        """
        ...


class BaseLLM(ABC):
    """LLM 抽象基类。
    
    所有 LLM 实现都应继承此类。
    """
    
    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs,
    ) -> Dict[str, Any]:
        """发送对话请求。
        
        Args:
            messages: OpenAI 风格的消息列表
            temperature: 采样温度
            max_tokens: 最大生成 token 数
            **kwargs: 其他参数
            
        Returns:
            响应消息字典，格式为 {"role": "assistant", "content": "..."}
        """
        raise NotImplementedError
    
    def chat_stream(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs,
    ) -> Generator[str, None, None]:
        """流式对话请求。
        
        Args:
            messages: OpenAI 风格的消息列表
            temperature: 采样温度
            max_tokens: 最大生成 token 数
            **kwargs: 其他参数
            
        Yields:
            逐块返回的内容字符串
        """
        # 默认实现：不支持流式
        response = self.chat(messages, temperature, max_tokens, **kwargs)
        yield response.get("content", "")

