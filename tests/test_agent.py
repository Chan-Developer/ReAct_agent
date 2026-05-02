# -*- coding: utf-8 -*-
"""Core tests for ReactAgent and message primitives."""

import pytest

from agents import ReactAgent
from core import Conversation, Message, Role
from tools import Calculator, ToolRegistry


class MockLLM:
    """Simple sequential mock LLM."""

    def __init__(self, responses, supports_native_tool_calling=False):
        self.responses = responses
        self.call_count = 0
        self.supports_native_tool_calling = supports_native_tool_calling
        self.calls = []

    def chat(self, messages, **kwargs):
        self.calls.append({"messages": messages, "kwargs": kwargs})
        response = self.responses[min(self.call_count, len(self.responses) - 1)]
        self.call_count += 1
        return response


class TestReactAgent:
    def test_init_with_tools(self):
        llm = MockLLM([{"content": "final_answer: ok"}])
        agent = ReactAgent(llm=llm, tools=[Calculator()])
        assert len(agent.tool_registry) == 1
        assert "calculator" in agent.tool_registry

    def test_init_with_registry(self):
        llm = MockLLM([{"content": "final_answer: ok"}])
        registry = ToolRegistry()
        registry.register(Calculator())
        agent = ReactAgent(llm=llm, tool_registry=registry)
        assert len(agent.tool_registry) == 1

    def test_simple_answer(self):
        llm = MockLLM([{"content": "final_answer: hello"}])
        agent = ReactAgent(llm=llm, tools=[])
        result = agent.run("hello")
        assert "hello" in result
        assert len(agent.conversation) == 2

    def test_tool_call_flow(self):
        responses = [
            {"content": 'Action: {"name": "calculator", "arguments": {"expression": "1+1"}}'},
            {"content": "final_answer: 1+1 = 2"},
        ]
        llm = MockLLM(responses)
        agent = ReactAgent(llm=llm, tools=[Calculator()])
        result = agent.run("calculate 1+1")
        assert "2" in result
        assert llm.call_count == 2

    def test_auto_finish_without_final_tag_after_tool_round(self):
        responses = [
            {"content": 'Action: {"name": "calculator", "arguments": {"expression": "1+1"}}'},
            {"content": "The result is 2."},
        ]
        llm = MockLLM(responses)
        agent = ReactAgent(llm=llm, tools=[Calculator()])
        result = agent.run("calculate 1+1")
        assert result == "The result is 2."

    def test_native_tool_call_flow(self):
        responses = [
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
        ]
        llm = MockLLM(responses, supports_native_tool_calling=True)
        agent = ReactAgent(llm=llm, tools=[Calculator()])

        result = agent.run("calculate 1+1")

        assert "2" in result
        assert "tools" in llm.calls[0]["kwargs"]
        second_messages = llm.calls[1]["messages"]
        assert any(msg["role"] == "tool" for msg in second_messages)

    def test_invalid_tool_arguments_are_blocked(self):
        responses = [
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
        ]
        llm = MockLLM(responses, supports_native_tool_calling=True)
        agent = ReactAgent(llm=llm, tools=[Calculator()])

        result = agent.run("calculate 1+1")

        assert "validation failed" in result
        tool_messages = [m for m in agent.conversation.to_list(compatible=False) if m["role"] == "tool"]
        assert "Tool argument validation failed" in tool_messages[0]["content"]

    def test_reset(self):
        llm = MockLLM([{"content": "final_answer: ok"}])
        agent = ReactAgent(llm=llm, tools=[])
        agent.run("test")
        assert len(agent.conversation) > 0
        agent.reset()
        assert len(agent.conversation) == 0


class TestConversation:
    def test_add_messages(self):
        conv = Conversation()
        conv.add_user("hello")
        conv.add_assistant("hi")
        conv.add_tool_result("test", "result")
        assert len(conv) == 3

    def test_to_list(self):
        conv = Conversation()
        conv.add_user("hello")
        messages = conv.to_list()
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "hello"

    def test_to_list_native_tool_result(self):
        conv = Conversation()
        conv.add_tool_result("calculator", "1+1 = 2", tool_call_id="call_1")
        messages = conv.to_list(compatible=False)
        assert messages[0]["role"] == "tool"
        assert messages[0]["tool_call_id"] == "call_1"

    def test_clear(self):
        conv = Conversation()
        conv.add_user("hello")
        conv.clear()
        assert len(conv) == 0


class TestMessage:
    def test_user_message(self):
        msg = Message.user("hello")
        assert msg.role == Role.USER
        assert msg.content == "hello"

    def test_tool_message_compatible(self):
        msg = Message.tool("calc", "result")
        data = msg.to_dict(compatible=True)
        assert data["role"] == "user"
        assert "calc" in data["content"]
        assert "result" in data["content"]

    def test_assistant_message_with_tool_calls(self):
        msg = Message.assistant(
            "",
            tool_calls=[
                {
                    "id": "call_1",
                    "type": "function",
                    "function": {"name": "calculator", "arguments": '{"expression":"1+1"}'},
                }
            ],
        )
        data = msg.to_dict(compatible=False)
        assert "tool_calls" in data
        assert data["tool_calls"][0]["function"]["name"] == "calculator"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
