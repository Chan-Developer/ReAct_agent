# -*- coding: utf-8 -*-
"""配置管理。

支持从 YAML 配置文件和环境变量加载配置。
优先级: 环境变量 > 配置文件 > 默认值
"""
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent


@dataclass
class LogConfig:
    """日志配置"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


@dataclass
class ModelScopeConfig:
    """ModelScope 配置"""
    api_key: str = ""
    base_url: str = "https://api-inference.modelscope.cn/v1"
    model: str = "Qwen/Qwen3-32B"


@dataclass
class VllmConfig:
    """vLLM 本地服务配置"""
    base_url: str = "http://localhost:8000/v1"
    model: str = "Qwen3-8B"


@dataclass
class LLMConfig:
    """LLM 通用配置"""
    provider: str = "modelscope"  # modelscope 或 vllm
    temperature: float = 0.7
    max_tokens: int = 1024
    timeout: int = 120
    modelscope: ModelScopeConfig = field(default_factory=ModelScopeConfig)
    vllm: VllmConfig = field(default_factory=VllmConfig)


@dataclass
class AgentConfig:
    """Agent 配置"""
    max_rounds: int = 5
    output_dir: str = "./output"


@dataclass
class Config:
    """全局配置"""
    log: LogConfig = field(default_factory=LogConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)
    
    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "Config":
        """加载配置。
        
        优先级: 环境变量 > 配置文件 > 默认值
        
        Args:
            config_path: 配置文件路径（可选）
            
        Returns:
            Config 实例
        """
        config = cls()
        
        # 1. 尝试从配置文件加载
        if config_path is None:
            config_path = PROJECT_ROOT / "configs" / "config.yaml"
        else:
            config_path = Path(config_path)
            
        if config_path.exists():
            config._load_from_yaml(config_path)
        
        # 2. 环境变量覆盖（优先级最高）
        config._load_from_env()
        
        return config
    
    def _load_from_yaml(self, path: Path) -> None:
        """从 YAML 文件加载配置。"""
        try:
            import yaml
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            
            # LLM 配置
            if "llm" in data:
                llm = data["llm"]
                if "provider" in llm:
                    self.llm.provider = llm["provider"]
                if "temperature" in llm:
                    self.llm.temperature = float(llm["temperature"])
                if "max_tokens" in llm:
                    self.llm.max_tokens = int(llm["max_tokens"])
                    
                # ModelScope 配置
                if "modelscope" in llm:
                    ms = llm["modelscope"]
                    if "api_key" in ms:
                        self.llm.modelscope.api_key = ms["api_key"]
                    if "base_url" in ms:
                        self.llm.modelscope.base_url = ms["base_url"]
                    if "model" in ms:
                        self.llm.modelscope.model = ms["model"]
                
                # vLLM 配置
                if "vllm" in llm:
                    vl = llm["vllm"]
                    if "base_url" in vl:
                        self.llm.vllm.base_url = vl["base_url"]
                    if "model" in vl:
                        self.llm.vllm.model = vl["model"]
            
            # Agent 配置
            if "agent" in data:
                agent = data["agent"]
                if "max_rounds" in agent:
                    self.agent.max_rounds = int(agent["max_rounds"])
                if "output_dir" in agent:
                    self.agent.output_dir = agent["output_dir"]
            
            # 日志配置
            if "logging" in data:
                if "level" in data["logging"]:
                    self.log.level = data["logging"]["level"]
                    
        except ImportError:
            pass  # 没有 PyYAML 就跳过
        except Exception:
            pass  # 配置文件解析失败就跳过
    
    def _load_from_env(self) -> None:
        """从环境变量加载配置。"""
        # ModelScope API Key（环境变量优先）
        if os.getenv("MODELSCOPE_API_KEY"):
            self.llm.modelscope.api_key = os.getenv("MODELSCOPE_API_KEY", "")
        if os.getenv("MODELSCOPE_BASE_URL"):
            self.llm.modelscope.base_url = os.getenv("MODELSCOPE_BASE_URL", "")
        if os.getenv("MODELSCOPE_MODEL"):
            self.llm.modelscope.model = os.getenv("MODELSCOPE_MODEL", "")
            
        # 其他配置
        if os.getenv("LOG_LEVEL"):
            self.log.level = os.getenv("LOG_LEVEL", "INFO")
        if os.getenv("LLM_TEMPERATURE"):
            self.llm.temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        if os.getenv("LLM_MAX_TOKENS"):
            self.llm.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "1024"))
        if os.getenv("AGENT_MAX_ROUNDS"):
            self.agent.max_rounds = int(os.getenv("AGENT_MAX_ROUNDS", "5"))


# 全局配置实例（延迟加载）
_config: Optional[Config] = None


def get_config() -> Config:
    """获取全局配置实例。"""
    global _config
    if _config is None:
        _config = Config.load()
    return _config


def reload_config(config_path: Optional[str] = None) -> Config:
    """重新加载配置。"""
    global _config
    _config = Config.load(config_path)
    return _config
