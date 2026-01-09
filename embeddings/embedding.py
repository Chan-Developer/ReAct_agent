# -*- coding: utf-8 -*-
"""Embedding 模型封装。"""
from typing import List, Union, TYPE_CHECKING
import numpy as np
import requests

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    """文本嵌入模型封装。
    
    支持多种后端：
    - sentence-transformers (本地)
    - ModelScope API
    """
    
    def __init__(
        self,
        model_name: str = "",
        use_local: bool = True,
        api_base: str = "http://localhost:8001",
    ):
        self.model_name = model_name
        self.use_local = use_local
        self._model = None
        self._dimension = None
        self.api_base = api_base
    
    def _init_model(self):
        """延迟初始化模型"""
        if self._model is not None:
            return
        
        if self.use_local:
            # 延迟导入，避免未安装时报错
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
            self._dimension = self._model.get_sentence_embedding_dimension()
        else:
            # 使用 API 模式
            self._model = "api"
            test_embedding = self._call_api(["test"])
            self._dimension = len(test_embedding[0])

    
    def _call_api(self, texts: List[str]) -> List[List[float]]:
        """调用 vLLM Embedding API（OpenAI 兼容格式）"""
        
        url = f"{self.api_base}/v1/embeddings"
        payload = {
            "model": self.model_name,
            "input": texts,
        }
        
        try:
            resp = requests.post(url, json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            
            # 按 index 排序，提取 embedding
            embeddings = sorted(data["data"], key=lambda x: x["index"])
            return [item["embedding"] for item in embeddings]
            
        except requests.exceptions.ConnectionError:
            raise RuntimeError(f"无法连接到 Embedding 服务: {url}")
        except Exception as e:
            raise RuntimeError(f"Embedding API 调用失败: {e}")
    
    @property
    def dimension(self) -> int:
        """获取向量维度"""
        self._init_model()
        return self._dimension
    
    def encode(
        self,
        texts: Union[str, List[str]],
        normalize: bool = True,
    ) -> np.ndarray:
        """将文本编码为向量
        
        Args:
            texts: 单个文本或文本列表
            normalize: 是否归一化
            
        Returns:
            向量数组 [n_texts, dimension]
        """
        self._init_model()
        
        if isinstance(texts, str):
            texts = [texts]
        
        if self.use_local:
            embeddings = self._model.encode(
                texts,
                normalize_embeddings=normalize,
                show_progress_bar=False,
            )
        else:
            embeddings = np.array(self._call_api(texts))
            if normalize: # L2 归一化
                embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

        return embeddings

if __name__ == "__main__":
    # embedding_model = EmbeddingModel(model_name="/data/clj/Model/qwen3-8b-embedding", use_local=True)
    # print(embedding_model.dimension)
    # print(embedding_model.encode("你好"))
    
    # served_model_name
    embedding_model = EmbeddingModel(model_name="/data/clj/Model/qwen3-8b-embedding", use_local=False, api_base="http://0.0.0.0:9300")
    print(embedding_model.dimension)
    print(embedding_model.encode("你好"))