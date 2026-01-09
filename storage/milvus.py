# -*- coding: utf-8 -*-
"""Milvus 向量数据库客户端。

提供 Milvus 向量数据库的操作封装，包括：
- 连接管理
- 集合（Collection）管理
- 向量插入
- 向量搜索
- 数据查询

Example:
    >>> from storage import MilvusClient
    >>> client = MilvusClient()
    >>> client.connect()
    >>> client.create_collection("my_collection", dimension=128)
    >>> client.insert("my_collection", vectors=[[0.1] * 128])
    >>> results = client.search("my_collection", vectors=[[0.1] * 128], top_k=10)
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from common.config import get_config

from pymilvus import connections
from pymilvus import utility
from pymilvus import Collection, FieldSchema, CollectionSchema, DataType

class MilvusClient:
    """Milvus 向量数据库客户端。
    
    Attributes:
        host: Milvus 服务器地址
        port: Milvus 服务器端口
        alias: 连接别名
        
    Example:
        >>> client = MilvusClient()
        >>> client.connect()
        >>> collections = client.list_collections()
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        alias: str = "default",
    ) -> None:
        """初始化 Milvus 客户端。
        
        Args:
            host: Milvus 服务器地址（默认从配置读取）
            port: Milvus 服务器端口（默认从配置读取）
            alias: 连接别名
        """
        self._host = host
        self._port = port
        self._alias = alias
        self._connected = False
        self._collections: Dict[str, Any] = {}

    @property
    def is_connected(self) -> bool:
        """是否已连接。"""
        return self._connected

    def connect(self) -> None:
        """建立与 Milvus 的连接。
        
        Raises:
            ImportError: pymilvus 未安装
            Exception: 连接失败
        """        
        if self._connected:
            return
        
        # 从配置读取连接信息
        config = get_config()
        host = self._host or config.milvus.host
        port = self._port or config.milvus.port
        
        # 建立连接
        connections.connect(
            alias=self._alias,
            host=host,
            port=port,
        )
        
        self._connected = True

    def disconnect(self) -> None:
        """断开连接。"""
        if not self._connected:
            return
            
        connections.disconnect(self._alias)
        self._connected = False
        self._collections.clear()

    def _ensure_connected(self) -> None:
        """确保已连接。"""
        if not self._connected:
            self.connect()

    def _get_collection(self, collection_name: str) -> Any:
        """获取集合对象。
        
        Args:
            collection_name: 集合名称
            
        Returns:
            Collection 对象
        """
        if collection_name in self._collections:
            return self._collections[collection_name]
        
        
        self._ensure_connected()
        collection = Collection(collection_name)
        self._collections[collection_name] = collection
        return collection

    # ==================== 集合管理 ====================

    def create_collection(
        self,
        collection_name: str,
        dimension: int,
        description: Optional[str] = None,
    ) -> None:
        """创建集合。
        
        Args:
            collection_name: 集合名称
            dimension: 向量维度
            description: 集合描述
        """
        
        
        self._ensure_connected()
        
        # 定义字段
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=dimension),
        ]
        
        # 创建 schema
        schema = CollectionSchema(
            fields, 
            description=description or f"Collection {collection_name}"
        )
        
        # 创建集合
        collection = Collection(collection_name, schema)
        self._collections[collection_name] = collection

    def list_collections(self) -> List[str]:
        """列出所有集合。
        
        Returns:
            集合名称列表
        """
        from pymilvus import utility
        
        self._ensure_connected()
        return utility.list_collections()

    def has_collection(self, collection_name: str) -> bool:
        """检查集合是否存在。
        
        Args:
            collection_name: 集合名称
            
        Returns:
            是否存在
        """
        from pymilvus import utility
        
        self._ensure_connected()
        return utility.has_collection(collection_name)

    def drop_collection(self, collection_name: str) -> None:
        """删除集合。
        
        Args:
            collection_name: 集合名称
        """
        from pymilvus import utility
        
        self._ensure_connected()
        utility.drop_collection(collection_name)
        
        if collection_name in self._collections:
            del self._collections[collection_name]

    def load_collection(self, collection_name: str) -> None:
        """将集合加载到内存。
        
        Args:
            collection_name: 集合名称
        """
        collection = self._get_collection(collection_name)
        collection.load()

    def release_collection(self, collection_name: str) -> None:
        """从内存释放集合。
        
        Args:
            collection_name: 集合名称
        """
        collection = self._get_collection(collection_name)
        collection.release()

    # ==================== 数据操作 ====================

    def insert(
        self,
        collection_name: str,
        vectors: List[List[float]],
        data: Optional[List[Dict]] = None,
    ) -> List[int]:
        """插入向量数据。
        
        Args:
            collection_name: 集合名称
            vectors: 向量数据列表
            data: 元数据列表（与向量对应）
            
        Returns:
            插入的主键 ID 列表
        """
        collection = self._get_collection(collection_name)
        
        # 准备数据
        entities = [vectors]
        if data:
            # 如果有元数据，按字段组织
            for field_name in data[0].keys():
                entities.append([item.get(field_name) for item in data])
        
        # 插入数据
        result = collection.insert(entities)
        collection.flush()
        
        return result.primary_keys

    def search(
        self,
        collection_name: str,
        vectors: List[List[float]],
        top_k: int = 10,
        filter_expr: Optional[str] = None,
        output_fields: Optional[List[str]] = None,
        metric_type: str = "L2",
        search_params: Optional[Dict] = None,
    ) -> List[List[Dict]]:
        """向量相似度搜索。
        
        Args:
            collection_name: 集合名称
            vectors: 查询向量列表
            top_k: 返回最相似的 K 个结果
            filter_expr: 过滤表达式
            output_fields: 输出字段列表
            metric_type: 距离度量类型（L2, IP, COSINE）
            search_params: 搜索参数
            
        Returns:
            搜索结果列表，每个查询向量对应一个结果列表
        """
        collection = self._get_collection(collection_name)
        collection.load()
        
        # 默认搜索参数
        params = search_params or {
            "metric_type": metric_type,
            "params": {"nprobe": 10},
        }
        
        # 执行搜索
        results = collection.search(
            data=vectors,
            anns_field="vector",
            param=params,
            limit=top_k,
            expr=filter_expr,
            output_fields=output_fields or [],
        )
        
        # 格式化结果
        formatted_results = []
        for hits in results:
            query_results = []
            for hit in hits:
                result = {
                    "id": hit.id,
                    "distance": hit.distance,
                }
                if output_fields:
                    result["entity"] = hit.entity
                query_results.append(result)
            formatted_results.append(query_results)
        
        return formatted_results

    def query(
        self,
        collection_name: str,
        filter_expr: str,
        output_fields: Optional[List[str]] = None,
        limit: int = 10,
    ) -> List[Dict]:
        """条件查询。
        
        Args:
            collection_name: 集合名称
            filter_expr: 过滤表达式
            output_fields: 输出字段列表
            limit: 返回数量限制
            
        Returns:
            查询结果列表
        """
        collection = self._get_collection(collection_name)
        collection.load()
        
        results = collection.query(
            expr=filter_expr,
            output_fields=output_fields or [],
            limit=limit,
        )
        
        return results

    def delete(
        self,
        collection_name: str,
        filter_expr: str,
    ) -> int:
        """删除数据。
        
        Args:
            collection_name: 集合名称
            filter_expr: 删除条件表达式
            
        Returns:
            删除的数据条数
        """
        collection = self._get_collection(collection_name)
        collection.load()
        
        result = collection.delete(expr=filter_expr)
        
        return result.delete_count if hasattr(result, 'delete_count') else 0

    # ==================== 上下文管理器 ====================

    def __enter__(self) -> "MilvusClient":
        """进入上下文时连接。"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """退出上下文时断开连接。"""
        self.disconnect()

    def __repr__(self) -> str:
        status = "connected" if self._connected else "disconnected"
        return f"MilvusClient(alias={self._alias!r}, status={status})"

