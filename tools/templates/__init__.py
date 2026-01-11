# -*- coding: utf-8 -*-
"""模板系统模块。

提供简历模板的管理、注册和选择功能。

支持两种模板定义方式：
1. JSON 配置文件（简单场景）
2. Python 类继承（高级自定义）
"""

from .base import BaseTemplate, TemplateConfig
from .registry import TemplateRegistry, get_registry

__all__ = [
    "BaseTemplate",
    "TemplateConfig", 
    "TemplateRegistry",
    "get_registry",
]
