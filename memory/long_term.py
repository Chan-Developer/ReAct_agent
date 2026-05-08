# -*- coding: utf-8 -*-
"""Long-term memory implementation backed by Milvus."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, List, Optional

from common.logger import get_logger
from .base import BaseMemory, MemoryItem, MemorySearchResult, MemoryType

if TYPE_CHECKING:
    from embeddings import EmbeddingModel

logger = get_logger(__name__)


class LongTermMemory(BaseMemory):
    """Semantic memory storage for durable recall."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 19530,
        alias: str = "default",
        embedding: Optional["EmbeddingModel"] = None,
        collection_name: str = "agent_long_term_memory",
        importance_threshold: float = 0.3,
        similarity_threshold: float = 0.0,
        recency_half_life_days: int = 30,
        recency_weight: float = 0.2,
    ):
        self.host = host
        self.port = port
        self.alias = alias
        self.embedding = embedding
        self.collection_name = collection_name
        self.importance_threshold = importance_threshold
        self.similarity_threshold = similarity_threshold
        self.recency_half_life_days = max(1, recency_half_life_days)
        self.recency_weight = max(0.0, min(1.0, recency_weight))
        self._initialized = False
        self._collection = None

    def init(self):
        if self._initialized:
            return

        try:
            from pymilvus import Collection, connections, utility

            connections.connect(
                alias=self.alias,
                host=self.host,
                port=self.port,
            )
            logger.info(
                "[LongTermMemory] connected to Milvus %s:%s alias=%s",
                self.host,
                self.port,
                self.alias,
            )

            if utility.has_collection(self.collection_name):
                self._collection = Collection(self.collection_name)
            else:
                self._create_collection()

            self._collection.load()
            self._initialized = True
        except Exception as exc:
            logger.error("[LongTermMemory] init failed: %s", exc)
            raise

    def _create_collection(self):
        from pymilvus import Collection, CollectionSchema, DataType, FieldSchema

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
        self._collection.create_index(
            field_name="vector",
            index_params={
                "metric_type": "COSINE",
                "index_type": "HNSW",
                "params": {"M": 16, "efConstruction": 256},
            },
        )
        logger.info("[LongTermMemory] created collection=%s dim=%s", self.collection_name, dim)

    def _encode(self, text: str) -> List[float]:
        if self.embedding is None:
            raise ValueError("Embedding model is not configured")
        return self.embedding.encode(text).tolist()

    def add(self, item: MemoryItem) -> bool:
        self.init()

        if item.importance < self.importance_threshold:
            logger.debug(
                "[LongTermMemory] skip low-importance item=%s importance=%.2f",
                item.id,
                item.importance,
            )
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
            return True
        except Exception as exc:
            logger.error("[LongTermMemory] add failed: %s", exc)
            return False

    def get(self, memory_id: str) -> Optional[MemoryItem]:
        self.init()
        try:
            results = self._collection.query(
                expr=f'id == "{memory_id}"',
                output_fields=[
                    "content",
                    "memory_type",
                    "importance",
                    "timestamp",
                    "session_id",
                    "metadata",
                ],
            )
            if results:
                return self._result_to_item(results[0])
            return None
        except Exception as exc:
            logger.error("[LongTermMemory] get failed: %s", exc)
            return None

    def _result_to_item(self, result: dict) -> MemoryItem:
        import json

        item = MemoryItem(
            content=result["content"],
            memory_type=MemoryType(result["memory_type"]),
            importance=result["importance"],
            timestamp=datetime.fromisoformat(result["timestamp"]),
            session_id=result["session_id"] or None,
            metadata=json.loads(result["metadata"]) if result["metadata"] else {},
        )
        return item

    def _score_with_recency(self, raw_score: float, timestamp: datetime) -> float:
        if self.recency_weight <= 0:
            return raw_score

        age_seconds = max(0.0, (datetime.now() - timestamp).total_seconds())
        half_life_seconds = float(self.recency_half_life_days * 24 * 3600)
        recency_score = 0.5 ** (age_seconds / half_life_seconds)
        return (raw_score * (1.0 - self.recency_weight)) + (
            recency_score * self.recency_weight
        )

    def _load_items_for_consolidation(
        self,
        max_age_days: int,
        limit: int,
        session_id: Optional[str] = None,
    ) -> List[MemoryItem]:
        self.init()

        cutoff = (datetime.now() - timedelta(days=max_age_days)).isoformat()
        expr_parts = [f'timestamp <= "{cutoff}"']
        if session_id:
            expr_parts.append(f'session_id == "{session_id}"')
        expr = " and ".join(expr_parts)

        rows = self._collection.query(
            expr=expr,
            limit=limit,
            output_fields=[
                "content",
                "memory_type",
                "importance",
                "timestamp",
                "session_id",
                "metadata",
            ],
        )

        items: List[MemoryItem] = []
        for row in rows:
            item = self._result_to_item(row)
            if item.metadata.get("consolidated_summary"):
                continue
            items.append(item)
        return items

    def search(
        self,
        query: str,
        top_k: int = 5,
        memory_type: Optional[MemoryType] = None,
        min_importance: float = 0.0,
        session_id: Optional[str] = None,
    ) -> List[MemorySearchResult]:
        self.init()

        try:
            query_vector = self._encode(query)

            expr_parts = []
            if memory_type:
                expr_parts.append(f'memory_type == "{memory_type.value}"')
            if min_importance > 0:
                expr_parts.append(f"importance >= {min_importance}")
            if session_id:
                expr_parts.append(f'session_id == "{session_id}"')

            expr = " and ".join(expr_parts) if expr_parts else None
            results = self._collection.search(
                data=[query_vector],
                anns_field="vector",
                param={"metric_type": "COSINE", "params": {"ef": 64}},
                limit=top_k,
                expr=expr,
                output_fields=[
                    "content",
                    "memory_type",
                    "importance",
                    "timestamp",
                    "session_id",
                    "metadata",
                ],
            )

            output: List[MemorySearchResult] = []
            for hits in results:
                for hit in hits:
                    if self.similarity_threshold > 0 and hit.distance < self.similarity_threshold:
                        continue
                    item = self._result_to_item(hit.entity)
                    output.append(
                        MemorySearchResult(
                            item=item,
                            score=self._score_with_recency(hit.distance, item.timestamp),
                            source="long_term",
                        )
                    )

            output.sort(key=lambda result: result.score, reverse=True)
            return output
        except Exception as exc:
            logger.error("[LongTermMemory] search failed: %s", exc)
            return []

    def delete(self, memory_id: str) -> bool:
        self.init()
        try:
            self._collection.delete(expr=f'id == "{memory_id}"')
            return True
        except Exception as exc:
            logger.error("[LongTermMemory] delete failed: %s", exc)
            return False

    def clear(self, session_id: Optional[str] = None) -> int:
        self.init()
        try:
            expr = f'session_id == "{session_id}"' if session_id else 'id != ""'
            count = len(self._collection.query(expr=expr, output_fields=["id"]))
            self._collection.delete(expr=expr)
            return count
        except Exception as exc:
            logger.error("[LongTermMemory] clear failed: %s", exc)
            return 0

    def count(self) -> int:
        self.init()
        try:
            return self._collection.num_entities
        except Exception as exc:
            logger.error("[LongTermMemory] count failed: %s", exc)
            return 0

    def consolidate(self, items: List[MemoryItem]) -> Optional[MemoryItem]:
        if not items:
            return None

        items = sorted(items, key=lambda item: item.timestamp)
        combined_content = "Consolidated Memory Summary:\n" + "\n".join(
            f"- {item.content}" for item in items
        )
        avg_importance = sum(item.importance for item in items) / len(items)
        memory_types = {item.memory_type for item in items}
        session_ids = {item.session_id for item in items if item.session_id}

        return MemoryItem(
            content=combined_content,
            memory_type=memory_types.pop() if len(memory_types) == 1 else MemoryType.EXPERIENCE,
            importance=min(avg_importance + 0.1, 1.0),
            timestamp=items[-1].timestamp,
            session_id=session_ids.pop() if len(session_ids) == 1 else None,
            metadata={
                "source_count": len(items),
                "source_ids": [item.id for item in items],
                "consolidated_summary": True,
                "time_range": {
                    "start": items[0].timestamp.isoformat(),
                    "end": items[-1].timestamp.isoformat(),
                },
            },
        )

    def consolidate_old_memories(
        self,
        max_age_days: int = 14,
        limit: int = 50,
        group_size: int = 5,
        session_id: Optional[str] = None,
    ) -> dict:
        try:
            items = self._load_items_for_consolidation(
                max_age_days=max_age_days,
                limit=limit,
                session_id=session_id,
            )
        except Exception as exc:
            logger.error("[LongTermMemory] consolidation scan failed: %s", exc)
            return {"candidates": 0, "summaries_created": 0, "items_deleted": 0}

        groups: dict[tuple[Optional[str], str], List[MemoryItem]] = {}
        for item in items:
            key = (item.session_id, item.memory_type.value)
            groups.setdefault(key, []).append(item)

        summaries_created = 0
        items_deleted = 0
        for grouped_items in groups.values():
            grouped_items.sort(key=lambda item: item.timestamp)
            while len(grouped_items) >= group_size:
                batch = grouped_items[:group_size]
                summary = self.consolidate(batch)
                if summary is None:
                    break
                if not self.add(summary):
                    break
                for item in batch:
                    if self.delete(item.id):
                        items_deleted += 1
                summaries_created += 1
                grouped_items = grouped_items[group_size:]

        return {
            "candidates": len(items),
            "summaries_created": summaries_created,
            "items_deleted": items_deleted,
        }
