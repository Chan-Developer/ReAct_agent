# -*- coding: utf-8 -*-
"""工具调用解析器。"""
import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from common import get_logger

logger = get_logger(__name__)


@dataclass
class ToolCall:
    """工具调用"""
    name: str
    arguments: Dict[str, Any]
    id: Optional[str] = None


def parse_tool_calls(response: Dict[str, Any]) -> Optional[List[ToolCall]]:
    """从 LLM 响应中解析工具调用"""
    
    # 1. 尝试 OpenAI 原生格式
    if tool_calls := response.get("tool_calls"):
        return _parse_native(tool_calls)
    
    # 2. 从文本解析
    if content := response.get("content"):
        return _parse_from_text(content)
    
    return None


def _parse_native(tool_calls: list) -> Optional[List[ToolCall]]:
    """解析 OpenAI 原生格式"""
    results = []
    for tc in tool_calls:
        try:
            func = tc.get("function", {})
            args = func.get("arguments", "{}")
            results.append(ToolCall(
                name=func.get("name"),
                arguments=json.loads(args) if isinstance(args, str) else args,
                id=tc.get("id"),
            ))
        except Exception as e:
            logger.warning(f"解析失败: {e}")
    return results or None


def _parse_from_text(content: str) -> Optional[List[ToolCall]]:
    """从文本解析工具调用"""
    
    # 匹配 Action: {...}
    match = re.search(r'Action:\s*(\{.+)', content, re.DOTALL)
    if match:
        json_str = _extract_json(match.group(1))
        if json_str:
            return _parse_json_call(json_str)
    
    # 匹配任意 {"name": ...}
    match = re.search(r'\{\s*"name"\s*:', content)
    if match:
        json_str = _extract_json(content[match.start():])
        if json_str:
            return _parse_json_call(json_str)
    
    return None


def _parse_json_call(json_str: str) -> Optional[List[ToolCall]]:
    """解析 JSON 格式的工具调用"""
    try:
        data = json.loads(json_str)
        if "name" not in data:
            logger.warning("JSON 中没有 'name' 字段")
            return None
        
        args = data.get("arguments", {})
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except json.JSONDecodeError as e:
                logger.warning(f"arguments 内部 JSON 解析失败: {e}")
                logger.warning(f"arguments 内容前200字符: {args[:200]}")
                return None
        
        logger.debug(f"解析到工具调用: {data['name']}")
        return [ToolCall(name=data["name"], arguments=args)]
    except json.JSONDecodeError as e:
        logger.warning(f"外层 JSON 解析失败: {e}")
        logger.warning(f"JSON 字符串前200字符: {json_str[:200]}")
        return None
    except Exception as e:
        logger.warning(f"解析异常: {type(e).__name__}: {e}")
        return None


def _extract_json(text: str) -> Optional[str]:
    """使用括号匹配提取完整 JSON"""
    if not text.startswith('{'):
        return None
    
    depth = 0
    in_str = False
    escape = False
    
    for i, c in enumerate(text):
        if escape:
            escape = False
            continue
        if c == '\\':
            escape = True
            continue
        if c == '"' and not escape:
            in_str = not in_str
            continue
        if in_str:
            continue
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return text[:i + 1]
    
    return None
