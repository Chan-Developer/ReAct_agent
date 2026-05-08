# -*- coding: utf-8 -*-
"""Focused tests for memory maintenance and long-term compaction."""

from __future__ import annotations

from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest


class TestLongTermMemoryMaintenance:
    @pytest.fixture
    def mock_embedding(self):
        import numpy as np

        embedding = MagicMock()
        embedding.dimension = 4
        embedding.encode.return_value = np.array([0.1, 0.2, 0.3, 0.4])
        return embedding

    def test_search_applies_recency_decay(self, mock_embedding):
        from memory.long_term import LongTermMemory

        now = datetime.now()
        newer = {
            "content": "recent memory",
            "memory_type": "experience",
            "importance": 0.8,
            "timestamp": now.isoformat(),
            "session_id": "session_1",
            "metadata": "{}",
        }
        older = {
            "content": "old memory",
            "memory_type": "experience",
            "importance": 0.8,
            "timestamp": (now - timedelta(days=60)).isoformat(),
            "session_id": "session_1",
            "metadata": "{}",
        }

        memory = LongTermMemory(
            embedding=mock_embedding,
            recency_half_life_days=30,
            recency_weight=0.5,
        )
        memory._initialized = True
        memory._collection = MagicMock()
        memory._collection.search.return_value = [
            [
                SimpleNamespace(distance=0.8, entity=older),
                SimpleNamespace(distance=0.8, entity=newer),
            ]
        ]

        results = memory.search("memory", top_k=2)

        assert len(results) == 2
        assert results[0].item.content == "recent memory"
        assert results[0].score > results[1].score

    def test_consolidate_old_memories_creates_summary(self, mock_embedding):
        from memory.long_term import LongTermMemory

        memory = LongTermMemory(
            embedding=mock_embedding,
            importance_threshold=0.5,
        )
        memory._initialized = True
        memory._collection = MagicMock()

        base_time = datetime.now() - timedelta(days=30)
        rows = []
        for index in range(5):
            rows.append(
                {
                    "content": f"memory {index}",
                    "memory_type": "experience",
                    "importance": 0.7,
                    "timestamp": (base_time + timedelta(minutes=index)).isoformat(),
                    "session_id": "session_1",
                    "metadata": "{}",
                }
            )
        memory._collection.query.return_value = rows

        stats = memory.consolidate_old_memories(
            max_age_days=14,
            limit=10,
            group_size=5,
            session_id="session_1",
        )

        assert stats["candidates"] == 5
        assert stats["summaries_created"] == 1
        assert stats["items_deleted"] == 5
        assert memory._collection.insert.call_count == 1
        assert memory._collection.delete.call_count == 5


class TestMemoryManagerMaintenance:
    @patch("memory.manager.ShortTermMemory")
    @patch("memory.manager.LongTermMemory")
    def test_runs_scheduled_long_term_maintenance(self, mock_lt_cls, mock_st_cls):
        from memory.base import MemoryItem, MemoryType
        from memory.manager import MemoryManager

        short_term = MagicMock()
        short_term.add.return_value = True
        short_term.host = "redis"
        short_term.port = 6379

        long_term = MagicMock()
        long_term.add.return_value = True
        long_term.host = "milvus"
        long_term.port = 19530
        long_term.consolidate_old_memories.return_value = {
            "candidates": 5,
            "summaries_created": 1,
            "items_deleted": 5,
        }

        mock_st_cls.return_value = short_term
        mock_lt_cls.return_value = long_term

        manager = MemoryManager(
            embedding=MagicMock(),
            long_term_threshold=0.6,
            long_term_consolidation_enabled=True,
            long_term_maintenance_interval=2,
        )

        for index in range(2):
            manager.add(
                MemoryItem(
                    content=f"important {index}",
                    memory_type=MemoryType.EXPERIENCE,
                    importance=0.9,
                )
            )

        long_term.consolidate_old_memories.assert_called_once()

    @patch("memory.manager.ShortTermMemory")
    @patch("memory.manager.LongTermMemory")
    def test_prefers_memory_short_term_ttl_when_customized(self, mock_lt_cls, mock_st_cls):
        from common.config import Config
        from memory.manager import MemoryManager

        cfg = Config()
        cfg.redis.ttl_seconds = 7200
        cfg.memory.short_term_ttl = 1800

        short_term = MagicMock()
        short_term.host = "redis"
        short_term.port = 6379
        long_term = MagicMock()
        long_term.host = "milvus"
        long_term.port = 19530

        mock_st_cls.return_value = short_term
        mock_lt_cls.return_value = long_term

        MemoryManager.from_config(config=cfg)

        kwargs = mock_st_cls.call_args.kwargs
        assert kwargs["ttl"] == 1800
