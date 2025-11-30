#!/usr/bin/env python
"""
优化功能测试脚本

测试内容：
1. 工具注册器基本功能
2. 装饰器注册
3. 批量注册
4. 工具查询和管理
"""
from __future__ import annotations

from core.tools.base import BaseTool
from core.tool_registry import ToolRegistry


def test_tool_registry_basic():
    """测试工具注册器基本功能"""
    print("=" * 60)
    print("测试 1: 工具注册器基本功能")
    print("=" * 60)
    
    registry = ToolRegistry()
    
    # 创建测试工具
    class TestTool(BaseTool):
        def __init__(self):
            super().__init__(
                name="test_tool",
                description="测试工具",
                parameters={
                    "type": "object",
                    "properties": {
                        "param": {"type": "string", "description": "参数"}
                    },
                    "required": ["param"]
                }
            )
        
        def execute(self, param: str):
            return f"执行成功: {param}"
    
    # 注册工具
    registry.register_tool(TestTool())
    
    # 验证注册
    assert len(registry) == 1, "工具数量应该为 1"
    assert "test_tool" in registry, "应该包含 test_tool"
    
    # 获取工具
    tool = registry.get_tool("test_tool")
    assert tool is not None, "应该能获取到工具"
    
    # 执行工具
    result = tool.execute("测试参数")
    assert "执行成功" in result, "工具执行应该成功"
    
    print(f"✅ 注册器信息: {registry}")
    print(f"✅ 工具执行结果: {result}")
    print()


def test_decorator_registration():
    """测试装饰器注册"""
    print("=" * 60)
    print("测试 2: 装饰器注册")
    print("=" * 60)
    
    registry = ToolRegistry()
    
    # 使用装饰器注册
    @registry.register
    class DecoratorTool(BaseTool):
        def __init__(self):
            super().__init__(
                name="decorator_tool",
                description="装饰器注册的工具",
                parameters={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            )
        
        def execute(self):
            return "装饰器工具执行成功"
    
    # 验证注册
    assert len(registry) == 1, "应该有 1 个工具"
    assert "decorator_tool" in registry, "应该包含 decorator_tool"
    
    # 执行工具
    tool = registry.get_tool("decorator_tool")
    result = tool.execute()
    
    print(f"✅ 注册器信息: {registry}")
    print(f"✅ 工具执行结果: {result}")
    print()


def test_batch_registration():
    """测试批量注册"""
    print("=" * 60)
    print("测试 3: 批量注册")
    print("=" * 60)
    
    from core.tools.builtin import Calculator, Search, AddFile
    
    registry = ToolRegistry()
    
    # 批量注册
    tools = [Calculator(), Search(), AddFile()]
    registry.register_tools(tools)
    
    # 验证注册
    assert len(registry) == 3, "应该有 3 个工具"
    assert "calculator" in registry, "应该包含 calculator"
    assert "search" in registry, "应该包含 search"
    assert "addFile" in registry, "应该包含 addFile"
    
    print(f"✅ 注册器信息: {registry}")
    print(f"✅ 已注册工具数量: {len(registry)}")
    print()


def test_tool_spec_generation():
    """测试工具规范生成"""
    print("=" * 60)
    print("测试 4: OpenAI 工具规范生成")
    print("=" * 60)
    
    from core.tools.builtin import Calculator
    import json
    
    registry = ToolRegistry()
    registry.register_tool(Calculator())
    
    # 获取工具规范
    specs = registry.get_tools_spec()
    
    assert len(specs) == 1, "应该有 1 个工具规范"
    assert specs[0]["type"] == "function", "类型应该是 function"
    assert "function" in specs[0], "应该包含 function 字段"
    
    print("✅ OpenAI 工具规范:")
    print(json.dumps(specs, indent=2, ensure_ascii=False))
    print()


def test_tool_management():
    """测试工具管理功能"""
    print("=" * 60)
    print("测试 5: 工具管理（注销、清空）")
    print("=" * 60)
    
    from core.tools.builtin import Calculator, Search
    
    registry = ToolRegistry()
    registry.register_tools([Calculator(), Search()])
    
    print(f"初始状态: {registry}")
    assert len(registry) == 2, "应该有 2 个工具"
    
    # 注销一个工具
    registry.unregister("calculator")
    print(f"注销 calculator 后: {registry}")
    assert len(registry) == 1, "应该剩 1 个工具"
    assert "calculator" not in registry, "不应该包含 calculator"
    
    # 清空所有工具
    registry.clear()
    print(f"清空后: {registry}")
    assert len(registry) == 0, "应该没有工具"
    
    print("✅ 工具管理功能正常")
    print()


def test_agent_integration():
    """测试 Agent 集成"""
    print("=" * 60)
    print("测试 6: Agent 集成测试")
    print("=" * 60)
    
    from core.agent import Agent
    from core.tools.builtin import Calculator, Search
    from llm_interface import VllmLLM
    
    # 方式 1: 使用工具列表
    llm = VllmLLM()
    agent1 = Agent(
        llm=llm,
        tools=[Calculator(), Search()],
        max_rounds=3
    )
    print(f"✅ Agent 方式1 创建成功: {agent1.tool_registry}")
    
    # 方式 2: 使用工具注册器
    registry = ToolRegistry()
    registry.register_tools([Calculator(), Search()])
    
    agent2 = Agent(
        llm=llm,
        tool_registry=registry,
        max_rounds=3
    )
    print(f"✅ Agent 方式2 创建成功: {agent2.tool_registry}")
    
    print()


def main():
    """运行所有测试"""
    print("\n" + "🧪 开始测试优化功能" + "\n")
    
    try:
        test_tool_registry_basic()
        test_decorator_registration()
        test_batch_registration()
        test_tool_spec_generation()
        test_tool_management()
        test_agent_integration()
        
        print("=" * 60)
        print("🎉 所有测试通过！")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

