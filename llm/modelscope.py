# -*- coding: utf-8 -*-
"""ModelScope OpenAI-compatible client."""

from __future__ import annotations

from typing import Any, Dict, Generator, List, Optional

from openai import OpenAI

from common import get_config, get_logger
from .base import BaseLLM

logger = get_logger(__name__)


class ModelScopeOpenAI(BaseLLM):
    """ModelScope chat client via the OpenAI-compatible API."""

    supports_native_tool_calling = True

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        config = get_config()
        ms_config = config.llm.modelscope

        self.base_url = base_url or ms_config.base_url
        self.api_key = api_key or ms_config.api_key
        self.model = model or ms_config.model

        if not self.api_key:
            raise ValueError(
                "ModelScope API Key not configured.\n"
                "Configure it via config, env var, or constructor argument."
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
        try:
            extra_body = {
                "enable_thinking": enable_thinking if stream else False,
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
                return response

            usage = getattr(response, "usage", None)
            if usage:
                logger.info(
                    f"[Token Usage] input: {usage.prompt_tokens}, "
                    f"output: {usage.completion_tokens}, "
                    f"total: {usage.total_tokens}"
                )

            message = response.choices[0].message
            tool_calls = []
            for tool_call in message.tool_calls or []:
                if hasattr(tool_call, "model_dump"):
                    tool_calls.append(tool_call.model_dump())
                else:
                    tool_calls.append(dict(tool_call))

            return {
                "role": "assistant",
                "content": message.content,
                "tool_calls": tool_calls,
                "usage": {
                    "prompt_tokens": usage.prompt_tokens if usage else 0,
                    "completion_tokens": usage.completion_tokens if usage else 0,
                    "total_tokens": usage.total_tokens if usage else 0,
                }
                if usage
                else None,
            }

        except Exception as err:
            raise RuntimeError(f"ModelScopeOpenAI request failed: {err}") from err

    def chat_stream(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        enable_thinking: bool = False,
        **kwargs,
    ) -> Generator[str, None, None]:
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
