# -*- coding: utf-8 -*-
"""记忆系统测试模块。

测试内容：
- MemoryItem / MemoryType 数据结构
- ShortTermMemory (Redis)
- LongTermMemory (Milvus)
- MemoryManager 统一管理
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
import json


# =============================================================================
# MemoryItem / MemoryType 测试
# =============================================================================

class TestMemoryType:
    """MemoryType 枚举测试"""
    
    def test_memory_types(self):
        """测试记忆类型"""
        from memory.base import MemoryType
        
        assert MemoryType.CONVERSATION.value == "conversation"
        assert MemoryType.TASK.value == "task"
        assert MemoryType.KNOWLEDGE.value == "knowledge"
        assert MemoryType.EXPERIENCE.value == "experience"
        assert MemoryType.USER_PREFERENCE.value == "user_pref"


class TestMemoryItem:
    """MemoryItem 测试"""
    
    def test_create_memory_item(self):
        """测试创建记忆项"""
        from memory.base import MemoryItem, MemoryType
        
        item = MemoryItem(
            content="用户询问了 Python 语法",
            memory_type=MemoryType.CONVERSATION,
            importance=0.5,
        )
        
        assert item.content == "用户询问了 Python 语法"
        assert item.memory_type == MemoryType.CONVERSATION
        assert item.importance == 0.5
        assert item.session_id is None
    
    def test_memory_item_id(self):
        """测试记忆项 ID 生成"""
        from memory.base import MemoryItem, MemoryType
        
        item = MemoryItem(
            content="测试内容",
            memory_type=MemoryType.TASK,
        )
        
        # ID 应该是 16 字符的 MD5 哈希
        assert len(item.id) == 16
        assert item.id.isalnum()
    
    def test_memory_item_to_dict(self):
        """测试转为字典"""
        from memory.base import MemoryItem, MemoryType
        
        item = MemoryItem(
            content="测试",
            memory_type=MemoryType.KNOWLEDGE,
            importance=0.8,
            session_id="session_001",
        )
        
        data = item.to_dict()
        
        assert data["content"] == "测试"
        assert data["memory_type"] == "knowledge"
        assert data["importance"] == 0.8
        assert data["session_id"] == "session_001"
        assert "id" in data
        assert "timestamp" in data
    
    def test_memory_item_from_dict(self):
        """测试从字典创建"""
        from memory.base import MemoryItem, MemoryType
        
        data = {
            "content": "测试内容",
            "memory_type": "experience",
            "timestamp": "2024-01-01T12:00:00",
            "importance": 0.7,
            "session_id": "s001",
            "metadata": {"key": "value"},
        }
        
        item = MemoryItem.from_dict(data)
        
        assert item.content == "测试内容"
        assert item.memory_type == MemoryType.EXPERIENCE
        assert item.importance == 0.7
        assert item.metadata["key"] == "value"
    
    def test_memory_item_json_serialization(self):
        """测试 JSON 序列化"""
        from memory.base import MemoryItem, MemoryType
        
        item = MemoryItem(
            content="JSON 测试",
            memory_type=MemoryType.CONVERSATION,
        )
        
        json_str = item.to_json()
        restored = MemoryItem.from_json(json_str)
        
        assert restored.content == item.content
        assert restored.memory_type == item.memory_type
    
    def test_memory_type_auto_convert(self):
        """测试字符串自动转换为 MemoryType"""
        from memory.base import MemoryItem, MemoryType
        
        item = MemoryItem(
            content="测试",
            memory_type="conversation",  # 字符串
        )
        
        assert item.memory_type == MemoryType.CONVERSATION


class TestMemorySearchResult:
    """MemorySearchResult 测试"""
    
    def test_create_search_result(self):
        """测试创建搜索结果"""
        from memory.base import MemoryItem, MemoryType, MemorySearchResult
        
        item = MemoryItem(content="测试", memory_type=MemoryType.TASK)
        result = MemorySearchResult(item=item, score=0.95, source="short_term")
        
        assert result.item.content == "测试"
        assert result.score == 0.95
        assert result.source == "short_term"


# =============================================================================
# ShortTermMemory 测试 (Mock Redis)
# =============================================================================

class TestShortTermMemory:
    """ShortTermMemory 测试"""
    
    @pytest.fixture
    def mock_redis_client(self):
        """模拟 Redis 客户端"""
        redis_mock = MagicMock()
        redis_mock.ping.return_value = True
        redis_mock.setex.return_value = True
        redis_mock.get.return_value = None
        redis_mock.zadd.return_value = 1
        redis_mock.zcard.return_value = 1
        redis_mock.zrevrange.return_value = []
        redis_mock.zrange.return_value = []
        redis_mock.delete.return_value = 1
        redis_mock.expire.return_value = True
        return redis_mock
    
    def test_init(self):
        """测试初始化参数"""
        from memory.short_term import ShortTermMemory
        
        memory = ShortTermMemory(host="localhost", port=6379, ttl=3600)
        
        assert memory.host == "localhost"
        assert memory.port == 6379
        assert memory.ttl == 3600
        assert memory._client is None  # 懒加载
    
    def test_add_memory(self, mock_redis_client):
        """测试添加记忆"""
        from memory.short_term import ShortTermMemory
        from memory.base import MemoryItem, MemoryType
        
        memory = ShortTermMemory()
        memory._client = mock_redis_client  # 注入 mock
        
        item = MemoryItem(
            content="测试记忆",
            memory_type=MemoryType.CONVERSATION,
            session_id="test_session",
        )
        
        result = memory.add(item)
        
        assert result is True
        mock_redis_client.setex.assert_called_once()
        mock_redis_client.zadd.assert_called_once()
    
    def test_get_memory(self, mock_redis_client):
        """测试获取记忆"""
        from memory.short_term import ShortTermMemory
        from memory.base import MemoryItem, MemoryType
        
        # 准备模拟数据
        item = MemoryItem(
            content="测试",
            memory_type=MemoryType.TASK,
        )
        mock_redis_client.get.return_value = item.to_json()
        
        memory = ShortTermMemory()
        memory._client = mock_redis_client
        
        result = memory.get("test_id")
        
        assert result is not None
        assert result.content == "测试"
    
    def test_get_nonexistent_memory(self, mock_redis_client):
        """测试获取不存在的记忆"""
        from memory.short_term import ShortTermMemory
        
        mock_redis_client.get.return_value = None
        
        memory = ShortTermMemory()
        memory._client = mock_redis_client
        
        result = memory.get("nonexistent_id")
        
        assert result is None
    
    def test_search_memory(self, mock_redis_client):
        """测试搜索记忆"""
        from memory.short_term import ShortTermMemory
        from memory.base import MemoryItem, MemoryType
        
        # 准备模拟数据
        item = MemoryItem(
            content="Python 是一种编程语言",
            memory_type=MemoryType.KNOWLEDGE,
            importance=0.7,
        )
        mock_redis_client.zrevrange.return_value = [item.id]
        mock_redis_client.get.return_value = item.to_json()
        
        memory = ShortTermMemory()
        memory._client = mock_redis_client
        
        results = memory.search("Python", top_k=5)
        
        assert len(results) == 1
        assert "Python" in results[0].item.content
        assert results[0].source == "short_term"
    
    def test_search_no_results(self, mock_redis_client):
        """测试搜索无结果"""
        from memory.short_term import ShortTermMemory
        
        mock_redis_client.zrevrange.return_value = []
        
        memory = ShortTermMemory()
        memory._client = mock_redis_client
        
        results = memory.search("不存在的查询")
        
        assert len(results) == 0
    
    def test_get_recent(self, mock_redis_client):
        """测试获取最近记忆"""
        from memory.short_term import ShortTermMemory
        from memory.base import MemoryItem, MemoryType
        
        item = MemoryItem(content="最近的记忆", memory_type=MemoryType.CONVERSATION)
        mock_redis_client.zrevrange.return_value = [item.id]
        mock_redis_client.get.return_value = item.to_json()
        
        memory = ShortTermMemory()
        memory._client = mock_redis_client
        
        results = memory.get_recent(n=5)
        
        assert len(results) == 1
        assert results[0].content == "最近的记忆"
    
    def test_delete_memory(self, mock_redis_client):
        """测试删除记忆"""
        from memory.short_term import ShortTermMemory
        
        mock_redis_client.delete.return_value = 1
        
        memory = ShortTermMemory()
        memory._client = mock_redis_client
        
        result = memory.delete("test_id")
        
        assert result is True
    
    def test_clear_session(self, mock_redis_client):
        """测试清空会话"""
        from memory.short_term import ShortTermMemory
        
        mock_redis_client.zrange.return_value = ["id1", "id2"]
        mock_redis_client.delete.return_value = 1
        
        memory = ShortTermMemory()
        memory._client = mock_redis_client
        
        count = memory.clear("test_session")
        
        assert count == 2
    
    def test_count(self, mock_redis_client):
        """测试计数"""
        from memory.short_term import ShortTermMemory
        
        mock_redis_client.zcard.return_value = 10
        
        memory = ShortTermMemory()
        memory._client = mock_redis_client
        
        count = memory.count("test_session")
        
        assert count == 10


# =============================================================================
# LongTermMemory 测试 (Mock Milvus)
# =============================================================================

class TestLongTermMemory:
    """LongTermMemory 测试"""
    
    @pytest.fixture
    def mock_embedding(self):
        """模拟 Embedding 模型"""
        import numpy as np
        embedding = MagicMock()
        embedding.dimension = 768
        embedding.encode.return_value = np.random.rand(768)
        return embedding
    
    def test_init(self, mock_embedding):
        """测试初始化"""
        from memory.long_term import LongTermMemory
        
        memory = LongTermMemory(
            host="localhost",
            port=19530,
            embedding=mock_embedding,
        )
        
        assert memory.host == "localhost"
        assert memory.port == 19530
        assert memory._initialized is False
    
    def test_skip_low_importance(self, mock_embedding):
        """测试跳过低重要性记忆"""
        from memory.long_term import LongTermMemory
        from memory.base import MemoryItem, MemoryType
        
        memory = LongTermMemory(embedding=mock_embedding, importance_threshold=0.5)
        memory._initialized = True
        
        item = MemoryItem(
            content="不重要的记忆",
            memory_type=MemoryType.CONVERSATION,
            importance=0.3,  # 低于阈值
        )
        
        result = memory.add(item)
        
        assert result is False
    
    def test_add_without_embedding(self):
        """测试无嵌入模型时添加"""
        from memory.long_term import LongTermMemory
        from memory.base import MemoryItem, MemoryType
        
        memory = LongTermMemory(embedding=None)
        memory._initialized = True
        
        item = MemoryItem(
            content="测试",
            memory_type=MemoryType.KNOWLEDGE,
            importance=0.8,
        )
        
        result = memory.add(item)
        
        assert result is False  # 应该失败
    
    def test_add_important_memory_with_mock(self, mock_embedding):
        """测试添加重要记忆（使用注入的 mock）"""
        from memory.long_term import LongTermMemory
        from memory.base import MemoryItem, MemoryType
        
        mock_collection = MagicMock()
        
        memory = LongTermMemory(embedding=mock_embedding, importance_threshold=0.5)
        memory._initialized = True
        memory._collection = mock_collection
        
        item = MemoryItem(
            content="重要经验",
            memory_type=MemoryType.EXPERIENCE,
            importance=0.8,  # 高于阈值
        )
        
        result = memory.add(item)
        
        assert result is True
        mock_collection.insert.assert_called_once()


# =============================================================================
# MemoryManager 测试
# =============================================================================

class TestMemoryManager:
    """MemoryManager 测试"""
    
    @pytest.fixture
    def mock_short_term(self):
        """模拟短期记忆"""
        st = MagicMock()
        st.add.return_value = True
        st.search.return_value = []
        st.get_recent.return_value = []
        st.clear.return_value = 0
        st.count.return_value = 0
        return st
    
    @pytest.fixture
    def mock_long_term(self):
        """模拟长期记忆"""
        lt = MagicMock()
        lt.add.return_value = True
        lt.search.return_value = []
        lt.count.return_value = 0
        return lt
    
    @patch("memory.manager.ShortTermMemory")
    @patch("memory.manager.LongTermMemory")
    def test_init(self, mock_lt_cls, mock_st_cls, mock_short_term, mock_long_term):
        """测试初始化"""
        from memory.manager import MemoryManager
        
        mock_st_cls.return_value = mock_short_term
        mock_lt_cls.return_value = mock_long_term
        
        manager = MemoryManager(
            redis_host="localhost",
            milvus_host="localhost",
        )
        
        assert manager.session_id is not None
        assert manager.long_term_threshold == 0.6
    
    @patch("memory.manager.ShortTermMemory")
    @patch("memory.manager.LongTermMemory")
    def test_add_low_importance(self, mock_lt_cls, mock_st_cls, mock_short_term, mock_long_term):
        """测试添加低重要性记忆（只存短期）"""
        from memory.manager import MemoryManager
        from memory.base import MemoryItem, MemoryType
        
        mock_st_cls.return_value = mock_short_term
        mock_lt_cls.return_value = mock_long_term
        
        manager = MemoryManager(long_term_threshold=0.6)
        
        item = MemoryItem(
            content="普通对话",
            memory_type=MemoryType.CONVERSATION,
            importance=0.3,  # 低于阈值
        )
        
        manager.add(item)
        
        mock_short_term.add.assert_called_once()
        mock_long_term.add.assert_not_called()
    
    @patch("memory.manager.ShortTermMemory")
    @patch("memory.manager.LongTermMemory")
    def test_add_high_importance(self, mock_lt_cls, mock_st_cls, mock_short_term, mock_long_term):
        """测试添加高重要性记忆（存入长期）"""
        from memory.manager import MemoryManager
        from memory.base import MemoryItem, MemoryType
        
        mock_st_cls.return_value = mock_short_term
        mock_lt_cls.return_value = mock_long_term
        
        manager = MemoryManager(long_term_threshold=0.6)
        
        item = MemoryItem(
            content="重要经验",
            memory_type=MemoryType.EXPERIENCE,
            importance=0.8,  # 高于阈值
        )
        
        manager.add(item)
        
        mock_short_term.add.assert_called_once()
        mock_long_term.add.assert_called_once()
    
    @patch("memory.manager.ShortTermMemory")
    @patch("memory.manager.LongTermMemory")
    def test_add_conversation(self, mock_lt_cls, mock_st_cls, mock_short_term, mock_long_term):
        """测试添加对话记忆"""
        from memory.manager import MemoryManager
        
        mock_st_cls.return_value = mock_short_term
        mock_lt_cls.return_value = mock_long_term
        
        manager = MemoryManager()
        result = manager.add_conversation("user", "你好")
        
        assert result is True
        mock_short_term.add.assert_called_once()
    
    @patch("memory.manager.ShortTermMemory")
    @patch("memory.manager.LongTermMemory")
    def test_add_task_result(self, mock_lt_cls, mock_st_cls, mock_short_term, mock_long_term):
        """测试添加任务结果"""
        from memory.manager import MemoryManager
        
        mock_st_cls.return_value = mock_short_term
        mock_lt_cls.return_value = mock_long_term
        
        manager = MemoryManager()
        result = manager.add_task_result(
            task="计算 1+1",
            result="2",
            success=True,
        )
        
        assert result is True
    
    @patch("memory.manager.ShortTermMemory")
    @patch("memory.manager.LongTermMemory")
    def test_add_experience(self, mock_lt_cls, mock_st_cls, mock_short_term, mock_long_term):
        """测试添加经验"""
        from memory.manager import MemoryManager
        
        mock_st_cls.return_value = mock_short_term
        mock_lt_cls.return_value = mock_long_term
        
        manager = MemoryManager()
        result = manager.add_experience("用户喜欢简洁代码", importance=0.8)
        
        assert result is True
        # 经验重要性高，应该存入长期
        mock_long_term.add.assert_called_once()
    
    @patch("memory.manager.ShortTermMemory")
    @patch("memory.manager.LongTermMemory")
    def test_search(self, mock_lt_cls, mock_st_cls, mock_short_term, mock_long_term):
        """测试统一搜索"""
        from memory.manager import MemoryManager
        from memory.base import MemoryItem, MemoryType, MemorySearchResult
        
        # 准备模拟搜索结果
        item1 = MemoryItem(content="短期结果", memory_type=MemoryType.CONVERSATION)
        item2 = MemoryItem(content="长期结果", memory_type=MemoryType.EXPERIENCE)
        
        mock_short_term.search.return_value = [
            MemorySearchResult(item=item1, score=0.8, source="short_term")
        ]
        mock_long_term.search.return_value = [
            MemorySearchResult(item=item2, score=0.9, source="long_term")
        ]
        
        mock_st_cls.return_value = mock_short_term
        mock_lt_cls.return_value = mock_long_term
        
        manager = MemoryManager(embedding=MagicMock())
        results = manager.search("测试查询")
        
        assert len(results) == 2
        # 应该按分数排序，长期结果在前
        assert results[0].source == "long_term"
    
    @patch("memory.manager.ShortTermMemory")
    @patch("memory.manager.LongTermMemory")
    def test_get_context(self, mock_lt_cls, mock_st_cls, mock_short_term, mock_long_term):
        """测试获取上下文"""
        from memory.manager import MemoryManager
        from memory.base import MemoryItem, MemoryType
        
        recent_item = MemoryItem(content="[user] 你好", memory_type=MemoryType.CONVERSATION)
        mock_short_term.get_recent.return_value = [recent_item]
        mock_short_term.search.return_value = []
        mock_long_term.search.return_value = []
        
        mock_st_cls.return_value = mock_short_term
        mock_lt_cls.return_value = mock_long_term
        
        manager = MemoryManager()
        context = manager.get_context("查询", max_items=3, include_recent=1)
        
        assert "最近对话" in context
        assert "你好" in context
    
    @patch("memory.manager.ShortTermMemory")
    @patch("memory.manager.LongTermMemory")
    def test_new_session(self, mock_lt_cls, mock_st_cls, mock_short_term, mock_long_term):
        """测试新建会话"""
        from memory.manager import MemoryManager
        
        mock_st_cls.return_value = mock_short_term
        mock_lt_cls.return_value = mock_long_term
        
        manager = MemoryManager()
        old_session = manager.session_id
        
        new_session = manager.new_session()
        
        assert new_session != old_session
        assert manager.session_id == new_session
    
    @patch("memory.manager.ShortTermMemory")
    @patch("memory.manager.LongTermMemory")
    def test_clear_session(self, mock_lt_cls, mock_st_cls, mock_short_term, mock_long_term):
        """测试清空会话"""
        from memory.manager import MemoryManager
        
        mock_short_term.clear.return_value = 5
        mock_st_cls.return_value = mock_short_term
        mock_lt_cls.return_value = mock_long_term
        
        manager = MemoryManager()
        count = manager.clear_session()
        
        assert count == 5
        mock_short_term.clear.assert_called_once()
    
    @patch("memory.manager.ShortTermMemory")
    @patch("memory.manager.LongTermMemory")
    def test_stats(self, mock_lt_cls, mock_st_cls, mock_short_term, mock_long_term):
        """测试统计信息"""
        from memory.manager import MemoryManager
        
        mock_short_term.count.return_value = 10
        mock_long_term.count.return_value = 5
        
        mock_st_cls.return_value = mock_short_term
        mock_lt_cls.return_value = mock_long_term
        
        manager = MemoryManager()
        stats = manager.stats()
        
        assert "session_id" in stats
        assert stats["short_term_count"] == 10
        assert stats["long_term_count"] == 5


# =============================================================================
# 集成测试 (需要真实 Redis)
# =============================================================================

class TestShortTermMemoryIntegration:
    """短期记忆集成测试（需要 Redis）"""
    
    @pytest.mark.skipif(
        True,  # 默认跳过，设为 False 以运行
        reason="跳过需要 Redis 的集成测试"
    )
    def test_real_redis_operations(self):
        """真实 Redis 操作测试"""
        from memory import ShortTermMemory, MemoryItem, MemoryType
        
        memory = ShortTermMemory(host="localhost", port=6379)
        session_id = "integration_test"
        
        try:
            # 添加
            item = MemoryItem(
                content="集成测试记忆",
                memory_type=MemoryType.CONVERSATION,
                session_id=session_id,
            )
            assert memory.add(item) is True
            
            # 获取
            retrieved = memory.get(item.id)
            assert retrieved is not None
            assert retrieved.content == "集成测试记忆"
            
            # 搜索
            results = memory.search("集成测试", session_id=session_id)
            assert len(results) >= 1
            
            # 计数
            count = memory.count(session_id)
            assert count >= 1
            
        finally:
            # 清理
            memory.clear(session_id)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
