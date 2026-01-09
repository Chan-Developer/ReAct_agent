# -*- coding: utf-8 -*-
"""Crew 模块测试。

测试内容：
- BaseCrew 基类
- ResumeCrew
"""
import pytest
from unittest.mock import MagicMock, patch
import time


# =============================================================================
# Mock 对象
# =============================================================================

class MockLLM:
    """模拟 LLM"""
    def chat(self, messages, **kwargs):
        return {"content": "mock response"}


class MockKnowledgeBase:
    """模拟知识库"""
    def retrieve_context(self, query, top_k=3):
        return ["参考1", "参考2", "参考3"]


class MockAgent:
    """模拟 Agent"""
    def __init__(self, name="MockAgent"):
        self.name = name
    
    def run(self, data):
        from agents.base import AgentResult
        return AgentResult(
            success=True,
            data=data if isinstance(data, dict) else {"data": data},
            suggestions=["建议1"]
        )
    
    def reset(self):
        pass


# =============================================================================
# BaseCrew 测试
# =============================================================================

class TestBaseCrew:
    """BaseCrew 测试"""
    
    def test_concrete_crew(self):
        """测试具体 Crew 实现"""
        from agents.crews.base import BaseCrew
        from core.task import Task, TaskResult
        
        class TestCrew(BaseCrew):
            CREW_NAME = "test_crew"
            
            def _init_agents(self):
                self.mock_agent = MockAgent()
                self.agents = [self.mock_agent]
            
            def _execute(self, task):
                result = self.mock_agent.run(task.input_data)
                return TaskResult(
                    success=True,
                    output=result.data,
                )
        
        llm = MockLLM()
        crew = TestCrew(llm)
        
        assert crew.CREW_NAME == "test_crew"
        assert len(crew.agents) == 1
    
    def test_run_with_kb(self):
        """测试带知识库的执行"""
        from agents.crews.base import BaseCrew
        from core.task import Task, TaskResult
        
        class TestCrew(BaseCrew):
            CREW_NAME = "test"
            
            def _init_agents(self):
                self.agents = []
            
            def _execute(self, task):
                # 验证 context 被注入
                refs = task.context.get("references", [])
                return TaskResult(success=True, output={"refs_count": len(refs)})
        
        llm = MockLLM()
        kb = MockKnowledgeBase()
        crew = TestCrew(llm, kb)
        
        task = Task(name="test", input_data={"query": "test"})
        result = crew.run(task)
        
        assert result.success is True
        assert result.output["refs_count"] == 3  # MockKB 返回 3 条
    
    def test_run_without_kb(self):
        """测试无知识库的执行"""
        from agents.crews.base import BaseCrew
        from core.task import Task, TaskResult
        
        class TestCrew(BaseCrew):
            CREW_NAME = "test"
            
            def _init_agents(self):
                self.agents = []
            
            def _execute(self, task):
                return TaskResult(success=True, output={"done": True})
        
        llm = MockLLM()
        crew = TestCrew(llm, knowledge_base=None)
        
        task = Task(name="test", input_data={})
        result = crew.run(task)
        
        assert result.success is True
        assert "references" not in task.context
    
    def test_logging(self):
        """测试日志记录"""
        from agents.crews.base import BaseCrew
        from core.task import Task, TaskResult
        
        class TestCrew(BaseCrew):
            CREW_NAME = "log_test"
            
            def _init_agents(self):
                self.agents = []
            
            def _execute(self, task):
                self._log("自定义日志")
                return TaskResult(success=True, output={})
        
        crew = TestCrew(MockLLM())
        result = crew.run(Task(name="test", input_data={}))
        
        assert len(result.logs) >= 2  # 至少有开始和自定义日志
        assert any("自定义日志" in log for log in result.logs)
    
    def test_reset(self):
        """测试重置"""
        from agents.crews.base import BaseCrew
        from core.task import Task, TaskResult
        
        class TestCrew(BaseCrew):
            CREW_NAME = "reset_test"
            
            def _init_agents(self):
                self.mock_agent = MockAgent()
                self.agents = [self.mock_agent]
            
            def _execute(self, task):
                return TaskResult(success=True, output={})
        
        crew = TestCrew(MockLLM())
        crew._logs.append("log1")
        
        crew.reset()
        
        assert len(crew._logs) == 0
    
    def test_exception_handling(self):
        """测试异常处理"""
        from agents.crews.base import BaseCrew
        from core.task import Task, TaskResult
        
        class ErrorCrew(BaseCrew):
            CREW_NAME = "error"
            
            def _init_agents(self):
                self.agents = []
            
            def _execute(self, task):
                raise ValueError("模拟错误")
        
        crew = ErrorCrew(MockLLM())
        result = crew.run(Task(name="error", input_data={}))
        
        assert result.success is False
        assert "模拟错误" in result.error


# =============================================================================
# ResumeCrew 测试
# =============================================================================

class TestResumeCrew:
    """ResumeCrew 测试"""
    
    def test_init(self):
        """测试初始化"""
        from agents.crews.resume.crew import ResumeCrew
        
        llm = MockLLM()
        crew = ResumeCrew(llm)
        
        assert crew.CREW_NAME == "resume"
        assert crew.content_agent is not None
        assert crew.layout_agent is not None
        assert len(crew.agents) == 2
    
    def test_build_retrieval_query_with_projects(self):
        """测试检索查询构建 - 有项目"""
        from agents.crews.resume.crew import ResumeCrew
        from core.task import Task
        
        crew = ResumeCrew(MockLLM())
        
        task = Task(
            name="resume",
            input_data={
                "projects": [{"description": "深度学习图像处理项目"}],
                "skills": ["Python", "PyTorch"]
            }
        )
        
        query = crew._build_retrieval_query(task)
        
        assert "深度学习" in query
    
    def test_build_retrieval_query_with_experience(self):
        """测试检索查询构建 - 有经验"""
        from agents.crews.resume.crew import ResumeCrew
        from core.task import Task
        
        crew = ResumeCrew(MockLLM())
        
        task = Task(
            name="resume",
            input_data={
                "experience": [{"description": "负责后端开发"}],
            }
        )
        
        query = crew._build_retrieval_query(task)
        
        assert "后端" in query
    
    def test_build_retrieval_query_with_skills_only(self):
        """测试检索查询构建 - 只有技能"""
        from agents.crews.resume.crew import ResumeCrew
        from core.task import Task
        
        crew = ResumeCrew(MockLLM())
        
        task = Task(
            name="resume",
            input_data={
                "skills": ["Python", "Java", "Go"]
            }
        )
        
        query = crew._build_retrieval_query(task)
        
        assert "Python" in query


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

