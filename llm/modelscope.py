# -*- coding: utf-8 -*-
"""ModelScope 云平台接口。

使用 ModelScope 提供的 OpenAI 兼容 API。
"""
from __future__ import annotations

from typing import Any, Dict, Generator, List, Optional

from openai import OpenAI

from .base import BaseLLM
from common import get_config, get_logger

logger = get_logger(__name__)


class ModelScopeOpenAI(BaseLLM):
    """ModelScope 云平台 OpenAI 兼容接口封装。
    
    配置读取优先级: 传入参数 > 环境变量 > 配置文件 > 默认值
    
    Attributes:
        client: OpenAI 客户端实例
        model: 模型 ID
        
    Example:
        >>> llm = ModelScopeOpenAI()  # 自动从配置文件读取
        >>> response = llm.chat([{"role": "user", "content": "你好"}])
        
        >>> llm = ModelScopeOpenAI(api_key="your-api-key")  # 或手动指定
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        """初始化 ModelScope 客户端。
        
        Args:
            base_url: API 基础 URL
            api_key: API 密钥
            model: 模型 ID
            
        Note:
            如果不传参数，会自动从 configs/config.yaml 或环境变量读取。
        """
        # 从配置系统获取配置
        config = get_config()
        ms_config = config.llm.modelscope
        
        # 优先级: 传入参数 > 配置文件（已含环境变量覆盖）
        self.base_url = base_url or ms_config.base_url
        self.api_key = api_key or ms_config.api_key
        self.model = model or ms_config.model
        
        if not self.api_key:
            raise ValueError(
                "ModelScope API Key 未设置。\n"
                "请选择以下任一方式配置:\n"
                "  1. 编辑 configs/config.yaml 填入 api_key\n"
                "  2. 设置环境变量 export MODELSCOPE_API_KEY='你的密钥'\n"
                "  3. 代码中传入 ModelScopeOpenAI(api_key='你的密钥')"
            )
        
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )

    def chat(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stream: bool = False,
        enable_thinking: bool = False,
        **kwargs,
    ) -> Dict[str, Any]:
        """与 ModelScope API 通信。
        
        Args:
            messages: OpenAI 风格的消息列表
            temperature: 采样温度
            max_tokens: 最大生成 token 数（默认 4096，适合生成长 JSON）
            stream: 是否启用流式输出
            enable_thinking: 是否启用思考模式（仅流式支持）
            **kwargs: 其他参数
            
        Returns:
            响应消息字典
            
        Note:
            Qwen3 等思考模型在非流式调用时必须关闭 enable_thinking。
        """
        try:
            # 非流式调用必须关闭 enable_thinking
            extra_body = {
                "enable_thinking": enable_thinking if stream else False
            }
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=stream,
                temperature=temperature,
                max_tokens=max_tokens,
                extra_body=extra_body,
                **kwargs,
            )
            
            if stream:
                # 流式模式返回迭代器
                return response
            
            # 记录 token 使用情况
            usage = getattr(response, 'usage', None)
            if usage:
                logger.info(
                    f"[Token Usage] input: {usage.prompt_tokens}, "
                    f"output: {usage.completion_tokens}, "
                    f"total: {usage.total_tokens}"
                )
            
            return {
                "role": "assistant",
                "content": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": usage.prompt_tokens if usage else 0,
                    "completion_tokens": usage.completion_tokens if usage else 0,
                    "total_tokens": usage.total_tokens if usage else 0,
                } if usage else None,
            }
            
        except Exception as err:
            raise RuntimeError(f"ModelScopeOpenAI 请求失败: {err}") from err

    def chat_stream(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        enable_thinking: bool = False,
        **kwargs,
    ) -> Generator[str, None, None]:
        """流式对话请求。
        
        Args:
            messages: OpenAI 风格的消息列表
            temperature: 采样温度
            max_tokens: 最大生成 token 数
            enable_thinking: 是否启用思考模式
            **kwargs: 其他参数
            
        Yields:
            逐块返回的内容字符串
        """
        response = self.chat(
            messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            enable_thinking=enable_thinking,
            **kwargs,
        )
        
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

