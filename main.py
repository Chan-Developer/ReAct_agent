#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Agent CLI 统一入口。

支持两种模式：
    1. solo - 单 Agent 模式（ReAct 思考-行动循环）
    2. crew - 多 Agent 团队模式（多角色协作）

运行方式：
    # Solo 模式（单 Agent）
    python main.py solo --prompt "计算 3*7+2"
    python main.py solo --prompt "帮我生成简历" --debug
    
    # Crew 模式（多 Agent 团队）
    python main.py crew --name "张三" --school "电子科技大学"
    python main.py crew --name "李四" --simple
"""
from __future__ import annotations

import argparse
import sys
import os
import json

# 公共模块
from common import setup_logging, set_level, get_logger

# Agent
from agents import ReactAgent, ResumeAgentOrchestrator

# 工具
from tools import Calculator, Search, AddFile, ReadFile, ToolRegistry
from tools.generators import ResumeGenerator

# LLM
from llm import VllmLLM, ModelScopeOpenAI

# 初始化日志
setup_logging()
logger = get_logger(__name__)


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


def build_solo_agent(args) -> ReactAgent:
    """构建单 Agent。"""
    if args.local:
        logger.info("使用本地 vLLM 模型")
        llm = VllmLLM()
        tools = create_default_tools(args.output_dir)
    else:
        logger.info("使用云端 ModelScope 模型")
        try:
            llm = ModelScopeOpenAI()
        except ValueError as e:
            logger.error(f"初始化 LLM 失败: {e}")
            sys.exit(1)
        tools = create_default_tools(args.output_dir, llm=llm)
    
    return ReactAgent(llm=llm, tools=tools, max_rounds=args.max_steps)


def run_solo_mode(args):
    """运行 Solo 模式（单 Agent）。"""
    print("\n" + "=" * 60)
    print("🧠 Solo 模式 - 单 Agent")
    print("=" * 60)
    
    agent = build_solo_agent(args)
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
# Crew 模式（多 Agent 团队）
# =============================================================================

def create_sample_resume(name: str, school: str, major: str) -> dict:
    """创建示例简历数据。"""
    return {
        "name": name,
        "phone": "138****1234",
        "email": f"{name.lower().replace(' ', '')}@example.com",
        "location": "成都",
        "summary": f"{school}{major}专业学生",
        "education": [
            {
                "school": school,
                "degree": "硕士研究生",
                "major": major,
                "start_date": "2024.09",
                "end_date": "2027.06",
                "gpa": "3.8/4.0"
            }
        ],
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
            {
                "name": "智能对话系统",
                "role": "核心开发者",
                "start_date": "2024.09",
                "end_date": "2024.12",
                "description": "基于大语言模型的对话系统",
                "highlights": ["实现多轮对话功能", "集成知识库检索"],
                "tech_stack": ["Python", "LangChain", "FastAPI"]
            }
        ],
        "skills": ["Python", "PyTorch", "TensorFlow", "深度学习", "计算机视觉", "NLP"],
        "skill_levels": [
            {"name": "Python", "level": 90},
            {"name": "PyTorch", "level": 85},
            {"name": "深度学习", "level": 80},
        ]
    }


def run_crew_mode(args):
    """运行 Crew 模式（多 Agent 团队）。"""
    print("\n" + "=" * 60)
    print("👥 Crew 模式 - 多 Agent 团队")
    print("=" * 60)
    
    # 创建简历数据
    resume_data = create_sample_resume(args.name, args.school, args.major)
    
    print(f"\n👤 姓名: {args.name}")
    print(f"🎓 学校: {args.school}")
    print(f"📚 专业: {args.major}")
    print(f"🎨 样式: {args.style}")
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    if args.simple:
        # 简单模式：直接生成
        print("\n📄 简单模式（不使用 AI 优化）...")
        generator = ResumeGenerator(output_dir=args.output_dir, llm=None)
        output = generator.execute(
            resume_data=json.dumps(resume_data, ensure_ascii=False),
            filename=f"{args.name}_resume",
            template_style=args.style,
            optimize=False,
        )
        print(f"\n{output}")
    else:
        # 多 Agent 模式
        print("\n📡 初始化 LLM...")
        try:
            llm = ModelScopeOpenAI()
        except ValueError as e:
            logger.error(f"初始化 LLM 失败: {e}")
            sys.exit(1)
        
        print("🤖 初始化多 Agent 协调器...")
        orchestrator = ResumeAgentOrchestrator(
            llm=llm,
            enable_content_optimization=True,
            enable_layout_optimization=True,
        )
        
        print("\n✨ 运行 Agent 优化流程...")
        print("  ├─ ContentAgent: 优化简历内容...")
        print("  └─ LayoutAgent: 编排简历布局...")
        
        result = orchestrator.optimize(resume_data, style_preference=args.style)
        
        if result.success:
            print(f"\n✅ 优化完成! 耗时: {result.execution_time:.2f}s")
            
            if result.content_suggestions:
                print("\n💡 内容优化建议:")
                for s in result.content_suggestions[:3]:
                    print(f"   • {s}")
            
            if result.layout_suggestions:
                print("\n📐 布局建议:")
                for s in result.layout_suggestions[:3]:
                    print(f"   • {s}")
            
            # 生成文档
            print("\n📝 生成 Word 文档...")
            generator = ResumeGenerator(output_dir=args.output_dir, llm=None)
            output = generator.execute(
                resume_data=json.dumps(result.optimized_resume, ensure_ascii=False),
                filename=f"{args.name}_resume",
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
        description="🤖 Agent CLI - 智能代理系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    subparsers = parser.add_subparsers(dest="mode", help="运行模式")
    
    # -------------------------------------------------------------------------
    # Solo 模式（单 Agent）
    # -------------------------------------------------------------------------
    solo_parser = subparsers.add_parser(
        "solo",
        help="单 Agent 模式（ReAct 思考-行动循环）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python main.py solo --prompt "计算 3*7+2 的结果"
    python main.py solo --prompt "帮我生成一份简历" --debug
    python main.py solo --local --prompt "你好"
        """
    )
    solo_parser.add_argument(
        "--prompt", "-p", type=str, required=True,
        help="用户输入的问题或指令"
    )
    solo_parser.add_argument(
        "--max_steps", "-m", type=int, default=5,
        help="最大思考轮数 (默认: 5)"
    )
    solo_parser.add_argument(
        "--output_dir", "-o", type=str, default="./output",
        help="输出目录 (默认: ./output)"
    )
    solo_parser.add_argument(
        "--local", action="store_true",
        help="使用本地 vLLM 而非云端 ModelScope"
    )
    solo_parser.add_argument(
        "--debug", "-d", action="store_true",
        help="启用调试模式"
    )
    
    # -------------------------------------------------------------------------
    # Crew 模式（多 Agent 团队）
    # -------------------------------------------------------------------------
    crew_parser = subparsers.add_parser(
        "crew",
        help="多 Agent 团队模式（多角色协作）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python main.py crew --name "张三" --school "电子科技大学"
    python main.py crew --name "李四" --style professional
    python main.py crew --name "王五" --simple

当前支持的 Agent 角色:
    • ContentAgent  - 内容优化专家
    • LayoutAgent   - 布局编排专家
        """
    )
    crew_parser.add_argument(
        "--name", "-n", type=str, default="陈亮江",
        help="姓名 (默认: 陈亮江)"
    )
    crew_parser.add_argument(
        "--school", "-s", type=str, default="电子科技大学",
        help="学校 (默认: 电子科技大学)"
    )
    crew_parser.add_argument(
        "--major", "-m", type=str, default="电子信息",
        help="专业 (默认: 电子信息)"
    )
    crew_parser.add_argument(
        "--style", type=str, default="modern",
        choices=["modern", "classic", "minimal", "professional"],
        help="简历样式 (默认: modern)"
    )
    crew_parser.add_argument(
        "--output_dir", "-o", type=str, default="./output",
        help="输出目录 (默认: ./output)"
    )
    crew_parser.add_argument(
        "--simple", action="store_true",
        help="简单模式（不使用 AI 优化）"
    )
    crew_parser.add_argument(
        "--debug", "-d", action="store_true",
        help="启用调试模式"
    )
    
    return parser.parse_args()


def main() -> None:
    """主函数。"""
    args = parse_args()
    
    # 未指定模式时显示帮助
    if args.mode is None:
        print("🤖 Agent CLI - 智能代理系统\n")
        print("可用模式:")
        print("  solo  - 单 Agent 模式（ReAct 思考-行动循环）")
        print("  crew  - 多 Agent 团队模式（多角色协作）")
        print("\n使用 --help 查看详细帮助:")
        print("  python main.py --help")
        print("  python main.py solo --help")
        print("  python main.py crew --help")
        return
    
    # 设置日志级别
    if hasattr(args, 'debug') and args.debug:
        set_level("DEBUG")
    
    # 运行对应模式
    if args.mode == "solo":
        run_solo_mode(args)
    elif args.mode == "crew":
        run_crew_mode(args)


if __name__ == "__main__":
    main()
