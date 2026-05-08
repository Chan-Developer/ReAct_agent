# -*- coding: utf-8 -*-
"""Unified layered memory manager."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from common import get_config
from common.logger import get_logger
from .base import MemoryItem, MemorySearchResult, MemoryType
from .long_term import LongTermMemory
from .short_term import ShortTermMemory

if TYPE_CHECKING:
    from common.config import Config
    from embeddings import EmbeddingModel

logger = get_logger(__name__)
DEFAULT_SHORT_TERM_TTL = 86400
DEFAULT_LONG_TERM_RECENCY_HALF_LIFE_DAYS = 30
DEFAULT_LONG_TERM_RECENCY_WEIGHT = 0.2


class MemoryManager:
    """Coordinates short-term and long-term memory backends."""

    def __init__(
        self,
        redis_host: Optional[str] = None,
        redis_port: Optional[int] = None,
        redis_db: Optional[int] = None,
        redis_password: Optional[str] = None,
        redis_ttl: Optional[int] = None,
        milvus_host: Optional[str] = None,
        milvus_port: Optional[int] = None,
        milvus_alias: Optional[str] = None,
        milvus_collection_name: Optional[str] = None,
        milvus_similarity_threshold: Optional[float] = None,
        embedding: Optional["EmbeddingModel"] = None,
        long_term_threshold: Optional[float] = None,
        short_term_ttl: Optional[int] = None,
        short_term_window_size: Optional[int] = None,
        cross_session_recall: Optional[bool] = None,
        long_term_recency_half_life_days: Optional[int] = None,
        long_term_recency_weight: Optional[float] = None,
        long_term_consolidation_enabled: Optional[bool] = None,
        long_term_consolidation_max_age_days: Optional[int] = None,
        long_term_consolidation_batch_size: Optional[int] = None,
        long_term_consolidation_group_size: Optional[int] = None,
        long_term_maintenance_interval: Optional[int] = None,
        session_id: Optional[str] = None,
        config: Optional["Config"] = None,
    ):
        cfg = config or get_config()

        self.long_term_threshold = (
            long_term_threshold
            if long_term_threshold is not None
            else cfg.memory.long_term_threshold
        )
        self.short_term_window_size = (
            short_term_window_size
            if short_term_window_size is not None
            else cfg.memory.short_term_window_size
        )
        configured_short_term_ttl = cfg.memory.short_term_ttl
        if short_term_ttl is not None:
            self.short_term_ttl = short_term_ttl
        elif configured_short_term_ttl != DEFAULT_SHORT_TERM_TTL:
            self.short_term_ttl = configured_short_term_ttl
        else:
            self.short_term_ttl = cfg.redis.ttl_seconds
        self.cross_session_recall = (
            cross_session_recall
            if cross_session_recall is not None
            else cfg.memory.cross_session_recall
        )
        self.long_term_recency_half_life_days = (
            long_term_recency_half_life_days
            if long_term_recency_half_life_days is not None
            else cfg.memory.long_term_recency_half_life_days
        )
        self.long_term_recency_weight = (
            long_term_recency_weight
            if long_term_recency_weight is not None
            else cfg.memory.long_term_recency_weight
        )
        self.long_term_consolidation_enabled = (
            long_term_consolidation_enabled
            if long_term_consolidation_enabled is not None
            else cfg.memory.long_term_consolidation_enabled
        )
        self.long_term_consolidation_max_age_days = (
            long_term_consolidation_max_age_days
            if long_term_consolidation_max_age_days is not None
            else cfg.memory.long_term_consolidation_max_age_days
        )
        self.long_term_consolidation_batch_size = (
            long_term_consolidation_batch_size
            if long_term_consolidation_batch_size is not None
            else cfg.memory.long_term_consolidation_batch_size
        )
        self.long_term_consolidation_group_size = (
            long_term_consolidation_group_size
            if long_term_consolidation_group_size is not None
            else cfg.memory.long_term_consolidation_group_size
        )
        self.long_term_maintenance_interval = (
            long_term_maintenance_interval
            if long_term_maintenance_interval is not None
            else cfg.memory.long_term_maintenance_interval
        )
        self.session_id = session_id or self._generate_session_id()
        self._long_term_write_count = 0

        self.short_term = ShortTermMemory(
            host=redis_host or cfg.redis.host,
            port=redis_port or cfg.redis.port,
            db=redis_db if redis_db is not None else cfg.redis.db,
            password=redis_password if redis_password is not None else cfg.redis.password,
            ttl=redis_ttl if redis_ttl is not None else self.short_term_ttl,
            max_items=self.short_term_window_size,
        )

        long_term_kwargs = {
            "host": milvus_host or cfg.milvus.host,
            "port": milvus_port or cfg.milvus.port,
            "alias": milvus_alias or cfg.milvus.alias,
            "embedding": embedding,
            "collection_name": milvus_collection_name or cfg.milvus.collection_name,
            "importance_threshold": self.long_term_threshold,
            "similarity_threshold": (
                milvus_similarity_threshold
                if milvus_similarity_threshold is not None
                else cfg.milvus.similarity_threshold
            ),
        }
        if self.long_term_recency_half_life_days != DEFAULT_LONG_TERM_RECENCY_HALF_LIFE_DAYS:
            long_term_kwargs["recency_half_life_days"] = self.long_term_recency_half_life_days
        if self.long_term_recency_weight != DEFAULT_LONG_TERM_RECENCY_WEIGHT:
            long_term_kwargs["recency_weight"] = self.long_term_recency_weight

        self.long_term = LongTermMemory(
            **long_term_kwargs,
        )

        self._embedding = embedding
        logger.info(
            "[MemoryManager] initialized session=%s redis=%s:%s milvus=%s:%s recall=%s",
            self.session_id,
            self.short_term.host,
            self.short_term.port,
            self.long_term.host,
            self.long_term.port,
            self.cross_session_recall,
        )

    @classmethod
    def from_config(
        cls,
        embedding: Optional["EmbeddingModel"] = None,
        session_id: Optional[str] = None,
        config: Optional["Config"] = None,
    ) -> "MemoryManager":
        """Construct the manager from the unified config object."""
        return cls(
            embedding=embedding,
            session_id=session_id,
            config=config,
        )

    @staticmethod
    def _generate_session_id() -> str:
        import uuid

        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

    def add(self, item: MemoryItem) -> bool:
        if item.session_id is None:
            item.session_id = self.session_id

        success = self.short_term.add(item)

        if item.importance >= self.long_term_threshold:
            try:
                long_term_saved = self.long_term.add(item)
                if long_term_saved:
                    self._long_term_write_count += 1
                    self._run_scheduled_maintenance()
            except Exception as exc:
                logger.warning("[MemoryManager] long-term write failed: %s", exc)

        return success

    def add_conversation(
        self,
        role: str,
        content: str,
        importance: float = 0.3,
        metadata: dict | None = None,
    ) -> bool:
        return self.add(
            MemoryItem(
                content=f"[{role}] {content}",
                memory_type=MemoryType.CONVERSATION,
                importance=importance,
                metadata=metadata or {"role": role},
                session_id=self.session_id,
            )
        )

    def add_task_result(
        self,
        task: str,
        result: str,
        success: bool,
        importance: float = 0.5,
    ) -> bool:
        return self.add(
            MemoryItem(
                content=f"Task: {task}\nResult: {result}\nStatus: {'success' if success else 'failed'}",
                memory_type=MemoryType.TASK,
                importance=importance if success else min(1.0, importance + 0.2),
                metadata={"task": task, "success": success},
                session_id=self.session_id,
            )
        )

    def add_experience(
        self,
        content: str,
        importance: float = 0.7,
        metadata: dict | None = None,
    ) -> bool:
        return self.add(
            MemoryItem(
                content=content,
                memory_type=MemoryType.EXPERIENCE,
                importance=importance,
                metadata=metadata or {},
                session_id=self.session_id,
            )
        )

    def search(
        self,
        query: str,
        top_k: int = 5,
        memory_type: Optional[MemoryType] = None,
        sources: Optional[List[str]] = None,
    ) -> List[MemorySearchResult]:
        sources = sources or ["short_term", "long_term"]
        results: List[MemorySearchResult] = []

        if "short_term" in sources:
            try:
                results.extend(
                    self.short_term.search(
                        query=query,
                        top_k=top_k,
                        memory_type=memory_type,
                        session_id=self.session_id,
                    )
                )
            except Exception as exc:
                logger.warning("[MemoryManager] short-term search failed: %s", exc)

        allow_long_term = self._embedding is not None and "long_term" in sources
        if allow_long_term:
            try:
                long_results = self.long_term.search(
                    query=query,
                    top_k=top_k,
                    memory_type=memory_type,
                    session_id=None if self.cross_session_recall else self.session_id,
                )
                results.extend(long_results)
            except Exception as exc:
                logger.warning("[MemoryManager] long-term search failed: %s", exc)

        unique_results: List[MemorySearchResult] = []
        seen_ids = set()
        for result in results:
            if result.item.id in seen_ids:
                continue
            seen_ids.add(result.item.id)
            unique_results.append(result)

        unique_results.sort(key=lambda item: item.score, reverse=True)
        return unique_results[:top_k]

    def get_context(
        self,
        query: str,
        max_items: int = 5,
        include_recent: int = 3,
    ) -> str:
        context_parts: List[str] = []

        if include_recent > 0:
            recent = self.short_term.get_recent(
                n=include_recent,
                session_id=self.session_id,
                memory_type=MemoryType.CONVERSATION,
            )
            if recent:
                context_parts.append("[Recent Conversation | 最近对话]")
                for item in recent:
                    context_parts.append(f"  {item.content}")

        search_results = self.search(query, top_k=max_items)
        if search_results:
            context_parts.append("\n[Relevant Memory]")
            for result in search_results:
                context_parts.append(f"  [{result.source}] {result.item.content}")

        return "\n".join(context_parts) if context_parts else ""

    def migrate_to_long_term(self, min_importance: float = 0.5) -> int:
        if not self._embedding:
            logger.warning("[MemoryManager] embedding not configured; skipping migration")
            return 0

        count = 0
        recent_items = self.short_term.get_recent(
            n=self.short_term_window_size,
            session_id=self.session_id,
        )
        for item in recent_items:
            if item.importance >= min_importance and self.long_term.add(item):
                count += 1

        logger.info("[MemoryManager] migrated %s items into long-term memory", count)
        return count

    def _run_scheduled_maintenance(self) -> None:
        if not self.long_term_consolidation_enabled:
            return
        if self.long_term_maintenance_interval <= 0:
            return
        if self._long_term_write_count % self.long_term_maintenance_interval != 0:
            return

        try:
            stats = self.run_long_term_maintenance()
            logger.info("[MemoryManager] long-term maintenance stats=%s", stats)
        except Exception as exc:
            logger.warning("[MemoryManager] long-term maintenance failed: %s", exc)

    def run_long_term_maintenance(self) -> dict:
        return self.long_term.consolidate_old_memories(
            max_age_days=self.long_term_consolidation_max_age_days,
            limit=self.long_term_consolidation_batch_size,
            group_size=self.long_term_consolidation_group_size,
            session_id=self.session_id,
        )

    def clear_session(self) -> int:
        return self.short_term.clear(session_id=self.session_id)

    def new_session(self) -> str:
        self.session_id = self._generate_session_id()
        logger.info("[MemoryManager] new session started: %s", self.session_id)
        return self.session_id

    def stats(self) -> dict:
        return {
            "session_id": self.session_id,
            "short_term_count": self.short_term.count(self.session_id),
            "long_term_count": self.long_term.count(),
            "long_term_threshold": self.long_term_threshold,
            "cross_session_recall": self.cross_session_recall,
            "short_term_ttl": self.short_term_ttl,
            "short_term_window_size": self.short_term_window_size,
            "long_term_recency_half_life_days": self.long_term_recency_half_life_days,
            "long_term_recency_weight": self.long_term_recency_weight,
            "long_term_consolidation_enabled": self.long_term_consolidation_enabled,
        }
