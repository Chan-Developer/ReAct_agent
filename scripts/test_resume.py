#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""简历生成测试脚本。

使用方法：
    python scripts/test_resume.py
"""
import json
import sys
sys.path.insert(0, ".")

from tools.generators import ResumeGenerator, ResumeEnhancer
from llm import ModelScopeOpenAI


def main():
    print("=" * 60)
    print("🧪 简历生成完整测试")
    print("=" * 60)
    
    # 1. 准备测试数据
    resume_data = {
        "name": "陈亮江",
        "phone": "138-1234-5678",
        "email": "chenlj@uestc.edu.cn",
        "location": "成都",
        "github": "github.com/chenlj",
        
        "education": [
            {
                "school": "电子科技大学",
                "degree": "硕士",
                "major": "电子信息",
                "start_date": "2024.09",
                "end_date": "2027.06",
                "gpa": "3.8/4.0"
            }
        ],
        
        "skills": [
            "Python", "PyTorch", "机器学习", 
            "深度学习", "信号处理", "C++", "Linux"
        ],
        
        "skill_levels": [
            {"name": "Python", "level": 90},
            {"name": "PyTorch", "level": 85},
            {"name": "机器学习", "level": 80},
            {"name": "C++", "level": 70}
        ],
        
        "projects": [
            {
                "name": "智能语音识别系统",
                "role": "核心开发者",
                "start_date": "2024.10",
                "end_date": "2025.01",
                "description": "基于 Transformer 架构的端到端语音识别系统",
                "highlights": [
                    "使用 Conformer 模型，在测试集上达到 95% 准确率",
                    "优化推理速度，单条音频处理时间降低 40%"
                ],
                "tech_stack": ["Python", "PyTorch", "Whisper", "ONNX"]
            }
        ],
        
        "certificates": ["CET-6 (580分)", "全国计算机二级"],
        "awards": ["研究生学业奖学金一等奖", "数学建模竞赛省级二等奖"]
    }
    
    # 2. 本地分析（不需要 LLM）
    print("\n📊 本地简历分析:")
    print("-" * 40)
    
    # 技能分类
    categorized = ResumeEnhancer.categorize_skills(resume_data["skills"])
    print("技能分类:")
    for cat, skills in categorized.items():
        print(f"  • {cat}: {', '.join(skills)}")
    
    # 完整度
    completeness = ResumeEnhancer.calculate_completeness(resume_data)
    print(f"\n简历完整度: {completeness}%")
    
    # 改进建议
    suggestions = ResumeEnhancer.suggest_improvements(resume_data)
    if suggestions:
        print("\n改进建议:")
        for s in suggestions:
            print(f"  {s}")
    
    # 3. 生成简历（需要 LLM）
    print("\n" + "-" * 40)
    print("📄 生成简历文档 (含 AI 优化):")
    print("-" * 40)
    
    try:
        llm = ModelScopeOpenAI()
        gen = ResumeGenerator(
            output_dir="./output",
            llm=llm,
            auto_optimize=True
        )
        
        # 生成 Word 版本
        result = gen.execute(
            resume_data=json.dumps(resume_data, ensure_ascii=False),
            filename="测试简历_Word",
            template_style="modern"
        )
        print(result)
        
    except ValueError as e:
        print(f"⚠️ LLM 未配置: {e}")
        print("提示: 请设置 MODELSCOPE_API_KEY 或编辑 configs/config.yaml")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()

