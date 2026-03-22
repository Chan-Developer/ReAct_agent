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
