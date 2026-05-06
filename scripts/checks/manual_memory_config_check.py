# -*- coding: utf-8 -*-
"""Minimal runtime verification for memory config wiring."""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ["LOG_FORMAT"] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from common.config import Config
from memory.manager import MemoryManager


class DummyShortTermMemory:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.host = kwargs.get("host")
        self.port = kwargs.get("port")

    def add(self, item):
        return True

    def search(self, **kwargs):
        return []

    def get_recent(self, **kwargs):
        return []

    def clear(self, **kwargs):
        return 0

    def count(self, *args, **kwargs):
        return 0


class DummyLongTermMemory:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.host = kwargs.get("host")
        self.port = kwargs.get("port")

    def add(self, item):
        return True

    def search(self, **kwargs):
        return []

    def count(self):
        return 0


def main() -> None:
    import memory.manager as manager_module

    original_short = manager_module.ShortTermMemory
    original_long = manager_module.LongTermMemory
    try:
        manager_module.ShortTermMemory = DummyShortTermMemory
        manager_module.LongTermMemory = DummyLongTermMemory

        cfg = Config()
        cfg.redis.host = "redis-service"
        cfg.redis.port = 6380
        cfg.redis.db = 2
        cfg.redis.password = "pw"
        cfg.redis.ttl_seconds = 3600
        cfg.milvus.host = "milvus-service"
        cfg.milvus.port = 19531
        cfg.milvus.alias = "default_v2"
        cfg.milvus.collection_name = "memory_runtime"
        cfg.milvus.similarity_threshold = 0.8
        cfg.memory.long_term_threshold = 0.75
        cfg.memory.short_term_window_size = 15
        cfg.memory.cross_session_recall = True

        manager = MemoryManager.from_config(config=cfg)

        assert manager.short_term.kwargs["host"] == "redis-service"
        assert manager.short_term.kwargs["port"] == 6380
        assert manager.short_term.kwargs["db"] == 2
        assert manager.short_term.kwargs["password"] == "pw"
        assert manager.short_term.kwargs["ttl"] == 3600
        assert manager.short_term.kwargs["max_items"] == 15

        assert manager.long_term.kwargs["host"] == "milvus-service"
        assert manager.long_term.kwargs["port"] == 19531
        assert manager.long_term.kwargs["alias"] == "default_v2"
        assert manager.long_term.kwargs["collection_name"] == "memory_runtime"
        assert manager.long_term.kwargs["importance_threshold"] == 0.75
        assert manager.long_term.kwargs["similarity_threshold"] == 0.8
        assert manager.cross_session_recall is True

        print("manual memory config check passed")
    finally:
        manager_module.ShortTermMemory = original_short
        manager_module.LongTermMemory = original_long


if __name__ == "__main__":
    main()
