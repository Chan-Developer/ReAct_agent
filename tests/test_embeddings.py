# -*- coding: utf-8 -*-
"""Embedding 模块测试。

测试内容：
- EmbeddingModel 本地模式
- EmbeddingModel API 模式
"""
import pytest
from unittest.mock import MagicMock, patch
import numpy as np

# 跳过需要 sentence_transformers 的测试
st = pytest.importorskip("sentence_transformers", reason="sentence_transformers not installed")


# =============================================================================
# EmbeddingModel 测试
# =============================================================================

class TestEmbeddingModel:
    """EmbeddingModel 测试"""
    
    def test_init_local(self):
        """测试本地模式初始化"""
        from embeddings import EmbeddingModel
        
        model = EmbeddingModel(
            model_name="test-model",
            use_local=True
        )
        
        assert model.model_name == "test-model"
        assert model.use_local is True
        assert model._model is None  # 延迟初始化
    
    def test_init_api(self):
        """测试 API 模式初始化"""
        from embeddings import EmbeddingModel
        
        model = EmbeddingModel(
            model_name="test-model",
            use_local=False,
            api_base="http://localhost:8001"
        )
        
        assert model.use_local is False
        assert model.api_base == "http://localhost:8001"
    
    @patch('sentence_transformers.SentenceTransformer')
    def test_local_encode(self, mock_st_cls):
        """测试本地编码"""
        from embeddings import EmbeddingModel
        
        # 设置模拟
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 768
        mock_model.encode.return_value = np.random.rand(2, 768)
        mock_st_cls.return_value = mock_model
        
        model = EmbeddingModel(use_local=True)
        
        result = model.encode(["文本1", "文本2"])
        
        assert result.shape == (2, 768)
        mock_model.encode.assert_called_once()
    
    @patch('sentence_transformers.SentenceTransformer')
    def test_local_encode_single_text(self, mock_st_cls):
        """测试单文本编码"""
        from embeddings import EmbeddingModel
        
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 768
        mock_model.encode.return_value = np.random.rand(1, 768)
        mock_st_cls.return_value = mock_model
        
        model = EmbeddingModel(use_local=True)
        
        result = model.encode("单个文本")
        
        assert result.shape == (1, 768)
    
    @patch('sentence_transformers.SentenceTransformer')
    def test_dimension_property(self, mock_st_cls):
        """测试 dimension 属性"""
        from embeddings import EmbeddingModel
        
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 1024
        mock_st_cls.return_value = mock_model
        
        model = EmbeddingModel(use_local=True)
        
        dim = model.dimension
        
        assert dim == 1024
    
    @patch('requests.post')
    def test_api_encode(self, mock_post):
        """测试 API 编码"""
        from embeddings import EmbeddingModel
        
        # 模拟 API 响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {"index": 0, "embedding": [0.1] * 768},
                {"index": 1, "embedding": [0.2] * 768},
            ]
        }
        mock_post.return_value = mock_response
        
        model = EmbeddingModel(
            use_local=False,
            api_base="http://localhost:8001"
        )
        model._model = "api"  # 跳过初始化
        model._dimension = 768
        
        result = model.encode(["文本1", "文本2"], normalize=False)
        
        assert result.shape == (2, 768)
        mock_post.assert_called()
    
    @patch('requests.post')
    def test_api_connection_error(self, mock_post):
        """测试 API 连接错误"""
        from embeddings import EmbeddingModel
        import requests
        
        mock_post.side_effect = requests.exceptions.ConnectionError("无法连接")
        
        model = EmbeddingModel(
            use_local=False,
            api_base="http://localhost:9999"
        )
        
        with pytest.raises(RuntimeError) as exc_info:
            model._init_model()
        
        assert "无法连接" in str(exc_info.value) or "Embedding" in str(exc_info.value)
    
    @patch('sentence_transformers.SentenceTransformer')
    def test_normalize_embeddings(self, mock_st_cls):
        """测试归一化"""
        from embeddings import EmbeddingModel
        
        # 返回未归一化的向量
        raw_embeddings = np.array([[3.0, 4.0]])  # 范数 = 5
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 2
        mock_model.encode.return_value = raw_embeddings
        mock_st_cls.return_value = mock_model
        
        model = EmbeddingModel(use_local=True)
        
        result = model.encode(["测试"], normalize=True)
        
        # 归一化后范数应为 1
        # 注意: sentence-transformers 的 encode 方法自己处理 normalize
        mock_model.encode.assert_called_with(
            ["测试"],
            normalize_embeddings=True,
            show_progress_bar=False,
        )


class TestEmbeddingModelEdgeCases:
    """EmbeddingModel 边界情况测试"""
    
    @patch('sentence_transformers.SentenceTransformer')
    def test_empty_input(self, mock_st_cls):
        """测试空输入"""
        from embeddings import EmbeddingModel
        
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 768
        mock_model.encode.return_value = np.array([]).reshape(0, 768)
        mock_st_cls.return_value = mock_model
        
        model = EmbeddingModel(use_local=True)
        
        result = model.encode([])
        
        assert result.shape[0] == 0
    
    @patch('sentence_transformers.SentenceTransformer')
    def test_lazy_init(self, mock_st_cls):
        """测试延迟初始化"""
        from embeddings import EmbeddingModel
        
        model = EmbeddingModel(use_local=True)
        
        # 初始化时不应调用 SentenceTransformer
        mock_st_cls.assert_not_called()
        
        # 访问 dimension 时应初始化
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 768
        mock_st_cls.return_value = mock_model
        
        _ = model.dimension
        
        mock_st_cls.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

