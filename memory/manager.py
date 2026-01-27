# -*- coding: utf-8 -*-
"""Memory Manager - 统一管理短期和长期记忆。

提供：
- 自动分流：根据重要性决定存储位置
- 统一检索：同时搜索短期和长期记忆
- 记忆迁移：将重要的短期记忆转为长期记忆
"""
from typing import List, Optional, TYPE_CHECKING
from datetime import datetime

from common.logger import get_logger
from .base import MemoryItem, MemoryType, MemorySearchResult
from .short_term import ShortTermMemory
from .long_term import LongTermMemory

if TYPE_CHECKING:
    from embeddings import EmbeddingModel

logger = get_logger(__name__)


class MemoryManager:
    """统一记忆管理器。
    
    整合短期记忆（Redis）和长期记忆（Milvus），提供：
    - 自动存储分流
    - 统一搜索接口
    - 记忆迁移与整合
    
    Example:
        >>> from embeddings import EmbeddingModel
        >>> manager = MemoryManager(
        ...     redis_host="localhost",
        ...     milvus_host="localhost",
        ...     embedding=EmbeddingModel()
        ... )
        >>> 
        >>> # 添加对话记忆（自动存入短期）
        >>> manager.add(MemoryItem(
        ...     content="用户询问 Python 用法",
        ...     memory_type=MemoryType.CONVERSATION,
        ...     importance=0.3
        ... ))
        >>> 
        >>> # 添加重要经验（自动存入长期）
        >>> manager.add(MemoryItem(
        ...     content="用户偏好简洁代码风格",
        ...     memory_type=MemoryType.USER_PREFERENCE,
        ...     importance=0.8
        ... ))
        >>> 
        >>> # 统一搜索
        >>> results = manager.search("Python 代码风格")
    """
    
    def __init__(
        self,
        # Redis 配置
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_password: Optional[str] = None,
        # Milvus 配置
        milvus_host: str = "localhost",
        milvus_port: int = 19530,
        # 嵌入模型
        embedding: Optional["EmbeddingModel"] = None,
        # 阈值配置
        long_term_threshold: float = 0.6,  # 重要性超过此值存入长期记忆
        # 会话配置
        session_id: Optional[str] = None,
    ):
        """初始化记忆管理器。
        
        Args:
            redis_host: Redis 主机
            redis_port: Redis 端口
            redis_password: Redis 密码
            milvus_host: Milvus 主机
            milvus_port: Milvus 端口
            embedding: 嵌入模型（长期记忆需要）
            long_term_threshold: 长期记忆重要性阈值
            session_id: 当前会话 ID
        """
        self.long_term_threshold = long_term_threshold
        self.session_id = session_id or self._generate_session_id()
        
        # 初始化短期记忆
        self.short_term = ShortTermMemory(
            host=redis_host,
            port=redis_port,
            password=redis_password,
        )
        
        # 初始化长期记忆
        self.long_term = LongTermMemory(
            host=milvus_host,
            port=milvus_port,
            embedding=embedding,
        )
        
        self._embedding = embedding
        logger.info(f"[MemoryManager] 初始化完成，会话: {self.session_id}")
    
    @staticmethod
    def _generate_session_id() -> str:
        """生成会话 ID"""
        import uuid
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    def add(self, item: MemoryItem) -> bool:
        """添加记忆（自动分流）。
        
        根据重要性自动决定存储位置：
        - 重要性 >= long_term_threshold: 同时存入短期和长期
        - 重要性 < long_term_threshold: 只存入短期
        """
        # 设置会话 ID
        if item.session_id is None:
            item.session_id = self.session_id
        
        success = True
        
        # 短期记忆总是存储
        if not self.short_term.add(item):
            success = False
        
        # 重要记忆存入长期
        if item.importance >= self.long_term_threshold:
            try:
                self.long_term.add(item)
                logger.debug(f"[MemoryManager] 重要记忆已存入长期: {item.id}")
            except Exception as e:
                logger.warning(f"[MemoryManager] 存入长期记忆失败: {e}")
        
        return success
    
    def add_conversation(
        self,
        role: str,
        content: str,
        importance: float = 0.3,
        metadata: dict = None,
    ) -> bool:
        """便捷方法：添加对话记忆。"""
        return self.add(MemoryItem(
            content=f"[{role}] {content}",
            memory_type=MemoryType.CONVERSATION,
            importance=importance,
            metadata=metadata or {"role": role},
            session_id=self.session_id,
        ))
    
    def add_task_result(
        self,
        task: str,
        result: str,
        success: bool,
        importance: float = 0.5,
    ) -> bool:
        """便捷方法：添加任务执行记录。"""
        return self.add(MemoryItem(
            content=f"任务: {task}\n结果: {result}\n状态: {'成功' if success else '失败'}",
            memory_type=MemoryType.TASK,
            importance=importance if success else importance + 0.2,  # 失败的任务更重要
            metadata={"task": task, "success": success},
            session_id=self.session_id,
        ))
    
    def add_experience(
        self,
        content: str,
        importance: float = 0.7,
        metadata: dict = None,
    ) -> bool:
        """便捷方法：添加经验总结。"""
        return self.add(MemoryItem(
            content=content,
            memory_type=MemoryType.EXPERIENCE,
            importance=importance,
            metadata=metadata or {},
            session_id=self.session_id,
        ))
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        memory_type: Optional[MemoryType] = None,
        sources: List[str] = None,  # ["short_term", "long_term"]
    ) -> List[MemorySearchResult]:
        """统一搜索短期和长期记忆。
        
        Args:
            query: 搜索查询
            top_k: 返回结果数
            memory_type: 记忆类型过滤
            sources: 搜索来源，默认两者都搜
            
        Returns:
            合并并排序后的搜索结果
        """
        sources = sources or ["short_term", "long_term"]
        results = []
        
        # 搜索短期记忆
        if "short_term" in sources:
            try:
                short_results = self.short_term.search(
                    query=query,
                    top_k=top_k,
                    memory_type=memory_type,
                    session_id=self.session_id,
                )
                results.extend(short_results)
            except Exception as e:
                logger.warning(f"[MemoryManager] 短期记忆搜索失败: {e}")
        
        # 搜索长期记忆
        if "long_term" in sources and self._embedding:
            try:
                long_results = self.long_term.search(
                    query=query,
                    top_k=top_k,
                    memory_type=memory_type,
                )
                results.extend(long_results)
            except Exception as e:
                logger.warning(f"[MemoryManager] 长期记忆搜索失败: {e}")
        
        # 合并去重并排序
        seen_ids = set()
        unique_results = []
        for r in results:
            if r.item.id not in seen_ids:
                seen_ids.add(r.item.id)
                unique_results.append(r)
        
        unique_results.sort(key=lambda x: x.score, reverse=True)
        return unique_results[:top_k]
    
    def get_context(
        self,
        query: str,
        max_items: int = 5,
        include_recent: int = 3,
    ) -> str:
        """获取与查询相关的上下文（用于注入 Prompt）。
        
        Args:
            query: 当前查询
            max_items: 最大记忆数
            include_recent: 包含最近 n 条对话
            
        Returns:
            格式化的上下文字符串
        """
        context_parts = []
        
        # 1. 最近对话
        if include_recent > 0:
            recent = self.short_term.get_recent(
                n=include_recent,
                session_id=self.session_id,
                memory_type=MemoryType.CONVERSATION,
            )
            if recent:
                context_parts.append("【最近对话】")
                for item in recent:
                    context_parts.append(f"  {item.content}")
        
        # 2. 相关记忆
        search_results = self.search(query, top_k=max_items)
        if search_results:
            context_parts.append("\n【相关记忆】")
            for r in search_results:
                source_tag = "短期" if r.source == "short_term" else "长期"
                context_parts.append(f"  [{source_tag}] {r.item.content}")
        
        return "\n".join(context_parts) if context_parts else ""
    
    def migrate_to_long_term(self, min_importance: float = 0.5) -> int:
        """将符合条件的短期记忆迁移到长期记忆。
        
        Args:
            min_importance: 最小重要性阈值
            
        Returns:
            迁移数量
        """
        if not self._embedding:
            logger.warning("[MemoryManager] 未配置嵌入模型，无法迁移到长期记忆")
            return 0
        
        count = 0
        recent_items = self.short_term.get_recent(n=50, session_id=self.session_id)
        
        for item in recent_items:
            if item.importance >= min_importance:
                if self.long_term.add(item):
                    count += 1
        
        logger.info(f"[MemoryManager] 迁移 {count} 条记忆到长期存储")
        return count
    
    def clear_session(self) -> int:
        """清空当前会话的短期记忆。"""
        return self.short_term.clear(session_id=self.session_id)
    
    def new_session(self) -> str:
        """开始新会话。"""
        self.session_id = self._generate_session_id()
        logger.info(f"[MemoryManager] 新会话: {self.session_id}")
        return self.session_id
    
    def stats(self) -> dict:
        """获取记忆统计信息。"""
        return {
            "session_id": self.session_id,
            "short_term_count": self.short_term.count(self.session_id),
            "long_term_count": self.long_term.count(),
            "long_term_threshold": self.long_term_threshold,
        }
