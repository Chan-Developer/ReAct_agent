# -*- coding: utf-8 -*-
"""Configuration loading utilities.

Priority: environment variables > YAML file > default values.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


PROJECT_ROOT = Path(__file__).parent.parent


@dataclass
class LogConfig:
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


@dataclass
class ModelScopeConfig:
    api_key: str = ""
    base_url: str = "https://api-inference.modelscope.cn/v1"
    model: str = "Qwen/Qwen3-32B"


@dataclass
class VllmConfig:
    base_url: str = "http://localhost:8000/v1"
    model: str = "Qwen3-8B"


@dataclass
class LLMConfig:
    provider: str = "modelscope"
    temperature: float = 0.7
    max_tokens: int = 1024
    timeout: int = 120
    modelscope: ModelScopeConfig = field(default_factory=ModelScopeConfig)
    vllm: VllmConfig = field(default_factory=VllmConfig)


@dataclass
class AgentConfig:
    max_rounds: int = 5
    output_dir: str = "./output"


@dataclass
class MilvusConfig:
    host: str = "localhost"
    port: int = 19530
    alias: str = "default"
    collection_name: str = "agent_long_term_memory"
    top_k: int = 5
    similarity_threshold: float = 0.75


@dataclass
class RedisConfig:
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: str = ""
    ttl_seconds: int = 86400


@dataclass
class MemoryConfig:
    enabled: bool = True
    long_term_threshold: float = 0.6
    short_term_ttl: int = 86400
    max_context_items: int = 5
    short_term_window_size: int = 12
    summary_trigger_tokens: int = 6000
    summary_max_tokens: int = 600
    cross_session_recall: bool = False
    long_term_recency_half_life_days: int = 30
    long_term_recency_weight: float = 0.2
    long_term_consolidation_enabled: bool = True
    long_term_consolidation_max_age_days: int = 14
    long_term_consolidation_batch_size: int = 50
    long_term_consolidation_group_size: int = 5
    long_term_maintenance_interval: int = 10


@dataclass
class WebSearchConfig:
    provider: str = "duckduckgo"
    tavily_api_key: str = ""
    max_results: int = 5


@dataclass
class GatewayConfig:
    host: str = "0.0.0.0"
    port: int = 8080
    cors_origins: list[str] = field(default_factory=lambda: ["http://localhost:3000"])


@dataclass
class RuntimeConfig:
    default_harness: str = "react"
    max_concurrent_runs: int = 32
    checkpoint_enabled: bool = True
    checkpoint_store: str = "postgres"


@dataclass
class TracingConfig:
    enabled: bool = True
    exporter: str = "postgres"
    sample_rate: float = 1.0
    save_prompt_preview: bool = True


@dataclass
class ReflectionConfig:
    enabled: bool = True
    quality_threshold: float = 0.65
    hallucination_threshold: float = 0.35
    retry_on_bad_score: bool = True
    max_retry_rounds: int = 1


@dataclass
class ETLConfig:
    enabled: bool = True
    input_formats: list[str] = field(default_factory=lambda: ["pdf", "txt", "md"])
    chunk_strategy: str = "semantic_chunk"
    chunk_size: int = 800
    chunk_overlap: int = 100
    semantic_chunk_min_size: int = 300


@dataclass
class WorkerConfig:
    enabled: bool = True
    queue_backend: str = "redis"
    concurrency: int = 8
    max_retries: int = 2


@dataclass
class StorageConfig:
    session_store: str = "postgres"
    trace_store: str = "postgres"
    artifact_store: str = "local"


@dataclass
class Config:
    log: LogConfig = field(default_factory=LogConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)
    milvus: MilvusConfig = field(default_factory=MilvusConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    web_search: WebSearchConfig = field(default_factory=WebSearchConfig)
    gateway: GatewayConfig = field(default_factory=GatewayConfig)
    runtime: RuntimeConfig = field(default_factory=RuntimeConfig)
    tracing: TracingConfig = field(default_factory=TracingConfig)
    reflection: ReflectionConfig = field(default_factory=ReflectionConfig)
    etl: ETLConfig = field(default_factory=ETLConfig)
    worker: WorkerConfig = field(default_factory=WorkerConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "Config":
        config = cls()
        config._load_dotenv()

        if config_path is None:
            config_path = PROJECT_ROOT / "configs" / "config.yaml"
        else:
            config_path = Path(config_path)

        if config_path.exists():
            config._load_from_yaml(config_path)

        config._load_from_env()
        return config

    def _load_dotenv(self) -> None:
        """Load .env values into os.environ without overriding existing env."""
        candidates = [PROJECT_ROOT / ".env"]
        cwd_env = Path.cwd() / ".env"
        if cwd_env not in candidates:
            candidates.append(cwd_env)

        try:
            from dotenv import load_dotenv

            for env_path in candidates:
                if env_path.exists():
                    load_dotenv(dotenv_path=env_path, override=False, encoding="utf-8")
            return
        except Exception:
            pass

        for env_path in candidates:
            if not env_path.exists():
                continue
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for raw in f:
                        line = raw.strip()
                        if not line or line.startswith("#"):
                            continue
                        if line.startswith("export "):
                            line = line[7:].strip()
                        if "=" not in line:
                            continue

                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip()

                        if (value.startswith('"') and value.endswith('"')) or (
                            value.startswith("'") and value.endswith("'")
                        ):
                            value = value[1:-1]

                        if key:
                            os.environ.setdefault(key, value)
            except Exception:
                pass

    def _load_from_yaml(self, path: Path) -> None:
        try:
            import yaml

            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

            self._apply_yaml(data)
        except ImportError:
            pass
        except Exception:
            pass

    def _apply_yaml(self, data: dict[str, Any]) -> None:
        self._apply_mapping(
            data.get("llm", {}),
            self.llm,
            {
                "provider": "provider",
                "temperature": ("temperature", float),
                "max_tokens": ("max_tokens", int),
                "timeout": ("timeout", int),
            },
        )
        self._apply_mapping(
            data.get("llm", {}).get("modelscope", {}),
            self.llm.modelscope,
            {"api_key": "api_key", "base_url": "base_url", "model": "model"},
        )
        self._apply_mapping(
            data.get("llm", {}).get("vllm", {}),
            self.llm.vllm,
            {"base_url": "base_url", "model": "model"},
        )

        self._apply_mapping(
            data.get("agent", {}),
            self.agent,
            {"max_rounds": ("max_rounds", int), "output_dir": "output_dir"},
        )
        self._apply_mapping(
            data.get("logging", {}),
            self.log,
            {"level": "level", "format": "format"},
        )
        self._apply_mapping(
            data.get("milvus", {}),
            self.milvus,
            {
                "host": "host",
                "port": ("port", int),
                "alias": "alias",
                "collection_name": "collection_name",
                "top_k": ("top_k", int),
                "similarity_threshold": ("similarity_threshold", float),
            },
        )
        self._apply_mapping(
            data.get("redis", {}),
            self.redis,
            {
                "host": "host",
                "port": ("port", int),
                "db": ("db", int),
                "password": "password",
                "ttl_seconds": ("ttl_seconds", int),
            },
        )
        self._apply_mapping(
            data.get("memory", {}),
            self.memory,
            {
                "enabled": ("enabled", self._as_bool),
                "long_term_threshold": ("long_term_threshold", float),
                "short_term_ttl": ("short_term_ttl", int),
                "max_context_items": ("max_context_items", int),
                "short_term_window_size": ("short_term_window_size", int),
                "summary_trigger_tokens": ("summary_trigger_tokens", int),
                "summary_max_tokens": ("summary_max_tokens", int),
                "cross_session_recall": ("cross_session_recall", self._as_bool),
                "long_term_recency_half_life_days": (
                    "long_term_recency_half_life_days",
                    int,
                ),
                "long_term_recency_weight": ("long_term_recency_weight", float),
                "long_term_consolidation_enabled": (
                    "long_term_consolidation_enabled",
                    self._as_bool,
                ),
                "long_term_consolidation_max_age_days": (
                    "long_term_consolidation_max_age_days",
                    int,
                ),
                "long_term_consolidation_batch_size": (
                    "long_term_consolidation_batch_size",
                    int,
                ),
                "long_term_consolidation_group_size": (
                    "long_term_consolidation_group_size",
                    int,
                ),
                "long_term_maintenance_interval": (
                    "long_term_maintenance_interval",
                    int,
                ),
            },
        )
        self._apply_mapping(
            data.get("web_search", {}),
            self.web_search,
            {
                "provider": "provider",
                "tavily_api_key": "tavily_api_key",
                "max_results": ("max_results", int),
            },
        )
        self._apply_mapping(
            data.get("gateway", {}),
            self.gateway,
            {
                "host": "host",
                "port": ("port", int),
                "cors_origins": ("cors_origins", list),
            },
        )
        self._apply_mapping(
            data.get("runtime", {}),
            self.runtime,
            {
                "default_harness": "default_harness",
                "max_concurrent_runs": ("max_concurrent_runs", int),
                "checkpoint_enabled": ("checkpoint_enabled", self._as_bool),
                "checkpoint_store": "checkpoint_store",
            },
        )
        self._apply_mapping(
            data.get("tracing", {}),
            self.tracing,
            {
                "enabled": ("enabled", self._as_bool),
                "exporter": "exporter",
                "sample_rate": ("sample_rate", float),
                "save_prompt_preview": ("save_prompt_preview", self._as_bool),
            },
        )
        self._apply_mapping(
            data.get("reflection", {}),
            self.reflection,
            {
                "enabled": ("enabled", self._as_bool),
                "quality_threshold": ("quality_threshold", float),
                "hallucination_threshold": ("hallucination_threshold", float),
                "retry_on_bad_score": ("retry_on_bad_score", self._as_bool),
                "max_retry_rounds": ("max_retry_rounds", int),
            },
        )
        self._apply_mapping(
            data.get("etl", {}),
            self.etl,
            {
                "enabled": ("enabled", self._as_bool),
                "input_formats": ("input_formats", list),
                "chunk_strategy": "chunk_strategy",
                "chunk_size": ("chunk_size", int),
                "chunk_overlap": ("chunk_overlap", int),
                "semantic_chunk_min_size": ("semantic_chunk_min_size", int),
            },
        )
        self._apply_mapping(
            data.get("worker", {}),
            self.worker,
            {
                "enabled": ("enabled", self._as_bool),
                "queue_backend": "queue_backend",
                "concurrency": ("concurrency", int),
                "max_retries": ("max_retries", int),
            },
        )
        self._apply_mapping(
            data.get("storage", {}),
            self.storage,
            {
                "session_store": "session_store",
                "trace_store": "trace_store",
                "artifact_store": "artifact_store",
            },
        )

    def _apply_mapping(self, source: dict[str, Any], target: Any, mapping: dict[str, Any]) -> None:
        for source_key, target_spec in mapping.items():
            if source_key not in source:
                continue
            if isinstance(target_spec, tuple):
                attr_name, caster = target_spec
                setattr(target, attr_name, caster(source[source_key]))
            else:
                setattr(target, target_spec, source[source_key])

    @staticmethod
    def _as_bool(value: Any) -> bool:
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in {"1", "true", "yes", "on"}

    def _load_from_env(self) -> None:
        self._apply_env("MODELSCOPE_API_KEY", self.llm.modelscope, "api_key")
        self._apply_env("MODELSCOPE_BASE_URL", self.llm.modelscope, "base_url")
        self._apply_env("MODELSCOPE_MODEL", self.llm.modelscope, "model")
        self._apply_env("VLLM_BASE_URL", self.llm.vllm, "base_url")
        self._apply_env("VLLM_MODEL", self.llm.vllm, "model")

        self._apply_env("LOG_LEVEL", self.log, "level")
        self._apply_env("LOG_FORMAT", self.log, "format")
        self._apply_env("LLM_PROVIDER", self.llm, "provider")
        self._apply_env("LLM_TEMPERATURE", self.llm, "temperature", float)
        self._apply_env("LLM_MAX_TOKENS", self.llm, "max_tokens", int)
        self._apply_env("LLM_TIMEOUT", self.llm, "timeout", int)
        self._apply_env("AGENT_MAX_ROUNDS", self.agent, "max_rounds", int)
        self._apply_env("AGENT_OUTPUT_DIR", self.agent, "output_dir")

        self._apply_env("MILVUS_HOST", self.milvus, "host")
        self._apply_env("MILVUS_PORT", self.milvus, "port", int)
        self._apply_env("MILVUS_ALIAS", self.milvus, "alias")
        self._apply_env("MILVUS_COLLECTION_NAME", self.milvus, "collection_name")
        self._apply_env("MILVUS_TOP_K", self.milvus, "top_k", int)
        self._apply_env(
            "MILVUS_SIMILARITY_THRESHOLD",
            self.milvus,
            "similarity_threshold",
            float,
        )

        self._apply_env("REDIS_HOST", self.redis, "host")
        self._apply_env("REDIS_PORT", self.redis, "port", int)
        self._apply_env("REDIS_DB", self.redis, "db", int)
        self._apply_env("REDIS_PASSWORD", self.redis, "password")
        self._apply_env("REDIS_TTL_SECONDS", self.redis, "ttl_seconds", int)

        self._apply_env("MEMORY_ENABLED", self.memory, "enabled", self._as_bool)
        self._apply_env(
            "MEMORY_LONG_TERM_THRESHOLD",
            self.memory,
            "long_term_threshold",
            float,
        )
        self._apply_env("MEMORY_SHORT_TERM_TTL", self.memory, "short_term_ttl", int)
        self._apply_env("MEMORY_MAX_CONTEXT_ITEMS", self.memory, "max_context_items", int)
        self._apply_env(
            "MEMORY_SHORT_TERM_WINDOW_SIZE",
            self.memory,
            "short_term_window_size",
            int,
        )
        self._apply_env(
            "MEMORY_SUMMARY_TRIGGER_TOKENS",
            self.memory,
            "summary_trigger_tokens",
            int,
        )
        self._apply_env(
            "MEMORY_SUMMARY_MAX_TOKENS",
            self.memory,
            "summary_max_tokens",
            int,
        )
        self._apply_env(
            "MEMORY_CROSS_SESSION_RECALL",
            self.memory,
            "cross_session_recall",
            self._as_bool,
        )
        self._apply_env(
            "MEMORY_LONG_TERM_RECENCY_HALF_LIFE_DAYS",
            self.memory,
            "long_term_recency_half_life_days",
            int,
        )
        self._apply_env(
            "MEMORY_LONG_TERM_RECENCY_WEIGHT",
            self.memory,
            "long_term_recency_weight",
            float,
        )
        self._apply_env(
            "MEMORY_LONG_TERM_CONSOLIDATION_ENABLED",
            self.memory,
            "long_term_consolidation_enabled",
            self._as_bool,
        )
        self._apply_env(
            "MEMORY_LONG_TERM_CONSOLIDATION_MAX_AGE_DAYS",
            self.memory,
            "long_term_consolidation_max_age_days",
            int,
        )
        self._apply_env(
            "MEMORY_LONG_TERM_CONSOLIDATION_BATCH_SIZE",
            self.memory,
            "long_term_consolidation_batch_size",
            int,
        )
        self._apply_env(
            "MEMORY_LONG_TERM_CONSOLIDATION_GROUP_SIZE",
            self.memory,
            "long_term_consolidation_group_size",
            int,
        )
        self._apply_env(
            "MEMORY_LONG_TERM_MAINTENANCE_INTERVAL",
            self.memory,
            "long_term_maintenance_interval",
            int,
        )

        self._apply_env("TAVILY_API_KEY", self.web_search, "tavily_api_key")
        self._apply_env("WEB_SEARCH_PROVIDER", self.web_search, "provider")
        self._apply_env("WEB_SEARCH_MAX_RESULTS", self.web_search, "max_results", int)

        self._apply_env("GATEWAY_HOST", self.gateway, "host")
        self._apply_env("GATEWAY_PORT", self.gateway, "port", int)
        self._apply_env(
            "GATEWAY_CORS_ORIGINS",
            self.gateway,
            "cors_origins",
            lambda value: [item.strip() for item in value.split(",") if item.strip()],
        )

        self._apply_env("RUNTIME_DEFAULT_HARNESS", self.runtime, "default_harness")
        self._apply_env(
            "RUNTIME_MAX_CONCURRENT_RUNS",
            self.runtime,
            "max_concurrent_runs",
            int,
        )
        self._apply_env(
            "RUNTIME_CHECKPOINT_ENABLED",
            self.runtime,
            "checkpoint_enabled",
            self._as_bool,
        )
        self._apply_env("RUNTIME_CHECKPOINT_STORE", self.runtime, "checkpoint_store")

        self._apply_env("TRACING_ENABLED", self.tracing, "enabled", self._as_bool)
        self._apply_env("TRACING_EXPORTER", self.tracing, "exporter")
        self._apply_env("TRACING_SAMPLE_RATE", self.tracing, "sample_rate", float)
        self._apply_env(
            "TRACING_SAVE_PROMPT_PREVIEW",
            self.tracing,
            "save_prompt_preview",
            self._as_bool,
        )

        self._apply_env("REFLECTION_ENABLED", self.reflection, "enabled", self._as_bool)
        self._apply_env(
            "REFLECTION_QUALITY_THRESHOLD",
            self.reflection,
            "quality_threshold",
            float,
        )
        self._apply_env(
            "REFLECTION_HALLUCINATION_THRESHOLD",
            self.reflection,
            "hallucination_threshold",
            float,
        )
        self._apply_env(
            "REFLECTION_RETRY_ON_BAD_SCORE",
            self.reflection,
            "retry_on_bad_score",
            self._as_bool,
        )
        self._apply_env(
            "REFLECTION_MAX_RETRY_ROUNDS",
            self.reflection,
            "max_retry_rounds",
            int,
        )

        self._apply_env("ETL_ENABLED", self.etl, "enabled", self._as_bool)
        self._apply_env(
            "ETL_INPUT_FORMATS",
            self.etl,
            "input_formats",
            lambda value: [item.strip() for item in value.split(",") if item.strip()],
        )
        self._apply_env("ETL_CHUNK_STRATEGY", self.etl, "chunk_strategy")
        self._apply_env("ETL_CHUNK_SIZE", self.etl, "chunk_size", int)
        self._apply_env("ETL_CHUNK_OVERLAP", self.etl, "chunk_overlap", int)
        self._apply_env(
            "ETL_SEMANTIC_CHUNK_MIN_SIZE",
            self.etl,
            "semantic_chunk_min_size",
            int,
        )

        self._apply_env("WORKER_ENABLED", self.worker, "enabled", self._as_bool)
        self._apply_env("WORKER_QUEUE_BACKEND", self.worker, "queue_backend")
        self._apply_env("WORKER_CONCURRENCY", self.worker, "concurrency", int)
        self._apply_env("WORKER_MAX_RETRIES", self.worker, "max_retries", int)

        self._apply_env("SESSION_STORE", self.storage, "session_store")
        self._apply_env("TRACE_STORE", self.storage, "trace_store")
        self._apply_env("ARTIFACT_STORE", self.storage, "artifact_store")

    @staticmethod
    def _apply_env(env_key: str, target: Any, attr_name: str, caster=None) -> None:
        value = os.getenv(env_key)
        if value is None:
            return
        setattr(target, attr_name, caster(value) if caster else value)


_config: Optional[Config] = None


def get_config() -> Config:
    global _config
    if _config is None:
        _config = Config.load()
    return _config


def reload_config(config_path: Optional[str] = None) -> Config:
    global _config
    _config = Config.load(config_path)
    return _config
