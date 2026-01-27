# -*- coding: utf-8 -*-
"""短期记忆实现 - 基于 Redis。

特点：
- 快速读写，低延迟
- 支持 TTL 自动过期
- 适合存储当前会话上下文、最近对话
"""
from typing import List, Optional
import json

from common.logger import get_logger
from .base import BaseMemory, MemoryItem, MemoryType, MemorySearchResult

logger = get_logger(__name__)


class ShortTermMemory(BaseMemory):
    """基于 Redis 的短期记忆。
    
    使用 Redis 存储近期对话和上下文，支持：
    - 按会话 ID 隔离记忆
    - 自动过期（TTL）
    - 关键词搜索
    
    Example:
        >>> memory = ShortTermMemory(host="localhost", port=6379)
        >>> memory.add(MemoryItem(
        ...     content="用户询问了 Python 的用法",
        ...     memory_type=MemoryType.CONVERSATION,
        ...     session_id="session_001"
        ... ))
        >>> results = memory.search("Python", session_id="session_001")
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        prefix: str = "agent:memory:short",
        ttl: int = 3600 * 24,  # 默认 24 小时过期
        max_items: int = 100,  # 每个会话最大记忆数
    ):
        """初始化短期记忆。
        
        Args:
            host: Redis 主机
            port: Redis 端口
            db: Redis 数据库编号
            password: Redis 密码
            prefix: 键前缀
            ttl: 记忆过期时间（秒）
            max_items: 每个会话最大记忆数量
        """
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.prefix = prefix
        self.ttl = ttl
        self.max_items = max_items
        self._client = None
    
    @property
    def client(self):
        """懒加载 Redis 客户端"""
        if self._client is None:
            try:
                import redis
                self._client = redis.Redis(
                    host=self.host,
                    port=self.port,
                    db=self.db,
                    password=self.password,
                    decode_responses=True,
                )
                self._client.ping()
                logger.info(f"[ShortTermMemory] 连接 Redis 成功: {self.host}:{self.port}")
            except Exception as e:
                logger.error(f"[ShortTermMemory] 连接 Redis 失败: {e}")
                raise
        return self._client
    
    def _make_key(self, session_id: Optional[str] = None) -> str:
        """生成 Redis 键"""
        if session_id:
            return f"{self.prefix}:{session_id}"
        return f"{self.prefix}:global"
    
    def _make_item_key(self, memory_id: str) -> str:
        """生成记忆项键"""
        return f"{self.prefix}:item:{memory_id}"
    
    def add(self, item: MemoryItem) -> bool:
        """添加记忆到 Redis。"""
        try:
            # 存储记忆项详情
            item_key = self._make_item_key(item.id)
            self.client.setex(item_key, self.ttl, item.to_json())
            
            # 添加到会话列表（按时间排序）
            list_key = self._make_key(item.session_id)
            score = item.timestamp.timestamp()
            self.client.zadd(list_key, {item.id: score})
            self.client.expire(list_key, self.ttl)
            
            # 维护列表大小，删除最旧的记忆
            if self.client.zcard(list_key) > self.max_items:
                # 删除最旧的记忆
                oldest_ids = self.client.zrange(list_key, 0, -self.max_items - 1)
                if oldest_ids:
                    self.client.zrem(list_key, *oldest_ids)
                    for old_id in oldest_ids:
                        self.client.delete(self._make_item_key(old_id))
            
            logger.debug(f"[ShortTermMemory] 添加记忆: {item.id}")
            return True
            
        except Exception as e:
            logger.error(f"[ShortTermMemory] 添加记忆失败: {e}")
            return False
    
    def get(self, memory_id: str) -> Optional[MemoryItem]:
        """获取指定记忆。"""
        try:
            item_key = self._make_item_key(memory_id)
            data = self.client.get(item_key)
            if data:
                return MemoryItem.from_json(data)
            return None
        except Exception as e:
            logger.error(f"[ShortTermMemory] 获取记忆失败: {e}")
            return None
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        memory_type: Optional[MemoryType] = None,
        session_id: Optional[str] = None,
    ) -> List[MemorySearchResult]:
        """搜索相关记忆（关键词匹配）。"""
        try:
            list_key = self._make_key(session_id)
            
            # 获取最近的记忆 ID
            memory_ids = self.client.zrevrange(list_key, 0, self.max_items - 1)
            
            results = []
            query_lower = query.lower()
            
            for mid in memory_ids:
                item = self.get(mid)
                if item is None:
                    continue
                
                # 类型过滤
                if memory_type and item.memory_type != memory_type:
                    continue
                
                # 简单关键词匹配计算相关性
                content_lower = item.content.lower()
                if query_lower in content_lower:
                    # 计算简单得分：匹配位置越靠前分数越高
                    pos = content_lower.find(query_lower)
                    score = 1.0 - (pos / len(content_lower)) if pos >= 0 else 0.0
                    score *= item.importance  # 乘以重要性
                    
                    results.append(MemorySearchResult(
                        item=item,
                        score=score,
                        source="short_term"
                    ))
            
            # 按得分排序，返回 top_k
            results.sort(key=lambda x: x.score, reverse=True)
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"[ShortTermMemory] 搜索失败: {e}")
            return []
    
    def get_recent(
        self,
        n: int = 10,
        session_id: Optional[str] = None,
        memory_type: Optional[MemoryType] = None,
    ) -> List[MemoryItem]:
        """获取最近 n 条记忆。"""
        try:
            list_key = self._make_key(session_id)
            memory_ids = self.client.zrevrange(list_key, 0, n * 2 - 1)  # 多获取一些以防过滤
            
            results = []
            for mid in memory_ids:
                item = self.get(mid)
                if item is None:
                    continue
                if memory_type and item.memory_type != memory_type:
                    continue
                results.append(item)
                if len(results) >= n:
                    break
            
            return results
            
        except Exception as e:
            logger.error(f"[ShortTermMemory] 获取最近记忆失败: {e}")
            return []
    
    def delete(self, memory_id: str) -> bool:
        """删除记忆。"""
        try:
            item_key = self._make_item_key(memory_id)
            result = self.client.delete(item_key)
            return result > 0
        except Exception as e:
            logger.error(f"[ShortTermMemory] 删除失败: {e}")
            return False
    
    def clear(self, session_id: Optional[str] = None) -> int:
        """清空记忆。"""
        try:
            list_key = self._make_key(session_id)
            memory_ids = self.client.zrange(list_key, 0, -1)
            
            count = 0
            for mid in memory_ids:
                if self.delete(mid):
                    count += 1
            
            self.client.delete(list_key)
            logger.info(f"[ShortTermMemory] 清空 {count} 条记忆")
            return count
            
        except Exception as e:
            logger.error(f"[ShortTermMemory] 清空失败: {e}")
            return 0
    
    def count(self, session_id: Optional[str] = None) -> int:
        """获取记忆数量。"""
        try:
            list_key = self._make_key(session_id)
            return self.client.zcard(list_key)
        except Exception as e:
            logger.error(f"[ShortTermMemory] 计数失败: {e}")
            return 0
