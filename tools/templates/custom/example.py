# -*- coding: utf-8 -*-
"""自定义模板示例 - 科研/学术岗位模板。

演示如何通过继承 BaseTemplate 创建自定义模板。
"""
from typing import Any, Dict, List

from ..base import BaseTemplate, TemplateConfig, FontConfig, SpacingConfig


class ResearchTemplate(BaseTemplate):
    """科研/学术岗位模板
    
    特点：
    - 突出教育背景和论文发表
    - 支持 publications 字段
    - 学术风格排版
    """
    
    @property
    def name(self) -> str:
        return "research"
    
    def get_default_config(self) -> TemplateConfig:
        return TemplateConfig(
            name="research",
            display_name="科研/学术岗",
            description="适合高校教职、研究院、博士后等学术岗位",
            tags=["科研", "学术", "高校", "研究"],
            job_keywords=[
                "研究员", "教授", "博士后", "科学家", "研究",
                "学术", "论文", "课题", "实验室"
            ],
            page_preference="two_pages",  # 学术简历通常较长
            section_order=[
                "header", "summary", "education", "publications",
                "projects", "experience", "skills", "awards"
            ],
            section_weights={
                "education": 1.5,
                "publications": 1.3,
                "projects": 1.0,
                "experience": 0.8,
            },
            style="classic",
            color_scheme="monochrome",
            font_config=FontConfig(
                title_size=14,
                heading_size=11,
                subheading_size=10,
                body_size=10,
                small_size=9,
            ),
            spacing_config=SpacingConfig(
                margin=0.6,
                section_gap=8,
                item_gap=3,
                line_height=1.2,
            ),
            use_icons=False,
            use_skill_bars=False,
            use_timeline=True,
            highlight_keywords=False,
            max_experiences=5,
            max_projects=4,
            max_highlights_per_item=5,
            max_skills=20,
        )
    
    def preprocess_resume(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """预处理：确保有 publications 字段"""
        data = resume_data.copy()
        
        # 如果没有 publications，尝试从 projects 中提取论文相关项目
        if "publications" not in data:
            data["publications"] = []
            
            # 从 awards 中提取论文相关
            awards = data.get("awards", [])
            paper_awards = [
                a for a in awards
                if any(kw in a.lower() for kw in ["论文", "paper", "发表", "期刊"])
            ]
            if paper_awards:
                data["publications"].extend(paper_awards)
        
        return data
    
    def postprocess_resume(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """后处理：格式化学术内容"""
        data = super().postprocess_resume(resume_data)
        
        # 确保教育经历包含研究方向
        for edu in data.get("education", []):
            if "研究方向" not in str(edu) and "research" not in str(edu).lower():
                # 可以在这里添加提示
                pass
        
        return data
    
    def format_publication(self, pub: Dict[str, Any]) -> str:
        """格式化单条论文引用
        
        Args:
            pub: 论文信息字典，包含 title, authors, venue, year 等
            
        Returns:
            格式化的引用字符串
        """
        authors = pub.get("authors", "")
        title = pub.get("title", "")
        venue = pub.get("venue", "")
        year = pub.get("year", "")
        
        # 学术引用格式
        return f"{authors}. \"{title}\". {venue}, {year}."


class TwoColumnTemplate(BaseTemplate):
    """双栏布局模板
    
    左侧放置联系信息和技能，右侧放置主要内容。
    适合内容较多但希望控制在一页的情况。
    """
    
    @property
    def name(self) -> str:
        return "two_column"
    
    def get_default_config(self) -> TemplateConfig:
        return TemplateConfig(
            name="two_column",
            display_name="双栏布局",
            description="左右分栏布局，信息密度高，适合内容丰富的简历",
            tags=["双栏", "紧凑", "信息密集"],
            job_keywords=[],  # 通用模板
            page_preference="one_page",
            section_order=[
                "header", "summary", "experience", "projects", "education", "skills"
            ],
            style="modern",
            font_config=FontConfig(
                title_size=14,
                heading_size=9,
                subheading_size=8,
                body_size=8,
                small_size=7,
            ),
            spacing_config=SpacingConfig(
                margin=0.3,
                section_gap=3,
                item_gap=1,
                line_height=1.0,
            ),
            max_experiences=4,
            max_projects=3,
            max_highlights_per_item=3,
        )
    
    def get_layout_config(self) -> Dict[str, Any]:
        """返回双栏专用布局配置"""
        config = super().get_layout_config()
        config["layout_type"] = "two_column"
        config["left_column_sections"] = ["contact", "skills", "languages", "certificates"]
        config["right_column_sections"] = ["summary", "experience", "projects", "education"]
        config["column_ratio"] = 0.3  # 左栏占 30%
        return config
