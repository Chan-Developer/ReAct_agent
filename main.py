#!/usr/bin/env python
"""简单 CLI，用于演示 agent 思考与工具调用流程。

运行：
    python -m agent.main
或
    python agent/main.py

新特性:
    - 支持工具注册器，实现工具解耦
    - 支持原生 Function Calling
    - 支持动态工具注入
"""
from __future__ import annotations

import argparse
import logging

from core.agent import Agent
from core.tool_registry import ToolRegistry
from core.tools.builtin import Calculator, Search, AddFile
from llm_interface import VllmLLM

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def build_agent_v1(max_steps: int) -> Agent:
    """方式1: 直接传入工具列表（XML模式，兼容不支持Function Calling的模型）"""
    tools = [Calculator(), Search(), AddFile()]
    llm = VllmLLM()
    return Agent(
        llm=llm,
        tools=tools,
        max_rounds=max_steps
    )

def build_agent_v2(max_steps: int) -> Agent:
    """方式2: 使用工具注册器（推荐）"""
    # 创建工具注册器
    registry = ToolRegistry()
    
    # 注册工具 - 方式1: 批量注册
    registry.register_tools([
        Calculator(),
        Search(),
        AddFile(),
    ])
    
    # 注册工具 - 方式2: 单个注册
    # registry.register_tool(Calculator())
    # registry.register_tool(Search())
    
    # 注册工具 - 方式3: 使用装饰器（需要在工具定义处）
    # @registry.register
    # class MyTool(BaseTool):
    #     pass
    
    llm = VllmLLM()
    return Agent(
        llm=llm,
        tool_registry=registry,
        max_rounds=max_steps,
        use_native_function_calling=True
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Simple ReAct agent demo with tool registry support"
    )
    parser.add_argument(
        "--max_steps", 
        help="Max steps for the agent",
        default=5,
        type=int
    )
    parser.add_argument(
        "--prompt", 
        help="User prompt for the agent",
        default="计算 3*7+2 的结果",
        type=str
    )

    parser.add_argument(
        "--debug",
        help="Enable debug logging",
        action="store_true"
    )
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 构建 Agent

    agent = build_agent_v1(args.max_steps)
    
    # 运行
    logger.info(f"用户输入: {args.prompt}")
    reply = agent.run(args.prompt)
    
    print("\n" + "="*60)
    print("🤖 Assistant:", reply)
    print("="*60)


if __name__ == "__main__":
    main()
