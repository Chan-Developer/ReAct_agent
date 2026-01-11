# -*- coding: utf-8 -*-
"""模板基类定义。

提供模板的基础数据结构和抽象接口。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import json


@dataclass
class FontConfig:
    """字体配置"""
    title_size: int = 16
    heading_size: int = 10
    subheading_size: int = 9
    body_size: int = 9
    small_size: int = 8
    family: str = "Microsoft YaHei"


@dataclass
class SpacingConfig:
    """间距配置"""
    margin: float = 0.4
    section_gap: int = 4
    item_gap: int = 1
    line_height: float = 1.0


@dataclass
class ColorConfig:
    """颜色配置"""
    primary: str = "#000000"
    secondary: str = "#333333"
    accent: str = "#0066cc"
    text: str = "#000000"


@dataclass
class TemplateConfig:
    """模板配置数据类
    
    包含模板的所有配置项，可从 JSON 或 Python 代码创建。
    """
    # 基本信息
    name: str = "default"
    display_name: str = "默认模板"
    description: str = ""
    tags: List[str] = field(default_factory=list)
    job_keywords: List[str] = field(default_factory=list)
    
    # 页面偏好
    page_preference: str = "auto"  # "one_page", "two_pages", "auto"
    
    # 章节配置
    section_order: List[str] = field(default_factory=lambda: [
        "header", "summary", "experience", "projects", "skills", "education"
    ])
    section_weights: Dict[str, float] = field(default_factory=lambda: {
        "experience": 1.0,
        "projects": 1.0,
        "skills": 1.0,
        "education": 0.8,
    })
    
    # 样式配置
    style: str = "modern"  # modern, classic, minimal, creative
    color_scheme: str = "professional"
    font_config: FontConfig = field(default_factory=FontConfig)
    spacing_config: SpacingConfig = field(default_factory=SpacingConfig)
    color_config: ColorConfig = field(default_factory=ColorConfig)
    
    # 视觉元素
    use_icons: bool = True
    use_skill_bars: bool = False
    use_timeline: bool = False
    highlight_keywords: bool = True
    
    # 内容限制
    max_experiences: int = 4
    max_projects: int = 3
    max_highlights_per_item: int = 4
    max_skills: int = 15
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TemplateConfig":
        """从字典创建配置"""
        # 处理嵌套的配置对象
        font_data = data.pop("font_config", {})
        spacing_data = data.pop("spacing_config", {})
        color_data = data.pop("color_config", {})
        
        # 兼容旧格式 style.font_config
        if "style" in data and isinstance(data["style"], dict):
            style_dict = data.pop("style")
            if "font_config" in style_dict:
                font_data.update(style_dict["font_config"])
            if "spacing_config" in style_dict:
                spacing_data.update(style_dict["spacing_config"])
            if "color_scheme" in style_dict:
                data["color_scheme"] = style_dict["color_scheme"]
        
        font_config = FontConfig(**font_data) if font_data else FontConfig()
        spacing_config = SpacingConfig(**spacing_data) if spacing_data else SpacingConfig()
        color_config = ColorConfig(**color_data) if color_data else ColorConfig()
        
        return cls(
            font_config=font_config,
            spacing_config=spacing_config,
            color_config=color_config,
            **data
        )
    
    @classmethod
    def from_json(cls, json_path: str) -> "TemplateConfig":
        """从 JSON 文件加载配置"""
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "tags": self.tags,
            "job_keywords": self.job_keywords,
            "page_preference": self.page_preference,
            "section_order": self.section_order,
            "section_weights": self.section_weights,
            "style": self.style,
            "color_scheme": self.color_scheme,
            "font_config": {
                "title_size": self.font_config.title_size,
                "heading_size": self.font_config.heading_size,
                "subheading_size": self.font_config.subheading_size,
                "body_size": self.font_config.body_size,
                "small_size": self.font_config.small_size,
                "family": self.font_config.family,
            },
            "spacing_config": {
                "margin": self.spacing_config.margin,
                "section_gap": self.spacing_config.section_gap,
                "item_gap": self.spacing_config.item_gap,
                "line_height": self.spacing_config.line_height,
            },
            "use_icons": self.use_icons,
            "use_skill_bars": self.use_skill_bars,
            "use_timeline": self.use_timeline,
            "max_experiences": self.max_experiences,
            "max_projects": self.max_projects,
            "max_highlights_per_item": self.max_highlights_per_item,
        }
    
    def to_layout_config(self) -> Dict[str, Any]:
        """转换为 LayoutAgent 兼容的配置格式"""
        return {
            "section_order": self.section_order,
            "style": self.style,
            "color_scheme": self.color_scheme,
            "font_config": {
                "title_size": self.font_config.title_size,
                "heading_size": self.font_config.heading_size,
                "subheading_size": self.font_config.subheading_size,
                "body_size": self.font_config.body_size,
                "small_size": self.font_config.small_size,
            },
            "spacing_config": {
                "margin": self.spacing_config.margin,
                "section_gap": self.spacing_config.section_gap,
                "item_gap": self.spacing_config.item_gap,
                "line_height": self.spacing_config.line_height,
            },
            "visual_elements": {
                "use_icons": self.use_icons,
                "use_skill_bars": self.use_skill_bars,
                "use_timeline": self.use_timeline,
                "highlight_keywords": self.highlight_keywords,
            },
            "content_limits": {
                "max_experiences": self.max_experiences,
                "max_projects": self.max_projects,
                "max_highlights_per_item": self.max_highlights_per_item,
            },
        }


class BaseTemplate(ABC):
    """模板基类
    
    用于高级自定义模板，可以覆盖渲染逻辑。
    简单场景直接使用 TemplateConfig + JSON 即可。
    """
    
    def __init__(self, config: Optional[TemplateConfig] = None):
        self.config = config or self.get_default_config()
    
    @property
    @abstractmethod
    def name(self) -> str:
        """模板唯一标识"""
        pass
    
    @property
    def display_name(self) -> str:
        """显示名称"""
        return self.config.display_name
    
    @abstractmethod
    def get_default_config(self) -> TemplateConfig:
        """获取默认配置"""
        pass
    
    def customize(self, **kwargs) -> "BaseTemplate":
        """自定义模板参数
        
        Args:
            **kwargs: 要覆盖的配置项
            
        Returns:
            新的模板实例
        """
        config_dict = self.config.to_dict()
        config_dict.update(kwargs)
        new_config = TemplateConfig.from_dict(config_dict)
        return self.__class__(config=new_config)
    
    def get_layout_config(self) -> Dict[str, Any]:
        """获取布局配置"""
        return self.config.to_layout_config()
    
    def match_score(self, job_description: str) -> float:
        """计算与职位描述的匹配度
        
        Args:
            job_description: 职位描述文本
            
        Returns:
            匹配分数 (0-1)
        """
        if not job_description:
            return 0.0
        
        jd_lower = job_description.lower()
        matched = 0
        total = len(self.config.job_keywords)
        
        if total == 0:
            return 0.0
        
        for keyword in self.config.job_keywords:
            if keyword.lower() in jd_lower:
                matched += 1
        
        return matched / total
    
    def preprocess_resume(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """预处理简历数据（可被子类覆盖）
        
        Args:
            resume_data: 原始简历数据
            
        Returns:
            处理后的简历数据
        """
        return resume_data
    
    def postprocess_resume(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """后处理简历数据（可被子类覆盖）
        
        Args:
            resume_data: 优化后的简历数据
            
        Returns:
            最终的简历数据
        """
        # 应用内容限制
        data = resume_data.copy()
        
        if "experience" in data:
            data["experience"] = data["experience"][:self.config.max_experiences]
            for exp in data["experience"]:
                if "highlights" in exp:
                    exp["highlights"] = exp["highlights"][:self.config.max_highlights_per_item]
        
        if "projects" in data:
            data["projects"] = data["projects"][:self.config.max_projects]
            for proj in data["projects"]:
                if "highlights" in proj:
                    proj["highlights"] = proj["highlights"][:self.config.max_highlights_per_item]
        
        if "skills" in data:
            data["skills"] = data["skills"][:self.config.max_skills]
        
        return data
