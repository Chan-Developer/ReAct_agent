# -*- coding: utf-8 -*-
"""Core tests for ReactAgent and message primitives."""

import pytest

from agents import ReactAgent
from core import Conversation, Message, Role
from tools import Calculator, ToolRegistry


class MockLLM:
    """Simple sequential mock LLM."""

    def __init__(self, responses):
        self.responses = responses
        self.call_count = 0

    def chat(self, messages, **kwargs):
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
