#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Agent CLI 统一入口。

支持三种模式：
    1. solo  - 单 Agent 模式（ReAct 思考-行动循环）
    2. task  - 通用任务模式（Orchestrator 自动路由到 Crew）
    3. resume - 简历优化（task 模式的快捷方式）

运行方式：
    # Solo 模式
    python main.py solo -p "计算 3*7+2"
    
    # 通用任务模式
    python main.py task --name resume --input '{"name": "张三"}'
    
    # 简历快捷模式
    python main.py resume --name "张三" --school "清华大学"
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
# Solo 模式（单 Agent）
# =============================================================================

def create_default_tools(output_dir: str = "./output", llm=None) -> list:
    """创建默认工具集。"""
    return [
        Calculator(),
        Search(),
        AddFile(),
        ReadFile(),
        ResumeGenerator(output_dir=output_dir, llm=llm, auto_optimize=True),
    ]


def run_solo_mode(args):
    """运行 Solo 模式。"""
    print("\n" + "=" * 60)
    print("🧠 Solo 模式 - 单 Agent")
    print("=" * 60)
    
    llm = create_llm(args.local)
    tools = create_default_tools(args.output_dir, llm=llm)
    agent = ReactAgent(llm=llm, tools=tools, max_rounds=args.max_steps)
    
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
    
    print("\n" + "=" * 60)
    print("🤖 Assistant:", reply)
    print("=" * 60)


# =============================================================================
# Task 模式（通用任务 - Orchestrator 路由）
# =============================================================================

def create_orchestrator(llm, kb=None) -> Orchestrator:
    """创建 Orchestrator 并注册所有 Crew。"""
    orchestrator = Orchestrator(llm, knowledge_base=kb)
    
    # 注册所有可用的 Crew
    orchestrator.register(ResumeCrew)
    # orchestrator.register(CodeReviewCrew)  # 未来扩展
    # orchestrator.register(DocWritingCrew)  # 未来扩展
    
    return orchestrator


def run_task_mode(args):
    """运行 Task 模式（通用任务）。"""
    print("\n" + "=" * 60)
    print("📋 Task 模式 - 通用任务")
    print("=" * 60)
    
    # 解析输入数据
    try:
        if args.input.startswith("@"):
            # 从文件读取
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
    
    print(f"\n📌 任务名称: {args.task_name}")
    print(f"📦 输入数据: {json.dumps(input_data, ensure_ascii=False)[:100]}...")
    
    # 初始化
    llm = create_llm(args.local)
    orchestrator = create_orchestrator(llm)
    
    print(f"\n✅ 已注册 Crew: {orchestrator.list_crews()}")
    
    # 创建任务
    task = Task(
        name=args.task_name,
        input_data=input_data,
        context={},
        metadata={"style": args.style} if hasattr(args, "style") else {},
    )
    
    # 执行
    print("\n⚡ 执行任务...")
    result = orchestrator.run(task)
    
    # 输出结果
    if result.success:
        print(f"\n✅ 任务完成!")
        print(f"\n📤 输出:")
        print(json.dumps(result.output, ensure_ascii=False, indent=2))
        
        if result.suggestions:
            print(f"\n💡 建议:")
            for s in result.suggestions[:5]:
                print(f"   • {s}")
    else:
        print(f"\n❌ 任务失败: {result.error}")


# =============================================================================
# Resume 模式（简历快捷方式）
# =============================================================================

def create_sample_resume(name: str, school: str, major: str) -> dict:
    """创建示例简历数据。"""
    return {
        "name": name,
        "phone": "138****1234",
        "email": f"{name.lower().replace(' ', '')}@example.com",
        "location": "成都",
        "summary": f"{school}{major}专业学生",
        "education": [{
            "school": school,
            "degree": "硕士研究生",
            "major": major,
            "start_date": "2024.09",
            "end_date": "2027.06",
            "gpa": "3.8/4.0"
        }],
        "projects": [
            {
                "name": "深度学习图像处理项目",
                "role": "项目负责人",
                "start_date": "2024.10",
                "end_date": "至今",
                "description": "基于深度学习的图像处理系统",
                "highlights": ["设计并实现图像处理算法", "优化模型性能"],
                "tech_stack": ["Python", "PyTorch", "OpenCV"]
            },
        ],
        "skills": ["Python", "PyTorch", "TensorFlow", "深度学习", "计算机视觉"],
    }


def run_resume_mode(args):
    """运行简历优化模式（task 模式的快捷方式）。"""
    print("\n" + "=" * 60)
    print("📄 Resume 模式 - 简历优化")
    print("=" * 60)
    
    # 准备数据
    if args.json_file:
        with open(args.json_file, "r", encoding="utf-8") as f:
            resume_data = json.load(f)
        print(f"\n📂 从文件加载: {args.json_file}")
    else:
        resume_data = create_sample_resume(args.name, args.school, args.major)
        print(f"\n👤 姓名: {args.name}")
        print(f"🎓 学校: {args.school}")
        print(f"📚 专业: {args.major}")
    
    print(f"🎨 样式: {args.style}")
    os.makedirs(args.output_dir, exist_ok=True)
    
    if args.simple:
        # 简单模式：不用 AI
        print("\n📄 简单模式（不使用 AI 优化）...")
        generator = ResumeGenerator(output_dir=args.output_dir, llm=None)
        output = generator.execute(
            resume_data=json.dumps(resume_data, ensure_ascii=False),
            filename=f"{resume_data.get('name', 'resume')}_resume",
            template_style=args.style,
            optimize=False,
        )
        print(f"\n{output}")
        return
    
    # 使用 Orchestrator
    llm = create_llm(args.local)
    orchestrator = create_orchestrator(llm)
    
    task = Task(
        name="resume",
        input_data=resume_data,
        metadata={"style": args.style},
    )
    
    print("\n⚡ 运行 Agent 优化流程...")
    result = orchestrator.run(task)
    
    if result.success:
        print(f"\n✅ 优化完成!")
        
        if result.suggestions:
            print("\n💡 优化建议:")
            for s in result.suggestions[:5]:
                print(f"   • {s}")
        
        # 生成 Word
        print("\n📝 生成 Word 文档...")
        output_data = result.output.get("resume_data", resume_data)
        generator = ResumeGenerator(output_dir=args.output_dir, llm=None)
        output = generator.execute(
            resume_data=json.dumps(output_data, ensure_ascii=False),
            filename=f"{output_data.get('name', 'resume')}_resume",
            template_style=args.style,
            optimize=False,
        )
        print(f"\n{output}")
    else:
        print(f"\n❌ 优化失败: {result.error}")


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
    # Solo 模式
    # -------------------------------------------------------------------------
    solo = subparsers.add_parser("solo", help="单 Agent 模式")
    solo.add_argument("-p", "--prompt", required=True, help="任务描述")
    solo.add_argument("-m", "--max_steps", type=int, default=5, help="最大轮数")
    solo.add_argument("-o", "--output_dir", default="./output", help="输出目录")
    solo.add_argument("--local", action="store_true", help="使用本地 vLLM")
    solo.add_argument("-d", "--debug", action="store_true", help="调试模式")
    
    # -------------------------------------------------------------------------
    # Task 模式（通用）
    # -------------------------------------------------------------------------
    task = subparsers.add_parser("task", help="通用任务模式")
    task.add_argument("-n", "--task_name", required=True, help="任务名称（如 resume, code_review）")
    task.add_argument("-i", "--input", required=True, help="输入数据 JSON 或 @文件路径")
    task.add_argument("--style", default="modern", help="样式偏好")
    task.add_argument("--local", action="store_true", help="使用本地 vLLM")
    task.add_argument("-d", "--debug", action="store_true", help="调试模式")
    
    # -------------------------------------------------------------------------
    # Resume 模式（快捷方式）
    # -------------------------------------------------------------------------
    resume = subparsers.add_parser("resume", help="简历优化（快捷方式）")
    resume.add_argument("-n", "--name", default="陈亮江", help="姓名")
    resume.add_argument("-s", "--school", default="电子科技大学", help="学校")
    resume.add_argument("-m", "--major", default="电子信息", help="专业")
    resume.add_argument("-j", "--json_file", help="从 JSON 文件加载简历数据")
    resume.add_argument("--style", default="modern", choices=["modern", "classic", "minimal"], help="样式")
    resume.add_argument("-o", "--output_dir", default="./output", help="输出目录")
    resume.add_argument("--simple", action="store_true", help="简单模式（不用 AI）")
    resume.add_argument("--local", action="store_true", help="使用本地 vLLM")
    resume.add_argument("-d", "--debug", action="store_true", help="调试模式")
    
    return parser.parse_args()


def main() -> None:
    """主函数。"""
    args = parse_args()
    
    if args.mode is None:
        print("🤖 Agent Framework CLI\n")
        print("可用模式:")
        print("  solo    单 Agent（ReAct 循环）")
        print("  task    通用任务（Orchestrator 路由）")
        print("  resume  简历优化（快捷方式）")
        print("\n示例:")
        print('  python main.py solo -p "计算 3*7"')
        print('  python main.py task -n resume -i \'{"name": "张三"}\'')
        print('  python main.py resume -n "张三" -s "清华大学"')
        return
    
    if hasattr(args, 'debug') and args.debug:
        set_level("DEBUG")
    
    if args.mode == "solo":
        run_solo_mode(args)
    elif args.mode == "task":
        run_task_mode(args)
    elif args.mode == "resume":
        run_resume_mode(args)


if __name__ == "__main__":
    main()
