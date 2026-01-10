#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Agent CLI 统一入口。

支持三种模式：
    1. solo     - 单 Agent 模式（ReAct 思考-行动循环，支持 Agent 工具）
    2. workflow - 工作流模式（硬编码流水线，Crew 按固定顺序执行）
    3. multi    - 多智能体模式（TODO: 动态编排器，自主规划和分配任务）

运行方式：
    # Solo 模式（推荐）
    python main.py solo -p "帮我优化简历并生成文档" --resume @data/resumes/my_resume.json
    
    # 工作流模式（固定流水线）
    python main.py workflow -n resume -i '{"name": "张三"}'
    
    # 多智能体模式（待实现）
    python main.py multi -i @data/resumes/my_resume.json
"""
from __future__ import annotations

import argparse
import sys
import os
import json

# 公共模块
from common import setup_logging, set_level, get_logger

# Core
from core import Orchestrator, Task

# Agent
from agents import ReactAgent, ResumeCrew

# 工具
from tools import Calculator, Search, AddFile, ReadFile
from tools.generators import ResumeGenerator
from tools.agents import ContentOptimizerTool, LayoutDesignerTool

# LLM
from llm import VllmLLM, ModelScopeOpenAI

# 初始化日志
setup_logging()
logger = get_logger(__name__)


# =============================================================================
# LLM 初始化
# =============================================================================

def create_llm(local: bool = False):
    """创建 LLM 实例。"""
    if local:
        logger.info("使用本地 vLLM")
        return VllmLLM()
    else:
        logger.info("使用云端 ModelScope")
        try:
            return ModelScopeOpenAI()
        except ValueError as e:
            logger.error(f"初始化 LLM 失败: {e}")
            sys.exit(1)


# =============================================================================
# Solo 模式（单 Agent + 工具，支持 Agent 工具）
# =============================================================================

def create_default_tools(output_dir: str = "./output", llm=None) -> list:
    """创建默认工具集（基础工具）。"""
    return [
        Calculator(),
        Search(),
        AddFile(),
        ReadFile(),
    ]


def create_resume_tools(output_dir: str = "./output", llm=None) -> list:
    """创建简历相关工具集（包含 Agent 工具）。
    
    包含：
    - ContentOptimizerTool: 内容优化（内部 Think-Execute-Reflect）
    - LayoutDesignerTool: 布局设计（内部 Think-Execute-Reflect）
    - ResumeGenerator: 文档生成
    """
    return [
        ContentOptimizerTool(llm),
        LayoutDesignerTool(llm),
        ResumeGenerator(output_dir=output_dir, llm=None, auto_optimize=False),
    ]


def run_solo_mode(args):
    """运行 Solo 模式。
    
    支持两种工具集：
    - 默认工具：计算器、搜索、文件操作
    - 简历工具：内容优化、布局设计、文档生成（通过 --resume 参数启用）
    """
    print("\n" + "=" * 60)
    print("🧠 Solo 模式 - 单 Agent")
    print("=" * 60)
    
    llm = create_llm(args.local)
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 根据参数选择工具集
    if args.resume:
        print("📄 加载简历工具集（含 Agent 工具）")
        tools = create_resume_tools(args.output_dir, llm=llm)
        
        # 如果提供了简历文件，构建完整的 prompt
        try:
            if args.resume.startswith("@"):
                with open(args.resume[1:], "r", encoding="utf-8") as f:
                    resume_data = json.load(f)
                resume_json = json.dumps(resume_data, ensure_ascii=False)
                prompt = f"""{args.prompt}

简历数据：
```json
{resume_json}
```"""
            else:
                prompt = args.prompt
        except FileNotFoundError as e:
            print(f"❌ 简历文件不存在: {e}")
            return
        except json.JSONDecodeError as e:
            print(f"❌ 简历文件 JSON 格式错误: {e}")
            return
    else:
        print("🔧 加载默认工具集")
        tools = create_default_tools(args.output_dir, llm=llm)
        prompt = args.prompt
    
    print(f"✅ 已加载工具: {[t.name for t in tools]}")
    
    agent = ReactAgent(llm=llm, tools=tools, max_rounds=args.max_steps)
    
    logger.info(f"用户输入: {prompt[:100]}...")
    
    try:
        reply = agent.run(prompt)
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断")
        return
    except Exception as e:
        logger.error(f"运行出错: {e}", exc_info=args.debug)
        print(f"\n❌ 错误: {e}")
        return
    
    print("\n" + "=" * 60)
    print("🤖 Assistant:", reply)
    print("=" * 60)


# =============================================================================
# Workflow 模式（工作流 - 硬编码流水线）
# =============================================================================

def create_orchestrator(llm, kb=None) -> Orchestrator:
    """创建 Orchestrator 并注册所有 Crew。"""
    orchestrator = Orchestrator(llm, knowledge_base=kb)
    
    # 注册所有可用的 Crew（工作流）
    orchestrator.register(ResumeCrew)
    # orchestrator.register(CodeReviewCrew)  # 未来扩展
    # orchestrator.register(DocWritingCrew)  # 未来扩展
    
    return orchestrator


def run_workflow_mode(args):
    """运行 Workflow 模式（硬编码工作流）。
    
    特点：
    - 执行顺序由程序员在 Crew 中预定义
    - 可控性高，保证按固定步骤执行
    - 适合流程固定的任务
    """
    print("\n" + "=" * 60)
    print("⚙️ Workflow 模式 - 工作流")
    print("=" * 60)
    
    # 解析输入数据
    try:
        if args.input.startswith("@"):
            with open(args.input[1:], "r", encoding="utf-8") as f:
                input_data = json.load(f)
        else:
            input_data = json.loads(args.input)
    except json.JSONDecodeError as e:
        print(f"❌ 输入数据 JSON 格式错误: {e}")
        return
    except FileNotFoundError as e:
        print(f"❌ 文件不存在: {e}")
        return
    
    print(f"\n📌 工作流名称: {args.workflow_name}")
    print(f"📦 输入数据: {json.dumps(input_data, ensure_ascii=False)[:100]}...")
    
    # 初始化
    llm = create_llm(args.local)
    orchestrator = create_orchestrator(llm)
    
    print(f"\n✅ 已注册工作流: {orchestrator.list_crews()}")
    
    # 创建任务
    task = Task(
        name=args.workflow_name,
        input_data=input_data,
        context={},
        metadata={"style": args.style} if hasattr(args, "style") else {},
    )
    
    # 执行
    print("\n⚡ 执行工作流...")
    result = orchestrator.run(task)
    
    # 输出结果
    if result.success:
        print(f"\n✅ 工作流完成!")
        print(f"\n📤 输出:")
        print(json.dumps(result.output, ensure_ascii=False, indent=2))
        
        if result.suggestions:
            print(f"\n💡 建议:")
            for s in result.suggestions[:5]:
                print(f"   • {s}")
    else:
        print(f"\n❌ 工作流失败: {result.error}")


# =============================================================================
# Multi 模式（多智能体 - TODO: 动态编排器）
# =============================================================================

def run_multi_mode(args):
    """运行多智能体模式（待实现）。
    
    TODO: 实现真正的多智能体架构
    
    目标架构：
        Planner/Orchestrator (编排层)
            ├─ 分析任务 → 拆解为子任务
            ├─ 动态创建/选择 Agent
            ├─ 分配任务给各 Agent
            ├─ 监控执行进度
            ├─ 收集各 Agent 结果
            └─ 整合最终输出
    
    与 Solo 模式的区别：
        - Solo: 单个 Agent 调用工具，工具内部可能有推理
        - Multi: 多个 Agent 协作，有专门的编排器规划和分配任务
    
    与 Workflow 模式的区别：
        - Workflow: 硬编码流水线，执行顺序固定
        - Multi: 动态规划，根据任务自主决定执行策略
    """
    print("\n" + "=" * 60)
    print("🤖 Multi 模式 - 多智能体协作")
    print("=" * 60)
    
    print("\n⚠️ 该模式尚未实现！")
    print("\n📋 计划实现的功能：")
    print("   1. Planner Agent - 任务规划和拆解")
    print("   2. 动态 Agent 创建 - 根据子任务创建专门的 Agent")
    print("   3. 任务分配和监控 - 协调多个 Agent 并行/串行执行")
    print("   4. 结果整合 - 收集和合并各 Agent 的输出")
    print("\n💡 目前请使用：")
    print("   - solo 模式：单 Agent + 工具（支持 Agent 工具）")
    print("   - workflow 模式：硬编码工作流")
    print("\n示例：")
    print('   python main.py solo -p "优化简历" --resume @data/resumes/my_resume.json')
    print('   python main.py workflow -n resume -i @data/resumes/my_resume.json')


# =============================================================================
# CLI 入口
# =============================================================================

def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(
        description="🤖 Agent Framework CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    subparsers = parser.add_subparsers(dest="mode", help="运行模式")
    
    # -------------------------------------------------------------------------
    # Solo 模式（单 Agent + 工具）
    # -------------------------------------------------------------------------
    solo = subparsers.add_parser("solo", help="单 Agent 模式（ReAct 循环）")
    solo.add_argument("-p", "--prompt", required=True, help="任务描述")
    solo.add_argument("-r", "--resume", help="简历数据 JSON 或 @文件路径（启用简历工具集）")
    solo.add_argument("-m", "--max_steps", type=int, default=10, help="最大轮数")
    solo.add_argument("-o", "--output_dir", default="./output", help="输出目录")
    solo.add_argument("--local", action="store_true", help="使用本地 vLLM")
    solo.add_argument("-d", "--debug", action="store_true", help="调试模式")
    
    # -------------------------------------------------------------------------
    # Workflow 模式（工作流 - 硬编码流水线）
    # -------------------------------------------------------------------------
    workflow = subparsers.add_parser("workflow", help="工作流模式（硬编码流水线）")
    workflow.add_argument("-n", "--workflow_name", required=True, help="工作流名称（如 resume）")
    workflow.add_argument("-i", "--input", required=True, help="输入数据 JSON 或 @文件路径")
    workflow.add_argument("--style", default="modern", help="样式偏好")
    workflow.add_argument("--local", action="store_true", help="使用本地 vLLM")
    workflow.add_argument("-d", "--debug", action="store_true", help="调试模式")
    
    # -------------------------------------------------------------------------
    # Multi 模式（多智能体 - 待实现）
    # -------------------------------------------------------------------------
    multi = subparsers.add_parser("multi", help="多智能体模式（待实现：动态编排器）")
    multi.add_argument("-i", "--input", help="输入数据 JSON 或 @文件路径")
    multi.add_argument("-d", "--debug", action="store_true", help="调试模式")
    
    return parser.parse_args()


def main() -> None:
    """主函数。"""
    args = parse_args()
    
    if args.mode is None:
        print("🤖 Agent Framework CLI\n")
        print("可用模式:")
        print("  solo      单 Agent（ReAct 循环 + 工具，支持 Agent 工具）")
        print("  workflow  工作流（硬编码流水线，Crew 按固定顺序执行）")
        print("  multi     多智能体（TODO: 动态编排器，自主规划和分配任务）")
        print("\n示例:")
        print('  python main.py solo -p "计算 3*7"')
        print('  python main.py solo -p "优化并生成简历" --resume @data/resumes/my_resume.json')
        print('  python main.py workflow -n resume -i @data/resumes/my_resume.json')
        return
    
    if hasattr(args, 'debug') and args.debug:
        set_level("DEBUG")
    
    if args.mode == "solo":
        run_solo_mode(args)
    elif args.mode == "workflow":
        run_workflow_mode(args)
    elif args.mode == "multi":
        run_multi_mode(args)


if __name__ == "__main__":
    main()
