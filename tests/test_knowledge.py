# -*- coding: utf-8 -*-
"""知识库模块测试。

测试内容：
- Document / SearchResult
- BaseKnowledgeBase 接口
- VectorKnowledgeBase（需 Milvus）
"""
import pytest
from unittest.mock import MagicMock, patch
import numpy as np


# =============================================================================
# Document / SearchResult 测试
# =============================================================================

class TestDocument:
    """Document 测试"""
    
    def test_create_document(self):
        """测试创建文档"""
        from core.knowledge import Document
        
        doc = Document(
            text="这是一段测试文本",
            source="test.pdf",
            category="experience"
        )
        
        assert doc.text == "这是一段测试文本"
        assert doc.source == "test.pdf"
        assert doc.category == "experience"
        assert doc.metadata == {}
    
    def test_document_with_metadata(self):
        """测试带元数据的文档"""
        from core.knowledge import Document
        
        doc = Document(
            text="测试",
            source="test.pdf",
            metadata={"page": 1, "author": "test"}
        )
        
        assert doc.metadata["page"] == 1


class TestSearchResult:
    """SearchResult 测试"""
    
    def test_create_result(self):
        """测试创建搜索结果"""
        from core.knowledge import SearchResult
        
        result = SearchResult(
            text="匹配的文本",
            score=0.95,
            source="doc.pdf",
            category="project"
        )
        
        assert result.text == "匹配的文本"
        assert result.score == 0.95
        assert result.source == "doc.pdf"
        assert result.category == "project"


# =============================================================================
# BaseKnowledgeBase 测试
# =============================================================================

class MockKnowledgeBase:
    """模拟知识库实现"""
    
    def __init__(self):
        self._docs = []
    
    def add(self, documents):
        self._docs.extend(documents)
        return len(documents)
    
    def search(self, query, top_k=5, category=None):
        from core.knowledge import SearchResult
        
        results = []
        for doc in self._docs[:top_k]:
            if category is None or doc.category == category:
                results.append(SearchResult(
                    text=doc.text,
                    score=0.9,
                    source=doc.source,
                    category=doc.category,
                ))
        return results
    
    def retrieve_context(self, query, top_k=3):
        results = self.search(query, top_k=top_k)
        return [r.text for r in results]


class TestBaseKnowledgeBase:
    """BaseKnowledgeBase 接口测试"""
    
    def test_add_documents(self):
        """测试添加文档"""
        from core.knowledge import Document
        
        kb = MockKnowledgeBase()
        docs = [
            Document(text="文档1", source="a.pdf", category="exp"),
            Document(text="文档2", source="b.pdf", category="proj"),
        ]
        
        count = kb.add(docs)
        assert count == 2
    
    def test_search(self):
        """测试搜索"""
        from core.knowledge import Document
        
        kb = MockKnowledgeBase()
        kb.add([Document(text="Python项目经验", source="a.pdf", category="exp")])
        
        results = kb.search("Python", top_k=5)
        
        assert len(results) == 1
        assert "Python" in results[0].text
    
    def test_retrieve_context(self):
        """测试检索上下文"""
        from core.knowledge import Document
        
        kb = MockKnowledgeBase()
        kb.add([
            Document(text="经验1", source="a.pdf", category="exp"),
            Document(text="经验2", source="b.pdf", category="exp"),
        ])
        
        context = kb.retrieve_context("经验", top_k=2)
        
        assert len(context) == 2
        assert isinstance(context[0], str)


# =============================================================================
# VectorKnowledgeBase 测试（Mock Milvus）
# =============================================================================

# 需要 pymilvus 的测试
pymilvus = pytest.importorskip("pymilvus", reason="pymilvus not installed")


class TestVectorKnowledgeBase:
    """VectorKnowledgeBase 测试"""
    
    @pytest.fixture
    def mock_milvus(self):
        """模拟 Milvus 客户端"""
        milvus = MagicMock()
        milvus.connect.return_value = None
        milvus.has_collection.return_value = True
        return milvus
    
    @pytest.fixture
    def mock_embedding(self):
        """模拟 Embedding 模型"""
        embedding = MagicMock()
        embedding.dimension = 768
        embedding.encode.return_value = np.random.rand(1, 768)
        return embedding
    
    def test_init(self, mock_milvus, mock_embedding):
        """测试初始化"""
        from knowledge.vector_kb import VectorKnowledgeBase
        
        kb = VectorKnowledgeBase(
            milvus=mock_milvus,
            embedding=mock_embedding,
            collection_name="test_kb"
        )
        
        assert kb.collection_name == "test_kb"
        assert kb._initialized is False
    
    def test_init_connects(self, mock_milvus, mock_embedding):
        """测试初始化时连接"""
        from knowledge.vector_kb import VectorKnowledgeBase
        
        kb = VectorKnowledgeBase(mock_milvus, mock_embedding)
        kb.init()
        
        mock_milvus.connect.assert_called_once()
        assert kb._initialized is True
    
    @patch('pymilvus.Collection')
    def test_add_documents(self, mock_collection_cls, mock_milvus, mock_embedding):
        """测试添加文档"""
        from knowledge.vector_kb import VectorKnowledgeBase
        from core.knowledge import Document
        
        # 设置模拟
        mock_collection = MagicMock()
        mock_collection.insert.return_value = MagicMock(primary_keys=[1, 2])
        mock_collection_cls.return_value = mock_collection
        mock_embedding.encode.return_value = np.random.rand(2, 768)
        
        kb = VectorKnowledgeBase(mock_milvus, mock_embedding)
        kb._initialized = True  # 跳过初始化
        
        docs = [
            Document(text="文本1", source="a.pdf", category="exp"),
            Document(text="文本2", source="b.pdf", category="proj"),
        ]
        
        count = kb.add(docs)
        
        assert count == 2
        mock_collection.insert.assert_called_once()
        mock_collection.flush.assert_called_once()
    
    def test_add_empty_documents(self, mock_milvus, mock_embedding):
        """测试添加空文档列表"""
        from knowledge.vector_kb import VectorKnowledgeBase
        
        kb = VectorKnowledgeBase(mock_milvus, mock_embedding)
        kb._initialized = True
        
        count = kb.add([])
        
        assert count == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

