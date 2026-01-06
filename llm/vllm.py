# -*- coding: utf-8 -*-
"""vLLM 本地服务接口。

使用本地部署的 vLLM 服务，通过 OpenAI 兼容接口通信。
"""
from __future__ import annotations

from typing import Any, Dict, List

import requests

from .base import BaseLLM


class VllmLLM(BaseLLM):
    """本地 vLLM OpenAI 兼容接口封装。
    
    Attributes:
        base_url: vLLM 服务地址
        model: 模型名称
        timeout: 请求超时时间（秒）
        
    Example:
        >>> llm = VllmLLM(base_url="http://localhost:8000/v1")
        >>> response = llm.chat([{"role": "user", "content": "你好"}])
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000/v1",
        model: str = "Qwen3-0.6B/",
        timeout: int = 120,
    ):
        """初始化 vLLM 客户端。
        
        Args:
            base_url: vLLM 服务基础 URL
            model: 模型名称/路径
            timeout: 请求超时时间（秒）
        """
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def chat(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs,
    ) -> Dict[str, Any]:
        """与 vLLM 服务通信。
        
        注意:
            vLLM 不支持原生的 tools 参数，工具信息应该编码到
            系统提示词中，由 Agent 层面处理。
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs,
        }

        url = f"{self.base_url}/chat/completions"
        
        try:
            resp = requests.post(url, json=payload, timeout=self.timeout)
            resp.raise_for_status()
        except requests.exceptions.Timeout:
            raise RuntimeError(f"VllmLLM 请求超时 ({self.timeout}s)")
        except requests.exceptions.ConnectionError:
            raise RuntimeError(f"VllmLLM 连接失败: {url}")
        except Exception as err:
            raise RuntimeError(f"VllmLLM 请求失败: {err}") from err

        data = resp.json()
        
        if not data.get("choices"):
            raise RuntimeError(f"VllmLLM 返回数据异常: {data}")

        return data["choices"][0]["message"]

