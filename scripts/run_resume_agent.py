#!/usr/bin/env python3
"""
多 Agent 简历生成启动脚本

使用方式：
    python scripts/run_resume_agent.py

可选参数：
    --name      姓名
    --school    学校
    --major     专业
    --output    输出目录
    --style     样式 (modern/classic/minimal/professional)
"""

import sys
import os
import argparse
import json

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm import ModelScopeOpenAI
from agents import ResumeAgentOrchestrator
from tools.generators import ResumeGenerator


def create_sample_resume(name: str, school: str, major: str) -> dict:
    """创建示例简历数据"""
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
                "highlights": [
                    "设计并实现图像处理算法",
                    "优化模型性能"
                ],
                "tech_stack": ["Python", "PyTorch", "OpenCV"]
            },
            {
                "name": "智能对话系统",
                "role": "核心开发者",
                "start_date": "2024.09",
                "end_date": "2024.12",
                "description": "基于大语言模型的对话系统",
                "highlights": [
                    "实现多轮对话功能",
                    "集成知识库检索"
                ],
                "tech_stack": ["Python", "LangChain", "FastAPI"]
            }
        ],
        "skills": ["Python", "PyTorch", "TensorFlow", "深度学习", "计算机视觉", "NLP"],
        "skill_levels": [
            {"name": "Python", "level": 90},
            {"name": "PyTorch", "level": 85},
            {"name": "深度学习", "level": 80},
            {"name": "计算机视觉", "level": 75}
        ]
    }


def run_with_multi_agent(resume_data: dict, output_dir: str, style: str):
    """使用多 Agent 架构生成简历"""
    print("\n" + "=" * 60)
    print("🚀 多 Agent 简历生成系统")
    print("=" * 60)
    
    # 创建 LLM
    print("\n📡 初始化 LLM...")
    llm = ModelScopeOpenAI()
    
    # 创建协调器
    print("🤖 初始化多 Agent 协调器...")
    orchestrator = ResumeAgentOrchestrator(
        llm=llm,
        enable_content_optimization=True,
        enable_layout_optimization=True,
    )
    
    # 运行优化
    print("\n✨ 运行 Agent 优化流程...")
    print("  ├─ ContentAgent: 优化简历内容...")
    print("  └─ LayoutAgent: 编排简历布局...")
    
    result = orchestrator.optimize(resume_data, style_preference=style)
    
    if result.success:
        print(f"\n✅ 优化完成! 耗时: {result.execution_time:.2f}s")
        
        # 显示建议
        if result.content_suggestions:
            print("\n💡 内容优化建议:")
            for s in result.content_suggestions[:3]:
                print(f"   • {s}")
        
        if result.layout_suggestions:
            print("\n📐 布局建议:")
            for s in result.layout_suggestions[:3]:
                print(f"   • {s}")
        
        # 使用优化后的数据生成简历
        print("\n📝 生成 Word 文档...")
        generator = ResumeGenerator(
            output_dir=output_dir,
            llm=None,  # 已经优化过了，不需要再次调用 LLM
            use_multi_agent=False,
        )
        
        filename = f"{resume_data['name']}_resume"
        output = generator.execute(
            resume_data=json.dumps(result.optimized_resume, ensure_ascii=False),
            filename=filename,
            template_style=style,
            optimize=False,
        )
        
        print(f"\n{output}")
        
    else:
        print(f"\n❌ 优化失败: {result.error}")


def run_simple_mode(resume_data: dict, output_dir: str, style: str):
    """简单模式：直接生成（不使用多 Agent）"""
    print("\n" + "=" * 60)
    print("📄 简单模式简历生成")
    print("=" * 60)
    
    generator = ResumeGenerator(
        output_dir=output_dir,
        llm=None,
        use_multi_agent=False,
    )
    
    filename = f"{resume_data['name']}_resume"
    output = generator.execute(
        resume_data=json.dumps(resume_data, ensure_ascii=False),
        filename=filename,
        template_style=style,
        optimize=False,
    )
    
    print(f"\n{output}")


def main():
    parser = argparse.ArgumentParser(description="多 Agent 简历生成系统")
    parser.add_argument("--name", default="陈亮江", help="姓名")
    parser.add_argument("--school", default="电子科技大学", help="学校")
    parser.add_argument("--major", default="电子信息", help="专业")
    parser.add_argument("--output", default="./output", help="输出目录")
    parser.add_argument("--style", default="modern", 
                       choices=["modern", "classic", "minimal", "professional"],
                       help="简历样式")
    parser.add_argument("--simple", action="store_true", help="简单模式（不使用AI优化）")
    
    args = parser.parse_args()
    
    # 创建示例简历
    resume_data = create_sample_resume(args.name, args.school, args.major)
    
    print(f"\n👤 姓名: {args.name}")
    print(f"🎓 学校: {args.school}")
    print(f"📚 专业: {args.major}")
    print(f"🎨 样式: {args.style}")
    
    if args.simple:
        run_simple_mode(resume_data, args.output, args.style)
    else:
        run_with_multi_agent(resume_data, args.output, args.style)


if __name__ == "__main__":
    main()

