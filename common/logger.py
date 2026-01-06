# -*- coding: utf-8 -*-
"""日志管理。"""
import logging
import sys
from typing import Optional

_initialized = False

# 默认日志格式（避免循环导入）
_DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
_DEFAULT_LEVEL = "INFO"


def setup_logging(level: Optional[str] = None) -> None:
    """初始化日志"""
    global _initialized
    if _initialized:
        return
    
    # 延迟导入配置，避免循环依赖
    try:
        from .config import get_config
        config = get_config()
        log_level = level or config.log.level
        log_format = config.log.format
    except Exception:
        log_level = level or _DEFAULT_LEVEL
        log_format = _DEFAULT_FORMAT
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format=log_format,
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    _initialized = True


def get_logger(name: str) -> logging.Logger:
    """获取日志器"""
    if not _initialized:
        setup_logging()
    return logging.getLogger(name)


def set_level(level: str) -> None:
    """设置日志级别"""
    logging.getLogger().setLevel(getattr(logging, level.upper(), logging.INFO))
