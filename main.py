#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Agent CLI 统一入口。

支持三种模式：
    1. solo     - 单 Agent 模式（LLM 自己决定调用工具顺序）
    2. workflow - 专家流水线模式（固定执行顺序，每个专家调用 LLM）
    3. multi    - 多智能体模式（TODO: 动态编排器）

运行方式：
    # Solo 模式 - LLM 自己决定
    python main.py solo -p "优化并生成简历" --resume @data/sample_resume.json
    
    # Workflow 模式 - 固定流水线（推荐）
    python main.py workflow -n resume -i @data/sample_resume.json
    python main.py workflow -n resume -i @data/sample_resume.json --jd data/sample_job.txt
"""
from __future__ import annotations

import argparse
import sys
import os
import json

# 公共模块
from common import setup_logging, set_level, get_logger

# Agent
from agents import ReactAgent

# 工具
from tools import Calculator, Search, AddFile, ReadFile
from tools.generators import ResumeGenerator
from tools.agent_wrappers import ContentOptimizerTool, LayoutDesignerTool, StyleSelectorTool

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
    - ContentOptimizerTool: 内容优化（支持职位匹配）
    - StyleSelectorTool: 模板选择（根据JD自动匹配）
    - LayoutDesignerTool: 布局设计（智能分页）
    - ResumeGenerator: 文档生成
    """
    return [
        ContentOptimizerTool(llm),
        StyleSelectorTool(llm),       # 新增：模板选择
        LayoutDesignerTool(llm),
        ResumeGenerator(output_dir=output_dir, llm=None, auto_optimize=False),
    ]


def run_solo_mode(args):
    """运行 Solo 模式。
    
    支持两种工具集：
    - 默认工具：计算器、搜索、文件操作
    - 简历工具：内容优化、模板选择、布局设计、文档生成（通过 --resume 参数启用）
    
    新增功能：
    - --jd: 职位描述文件，用于内容匹配和模板选择
    - --template: 指定模板名称
    - --page: 页面偏好 (one_page/two_pages/auto)
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
        
        # 如果提供了简历文件，保存到临时文件供工具使用
        import tempfile
        temp_dir = tempfile.gettempdir()
        
        try:
            if args.resume.startswith("@"):
                with open(args.resume[1:], "r", encoding="utf-8") as f:
                    resume_data = json.load(f)
                
                # 保存原始数据到临时文件
                temp_file = os.path.join(temp_dir, "original_resume.json")
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(resume_data, f, ensure_ascii=False, indent=2)
                print(f"  简历: {resume_data.get('name', '未知')}")
            else:
                resume_data = None
        except FileNotFoundError as e:
            print(f"❌ 简历文件不存在: {e}")
            return
        except json.JSONDecodeError as e:
            print(f"❌ 简历文件 JSON 格式错误: {e}")
            return
        
        # 加载职位描述
        job_description = ""
        if hasattr(args, 'jd') and args.jd:
            try:
                with open(args.jd, 'r', encoding='utf-8') as f:
                    job_description = f.read()
                # 保存到临时文件
                with open(os.path.join(temp_dir, "job_description.txt"), 'w', encoding='utf-8') as f:
                    f.write(job_description)
                print(f"  职位描述: {len(job_description)} 字符")
            except FileNotFoundError:
                print(f"⚠️ 职位描述文件不存在: {args.jd}")
        
        # 构建增强的 prompt
        prompt_parts = [args.prompt]
        prompt_parts.append("\n简历数据已保存，调用工具时请使用 resume_json=\"@original\" 来引用原始数据。")
        
        if job_description:
            prompt_parts.append(f"\n职位描述已提供，请在 content_optimizer 和 style_selector 中使用 job_description 参数。")
        
        if hasattr(args, 'template') and args.template:
            prompt_parts.append(f"\n请使用模板: {args.template}")
        
        if hasattr(args, 'page') and args.page != "auto":
            prompt_parts.append(f"\n页面偏好: {args.page}")
        
        prompt = "".join(prompt_parts)
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
# Workflow 模式（专家流水线）
# =============================================================================

def run_workflow_mode(args):
    """运行 Workflow 模式（专家流水线）。
    
    特点：
    - 固定的专家执行顺序
    - 每个专家调用 LLM 进行思考和执行
    - 专家之间通过数据传递协作
    
    可用工作流：
    - resume: 简历生成流水线
      ContentAgent → StyleSelector → LayoutAgent → Generator
    """
    print("\n" + "=" * 60)
    print("⚙️ Workflow 模式 - 专家流水线")
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
    
    # 加载职位描述
    job_description = ""
    if hasattr(args, 'jd') and args.jd:
        try:
            with open(args.jd, 'r', encoding='utf-8') as f:
                job_description = f.read()
            print(f"📋 职位描述: {len(job_description)} 字符")
        except FileNotFoundError:
            print(f"⚠️ 职位描述文件不存在: {args.jd}")
    
    print(f"\n📌 工作流: {args.workflow_name}")
    print(f"📦 输入数据: {input_data.get('name', '未知')}")
    
    # 初始化 LLM
    llm = create_llm(args.local)
    
    # 选择工作流
    if args.workflow_name == "resume":
        from workflows import ResumePipeline
        
        pipeline = ResumePipeline(llm=llm, output_dir=args.output_dir)
        
        print(f"\n✅ 工作流: {pipeline.WORKFLOW_NAME}")
        print(f"📋 步骤: {' → '.join(pipeline.WORKFLOW_STEPS)}")
        
        # 执行
        print("\n⚡ 执行工作流...")
        result = pipeline.run(
            input_data=input_data,
            job_description=job_description,
            template_name=getattr(args, 'template', ''),
            page_preference=getattr(args, 'page', 'auto'),
            output_dir=args.output_dir,
        )
        
        # 输出结果
        if result.success:
            print(f"\n✅ 工作流完成!")
            print(f"⏱️ 耗时: {result.execution_time:.2f}s")
            print(f"📊 完成步骤: {result.steps_completed}/{result.total_steps}")
            
            if result.output.get("output_path"):
                print(f"\n📄 输出文件: {result.output['output_path']}")
            
            if result.suggestions:
                print(f"\n💡 建议:")
                for s in result.suggestions[:5]:
                    print(f"   • {s}")
            
            # 显示日志
            if hasattr(args, 'debug') and args.debug:
                print(f"\n📝 执行日志:")
                for log in result.logs:
                    print(f"   {log}")
        else:
            print(f"\n❌ 工作流失败: {result.error}")
            print(f"📊 完成步骤: {result.steps_completed}/{result.total_steps}")
    else:
        print(f"❌ 未知工作流: {args.workflow_name}")
        print("可用工作流: resume")


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
    solo.add_argument("--jd", help="职位描述文件路径（用于内容匹配和模板选择）")
    solo.add_argument("-t", "--template", help="模板名称: tech_modern, tech_classic, management, creative, fresh_graduate")
    solo.add_argument("--page", choices=["one_page", "two_pages", "auto"], default="auto", help="页面偏好")
    solo.add_argument("-m", "--max_steps", type=int, default=10, help="最大轮数")
    solo.add_argument("-o", "--output_dir", default="./output", help="输出目录")
    solo.add_argument("--local", action="store_true", help="使用本地 vLLM")
    solo.add_argument("-d", "--debug", action="store_true", help="调试模式")
    
    # -------------------------------------------------------------------------
    # Workflow 模式（专家流水线）
    # -------------------------------------------------------------------------
    workflow = subparsers.add_parser("workflow", help="专家流水线模式（固定执行顺序）")
    workflow.add_argument("-n", "--workflow_name", required=True, help="工作流名称: resume")
    workflow.add_argument("-i", "--input", required=True, help="输入数据 JSON 或 @文件路径")
    workflow.add_argument("--jd", help="职位描述文件路径")
    workflow.add_argument("-t", "--template", help="模板名称")
    workflow.add_argument("--page", choices=["one_page", "two_pages", "auto"], default="auto", help="页面偏好")
    workflow.add_argument("-o", "--output_dir", default="./output", help="输出目录")
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
        print("  solo      单 Agent（LLM 自己决定调用工具顺序）")
        print("  workflow  专家流水线（固定执行顺序，每个专家调用 LLM）")
        print("  multi     多智能体（TODO: 动态编排器）")
        print("\n简历生成示例:")
        print()
        print("  # Solo 模式 - LLM 自己决定调用顺序")
        print('  python main.py solo -p "优化并生成简历" --resume @data/sample_resume.json')
        print()
        print("  # Workflow 模式 - 固定专家流水线（推荐）")
        print('  python main.py workflow -n resume -i @data/sample_resume.json')
        print('  python main.py workflow -n resume -i @data/sample_resume.json --jd data/sample_job.txt')
        print('  python main.py workflow -n resume -i @data/sample_resume.json --template tech_modern --page one_page')
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
