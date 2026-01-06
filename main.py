#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Agent CLI 入口。

运行方式：
    python main.py --prompt "你的问题"
    python main.py --prompt "帮我生成简历" --debug

功能特性:
    - ReAct 风格的智能代理
    - 支持工具调用（计算器、搜索、文件操作、简历生成等）
    - 支持多轮对话
"""
from __future__ import annotations

import argparse
import sys

# 核心模块
from core import Agent
from common import setup_logging, set_level, get_logger

# 工具
from tools import Calculator, Search, AddFile, ReadFile, ToolRegistry
from tools.generators import ResumeGenerator

# LLM
from llm import VllmLLM, ModelScopeOpenAI

# 初始化日志
setup_logging()
logger = get_logger(__name__)


def create_default_tools(output_dir: str = "./output", llm=None) -> list:
    """创建默认工具集。
    
    Args:
        output_dir: 输出目录路径
        llm: LLM 实例（用于简历内容优化）
        
    Returns:
        工具实例列表
    """
    return [
        Calculator(),
        Search(),
        AddFile(),
        ReadFile(),
        # 简历生成器：注入 LLM 以支持内容优化
        ResumeGenerator(output_dir=output_dir, llm=llm, auto_optimize=True),
    ]


def build_agent_cloud(max_rounds: int, output_dir: str = "./output") -> Agent:
    """构建使用云端 LLM 的 Agent（ModelScope）。
    
    Args:
        max_rounds: 最大迭代轮数
        output_dir: 输出目录
        
    Returns:
        Agent 实例
    """
    try:
        llm = ModelScopeOpenAI()
    except ValueError as e:
        logger.error(f"初始化 ModelScope LLM 失败: {e}")
        logger.info("请设置环境变量 MODELSCOPE_API_KEY")
        sys.exit(1)
    
    # 创建工具时注入 LLM，使简历生成器可以优化内容
    tools = create_default_tools(output_dir, llm=llm)
    
    return Agent(
        llm=llm,
        tools=tools,
        max_rounds=max_rounds,
    )


def build_agent_local(max_rounds: int) -> Agent:
    """构建使用本地 LLM 的 Agent（vLLM）。
    
    Args:
        max_rounds: 最大迭代轮数
        
    Returns:
        Agent 实例
    """
    registry = ToolRegistry()
    registry.register_tools([
        Calculator(),
        Search(),
        AddFile(),
        ReadFile(),
    ])
    
    llm = VllmLLM()
    
    return Agent(
        llm=llm,
        tool_registry=registry,
        max_rounds=max_rounds,
    )


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(
        description="🤖 ReAct Agent CLI - 智能对话助手",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python main.py --prompt "计算 3*7+2 的结果"
    python main.py --prompt "帮我生成一份简历，我叫张三" --debug
    python main.py --prompt "搜索 Python 相关信息" --max_steps 10
    python main.py --local --prompt "你好"
        """
    )
    
    parser.add_argument(
        "--prompt", "-p",
        type=str,
        default="计算 3*7+2 的结果",
        help="用户输入的问题或指令",
    )
    
    parser.add_argument(
        "--max_steps", "-m",
        type=int,
        default=5,
        help="最大思考轮数 (默认: 5)",
    )
    
    parser.add_argument(
        "--output_dir", "-o",
        type=str,
        default="./output",
        help="输出目录 (默认: ./output)",
    )
    
    parser.add_argument(
        "--local",
        action="store_true",
        help="使用本地 vLLM 而非云端 ModelScope",
    )

    parser.add_argument(
        "--debug", "-d",
        action="store_true",
        help="启用调试模式（显示详细日志）",
    )
    
    return parser.parse_args()


def main() -> None:
    """主函数。"""
    args = parse_args()
    
    # 设置日志级别
    if args.debug:
        set_level("DEBUG")
    
    # 构建 Agent
    if args.local:
        logger.info("使用本地 vLLM 模型")
        agent = build_agent_local(args.max_steps)
    else:
        logger.info("使用云端 ModelScope 模型")
        agent = build_agent_cloud(args.max_steps, args.output_dir)
    
    # 运行
    logger.info(f"用户输入: {args.prompt}")
    
    try:
    reply = agent.run(args.prompt)
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断")
        return
    except Exception as e:
        logger.error(f"运行出错: {e}", exc_info=args.debug)
        print(f"\n❌ 错误: {e}")
        return
    
    # 输出结果
    print("\n" + "=" * 60)
    print("🤖 Assistant:", reply)
    print("=" * 60)


if __name__ == "__main__":
    main()
