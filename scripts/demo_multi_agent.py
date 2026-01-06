#!/usr/bin/env python3
"""
多 Agent 简历优化演示脚本

展示 ContentAgent + LayoutAgent 协同工作的效果。
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import (
    ContentAgent,
    LayoutAgent,
    ResumeAgentOrchestrator,
)


def demo_with_mock_llm():
    """使用 Mock LLM 演示"""
    import json
    
    class MockLLM:
        """模拟 LLM"""
        def __init__(self):
            self.call_count = 0
        
        def chat(self, prompt: str, system_prompt: str = None) -> str:
            self.call_count += 1
            
            # 根据 prompt 内容返回不同响应
            if "分析" in prompt or "维度" in prompt:
                return json.dumps({
                    "analysis": {
                        "summary_score": 6,
                        "experience_score": 5,
                        "project_score": 7,
                        "skills_score": 6,
                        "overall_score": 6
                    },
                    "weaknesses": [
                        "个人简介过于简短，缺乏亮点",
                        "项目经历缺少量化指标",
                        "技能描述不够具体"
                    ],
                    "opportunities": [
                        "添加具体的量化成果",
                        "使用STAR法则重构项目描述",
                        "突出技术深度和解决的挑战"
                    ],
                    "reasoning": "简历基本信息完整，但需要加强内容的专业性和影响力展示"
                }, ensure_ascii=False)
            
            elif "优化" in prompt:
                return """```json
{
    "name": "陈亮江",
    "title": "AI/机器学习工程师",
    "summary": "电子科技大学研究生，专注于深度学习与计算机视觉领域。熟练掌握 PyTorch/TensorFlow 深度学习框架，具备扎实的算法基础和工程实践能力。在校期间主导多个 AI 项目，包括医学图像处理、大语言模型应用等方向。",
    "education": [
        {
            "school": "电子科技大学",
            "degree": "硕士研究生",
            "major": "电子信息",
            "start_date": "2024.09",
            "end_date": "2027.06"
        }
    ],
    "experiences": [],
    "projects": [
        {
            "name": "医学图像金属伪影去除系统",
            "role": "项目负责人",
            "description": "基于深度学习的 CT 图像金属伪影校正系统",
            "highlights": [
                "设计并实现线性插值+深度学习的混合算法，伪影去除率达 85%",
                "优化 Radon 变换投影域处理流程，处理速度提升 40%",
                "构建医学图像数据集 500+ 样本，覆盖多种金属伪影场景"
            ],
            "tech_stack": ["Python", "PyTorch", "scikit-image", "NumPy"]
        },
        {
            "name": "智能简历生成 Agent",
            "role": "核心开发者",
            "description": "基于 ReAct 架构的多 Agent 简历优化系统",
            "highlights": [
                "设计 ContentAgent + LayoutAgent 多智能体协作架构",
                "集成 LLM 实现简历内容自动优化，专业度评分提升 30%",
                "支持多种模板样式，生成企业级 Word 文档"
            ],
            "tech_stack": ["Python", "LangChain", "python-docx", "OpenAI API"]
        }
    ],
    "skills": [
        {"name": "Python", "level": "expert"},
        {"name": "PyTorch", "level": "proficient"},
        {"name": "TensorFlow", "level": "familiar"},
        {"name": "深度学习", "level": "proficient"},
        {"name": "计算机视觉", "level": "proficient"}
    ]
}
```"""
            
            elif "布局" in prompt or "配置" in prompt:
                return json.dumps({
                    "section_order": ["header", "summary", "education", "projects", "skills"],
                    "style": "modern",
                    "color_scheme": "professional",
                    "font_config": {
                        "family": "Microsoft YaHei",
                        "title_size": 18,
                        "heading_size": 11,
                        "body_size": 9
                    },
                    "spacing_config": {
                        "margin": 0.5,
                        "section_gap": 8,
                        "item_gap": 3
                    },
                    "visual_elements": {
                        "use_icons": True,
                        "use_skill_bars": True,
                        "use_timeline": False,
                        "highlight_keywords": True
                    },
                    "content_limits": {
                        "compact_mode": False,
                        "max_experiences": 4,
                        "max_projects": 3,
                        "max_highlights_per_item": 4
                    },
                    "design_notes": "应届研究生简历，教育和项目经历优先展示，突出技术能力和研究潜力"
                }, ensure_ascii=False)
            
            return "{}"
    
    # 原始简历数据
    original_resume = {
        "name": "陈亮江",
        "email": "chenliangjiang@example.com",
        "phone": "138****1234",
        "summary": "研一学生",
        "education": [
            {
                "school": "电子科技大学",
                "degree": "硕士研究生",
                "major": "电子信息",
                "start_date": "2024.09",
                "end_date": "2027.06"
            }
        ],
        "projects": [
            {
                "name": "图像处理项目",
                "description": "处理医学图像"
            }
        ],
        "skills": ["Python", "PyTorch", "深度学习"]
    }
    
    print("=" * 60)
    print("多 Agent 简历优化演示")
    print("=" * 60)
    
    # 创建 Mock LLM
    llm = MockLLM()
    
    # 创建协调器
    orchestrator = ResumeAgentOrchestrator(
        llm=llm,
        enable_content_optimization=True,
        enable_layout_optimization=True,
    )
    
    print("\n📝 原始简历:")
    print(f"  姓名: {original_resume['name']}")
    print(f"  简介: {original_resume['summary']}")
    print(f"  项目数: {len(original_resume['projects'])}")
    
    # 运行优化
    print("\n🚀 开始多 Agent 优化...")
    result = orchestrator.optimize(original_resume)
    
    print("\n📊 优化结果:")
    print(f"  成功: {result.success}")
    print(f"  耗时: {result.execution_time:.2f}s")
    print(f"  LLM 调用次数: {llm.call_count}")
    
    if result.success:
        print("\n✨ 优化后的简历:")
        optimized = result.optimized_resume
        print(f"  姓名: {optimized.get('name', 'N/A')}")
        print(f"  职位: {optimized.get('title', 'N/A')}")
        print(f"  简介: {optimized.get('summary', 'N/A')[:50]}...")
        
        projects = optimized.get('projects', [])
        print(f"  项目数: {len(projects)}")
        for i, proj in enumerate(projects[:2], 1):
            print(f"    {i}. {proj.get('name', 'N/A')}")
            highlights = proj.get('highlights', [])
            for h in highlights[:2]:
                print(f"       • {h[:40]}...")
        
        print("\n📐 布局配置:")
        layout = result.layout_config
        print(f"  章节顺序: {' → '.join(layout.get('section_order', []))}")
        print(f"  样式: {layout.get('style', 'N/A')}")
        print(f"  设计说明: {layout.get('design_notes', 'N/A')}")
        
        if result.content_suggestions:
            print("\n💡 内容优化建议:")
            for s in result.content_suggestions[:3]:
                print(f"  • {s}")
    
    print("\n" + "=" * 60)
    print("演示完成!")
    print("=" * 60)


def demo_single_agents():
    """演示单独使用各 Agent"""
    import json
    
    class SimpleMockLLM:
        def chat(self, prompt: str, system_prompt: str = None) -> str:
            return json.dumps({
                "analysis": {"overall_score": 7},
                "weaknesses": ["需要量化成果"],
                "opportunities": ["添加具体数据"],
                "reasoning": "整体不错"
            }, ensure_ascii=False)
    
    llm = SimpleMockLLM()
    
    print("\n--- ContentAgent 单独使用 ---")
    content_agent = ContentAgent(llm)
    
    resume = {"name": "测试", "summary": "工程师"}
    reasoning = content_agent.think(resume)
    print(f"分析结果: {reasoning[:100]}...")
    
    print("\n--- LayoutAgent 单独使用 ---")
    layout_agent = LayoutAgent(llm)
    
    config = layout_agent._get_default_config(resume)
    print(f"默认配置 - 样式: {config['style']}")
    print(f"默认配置 - 章节顺序: {config['section_order']}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("        多 Agent 架构演示")
    print("=" * 60)
    
    # 使用 Mock LLM 演示完整流程
    demo_with_mock_llm()
    
    # 演示单独使用各 Agent
    demo_single_agents()

