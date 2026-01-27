# -*- coding: utf-8 -*-
"""联网搜索工具。

提供多种联网搜索后端：
- TavilySearch: 使用 Tavily API（推荐，专为 AI Agent 设计）
- DuckDuckGoSearch: 使用 DuckDuckGo（免费，无需 API Key）
- WebSearch: 统一接口，根据配置自动选择后端
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import requests

from ..base import BaseTool


class TavilySearch(BaseTool):
    """Tavily 搜索工具。
    
    使用 Tavily API 进行联网搜索，专为 AI Agent 设计，
    返回结构化、干净的搜索结果。
    
    需要 API Key，可通过以下方式获取：
    1. 访问 https://tavily.com 注册账号
    2. 免费额度：1000次/月
    
    Example:
        >>> search = TavilySearch(api_key="tvly-xxx")
        >>> result = search.execute(query="Python 最新版本")
        >>> print(result)
    """
    
    API_URL = "https://api.tavily.com/search"
    
    def __init__(self, api_key: Optional[str] = None, max_results: int = 5) -> None:
        """初始化 Tavily 搜索工具。
        
        Args:
            api_key: Tavily API Key，若不提供则从环境变量 TAVILY_API_KEY 读取
            max_results: 默认返回结果数量
        """
        super().__init__(
            name="tavily_search",
            description="使用 Tavily API 进行联网搜索，返回最新的网络信息",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词或问题",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "返回结果数量（默认5）",
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
        )
        self.api_key = api_key or os.getenv("TAVILY_API_KEY", "")
        self.default_max_results = max_results
    
    def execute(self, query: str, max_results: Optional[int] = None) -> str:
        """执行 Tavily 搜索。
        
        Args:
            query: 搜索关键词
            max_results: 返回结果数量
            
        Returns:
            格式化的搜索结果
        """
        if not self.api_key:
            return "错误：未配置 TAVILY_API_KEY。请设置环境变量或在初始化时传入 api_key。"
        
        max_results = max_results or self.default_max_results
        
        try:
            response = requests.post(
                self.API_URL,
                json={
                    "api_key": self.api_key,
                    "query": query,
                    "max_results": max_results,
                    "include_answer": True,
                    "include_raw_content": False,
                },
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            
            return self._format_results(query, data)
            
        except requests.exceptions.Timeout:
            return f"搜索超时，请稍后重试。查询: {query}"
        except requests.exceptions.RequestException as e:
            return f"搜索请求失败: {e}"
        except Exception as e:
            return f"搜索出错: {e}"
    
    def _format_results(self, query: str, data: Dict[str, Any]) -> str:
        """格式化搜索结果。"""
        lines = [f"搜索: {query}", ""]
        
        # 如果有直接答案
        if data.get("answer"):
            lines.append(f"📝 摘要: {data['answer']}")
            lines.append("")
        
        # 搜索结果列表
        results = data.get("results", [])
        if results:
            lines.append("🔍 搜索结果:")
            for i, item in enumerate(results, 1):
                title = item.get("title", "无标题")
                url = item.get("url", "")
                content = item.get("content", "")[:200]  # 截取前200字符
                lines.append(f"\n{i}. {title}")
                lines.append(f"   链接: {url}")
                lines.append(f"   摘要: {content}...")
        else:
            lines.append("未找到相关结果。")
        
        return "\n".join(lines)


class DuckDuckGoSearch(BaseTool):
    """DuckDuckGo 搜索工具。
    
    使用 DuckDuckGo 进行联网搜索，完全免费，无需 API Key。
    
    Example:
        >>> search = DuckDuckGoSearch()
        >>> result = search.execute(query="Python 教程")
        >>> print(result)
    """
    
    def __init__(self, max_results: int = 5) -> None:
        """初始化 DuckDuckGo 搜索工具。
        
        Args:
            max_results: 默认返回结果数量
        """
        super().__init__(
            name="duckduckgo_search",
            description="使用 DuckDuckGo 进行联网搜索（免费，无需 API Key）",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词或问题",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "返回结果数量（默认5）",
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
        )
        self.default_max_results = max_results
    
    def execute(self, query: str, max_results: Optional[int] = None) -> str:
        """执行 DuckDuckGo 搜索。
        
        Args:
            query: 搜索关键词
            max_results: 返回结果数量
            
        Returns:
            格式化的搜索结果
        """
        max_results = max_results or self.default_max_results
        
        # 尝试导入新版或旧版库
        try:
            from ddgs import DDGS
        except ImportError:
            try:
                from duckduckgo_search import DDGS
            except ImportError:
                return "错误：未安装搜索库。请运行: pip install ddgs"
        
        try:
            ddgs = DDGS()
            results = list(ddgs.text(query, max_results=max_results))
            
            return self._format_results(query, results)
            
        except Exception as e:
            return f"搜索出错: {e}"
    
    def _format_results(self, query: str, results: List[Dict[str, Any]]) -> str:
        """格式化搜索结果。"""
        lines = [f"搜索: {query}", ""]
        
        if results:
            lines.append("🔍 搜索结果:")
            for i, item in enumerate(results, 1):
                title = item.get("title", "无标题")
                url = item.get("href", item.get("link", ""))
                body = item.get("body", item.get("snippet", ""))[:200]
                lines.append(f"\n{i}. {title}")
                lines.append(f"   链接: {url}")
                lines.append(f"   摘要: {body}...")
        else:
            lines.append("未找到相关结果。")
        
        return "\n".join(lines)


class WebSearch(BaseTool):
    """统一的联网搜索工具。
    
    根据配置自动选择搜索后端：
    - 如果配置了 TAVILY_API_KEY，使用 Tavily
    - 否则使用 DuckDuckGo（免费）
    
    Example:
        >>> search = WebSearch()
        >>> result = search.execute(query="最新科技新闻")
        >>> print(result)
    """
    
    def __init__(
        self, 
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        max_results: int = 5,
    ) -> None:
        """初始化联网搜索工具。
        
        Args:
            provider: 搜索后端，"tavily" 或 "duckduckgo"，
                      若不指定则根据 API Key 自动选择
            api_key: Tavily API Key（使用 Tavily 时需要）
            max_results: 默认返回结果数量
        """
        super().__init__(
            name="web_search",
            description="联网搜索，获取最新的网络信息",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词或问题",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "返回结果数量（默认5）",
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
        )
        
        self.api_key = api_key or os.getenv("TAVILY_API_KEY", "")
        self.max_results = max_results
        
        # 自动选择后端
        if provider:
            self.provider = provider.lower()
        elif self.api_key:
            self.provider = "tavily"
        else:
            self.provider = "duckduckgo"
        
        # 初始化对应的搜索工具
        if self.provider == "tavily":
            self._search_tool = TavilySearch(api_key=self.api_key, max_results=max_results)
        else:
            self._search_tool = DuckDuckGoSearch(max_results=max_results)
    
    def execute(self, query: str, max_results: Optional[int] = None) -> str:
        """执行联网搜索。
        
        Args:
            query: 搜索关键词
            max_results: 返回结果数量
            
        Returns:
            格式化的搜索结果
        """
        return self._search_tool.execute(query, max_results)
