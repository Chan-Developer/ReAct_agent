# -*- coding: utf-8 -*-
"""专家 Agent 模块测试。

测试内容：
- ContentAgent
- LayoutAgent
- ResumePipeline (Workflow)
"""
import pytest
from unittest.mock import MagicMock, patch
import json


# =============================================================================
# Mock 对象
# =============================================================================

class MockLLM:
    """模拟 LLM"""
    def chat(self, messages, **kwargs):
        # 返回一个基本的优化建议
        return json.dumps({
            "analysis": {"overall_score": 7},
            "weaknesses": ["可以更量化"],
            "opportunities": ["添加技术细节"],
            "reasoning": "分析完成"
        })


SAMPLE_RESUME = {
    "name": "张三",
    "email": "zhangsan@example.com",
    "summary": "5年Python开发经验",
    "experience": [
        {
            "company": "阿里巴巴",
            "position": "后端工程师",
            "highlights": ["主导系统重构"]
        }
    ],
    "skills": ["Python", "Django", "MySQL"]
}


# =============================================================================
# ContentAgent 测试
# =============================================================================

class TestContentAgent:
    """ContentAgent 测试"""
    
    def test_init(self):
        """测试初始化"""
        from agents import ContentAgent
        
        llm = MockLLM()
        agent = ContentAgent(llm)
        
        assert agent.name == "ContentAgent"
    
    def test_job_description_support(self):
        """测试职位描述支持"""
        from agents import ContentAgent
        
        llm = MockLLM()
        agent = ContentAgent(llm)
        
        # 传入职位描述
        result = agent.run(SAMPLE_RESUME.copy(), job_description="招聘Python工程师")
        
        # 不需要真正的 LLM，只验证方法能接受 job_description
        assert result is not None


# =============================================================================
# LayoutAgent 测试
# =============================================================================

class TestLayoutAgent:
    """LayoutAgent 测试"""
    
    def test_init(self):
        """测试初始化"""
        from agents import LayoutAgent
        
        llm = MockLLM()
        agent = LayoutAgent(llm)
        
        assert agent.name == "LayoutAgent"


# =============================================================================
# ResumePipeline (Workflow) 测试
# =============================================================================

class TestResumePipeline:
    """ResumePipeline 工作流测试"""
    
    def test_init(self):
        """测试初始化"""
        from workflows import ResumePipeline
        
        pipeline = ResumePipeline(llm=None)
        
        assert pipeline.WORKFLOW_NAME == "resume_pipeline"
        assert len(pipeline.WORKFLOW_STEPS) == 5
        assert "内容优化" in pipeline.WORKFLOW_STEPS
        assert "模板选择" in pipeline.WORKFLOW_STEPS
    
    def test_workflow_steps(self):
        """测试工作流步骤"""
        from workflows import ResumePipeline
        
        pipeline = ResumePipeline(llm=None)
        
        expected_steps = ["内容优化", "模板选择", "布局设计", "分页优化", "生成文档"]
        assert pipeline.WORKFLOW_STEPS == expected_steps
    
    def test_template_selection_in_workflow(self):
        """测试工作流中的模板选择"""
        from workflows import ResumePipeline
        from workflows.base import WorkflowContext
        
        pipeline = ResumePipeline(llm=None)
        
        ctx = WorkflowContext(
            input_data=SAMPLE_RESUME,
            template_name="tech_modern",
        )
        
        # 测试模板选择方法
        template_config = pipeline._select_template(ctx)
        
        assert template_config is not None
        assert "font_config" in template_config
    
    def test_template_auto_match(self):
        """测试模板自动匹配"""
        from workflows import ResumePipeline
        from workflows.base import WorkflowContext
        
        pipeline = ResumePipeline(llm=None)
        
        ctx = WorkflowContext(
            input_data=SAMPLE_RESUME,
            job_description="招聘Python后端工程师，熟悉Django框架",
        )
        
        # 应该根据 JD 自动匹配模板
        template_config = pipeline._select_template(ctx)
        
        assert template_config is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

