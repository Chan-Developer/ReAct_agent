"""
测试多 Agent 架构

包含：
- ContentAgent 测试
- LayoutAgent 测试
- ResumeAgentOrchestrator 测试
"""

import pytest
from unittest.mock import MagicMock, patch
import json


class MockLLM:
    """模拟 LLM"""
    
    def __init__(self, response: str = ""):
        self.response = response
        self.call_count = 0
    
    def chat(self, prompt: str, system_prompt: str = None) -> str:
        self.call_count += 1
        return self.response


class TestContentAgent:
    """测试 ContentAgent"""
    
    def test_init(self):
        """测试初始化"""
        from agents import ContentAgent
        
        llm = MockLLM()
        agent = ContentAgent(llm)
        
        assert agent.name == "ContentAgent"
        assert agent.role == "简历内容优化专家"
        assert agent.llm == llm
    
    def test_think(self):
        """测试思考阶段"""
        from agents import ContentAgent
        
        mock_response = json.dumps({
            "analysis": {
                "summary_score": 6,
                "experience_score": 7,
                "project_score": 8,
                "skills_score": 7,
                "overall_score": 7
            },
            "weaknesses": ["缺少量化数据", "描述不够具体"],
            "opportunities": ["可以添加具体指标", "使用STAR法则"],
            "reasoning": "简历整体结构完整，但需要加强量化描述"
        })
        
        llm = MockLLM(response=mock_response)
        agent = ContentAgent(llm)
        
        resume_data = {
            "name": "测试用户",
            "summary": "软件工程师",
            "experiences": []
        }
        
        reasoning = agent.think(resume_data)
        
        assert llm.call_count == 1
        assert "analysis" in reasoning or "weaknesses" in reasoning
    
    def test_execute(self):
        """测试执行阶段"""
        from agents import ContentAgent
        
        optimized_resume = {
            "name": "测试用户",
            "summary": "优化后的简介：资深软件工程师...",
            "experiences": [
                {
                    "company": "科技公司",
                    "position": "高级工程师",
                    "highlights": ["提升系统性能30%", "主导重构项目"]
                }
            ]
        }
        
        mock_response = f"```json\n{json.dumps(optimized_resume, ensure_ascii=False)}\n```"
        
        llm = MockLLM(response=mock_response)
        agent = ContentAgent(llm)
        
        resume_data = {"name": "测试用户", "summary": "工程师"}
        reasoning = "分析结果..."
        
        result = agent.execute(resume_data, reasoning)
        
        assert result.success == True
        assert "name" in result.data


class TestLayoutAgent:
    """测试 LayoutAgent"""
    
    def test_init(self):
        """测试初始化"""
        from agents import LayoutAgent
        
        llm = MockLLM()
        agent = LayoutAgent(llm)
        
        assert agent.name == "LayoutAgent"
        assert agent.role == "简历布局编排专家"
    
    def test_default_config(self):
        """测试默认配置生成"""
        from agents import LayoutAgent
        
        llm = MockLLM()
        agent = LayoutAgent(llm)
        
        # 应届生简历
        fresh_grad_data = {
            "name": "新毕业生",
            "education": [{"school": "某大学"}],
            "experiences": []
        }
        
        config = agent._get_default_config(fresh_grad_data)
        
        # 应届生应该把教育放在前面
        assert "education" in config["section_order"]
        assert config["section_order"].index("education") < config["section_order"].index("experience")
    
    def test_trim_content(self):
        """测试内容精简"""
        from agents import LayoutAgent
        
        llm = MockLLM()
        agent = LayoutAgent(llm)
        
        resume_data = {
            "experiences": [
                {"company": f"公司{i}", "highlights": [f"成就{j}" for j in range(10)]}
                for i in range(10)
            ],
            "projects": [
                {"name": f"项目{i}"}
                for i in range(10)
            ]
        }
        
        layout_config = {
            "content_limits": {
                "max_experiences": 3,
                "max_projects": 2,
                "max_highlights_per_item": 4
            }
        }
        
        trimmed = agent._trim_content(resume_data, layout_config)
        
        assert len(trimmed["experiences"]) == 3
        assert len(trimmed["projects"]) == 2
        assert len(trimmed["experiences"][0]["highlights"]) == 4


class TestOrchestrator:
    """测试通用 Orchestrator"""
    
    def test_init(self):
        """测试初始化"""
        from core import Orchestrator
        from agents import ResumeCrew
        
        llm = MockLLM()
        orchestrator = Orchestrator(llm)
        orchestrator.register(ResumeCrew)
        
        assert "resume" in orchestrator.list_crews()
    
    def test_get_crew(self):
        """测试获取 Crew"""
        from core import Orchestrator, Task
        from agents import ResumeCrew
        
        llm = MockLLM()
        orchestrator = Orchestrator(llm)
        orchestrator.register(ResumeCrew)
        
        crew = orchestrator.get_crew("resume")
        assert crew is not None
        assert crew.CREW_NAME == "resume"
    
    def test_crew_not_found(self):
        """测试找不到 Crew"""
        from core import Orchestrator, Task
        
        llm = MockLLM()
        orchestrator = Orchestrator(llm)
        
        task = Task(name="unknown_task", input_data={})
        result = orchestrator.run(task)
        
        assert result.success is False
        assert "未找到" in result.error


class TestAgentResult:
    """测试 AgentResult"""
    
    def test_agent_result_creation(self):
        """测试结果对象创建"""
        from agents.base import AgentResult
        
        result = AgentResult(
            success=True,
            data={"key": "value"},
            reasoning="分析过程",
            suggestions=["建议1", "建议2"]
        )
        
        assert result.success == True
        assert result.data["key"] == "value"
        assert len(result.suggestions) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

