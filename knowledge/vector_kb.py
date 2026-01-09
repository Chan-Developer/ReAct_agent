# -*- coding: utf-8 -*-
"""向量知识库实现。"""
from typing import List, Optional, TYPE_CHECKING

from core.knowledge import BaseKnowledgeBase, Document, SearchResult
from common.logger import get_logger

if TYPE_CHECKING:
    from storage import MilvusClient
    from embeddings import EmbeddingModel

logger = get_logger(__name__)


class VectorKnowledgeBase(BaseKnowledgeBase):
    """基于向量数据库的知识库
    
    Usage:
        from storage import MilvusClient
        from embeddings import EmbeddingModel
        from knowledge import VectorKnowledgeBase
        
        kb = VectorKnowledgeBase(
            milvus=MilvusClient(),
            embedding=EmbeddingModel(),
            collection_name="my_kb"
        )
        kb.init()
        kb.add([Document(text="...", category="...")])
        results = kb.search("query")
    """
    
    def __init__(
        self,
        milvus: "MilvusClient",
        embedding: "EmbeddingModel",
        collection_name: str = "knowledge_base",
    ):
        self.milvus = milvus
        self.embedding = embedding
        self.collection_name = collection_name
        self._initialized = False
    
    def init(self):
        """初始化知识库（连接 + 创建集合）"""
        if self._initialized:
            return
        
        self.milvus.connect()
        
        if not self.milvus.has_collection(self.collection_name):
            self._create_collection()
        
        self._initialized = True
        logger.info(f"[VectorKB] 初始化完成: {self.collection_name}")
    
    def _create_collection(self):
        """创建集合"""
        from pymilvus import FieldSchema, CollectionSchema, DataType, Collection
        
        dim = self.embedding.dimension
        
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=dim),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=512),
            FieldSchema(name="category", dtype=DataType.VARCHAR, max_length=64),
        ]
        
        schema = CollectionSchema(fields, description=f"Knowledge Base: {self.collection_name}")
        collection = Collection(self.collection_name, schema)
        
        # 创建索引
        collection.create_index(
            field_name="vector",
            index_params={
                "metric_type": "COSINE",
                "index_type": "HNSW",
                "params": {"M": 16, "efConstruction": 256}
            }
        )
        logger.info(f"[VectorKB] 创建集合: {self.collection_name}, dim={dim}")
    
    def add(self, documents: List[Document]) -> int:
        """添加文档"""
        self.init()
        
        if not documents:
            return 0
        
        from pymilvus import Collection
        
        texts = [d.text for d in documents]
        vectors = self.embedding.encode(texts).tolist()
        
        collection = Collection(self.collection_name)
        
        data = [
            vectors,
            texts,
            [d.source for d in documents],
            [d.category for d in documents],
        ]
        
        result = collection.insert(data)
        collection.flush()
        
        count = len(result.primary_keys)
        logger.info(f"[VectorKB] 添加 {count} 条文档")
        return count
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        category: Optional[str] = None,
    ) -> List[SearchResult]:
        """检索文档"""
        self.init()
        
        from pymilvus import Collection
        
        vector = self.embedding.encode(query).tolist()
        
        collection = Collection(self.collection_name)
        collection.load()
        
        expr = f'category == "{category}"' if category else None
        
        results = collection.search(
            data=[vector],
            anns_field="vector",
            param={"metric_type": "COSINE", "params": {"ef": 64}},
            limit=top_k,
            expr=expr,
            output_fields=["text", "source", "category"],
        )
        
        output = []
        for hits in results:
            for hit in hits:
                output.append(SearchResult(
                    text=hit.entity.get("text"),
                    source=hit.entity.get("source", ""),
                    category=hit.entity.get("category", ""),
                    score=hit.distance,
                ))
        
        return output
    
    def count(self) -> int:
        """获取文档数量"""
        self.init()
        from pymilvus import Collection
        collection = Collection(self.collection_name)
        return collection.num_entities

