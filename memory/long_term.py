# -*- coding: utf-8 -*-
"""长期记忆实现 - 基于 Milvus 向量数据库。

特点：
- 语义搜索，根据含义检索相关记忆
- 持久化存储，永久保存重要经验
- 适合存储学到的知识、经验总结
"""
from typing import List, Optional, TYPE_CHECKING
from datetime import datetime

from common.logger import get_logger
from .base import BaseMemory, MemoryItem, MemoryType, MemorySearchResult

if TYPE_CHECKING:
    from embeddings import EmbeddingModel

logger = get_logger(__name__)


class LongTermMemory(BaseMemory):
    """基于 Milvus 的长期记忆。
    
    使用向量数据库存储重要记忆，支持：
    - 语义相似度搜索
    - 按类型和重要性过滤
    - 持久化存储
    
    Example:
        >>> from embeddings import EmbeddingModel
        >>> embedding = EmbeddingModel()
        >>> memory = LongTermMemory(
        ...     host="localhost",
        ...     port=19530,
        ...     embedding=embedding
        ... )
        >>> memory.init()
        >>> memory.add(MemoryItem(
        ...     content="用户喜欢简洁的代码风格",
        ...     memory_type=MemoryType.USER_PREFERENCE,
        ...     importance=0.8
        ... ))
        >>> results = memory.search("代码风格偏好")
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 19530,
        embedding: Optional["EmbeddingModel"] = None,
        collection_name: str = "agent_long_term_memory",
        importance_threshold: float = 0.3,  # 只存储重要性高于此阈值的记忆
    ):
        """初始化长期记忆。
        
        Args:
            host: Milvus 主机
            port: Milvus 端口
            embedding: 嵌入模型
            collection_name: 集合名称
            importance_threshold: 重要性阈值
        """
        self.host = host
        self.port = port
        self.embedding = embedding
        self.collection_name = collection_name
        self.importance_threshold = importance_threshold
        self._initialized = False
        self._collection = None
    
    def init(self):
        """初始化连接和集合。"""
        if self._initialized:
            return
        
        try:
            from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
            
            # 连接 Milvus
            connections.connect(
                alias="default",
                host=self.host,
                port=self.port,
            )
            logger.info(f"[LongTermMemory] 连接 Milvus 成功: {self.host}:{self.port}")
            
            # 创建或获取集合
            if utility.has_collection(self.collection_name):
                self._collection = Collection(self.collection_name)
                logger.info(f"[LongTermMemory] 使用已有集合: {self.collection_name}")
            else:
                self._create_collection()
            
            # 加载集合到内存
            self._collection.load()
            self._initialized = True
            
        except Exception as e:
            logger.error(f"[LongTermMemory] 初始化失败: {e}")
            raise
    
    def _create_collection(self):
        """创建集合。"""
        from pymilvus import Collection, FieldSchema, CollectionSchema, DataType
        
        # 获取向量维度
        dim = self.embedding.dimension if self.embedding else 1024
        
        fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=32),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=dim),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="memory_type", dtype=DataType.VARCHAR, max_length=32),
            FieldSchema(name="importance", dtype=DataType.FLOAT),
            FieldSchema(name="timestamp", dtype=DataType.VARCHAR, max_length=32),
            FieldSchema(name="session_id", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="metadata", dtype=DataType.VARCHAR, max_length=4096),
        ]
        
        schema = CollectionSchema(fields, description="Agent Long-Term Memory")
        self._collection = Collection(self.collection_name, schema)
        
        # 创建向量索引
        self._collection.create_index(
            field_name="vector",
            index_params={
                "metric_type": "COSINE",
                "index_type": "HNSW",
                "params": {"M": 16, "efConstruction": 256}
            }
        )
        
        logger.info(f"[LongTermMemory] 创建集合: {self.collection_name}, dim={dim}")
    
    def _encode(self, text: str) -> List[float]:
        """文本转向量。"""
        if self.embedding is None:
            raise ValueError("未配置嵌入模型")
        return self.embedding.encode(text).tolist()
    
    def add(self, item: MemoryItem) -> bool:
        """添加记忆到长期存储。"""
        self.init()
        
        # 重要性过滤
        if item.importance < self.importance_threshold:
            logger.debug(f"[LongTermMemory] 跳过低重要性记忆: {item.importance:.2f}")
            return False
        
        try:
            import json
            
            vector = self._encode(item.content)
            
            data = [
                [item.id],
                [vector],
                [item.content],
                [item.memory_type.value],
                [item.importance],
                [item.timestamp.isoformat()],
                [item.session_id or ""],
                [json.dumps(item.metadata, ensure_ascii=False)],
            ]
            
            self._collection.insert(data)
            self._collection.flush()
            
            logger.debug(f"[LongTermMemory] 添加记忆: {item.id}, 重要性: {item.importance:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"[LongTermMemory] 添加记忆失败: {e}")
            return False
    
    def get(self, memory_id: str) -> Optional[MemoryItem]:
        """获取指定记忆。"""
        self.init()
        
        try:
            results = self._collection.query(
                expr=f'id == "{memory_id}"',
                output_fields=["content", "memory_type", "importance", "timestamp", "session_id", "metadata"]
            )
            
            if results:
                return self._result_to_item(results[0])
            return None
            
        except Exception as e:
            logger.error(f"[LongTermMemory] 获取记忆失败: {e}")
            return None
    
    def _result_to_item(self, result: dict) -> MemoryItem:
        """将查询结果转为 MemoryItem。"""
        import json
        return MemoryItem(
            content=result["content"],
            memory_type=MemoryType(result["memory_type"]),
            importance=result["importance"],
            timestamp=datetime.fromisoformat(result["timestamp"]),
            session_id=result["session_id"] or None,
            metadata=json.loads(result["metadata"]) if result["metadata"] else {},
        )
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        memory_type: Optional[MemoryType] = None,
        min_importance: float = 0.0,
    ) -> List[MemorySearchResult]:
        """语义搜索相关记忆。"""
        self.init()
        
        try:
            query_vector = self._encode(query)
            
            # 构建过滤表达式
            expr_parts = []
            if memory_type:
                expr_parts.append(f'memory_type == "{memory_type.value}"')
            if min_importance > 0:
                expr_parts.append(f'importance >= {min_importance}')
            
            expr = " and ".join(expr_parts) if expr_parts else None
            
            # 搜索
            results = self._collection.search(
                data=[query_vector],
                anns_field="vector",
                param={"metric_type": "COSINE", "params": {"ef": 64}},
                limit=top_k,
                expr=expr,
                output_fields=["content", "memory_type", "importance", "timestamp", "session_id", "metadata"]
            )
            
            output = []
            for hits in results:
                for hit in hits:
                    item = self._result_to_item(hit.entity)
                    output.append(MemorySearchResult(
                        item=item,
                        score=hit.distance,  # COSINE 相似度
                        source="long_term"
                    ))
            
            return output
            
        except Exception as e:
            logger.error(f"[LongTermMemory] 搜索失败: {e}")
            return []
    
    def delete(self, memory_id: str) -> bool:
        """删除记忆。"""
        self.init()
        
        try:
            self._collection.delete(expr=f'id == "{memory_id}"')
            return True
        except Exception as e:
            logger.error(f"[LongTermMemory] 删除失败: {e}")
            return False
    
    def clear(self, session_id: Optional[str] = None) -> int:
        """清空记忆。"""
        self.init()
        
        try:
            if session_id:
                # 删除指定会话的记忆
                expr = f'session_id == "{session_id}"'
            else:
                # 删除所有
                expr = 'id != ""'
            
            # 先查询数量
            count = len(self._collection.query(expr=expr, output_fields=["id"]))
            
            # 删除
            self._collection.delete(expr=expr)
            
            logger.info(f"[LongTermMemory] 清空 {count} 条记忆")
            return count
            
        except Exception as e:
            logger.error(f"[LongTermMemory] 清空失败: {e}")
            return 0
    
    def count(self) -> int:
        """获取记忆数量。"""
        self.init()
        
        try:
            return self._collection.num_entities
        except Exception as e:
            logger.error(f"[LongTermMemory] 计数失败: {e}")
            return 0
    
    def consolidate(self, items: List[MemoryItem], summary_prompt: str = None) -> Optional[MemoryItem]:
        """整合多条记忆为一条经验总结。
        
        Args:
            items: 要整合的记忆列表
            summary_prompt: 总结提示（可选，需要 LLM 支持）
            
        Returns:
            整合后的记忆项
        """
        if not items:
            return None
        
        # 简单合并内容
        contents = [f"- {item.content}" for item in items]
        combined_content = f"经验总结:\n" + "\n".join(contents)
        
        # 计算平均重要性
        avg_importance = sum(item.importance for item in items) / len(items)
        
        return MemoryItem(
            content=combined_content,
            memory_type=MemoryType.EXPERIENCE,
            importance=min(avg_importance + 0.1, 1.0),  # 总结的重要性略高
            metadata={"source_count": len(items)}
        )
