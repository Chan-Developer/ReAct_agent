# -*- coding: utf-8 -*-
"""Configuration loading utilities.

Priority: environment variables > YAML file > default values.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


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
    provider: str = "modelscope"  # modelscope or vllm
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


@dataclass
class RedisConfig:
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: str = ""


@dataclass
class MemoryConfig:
    enabled: bool = True
    long_term_threshold: float = 0.6
    short_term_ttl: int = 86400
    max_context_items: int = 5


@dataclass
class WebSearchConfig:
    provider: str = "duckduckgo"  # tavily or duckduckgo
    tavily_api_key: str = ""
    max_results: int = 5


@dataclass
class Config:
    log: LogConfig = field(default_factory=LogConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)
    milvus: MilvusConfig = field(default_factory=MilvusConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    web_search: WebSearchConfig = field(default_factory=WebSearchConfig)

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

        # Preferred parser if installed.
        try:
            from dotenv import load_dotenv

            for env_path in candidates:
                if env_path.exists():
                    load_dotenv(dotenv_path=env_path, override=False, encoding="utf-8")
            return
        except Exception:
            pass

        # Fallback parser.
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

            if "llm" in data:
                llm = data["llm"]
                if "provider" in llm:
                    self.llm.provider = llm["provider"]
                if "temperature" in llm:
                    self.llm.temperature = float(llm["temperature"])
                if "max_tokens" in llm:
                    self.llm.max_tokens = int(llm["max_tokens"])

                if "modelscope" in llm:
                    ms = llm["modelscope"]
                    if "api_key" in ms:
                        self.llm.modelscope.api_key = ms["api_key"]
                    if "base_url" in ms:
                        self.llm.modelscope.base_url = ms["base_url"]
                    if "model" in ms:
                        self.llm.modelscope.model = ms["model"]

                if "vllm" in llm:
                    vl = llm["vllm"]
                    if "base_url" in vl:
                        self.llm.vllm.base_url = vl["base_url"]
                    if "model" in vl:
                        self.llm.vllm.model = vl["model"]

            if "agent" in data:
                agent = data["agent"]
                if "max_rounds" in agent:
                    self.agent.max_rounds = int(agent["max_rounds"])
                if "output_dir" in agent:
                    self.agent.output_dir = agent["output_dir"]

            if "logging" in data and "level" in data["logging"]:
                self.log.level = data["logging"]["level"]

            if "milvus" in data:
                milvus = data["milvus"]
                if "host" in milvus:
                    self.milvus.host = milvus["host"]
                if "port" in milvus:
                    self.milvus.port = int(milvus["port"])
                if "alias" in milvus:
                    self.milvus.alias = milvus["alias"]

            if "web_search" in data:
                ws = data["web_search"]
                if "provider" in ws:
                    self.web_search.provider = ws["provider"]
                if "tavily_api_key" in ws:
                    self.web_search.tavily_api_key = ws["tavily_api_key"]
                if "max_results" in ws:
                    self.web_search.max_results = int(ws["max_results"])

            if "redis" in data:
                redis = data["redis"]
                if "host" in redis:
                    self.redis.host = redis["host"]
                if "port" in redis:
                    self.redis.port = int(redis["port"])
                if "db" in redis:
                    self.redis.db = int(redis["db"])
                if "password" in redis:
                    self.redis.password = redis["password"]

            if "memory" in data:
                mem = data["memory"]
                if "enabled" in mem:
                    self.memory.enabled = bool(mem["enabled"])
                if "long_term_threshold" in mem:
                    self.memory.long_term_threshold = float(mem["long_term_threshold"])
                if "short_term_ttl" in mem:
                    self.memory.short_term_ttl = int(mem["short_term_ttl"])
                if "max_context_items" in mem:
                    self.memory.max_context_items = int(mem["max_context_items"])

        except ImportError:
            pass
        except Exception:
            pass

    def _load_from_env(self) -> None:
        if os.getenv("MODELSCOPE_API_KEY"):
            self.llm.modelscope.api_key = os.getenv("MODELSCOPE_API_KEY", "")
        if os.getenv("MODELSCOPE_BASE_URL"):
            self.llm.modelscope.base_url = os.getenv("MODELSCOPE_BASE_URL", "")
        if os.getenv("MODELSCOPE_MODEL"):
            self.llm.modelscope.model = os.getenv("MODELSCOPE_MODEL", "")

        if os.getenv("LOG_LEVEL"):
            self.log.level = os.getenv("LOG_LEVEL", "INFO")
        if os.getenv("LLM_TEMPERATURE"):
            self.llm.temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        if os.getenv("LLM_MAX_TOKENS"):
            self.llm.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "1024"))
        if os.getenv("AGENT_MAX_ROUNDS"):
            self.agent.max_rounds = int(os.getenv("AGENT_MAX_ROUNDS", "5"))

        if os.getenv("MILVUS_HOST"):
            self.milvus.host = os.getenv("MILVUS_HOST", "localhost")
        if os.getenv("MILVUS_PORT"):
            self.milvus.port = int(os.getenv("MILVUS_PORT", "19530"))
        if os.getenv("MILVUS_ALIAS"):
            self.milvus.alias = os.getenv("MILVUS_ALIAS", "default")

        if os.getenv("TAVILY_API_KEY"):
            self.web_search.tavily_api_key = os.getenv("TAVILY_API_KEY", "")
        if os.getenv("WEB_SEARCH_PROVIDER"):
            self.web_search.provider = os.getenv("WEB_SEARCH_PROVIDER", "duckduckgo")
        if os.getenv("WEB_SEARCH_MAX_RESULTS"):
            self.web_search.max_results = int(os.getenv("WEB_SEARCH_MAX_RESULTS", "5"))

        if os.getenv("REDIS_HOST"):
            self.redis.host = os.getenv("REDIS_HOST", "localhost")
        if os.getenv("REDIS_PORT"):
            self.redis.port = int(os.getenv("REDIS_PORT", "6379"))
        if os.getenv("REDIS_PASSWORD"):
            self.redis.password = os.getenv("REDIS_PASSWORD", "")

        if os.getenv("MEMORY_ENABLED"):
            self.memory.enabled = os.getenv("MEMORY_ENABLED", "true").lower() == "true"
        if os.getenv("MEMORY_LONG_TERM_THRESHOLD"):
            self.memory.long_term_threshold = float(
                os.getenv("MEMORY_LONG_TERM_THRESHOLD", "0.6")
            )


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
