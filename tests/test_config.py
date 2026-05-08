# -*- coding: utf-8 -*-
"""Config loading tests."""

from pathlib import Path


def test_loads_env_from_dotenv(monkeypatch, tmp_path: Path):
    from common import config as config_module

    monkeypatch.setattr(config_module, "PROJECT_ROOT", tmp_path)
    monkeypatch.delenv("REDIS_PASSWORD", raising=False)
    monkeypatch.delenv("REDIS_HOST", raising=False)

    (tmp_path / ".env").write_text(
        "REDIS_PASSWORD=from_dotenv\nREDIS_HOST=redis-from-dotenv\n",
        encoding="utf-8",
    )

    cfg = config_module.Config.load(config_path=str(tmp_path / "missing.yaml"))

    assert cfg.redis.password == "from_dotenv"
    assert cfg.redis.host == "redis-from-dotenv"


def test_env_overrides_dotenv(monkeypatch, tmp_path: Path):
    from common import config as config_module

    monkeypatch.setattr(config_module, "PROJECT_ROOT", tmp_path)
    monkeypatch.setenv("REDIS_PASSWORD", "from_env")

    (tmp_path / ".env").write_text("REDIS_PASSWORD=from_dotenv\n", encoding="utf-8")

    cfg = config_module.Config.load(config_path=str(tmp_path / "missing.yaml"))

    assert cfg.redis.password == "from_env"


def test_dotenv_parses_quoted_values(monkeypatch, tmp_path: Path):
    from common import config as config_module

    monkeypatch.setattr(config_module, "PROJECT_ROOT", tmp_path)
    monkeypatch.delenv("REDIS_PASSWORD", raising=False)

    (tmp_path / ".env").write_text('REDIS_PASSWORD="quoted_value"\n', encoding="utf-8")

    cfg = config_module.Config.load(config_path=str(tmp_path / "missing.yaml"))

    assert cfg.redis.password == "quoted_value"


def test_loads_v2_yaml_sections(tmp_path: Path):
    from common.config import Config

    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """
gateway:
  host: "127.0.0.1"
  port: 9000
  cors_origins:
    - "http://localhost:5173"
runtime:
  default_harness: "per"
  max_concurrent_runs: 64
tracing:
  enabled: true
  exporter: "stdout"
reflection:
  quality_threshold: 0.8
memory:
  cross_session_recall: true
milvus:
  collection_name: "memory_v2"
etl:
  chunk_strategy: "hierarchical_chunk"
worker:
  concurrency: 16
storage:
  trace_store: "postgres"
""",
        encoding="utf-8",
    )

    cfg = Config.load(config_path=str(config_path))

    assert cfg.gateway.host == "127.0.0.1"
    assert cfg.gateway.port == 9000
    assert cfg.runtime.default_harness == "per"
    assert cfg.runtime.max_concurrent_runs == 64
    assert cfg.tracing.exporter == "stdout"
    assert cfg.reflection.quality_threshold == 0.8
    assert cfg.memory.cross_session_recall is True
    assert cfg.milvus.collection_name == "memory_v2"
    assert cfg.etl.chunk_strategy == "hierarchical_chunk"
    assert cfg.worker.concurrency == 16
    assert cfg.storage.trace_store == "postgres"


def test_env_overrides_v2_fields(monkeypatch, tmp_path: Path):
    from common.config import Config

    monkeypatch.setenv("GATEWAY_PORT", "8123")
    monkeypatch.setenv("MEMORY_CROSS_SESSION_RECALL", "true")
    monkeypatch.setenv("TRACING_SAMPLE_RATE", "0.5")

    cfg = Config.load(config_path=str(tmp_path / "missing.yaml"))

    assert cfg.gateway.port == 8123
    assert cfg.memory.cross_session_recall is True
    assert cfg.tracing.sample_rate == 0.5
