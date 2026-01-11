# -*- coding: utf-8 -*-
"""模板注册表。

管理所有可用模板，支持：
1. 从 presets/ 目录自动加载 JSON 模板
2. 注册自定义 Python 模板类
3. 根据职位描述智能匹配模板
"""
from __future__ import annotations

import os
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Tuple

from .base import BaseTemplate, TemplateConfig

# 单例注册表
_registry: Optional["TemplateRegistry"] = None


def get_registry() -> "TemplateRegistry":
    """获取全局模板注册表（单例）"""
    global _registry
    if _registry is None:
        _registry = TemplateRegistry()
        _registry.load_presets()
    return _registry


class TemplateRegistry:
    """模板注册表
    
    管理所有可用的简历模板，支持：
    - 从 JSON 文件加载预设模板
    - 注册自定义 Python 模板类
    - 根据职位描述智能匹配最佳模板
    """
    
    def __init__(self):
        self._templates: Dict[str, TemplateConfig] = {}
        self._custom_templates: Dict[str, Type[BaseTemplate]] = {}
        self._presets_dir = Path(__file__).parent / "presets"
        self._custom_dir = Path(__file__).parent / "custom"
    
    def load_presets(self) -> None:
        """从 presets 目录加载所有 JSON 模板"""
        if not self._presets_dir.exists():
            return
        
        for json_file in self._presets_dir.glob("*.json"):
            try:
                config = TemplateConfig.from_json(str(json_file))
                self._templates[config.name] = config
            except Exception as e:
                print(f"[TemplateRegistry] 加载模板失败 {json_file}: {e}")
    
    def register(self, config: TemplateConfig) -> None:
        """注册模板配置
        
        Args:
            config: 模板配置对象
        """
        self._templates[config.name] = config
    
    def register_class(self, template_class: Type[BaseTemplate]) -> None:
        """注册自定义模板类
        
        Args:
            template_class: 继承自 BaseTemplate 的模板类
        """
        instance = template_class()
        self._custom_templates[instance.name] = template_class
        self._templates[instance.name] = instance.config
    
    def get(self, name: str) -> Optional[TemplateConfig]:
        """获取指定名称的模板配置
        
        Args:
            name: 模板名称
            
        Returns:
            模板配置，如果不存在则返回 None
        """
        return self._templates.get(name)
    
    def get_template_instance(self, name: str) -> Optional[BaseTemplate]:
        """获取自定义模板类的实例
        
        Args:
            name: 模板名称
            
        Returns:
            模板实例，如果不是自定义类则返回 None
        """
        if name in self._custom_templates:
            return self._custom_templates[name]()
        return None
    
    def list_all(self) -> List[Dict[str, Any]]:
        """列出所有可用模板
        
        Returns:
            模板信息列表
        """
        result = []
        for name, config in self._templates.items():
            result.append({
                "name": name,
                "display_name": config.display_name,
                "description": config.description,
                "tags": config.tags,
                "page_preference": config.page_preference,
                "style": config.style,
            })
        return result
    
    def list_by_tag(self, tag: str) -> List[TemplateConfig]:
        """按标签筛选模板
        
        Args:
            tag: 标签名称
            
        Returns:
            匹配的模板配置列表
        """
        return [
            config for config in self._templates.values()
            if tag.lower() in [t.lower() for t in config.tags]
        ]
    
    def match_job(self, job_description: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """根据职位描述匹配最佳模板
        
        Args:
            job_description: 职位描述文本
            top_k: 返回前 k 个匹配结果
            
        Returns:
            [(模板名称, 匹配分数), ...] 按分数降序排列
        """
        if not job_description:
            return []
        
        jd_lower = job_description.lower()
        scores = []
        
        for name, config in self._templates.items():
            score = 0.0
            total_keywords = len(config.job_keywords)
            
            if total_keywords > 0:
                matched = sum(
                    1 for kw in config.job_keywords
                    if kw.lower() in jd_lower
                )
                score = matched / total_keywords
            
            # 标签也参与匹配
            tag_matched = sum(
                1 for tag in config.tags
                if tag.lower() in jd_lower
            )
            if config.tags:
                score += 0.3 * (tag_matched / len(config.tags))
            
            scores.append((name, min(score, 1.0)))
        
        # 按分数降序排序
        scores.sort(key=lambda x: x[1], reverse=True)
        
        return scores[:top_k]
    
    def get_best_match(self, job_description: str) -> Optional[TemplateConfig]:
        """获取最匹配职位描述的模板
        
        Args:
            job_description: 职位描述文本
            
        Returns:
            最匹配的模板配置，无匹配时返回默认模板
        """
        matches = self.match_job(job_description, top_k=1)
        
        if matches and matches[0][1] > 0.1:
            return self._templates.get(matches[0][0])
        
        # 返回默认模板
        if "tech_modern" in self._templates:
            return self._templates["tech_modern"]
        
        # 返回任意一个
        if self._templates:
            return next(iter(self._templates.values()))
        
        return None
    
    def create_from_dict(self, data: Dict[str, Any]) -> TemplateConfig:
        """从字典创建临时模板配置
        
        Args:
            data: 配置字典
            
        Returns:
            模板配置对象
        """
        return TemplateConfig.from_dict(data)
    
    @property
    def available_templates(self) -> List[str]:
        """获取所有可用模板名称"""
        return list(self._templates.keys())
    
    def __len__(self) -> int:
        return len(self._templates)
    
    def __contains__(self, name: str) -> bool:
        return name in self._templates
