# -*- coding: utf-8 -*-
"""核心模块测试。

测试内容：
- Task / TaskResult
- Orchestrator
"""
import pytest
from unittest.mock import MagicMock, patch


# =============================================================================
# Task / TaskResult 测试
# =============================================================================

class TestTask:
    """Task 测试"""
    
    def test_create_task(self):
        """测试创建任务"""
        from core.task import Task
        
        task = Task(
            name="test_task",
            input_data={"key": "value"}
        )
        
        assert task.name == "test_task"
        assert task.input_data == {"key": "value"}
        assert task.context == {}
        assert task.metadata == {}
    
    def test_task_with_context(self):
        """测试带上下文的任务"""
        from core.task import Task
        
        task = Task(
            name="rag_task",
            input_data={"query": "test"},
            context={"references": ["ref1", "ref2"]},
        )
        
        assert len(task.context["references"]) == 2


class TestTaskResult:
    """TaskResult 测试"""
    
    def test_success_result(self):
        """测试成功结果"""
        from core.task import TaskResult
        
        result = TaskResult(
            success=True,
            output={"data": "test"},
            suggestions=["suggestion1"],
        )
        
        assert result.success is True
        assert result.output["data"] == "test"
        assert len(result.suggestions) == 1
        assert result.error is None
    
    def test_failure_result(self):
        """测试失败结果"""
        from core.task import TaskResult
        
        result = TaskResult(
            success=False,
            output=None,
            error="Something went wrong",
        )
        
        assert result.success is False
        assert result.output is None
        assert result.error == "Something went wrong"


# =============================================================================
# Orchestrator 测试
# =============================================================================

class MockLLM:
    """模拟 LLM"""
    def chat(self, messages, **kwargs):
        return {"content": "mock response"}


class MockCrew:
    """模拟 Crew"""
    CREW_NAME = "mock_crew"
    
    def __init__(self, llm, knowledge_base=None):
        self.llm = llm
        self.kb = knowledge_base
    
    def run(self, task):
        from core.task import TaskResult
        return TaskResult(success=True, output={"processed": True})


class TestOrchestrator:
    """Orchestrator 测试"""
    
    def test_init(self):
        """测试初始化"""
        from core.orchestrator import Orchestrator
        
        llm = MockLLM()
        orchestrator = Orchestrator(llm)
        
        assert orchestrator.llm == llm
        assert orchestrator.kb is None
        assert len(orchestrator._crew_registry) == 0
    
    def test_register_crew(self):
        """测试注册 Crew"""
        from core.orchestrator import Orchestrator
        
        llm = MockLLM()
        orchestrator = Orchestrator(llm)
        
        orchestrator.register(MockCrew)
        
        assert "mock_crew" in orchestrator.list_crews()
    
    def test_register_with_custom_names(self):
        """测试使用自定义名称注册"""
        from core.orchestrator import Orchestrator
        
        llm = MockLLM()
        orchestrator = Orchestrator(llm)
        
        orchestrator.register(MockCrew, task_names=["task_a", "task_b"])
        
        assert "task_a" in orchestrator.list_crews()
        assert "task_b" in orchestrator.list_crews()
    
    def test_run_task(self):
        """测试执行任务"""
        from core.orchestrator import Orchestrator
        from core.task import Task
        
        llm = MockLLM()
        orchestrator = Orchestrator(llm)
        orchestrator.register(MockCrew)
        
        task = Task(name="mock_crew", input_data={"test": True})
        result = orchestrator.run(task)
        
        assert result.success is True
        assert result.output["processed"] is True
    
    def test_run_unregistered_task(self):
        """测试执行未注册的任务"""
        from core.orchestrator import Orchestrator
        from core.task import Task
        
        llm = MockLLM()
        orchestrator = Orchestrator(llm)
        
        task = Task(name="unknown", input_data={})
        result = orchestrator.run(task)
        
        assert result.success is False
        assert "未找到" in result.error
    
    def test_crew_instance_caching(self):
        """测试 Crew 实例缓存"""
        from core.orchestrator import Orchestrator
        from core.task import Task
        
        llm = MockLLM()
        orchestrator = Orchestrator(llm)
        orchestrator.register(MockCrew)
        
        # 执行两次，应该使用同一个 Crew 实例
        task1 = Task(name="mock_crew", input_data={})
        task2 = Task(name="mock_crew", input_data={})
        
        orchestrator.run(task1)
        orchestrator.run(task2)
        
        # 只有一个实例
        assert len(orchestrator._crew_instances) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

