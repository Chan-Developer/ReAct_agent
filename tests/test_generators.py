# -*- coding: utf-8 -*-
"""简历生成器测试。"""
import json
import os
import pytest
from tools.generators import ResumeGenerator, ResumeEnhancer


class TestResumeEnhancer:
    """简历增强器测试"""
    
    def test_categorize_skills(self):
        skills = ["Python", "PyTorch", "机器学习", "Linux"]
        result = ResumeEnhancer.categorize_skills(skills)
        
        assert "编程语言" in result
        assert "Python" in result["编程语言"]
    
    def test_calculate_completeness(self):
        # 空简历
        empty = {}
        assert ResumeEnhancer.calculate_completeness(empty) == 0
        
        # 部分填写
        partial = {"name": "张三", "email": "test@test.com"}
        assert ResumeEnhancer.calculate_completeness(partial) > 0
    
    def test_suggest_improvements(self):
        data = {"name": "张三"}
        suggestions = ResumeEnhancer.suggest_improvements(data)
        
        assert len(suggestions) > 0


class TestResumeGenerator:
    """简历生成器测试"""
    
    def setup_method(self):
        self.gen = ResumeGenerator(output_dir="./output")
    
    def test_init(self):
        assert self.gen.name == "generate_resume"
        assert os.path.exists(self.gen.output_dir)
    
    def test_invalid_json(self):
        result = self.gen.execute(resume_data="invalid json")
        assert "❌" in result
    
    def test_generate_docx(self):
        data = {
            "name": "测试用户",
            "email": "test@test.com",
            "education": [{"school": "测试大学", "major": "计算机"}],
            "skills": ["Python", "Java"],
        }
        
        result = self.gen.execute(
            resume_data=json.dumps(data, ensure_ascii=False),
            filename="test_resume",
            template_style="modern",
            optimize=False,
        )
        
        assert "✅" in result
        assert os.path.exists("./output/test_resume.docx")
    
    def teardown_method(self):
        # 清理测试文件
        test_file = "./output/test_resume.docx"
        if os.path.exists(test_file):
            os.remove(test_file)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

