# -*- coding: utf-8 -*-
"""Agent 核心测试。"""
import pytest
from unittest.mock import MagicMock, patch

from agents import ReactAgent
from core import Conversation, Message, Role
from tools import Calculator, ToolRegistry


class MockLLM:
    """模拟 LLM"""
    def __init__(self, responses):
        self.responses = responses
        self.call_count = 0
    
    def chat(self, messages, **kwargs):
        response = self.responses[min(self.call_count, len(self.responses) - 1)]
        self.call_count += 1
        return response


class TestReactAgent:
    """ReactAgent 测试"""
    
    def test_init_with_tools(self):
        """测试使用工具列表初始化"""
        llm = MockLLM([{"content": "final_answer: ok"}])
        agent = ReactAgent(llm=llm, tools=[Calculator()])
        
        assert len(agent.tool_registry) == 1
        assert "calculator" in agent.tool_registry
    
    def test_init_with_registry(self):
        """测试使用注册器初始化"""
        llm = MockLLM([{"content": "final_answer: ok"}])
        registry = ToolRegistry()
        registry.register(Calculator())
        
        agent = ReactAgent(llm=llm, tool_registry=registry)
        
        assert len(agent.tool_registry) == 1
    
    def test_simple_answer(self):
        """测试直接回答"""
        llm = MockLLM([{"content": "final_answer: 你好！"}])
        agent = ReactAgent(llm=llm, tools=[])
        
        result = agent.run("你好")
        
        assert "你好" in result
        assert len(agent.conversation) == 2  # user + assistant
    
    def test_tool_call_flow(self):
        """测试工具调用流程"""
        responses = [
            {"content": 'Action: {"name": "calculator", "arguments": {"expression": "1+1"}}'},
            {"content": "final_answer: 1+1 = 2"},
        ]
        llm = MockLLM(responses)
        agent = ReactAgent(llm=llm, tools=[Calculator()])
        
        result = agent.run("计算 1+1")
        
        assert "2" in result
        assert llm.call_count == 2
    
    def test_reset(self):
        """测试重置对话"""
        llm = MockLLM([{"content": "final_answer: ok"}])
        agent = ReactAgent(llm=llm, tools=[])
        
        agent.run("test")
        assert len(agent.conversation) > 0
        
        agent.reset()
        assert len(agent.conversation) == 0


class TestConversation:
    """对话管理测试"""
    
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
    """消息测试"""
    
    def test_user_message(self):
        msg = Message.user("hello")
        
        assert msg.role == Role.USER
        assert msg.content == "hello"
    
    def test_tool_message_compatible(self):
        msg = Message.tool("calc", "result")
        
        data = msg.to_dict(compatible=True)
        
        assert data["role"] == "user"
        assert "[工具 calc 返回结果]" in data["content"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

