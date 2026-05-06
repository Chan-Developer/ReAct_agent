# -*- coding: utf-8 -*-
"""Minimal runtime verification for the structured tool-calling refactor."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.react_agent import ReactAgent


class Calculator:
    name = "calculator"
    description = "Simple test calculator"

    def as_function_spec(self):
        return {
            "name": "calculator",
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Math expression",
                    }
                },
                "required": ["expression"],
            },
        }

    def execute(self, expression: str) -> str:
        return f"{expression} = {eval(expression)}"


class MinimalRegistry:
    def __init__(self, tools):
        self._tools = {tool.name: tool for tool in tools}

    def get(self, name):
        return self._tools.get(name)

    def get_all(self):
        return list(self._tools.values())

    def as_function_specs(self):
        return [tool.as_function_spec() for tool in self._tools.values()]

    def validate_call(self, name, arguments):
        tool = self.get(name)
        if tool is None:
            return False, f"Tool not found: '{name}'"
        if not isinstance(arguments, dict):
            return False, "Tool arguments must be an object"
        if "expression" not in arguments:
            return False, "Missing required argument: 'expression'"
        if not isinstance(arguments["expression"], str):
            return False, "Invalid argument type for 'expression': expected string"
        return True, ""

    def __len__(self):
        return len(self._tools)


class MockLLM:
    def __init__(self, responses, supports_native_tool_calling: bool = False):
        self.responses = responses
        self.supports_native_tool_calling = supports_native_tool_calling
        self.call_count = 0
        self.calls = []

    def chat(self, messages, **kwargs):
        self.calls.append({"messages": messages, "kwargs": kwargs})
        index = min(self.call_count, len(self.responses) - 1)
        self.call_count += 1
        return self.responses[index]


def check_text_tool_call() -> None:
    llm = MockLLM(
        [
            {"content": 'Action: {"name": "calculator", "arguments": {"expression": "1+1"}}'},
            {"content": "final_answer: 1+1 = 2"},
        ]
    )
    agent = ReactAgent(llm=llm, tool_registry=MinimalRegistry([Calculator()]))
    result = agent.run("calculate 1+1")
    assert "2" in result, result


def check_native_tool_call() -> None:
    llm = MockLLM(
        [
            {
                "content": "",
                "tool_calls": [
                    {
                        "id": "call_1",
                        "function": {
                            "name": "calculator",
                            "arguments": '{"expression": "1+1"}',
                        },
                    }
                ],
            },
            {"content": "final_answer: 1+1 = 2"},
        ],
        supports_native_tool_calling=True,
    )
    agent = ReactAgent(llm=llm, tool_registry=MinimalRegistry([Calculator()]))
    result = agent.run("calculate 1+1")
    assert "2" in result, result
    assert "tools" in llm.calls[0]["kwargs"], llm.calls[0]
    assert any(
        msg["role"] == "tool" for msg in llm.calls[1]["messages"]
    ), llm.calls[1]["messages"]


def check_invalid_arguments_blocked() -> None:
    llm = MockLLM(
        [
            {
                "content": "",
                "tool_calls": [
                    {
                        "id": "call_1",
                        "function": {
                            "name": "calculator",
                            "arguments": "{}",
                        },
                    }
                ],
            },
            {"content": "final_answer: validation failed"},
        ],
        supports_native_tool_calling=True,
    )
    agent = ReactAgent(llm=llm, tool_registry=MinimalRegistry([Calculator()]))
    result = agent.run("calculate 1+1")
    assert "validation failed" in result, result
    tool_messages = [
        msg for msg in agent.conversation.to_list(compatible=False) if msg["role"] == "tool"
    ]
    assert tool_messages, "Expected at least one tool result message"
    assert "Tool argument validation failed" in tool_messages[0]["content"]


def main() -> None:
    check_text_tool_call()
    check_native_tool_call()
    check_invalid_arguments_blocked()
    print("manual runtime check passed")


if __name__ == "__main__":
    main()
