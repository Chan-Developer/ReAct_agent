# -*- coding: utf-8 -*-
"""Local vLLM OpenAI-compatible client."""

from __future__ import annotations

from typing import Any, Dict, List

import requests

from .base import BaseLLM


class VllmLLM(BaseLLM):
    """Thin wrapper around a local vLLM chat endpoint."""

    supports_native_tool_calling = False

    def __init__(
        self,
        base_url: str = "http://localhost:8000/v1",
        model: str = "Qwen3-0.6B/",
        timeout: int = 120,
    ):
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
            raise RuntimeError(f"VllmLLM request timed out ({self.timeout}s)")
        except requests.exceptions.ConnectionError:
            raise RuntimeError(f"VllmLLM connection failed: {url}")
        except Exception as err:
            raise RuntimeError(f"VllmLLM request failed: {err}") from err

        data = resp.json()
        if not data.get("choices"):
            raise RuntimeError(f"VllmLLM returned invalid payload: {data}")

        return data["choices"][0]["message"]
