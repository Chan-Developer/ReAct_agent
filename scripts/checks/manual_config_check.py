# -*- coding: utf-8 -*-
"""Minimal runtime verification for V2 config loading."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from common.config import Config


def check_env_override() -> None:
    os.environ["GATEWAY_PORT"] = "8123"
    os.environ["MEMORY_CROSS_SESSION_RECALL"] = "true"
    os.environ["TRACING_SAMPLE_RATE"] = "0.5"

    cfg = Config.load(config_path=str(Path(tempfile.gettempdir()) / "missing.yaml"))
    assert cfg.gateway.port == 8123
    assert cfg.memory.cross_session_recall is True
    assert cfg.tracing.sample_rate == 0.5


def check_yaml_loading() -> None:
    try:
        import yaml  # noqa: F401
    except Exception:
        print("yaml not installed; skipped yaml config check")
        return

    with tempfile.TemporaryDirectory() as tmp_dir:
        config_path = Path(tmp_dir) / "config.yaml"
        config_path.write_text(
            """
gateway:
  host: "127.0.0.1"
  port: 9000
runtime:
  default_harness: "per"
tracing:
  exporter: "stdout"
reflection:
  quality_threshold: 0.8
memory:
  cross_session_recall: true
milvus:
  collection_name: "memory_v2"
""",
            encoding="utf-8",
        )
        cfg = Config.load(config_path=str(config_path))
        assert cfg.gateway.host == "127.0.0.1"
        assert cfg.gateway.port == 8123 or cfg.gateway.port == 9000
        assert cfg.runtime.default_harness == "per"
        assert cfg.tracing.exporter == "stdout"
        assert cfg.reflection.quality_threshold == 0.8
        assert cfg.memory.cross_session_recall is True
        assert cfg.milvus.collection_name == "memory_v2"


def main() -> None:
    check_env_override()
    check_yaml_loading()
    print("manual config check passed")


if __name__ == "__main__":
    main()
