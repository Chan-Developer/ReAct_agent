# -*- coding: utf-8 -*-
"""pytest 共享 fixtures。"""
import pytest
import sys
from pathlib import Path

# 确保项目根目录在 Python 路径中
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# =============================================================================
# Mock 对象
# =============================================================================

class MockLLM:
    """模拟 LLM"""
    
    def __init__(self, response: str = "mock response"):
        self.response = response
        self.call_count = 0
    
    def chat(self, messages, **kwargs):
        self.call_count += 1
        if isinstance(messages, list):
            return {"content": self.response}
        return self.response


class MockKnowledgeBase:
    """模拟知识库"""
    
    def __init__(self, results=None):
        self._results = results or ["参考1", "参考2", "参考3"]
    
    def retrieve_context(self, query, top_k=3):
        return self._results[:top_k]
    
    def search(self, query, top_k=5, category=None):
        from core.knowledge import SearchResult
        return [
            SearchResult(text=r, score=0.9, source="mock", category="test")
            for r in self._results[:top_k]
        ]


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_llm():
    """提供 Mock LLM"""
    return MockLLM()


@pytest.fixture
def mock_llm_json():
    """提供返回 JSON 的 Mock LLM"""
    import json
    return MockLLM(response=json.dumps({"result": "success"}))


@pytest.fixture
def mock_kb():
    """提供 Mock 知识库"""
    return MockKnowledgeBase()


@pytest.fixture
def sample_resume_data():
    """提供示例简历数据"""
    return {
        "name": "张三",
        "phone": "13800138000",
        "email": "zhangsan@example.com",
        "location": "北京",
        "summary": "5年Python开发经验",
        "education": [
            {
                "school": "清华大学",
                "degree": "硕士",
                "major": "计算机科学",
                "start_date": "2018.09",
                "end_date": "2021.06",
            }
        ],
        "experience": [
            {
                "company": "科技公司",
                "position": "高级工程师",
                "start_date": "2021.07",
                "end_date": "至今",
                "description": "负责后端系统开发",
                "highlights": ["优化系统性能50%", "主导微服务重构"]
            }
        ],
        "projects": [
            {
                "name": "AI平台",
                "role": "技术负责人",
                "description": "企业级AI平台开发",
                "highlights": ["日处理100万请求"],
                "tech_stack": ["Python", "PyTorch", "K8s"]
            }
        ],
        "skills": ["Python", "Go", "PyTorch", "Docker", "K8s"]
    }


@pytest.fixture
def sample_task():
    """提供示例任务"""
    from core.task import Task
    return Task(
        name="test_task",
        input_data={"key": "value"}
    )

