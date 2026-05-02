# -*- coding: utf-8 -*-
"""Tool registry and validation helpers."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Tuple

from .base import BaseTool


class ToolRegistry:
    """Central registry for agent tools."""

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' already registered")
        self._tools[tool.name] = tool

    def register_tools(self, tools: Iterable[BaseTool]) -> None:
        for tool in tools:
            self.register(tool)

    def unregister(self, name: str) -> bool:
        if name in self._tools:
            del self._tools[name]
            return True
        return False

    def get(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name)

    def get_tool(self, name: str) -> Optional[BaseTool]:
        return self.get(name)

    def get_all(self) -> List[BaseTool]:
        return list(self._tools.values())

    def get_all_tools(self) -> List[BaseTool]:
        return self.get_all()

    def get_names(self) -> List[str]:
        return list(self._tools.keys())

    def get_tool_names(self) -> List[str]:
        return self.get_names()

    def has(self, name: str) -> bool:
        return name in self._tools

    def clear(self) -> None:
        self._tools.clear()

    def as_function_specs(self) -> List[Dict[str, Any]]:
        return [tool.as_function_spec() for tool in self._tools.values()]

    def validate_call(self, name: str, arguments: Dict[str, Any]) -> Tuple[bool, str]:
        tool = self.get(name)
        if tool is None:
            return False, f"Tool not found: '{name}'"
        if not isinstance(arguments, dict):
            return False, "Tool arguments must be an object"

        schema = tool.as_function_spec().get("parameters", {})
        required = schema.get("required", [])
        properties = schema.get("properties", {})

        for field in required:
            if field not in arguments:
                return False, f"Missing required argument: '{field}'"

        for key, value in arguments.items():
            expected = properties.get(key, {}).get("type")
            if expected and not self._matches_type(value, expected):
                return False, (
                    f"Invalid argument type for '{key}': "
                    f"expected {expected}, got {type(value).__name__}"
                )

        return True, ""

    @staticmethod
    def _matches_type(value: Any, expected: str) -> bool:
        type_map = {
            "string": lambda v: isinstance(v, str),
            "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
            "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
            "boolean": lambda v: isinstance(v, bool),
            "object": lambda v: isinstance(v, dict),
            "array": lambda v: isinstance(v, list),
        }
        checker = type_map.get(expected)
        return checker(value) if checker else True

    def __len__(self) -> int:
        return len(self._tools)

    def __contains__(self, name: str) -> bool:
        return name in self._tools

    def __iter__(self):
        return iter(self._tools.values())

    def __repr__(self) -> str:
        return f"ToolRegistry(tools={list(self._tools.keys())})"
