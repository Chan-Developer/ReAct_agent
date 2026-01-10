# -*- coding: utf-8 -*-
"""简历文档生成工具 v2.0。

支持生成 Word 格式的专业简历文档。
功能特点：
- LLM 内容优化
- 技能进度条
- 专业模板样式
- 自动生成个人简介

需要安装依赖: pip install python-docx
"""
from __future__ import annotations

import os
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, Type, TYPE_CHECKING

from ..base import BaseTool

if TYPE_CHECKING:
    from agents import ResumeAgentOrchestrator

__all__ = ["ResumeGenerator"]


# =============================================================================
# 数据模型 (增强版)
# =============================================================================

@dataclass
class Education:
    """教育经历"""
    school: str = ""
    degree: str = ""
    major: str = ""
    start_date: str = ""
    end_date: str = ""
    gpa: str = ""  # 新增：GPA
    courses: List[str] = field(default_factory=list)  # 新增：主修课程


@dataclass
class Experience:
    """工作/实习经历"""
    company: str = ""
    position: str = ""
    start_date: str = ""
    end_date: str = ""
    description: str = ""
    highlights: List[str] = field(default_factory=list)  # 新增：工作亮点


@dataclass
class Project:
    """项目经历"""
    name: str = ""
    role: str = ""
    start_date: str = ""  # 新增
    end_date: str = ""    # 新增
    description: str = ""
    highlights: List[str] = field(default_factory=list)
    tech_stack: List[str] = field(default_factory=list)  # 新增：技术栈


@dataclass
class SkillLevel:
    """带等级的技能"""
    name: str
    level: int = 80  # 1-100 百分比
    category: str = ""  # 如：编程语言、框架、工具


@dataclass
class ResumeData:
    """简历数据模型 (增强版)"""
    # 基本信息
    name: str = ""
    phone: str = ""
    email: str = ""
    location: str = ""
    
    # 社交链接 (新增)
    linkedin: str = ""
    github: str = ""
    website: str = ""
    
    # 核心内容
    summary: str = ""
    education: List[Education] = field(default_factory=list)
    experience: List[Experience] = field(default_factory=list)
    projects: List[Project] = field(default_factory=list)
    
    # 技能 (增强)
    skills: List[str] = field(default_factory=list)
    skill_levels: List[SkillLevel] = field(default_factory=list)
    
    # 附加信息 (新增)
    certificates: List[str] = field(default_factory=list)  # 证书
    awards: List[str] = field(default_factory=list)        # 荣誉奖项
    languages: List[str] = field(default_factory=list)     # 语言能力
    interests: List[str] = field(default_factory=list)     # 兴趣爱好

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResumeData":
        """从字典创建 ResumeData 实例"""
        # 解析教育经历
        education_list = []
        for edu in data.get("education", []):
            if isinstance(edu, dict):
                education_list.append(Education(
                    school=edu.get("school", ""),
                    degree=edu.get("degree", ""),
                    major=edu.get("major", ""),
                    start_date=edu.get("start_date", ""),
                    end_date=edu.get("end_date", ""),
                    gpa=edu.get("gpa", ""),
                    courses=edu.get("courses", []),
                ))
        
        # 解析工作经历
        experience_list = []
        for exp in data.get("experience", []):
            if isinstance(exp, dict):
                experience_list.append(Experience(
                    company=exp.get("company", ""),
                    position=exp.get("position", ""),
                    start_date=exp.get("start_date", ""),
                    end_date=exp.get("end_date", ""),
                    description=exp.get("description", ""),
                    highlights=exp.get("highlights", []),
                ))
        
        # 解析项目经历
        project_list = []
        for proj in data.get("projects", []):
            if isinstance(proj, dict):
                project_list.append(Project(
                    name=proj.get("name", ""),
                    role=proj.get("role", ""),
                    start_date=proj.get("start_date", ""),
                    end_date=proj.get("end_date", ""),
                    description=proj.get("description", ""),
                    highlights=proj.get("highlights", []),
                    tech_stack=proj.get("tech_stack", []),
                ))
        
        # 解析技能等级
        skill_levels = []
        for skill in data.get("skill_levels", []):
            if isinstance(skill, dict):
                skill_levels.append(SkillLevel(
                    name=skill.get("name", ""),
                    level=skill.get("level", 80),
                    category=skill.get("category", ""),
                ))
        
        # 解析 skills 列表（兼容字符串和 dict 格式）
        raw_skills = data.get("skills", [])
        skills_list = []
        for skill in raw_skills:
            if isinstance(skill, str):
                skills_list.append(skill)
            elif isinstance(skill, dict):
                # 如果是 dict，提取 name 并添加到 skill_levels
                skill_name = skill.get("name", "")
                if skill_name:
                    skills_list.append(skill_name)
                    # 同时添加到 skill_levels（如果有 level）
                    if "level" in skill:
                        level_val = skill.get("level", 80)
                        # 处理 level 可能是字符串的情况
                        if isinstance(level_val, str):
                            level_map = {"expert": 95, "proficient": 80, "familiar": 60}
                            level_val = level_map.get(level_val.lower(), 70)
                        skill_levels.append(SkillLevel(
                            name=skill_name,
                            level=level_val,
                            category=skill.get("category", ""),
                        ))
        
        return cls(
            name=data.get("name", ""),
            phone=data.get("phone", ""),
            email=data.get("email", ""),
            location=data.get("location", ""),
            linkedin=data.get("linkedin", ""),
            github=data.get("github", ""),
            website=data.get("website", ""),
            summary=data.get("summary", ""),
            education=education_list,
            experience=experience_list,
            projects=project_list,
            skills=skills_list,
            skill_levels=skill_levels,
            certificates=data.get("certificates", []),
            awards=data.get("awards", []),
            languages=data.get("languages", []),
            interests=data.get("interests", []),
        )

    @property
    def contact_info(self) -> List[str]:
        """获取联系信息列表"""
        info = []
        if self.phone:
            info.append(f"📱 {self.phone}")
        if self.email:
            info.append(f"📧 {self.email}")
        if self.location:
            info.append(f"📍 {self.location}")
        return info
    
    @property
    def social_links(self) -> List[str]:
        """获取社交链接"""
        links = []
        if self.github:
            links.append(f"GitHub: {self.github}")
        if self.linkedin:
            links.append(f"LinkedIn: {self.linkedin}")
        if self.website:
            links.append(f"Website: {self.website}")
        return links


# =============================================================================
# 样式配置 (增强版)
# =============================================================================

class TemplateStyle(str, Enum):
    """模板样式枚举"""
    CLASSIC = "classic"      # 经典：蓝色主题，传统布局
    MODERN = "modern"        # 现代：扁平化设计
    MINIMAL = "minimal"      # 简约：黑白为主
    PROFESSIONAL = "professional"  # 专业：双栏布局 (新增)


@dataclass
class ColorScheme:
    """颜色方案 - 统一黑色字体"""
    primary: str = "#000000"    # 主色调（标题）- 黑色
    secondary: str = "#000000"  # 次要色（时间等）- 黑色
    accent: str = "#000000"     # 强调色（分隔线等）- 黑色
    text: str = "#000000"       # 正文颜色 - 黑色
    light: str = "#f5f5f5"      # 浅色背景
    success: str = "#000000"    # 成功色（技能条）- 黑色


@dataclass
class FontConfig:
    """字体配置 - 紧凑版（适合一页简历）"""
    title_size: int = 16        # 姓名标题（缩小）
    heading_size: int = 10      # 章节标题（缩小）
    subheading_size: int = 9    # 子标题（公司/项目名）
    body_size: int = 9          # 正文
    small_size: int = 8         # 小字（时间等）


@dataclass
class SpacingConfig:
    """间距配置（单位: Pt）- 极紧凑版（适合一页简历）"""
    margin: float = 0.4         # 页边距（inch）- 更窄
    section_gap: int = 4        # 章节间距（Pt）- 更紧凑
    item_gap: int = 1           # 条目间距（Pt）- 更紧凑
    line_height: float = 1.0    # 行高


@dataclass
class StyleConfig:
    """完整样式配置"""
    colors: ColorScheme
    fonts: FontConfig
    spacing: SpacingConfig
    show_skill_bars: bool = True   # 是否显示技能进度条
    show_icons: bool = True        # 是否显示图标
    show_timeline: bool = False    # 是否显示时间轴

    @classmethod
    def get_style(cls, style: TemplateStyle | str) -> "StyleConfig":
        """获取预定义样式配置"""
        if isinstance(style, str):
            try:
                style = TemplateStyle(style)
            except ValueError:
                style = TemplateStyle.CLASSIC
        
        # 统一使用黑色字体
        black_colors = ColorScheme()  # 使用默认值（全黑）
        
        styles = {
            TemplateStyle.CLASSIC: cls(
                colors=black_colors,
                fonts=FontConfig(),
                spacing=SpacingConfig(),
                show_skill_bars=True,
                show_icons=True,
            ),
            TemplateStyle.MODERN: cls(
                colors=black_colors,
                fonts=FontConfig(),
                spacing=SpacingConfig(),
                show_skill_bars=True,
                show_icons=True,
            ),
            TemplateStyle.MINIMAL: cls(
                colors=black_colors,
                fonts=FontConfig(),
                spacing=SpacingConfig(),
                show_skill_bars=False,
                show_icons=False,
            ),
            TemplateStyle.PROFESSIONAL: cls(
                colors=black_colors,
                fonts=FontConfig(),
                spacing=SpacingConfig(),
                show_skill_bars=True,
                show_icons=True,
            ),
        }
        
        return styles.get(style, styles[TemplateStyle.CLASSIC])


# =============================================================================
# 文档生成器抽象基类
# =============================================================================

class BaseDocumentGenerator(ABC):
    """文档生成器抽象基类"""

    def __init__(self, style: StyleConfig):
        self.style = style

    @abstractmethod
    def generate(self, data: ResumeData, output_path: str) -> bool:
        """生成文档"""
        raise NotImplementedError


# =============================================================================
# Word 文档生成器 (增强版)
# =============================================================================

class DocxGenerator(BaseDocumentGenerator):
    """Word 文档生成器 (紧凑专业版)
    
    特点：
    - 紧凑单页布局
    - 专业配色层次
    - 正式符号图标
    - 技能进度条
    """

    # 章节图标映射（正式符号）
    SECTION_ICONS = {
        "个人简介": "▎",
        "教育背景": "▎",
        "工作经历": "▎",
        "实习经历": "▎",
        "项目经验": "▎",
        "专业技能": "▎",
        "证书资质": "▎",
        "荣誉奖项": "▎",
        "语言能力": "▎",
    }

    def generate(self, data: ResumeData, output_path: str) -> bool:
        from docx import Document
        from docx.shared import Inches, Pt, RGBColor, Cm
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.enum.table import WD_TABLE_ALIGNMENT
        from docx.oxml.ns import qn
        from docx.oxml import OxmlElement
        
        doc = Document()
        
        # 设置页面边距
        for section in doc.sections:
            section.top_margin = Inches(self.style.spacing.margin)
            section.bottom_margin = Inches(self.style.spacing.margin)
            section.left_margin = Inches(self.style.spacing.margin)
            section.right_margin = Inches(self.style.spacing.margin)
        
        # 生成各个部分
        self._add_header(doc, data)
        self._add_summary(doc, data)
        self._add_education(doc, data)
        self._add_experience(doc, data)
        self._add_projects(doc, data)
        self._add_skills(doc, data)
        self._add_certificates(doc, data)
        self._add_awards(doc, data)
        
        doc.save(output_path)
        return True

    def _hex_to_rgb(self, hex_color: str):
        """将十六进制颜色转换为 RGBColor"""
        from docx.shared import RGBColor
        hex_color = hex_color.lstrip("#")
        return RGBColor(
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16),
        )

    def _add_header(self, doc, data: ResumeData) -> None:
        """添加页眉（姓名和联系方式）- 紧凑版"""
        from docx.shared import Pt
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.oxml.ns import qn
        
        # 姓名
        title = doc.add_paragraph()
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title.paragraph_format.space_before = Pt(0)
        title.paragraph_format.space_after = Pt(2)
        
        run = title.add_run(data.name or "姓名")
        run.bold = True
        run.font.size = Pt(self.style.fonts.title_size)
        run.font.color.rgb = self._hex_to_rgb(self.style.colors.primary)
        run.font.name = 'Microsoft YaHei'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')
        
        # 联系信息（紧凑一行）
        contact_parts = []
        if data.phone:
            contact_parts.append(data.phone)
        if data.email:
            contact_parts.append(data.email)
        if data.location:
            contact_parts.append(data.location)
        
        if contact_parts:
            contact = doc.add_paragraph()
            contact.alignment = WD_ALIGN_PARAGRAPH.CENTER
            contact.paragraph_format.space_before = Pt(0)
            contact.paragraph_format.space_after = Pt(1)
            
            run = contact.add_run(" | ".join(contact_parts))
            run.font.size = Pt(self.style.fonts.small_size)
            run.font.color.rgb = self._hex_to_rgb(self.style.colors.text)
        
        # 社交链接（紧凑一行）
        if data.social_links:
            social = doc.add_paragraph()
            social.alignment = WD_ALIGN_PARAGRAPH.CENTER
            social.paragraph_format.space_before = Pt(0)
            social.paragraph_format.space_after = Pt(2)
            
            run = social.add_run(" | ".join(data.social_links))
            run.font.size = Pt(self.style.fonts.small_size)
            run.font.color.rgb = self._hex_to_rgb(self.style.colors.accent)
        
        # 分隔线
        self._add_horizontal_line(doc)

    def _add_horizontal_line(self, doc) -> None:
        """添加水平分隔线"""
        from docx.shared import Pt
        from docx.oxml.ns import qn
        from docx.oxml import OxmlElement
        
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)
        
        pPr = p._p.get_or_add_pPr()
        pBdr = OxmlElement('w:pBdr')
        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single')
        bottom.set(qn('w:sz'), '8')
        bottom.set(qn('w:color'), self.style.colors.primary.lstrip('#'))
        pBdr.append(bottom)
        pPr.append(pBdr)

    def _add_section_heading(self, doc, title: str) -> None:
        """添加章节标题 - 紧凑专业版"""
        from docx.shared import Pt
        from docx.oxml.ns import qn
        from docx.oxml import OxmlElement
        
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(self.style.spacing.section_gap)
        p.paragraph_format.space_after = Pt(2)
        
        # 色块标记 + 标题
        if self.style.show_icons:
            run = p.add_run("▌")
            run.font.size = Pt(self.style.fonts.heading_size)
            run.font.color.rgb = self._hex_to_rgb(self.style.colors.accent)
        
        run = p.add_run(title)
        run.bold = True
        run.font.size = Pt(self.style.fonts.heading_size)
        run.font.color.rgb = self._hex_to_rgb(self.style.colors.primary)
        run.font.name = 'Microsoft YaHei'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')
        
        # 细下划线
        pPr = p._p.get_or_add_pPr()
        pBdr = OxmlElement('w:pBdr')
        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single')
        bottom.set(qn('w:sz'), '4')
        bottom.set(qn('w:color'), self.style.colors.accent.lstrip('#'))
        pBdr.append(bottom)
        pPr.append(pBdr)

    def _add_summary(self, doc, data: ResumeData) -> None:
        """添加个人简介 - 紧凑版"""
        if not data.summary:
            return
            
        from docx.shared import Pt
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        
        self._add_section_heading(doc, "个人简介")
        
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        
        run = p.add_run(data.summary)
        run.font.size = Pt(self.style.fonts.body_size)
        run.font.color.rgb = self._hex_to_rgb(self.style.colors.text)

    def _add_education(self, doc, data: ResumeData) -> None:
        """添加教育背景 - 紧凑版"""
        if not data.education:
            return
            
        from docx.shared import Pt, Inches
        
        self._add_section_heading(doc, "教育背景")
        
        for edu in data.education:
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(1)
            
            # 学校名称（深色）
            run = p.add_run(edu.school)
            run.bold = True
            run.font.size = Pt(self.style.fonts.subheading_size)
            run.font.color.rgb = self._hex_to_rgb(self.style.colors.primary)
            
            # 时间（浅色，右侧）
            run = p.add_run("\t" * 5)
            run = p.add_run(f"{edu.start_date} - {edu.end_date}")
            run.font.size = Pt(self.style.fonts.small_size)
            run.font.color.rgb = self._hex_to_rgb(self.style.colors.secondary)
            
            # 学位 · 专业 · GPA（同一行）
            if edu.degree or edu.major:
                p2 = doc.add_paragraph()
                p2.paragraph_format.space_before = Pt(0)
                p2.paragraph_format.space_after = Pt(0)
                p2.paragraph_format.left_indent = Inches(0.1)
                
                info_parts = []
                if edu.degree:
                    info_parts.append(edu.degree)
                if edu.major:
                    info_parts.append(edu.major)
                if edu.gpa:
                    info_parts.append(f"GPA: {edu.gpa}")
                
                run = p2.add_run(" · ".join(info_parts))
                run.font.size = Pt(self.style.fonts.body_size)
                run.font.color.rgb = self._hex_to_rgb(self.style.colors.text)

    def _add_experience(self, doc, data: ResumeData) -> None:
        """添加工作经验 - 紧凑版"""
        if not data.experience:
            return
            
        from docx.shared import Pt, Inches
        
        self._add_section_heading(doc, "工作经历")
        
        for exp in data.experience:
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(1)
            
            # 公司（深色加粗）
            run = p.add_run(exp.company)
            run.bold = True
            run.font.size = Pt(self.style.fonts.subheading_size)
            run.font.color.rgb = self._hex_to_rgb(self.style.colors.primary)
            
            # 职位（强调色）
            run = p.add_run(f" | {exp.position}")
            run.font.size = Pt(self.style.fonts.body_size)
            run.font.color.rgb = self._hex_to_rgb(self.style.colors.accent)
            
            # 时间（浅色）
            run = p.add_run("\t" * 4)
            run = p.add_run(f"{exp.start_date} - {exp.end_date}")
            run.font.size = Pt(self.style.fonts.small_size)
            run.font.color.rgb = self._hex_to_rgb(self.style.colors.secondary)
            
            # 工作描述
            if exp.description:
                p2 = doc.add_paragraph()
                p2.paragraph_format.left_indent = Inches(0.1)
                p2.paragraph_format.space_before = Pt(0)
                p2.paragraph_format.space_after = Pt(0)
                
                run = p2.add_run(exp.description)
                run.font.size = Pt(self.style.fonts.body_size)
                run.font.color.rgb = self._hex_to_rgb(self.style.colors.text)
            
            # 工作亮点
            for highlight in exp.highlights:
                p3 = doc.add_paragraph()
                p3.paragraph_format.left_indent = Inches(0.15)
                p3.paragraph_format.space_before = Pt(0)
                p3.paragraph_format.space_after = Pt(0)
                
                run = p3.add_run("• ")
                run.font.size = Pt(self.style.fonts.body_size)
                run.font.color.rgb = self._hex_to_rgb(self.style.colors.accent)
                run = p3.add_run(highlight)
                run.font.size = Pt(self.style.fonts.body_size)
                run.font.color.rgb = self._hex_to_rgb(self.style.colors.text)

    def _add_projects(self, doc, data: ResumeData) -> None:
        """添加项目经验 - 紧凑版"""
        if not data.projects:
            return
            
        from docx.shared import Pt, Inches
        
        self._add_section_heading(doc, "项目经验")
        
        for proj in data.projects:
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(1)
            
            # 项目名称（深色加粗）
            run = p.add_run(proj.name)
            run.bold = True
            run.font.size = Pt(self.style.fonts.subheading_size)
            run.font.color.rgb = self._hex_to_rgb(self.style.colors.primary)
            
            # 角色（强调色）
            if proj.role:
                run = p.add_run(f" | {proj.role}")
                run.font.size = Pt(self.style.fonts.body_size)
                run.font.color.rgb = self._hex_to_rgb(self.style.colors.accent)
            
            # 时间（浅色）
            if proj.start_date or proj.end_date:
                run = p.add_run("\t" * 4)
                run = p.add_run(f"{proj.start_date} - {proj.end_date}")
                run.font.size = Pt(self.style.fonts.small_size)
                run.font.color.rgb = self._hex_to_rgb(self.style.colors.secondary)
            
            # 技术栈（紧凑一行）
            if proj.tech_stack:
                p_tech = doc.add_paragraph()
                p_tech.paragraph_format.left_indent = Inches(0.1)
                p_tech.paragraph_format.space_before = Pt(0)
                p_tech.paragraph_format.space_after = Pt(0)
                
                run = p_tech.add_run("技术栈: ")
                run.font.size = Pt(self.style.fonts.small_size)
                run.font.color.rgb = self._hex_to_rgb(self.style.colors.secondary)
                
                run = p_tech.add_run(" | ".join(proj.tech_stack))
                run.font.size = Pt(self.style.fonts.small_size)
                run.font.color.rgb = self._hex_to_rgb(self.style.colors.accent)
            
            # 项目描述
            if proj.description:
                p2 = doc.add_paragraph()
                p2.paragraph_format.left_indent = Inches(0.1)
                p2.paragraph_format.space_before = Pt(0)
                p2.paragraph_format.space_after = Pt(0)
                
                run = p2.add_run(proj.description)
                run.font.size = Pt(self.style.fonts.body_size)
                run.font.color.rgb = self._hex_to_rgb(self.style.colors.text)
            
            # 项目亮点（绿色勾）
            for highlight in proj.highlights:
                p3 = doc.add_paragraph()
                p3.paragraph_format.left_indent = Inches(0.15)
                p3.paragraph_format.space_before = Pt(0)
                p3.paragraph_format.space_after = Pt(0)
                
                run = p3.add_run("✓ ")
                run.font.size = Pt(self.style.fonts.body_size)
                run.font.color.rgb = self._hex_to_rgb(self.style.colors.success)
                run = p3.add_run(highlight)
                run.font.size = Pt(self.style.fonts.body_size)
                run.font.color.rgb = self._hex_to_rgb(self.style.colors.text)

    def _add_skills(self, doc, data: ResumeData) -> None:
        """添加专业技能 - 紧凑版"""
        if not data.skills and not data.skill_levels:
            return
            
        from docx.shared import Pt
        
        self._add_section_heading(doc, "专业技能")
        
        # 技能进度条（如果有等级）
        if data.skill_levels and self.style.show_skill_bars:
            self._add_skill_bars(doc, data.skill_levels)
        
        # 普通技能列表（一行显示）
        if data.skills:
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(0)
            
            run = p.add_run(" | ".join(data.skills))
            run.font.size = Pt(self.style.fonts.body_size)
            run.font.color.rgb = self._hex_to_rgb(self.style.colors.text)

    def _add_skill_bars(self, doc, skill_levels: List[SkillLevel]) -> None:
        """添加技能进度条 - 紧凑版"""
        from docx.shared import Pt, Inches
        from docx.enum.table import WD_TABLE_ALIGNMENT
        
        # 两列布局
        cols = 2
        rows = (len(skill_levels) + 1) // cols
        
        table = doc.add_table(rows=rows, cols=cols * 2)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        for i, skill in enumerate(skill_levels):
            row_idx = i // cols
            col_offset = (i % cols) * 2
            
            if row_idx >= rows:
                break
            
            row = table.rows[row_idx]
            
            # 技能名称
            cell1 = row.cells[col_offset]
            cell1.width = Inches(0.8)
            p = cell1.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            run = p.add_run(skill.name)
            run.font.size = Pt(self.style.fonts.small_size)
            run.font.color.rgb = self._hex_to_rgb(self.style.colors.text)
            
            # 进度条
            cell2 = row.cells[col_offset + 1]
            cell2.width = Inches(2.5)
            p = cell2.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            
            filled = int(skill.level / 10)
            empty = 10 - filled
            
            run = p.add_run("█" * filled)
            run.font.size = Pt(8)
            run.font.color.rgb = self._hex_to_rgb(self.style.colors.accent)
            
            run = p.add_run("░" * empty)
            run.font.size = Pt(8)
            run.font.color.rgb = self._hex_to_rgb("#d0d0d0")
            
            run = p.add_run(f" {skill.level}%")
            run.font.size = Pt(self.style.fonts.small_size)
            run.font.color.rgb = self._hex_to_rgb(self.style.colors.secondary)

    def _add_certificates(self, doc, data: ResumeData) -> None:
        """添加证书资质 - 紧凑版"""
        if not data.certificates:
            return
            
        from docx.shared import Pt
        
        self._add_section_heading(doc, "证书资质")
        
        # 一行显示所有证书
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        
        for i, cert in enumerate(data.certificates):
            if i > 0:
                run = p.add_run(" | ")
                run.font.size = Pt(self.style.fonts.body_size)
                run.font.color.rgb = self._hex_to_rgb(self.style.colors.secondary)
            run = p.add_run(cert)
            run.font.size = Pt(self.style.fonts.body_size)
            run.font.color.rgb = self._hex_to_rgb(self.style.colors.text)

    def _add_awards(self, doc, data: ResumeData) -> None:
        """添加荣誉奖项 - 紧凑版"""
        if not data.awards:
            return
            
        from docx.shared import Pt
        
        self._add_section_heading(doc, "荣誉奖项")
        
        # 一行显示所有奖项
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        
        for i, award in enumerate(data.awards):
            if i > 0:
                run = p.add_run(" | ")
                run.font.size = Pt(self.style.fonts.body_size)
                run.font.color.rgb = self._hex_to_rgb(self.style.colors.secondary)
            run = p.add_run(award)
            run.font.size = Pt(self.style.fonts.body_size)
            run.font.color.rgb = self._hex_to_rgb(self.style.colors.text)


# =============================================================================
# 生成器工厂
# =============================================================================

class DocumentGeneratorFactory:
    """文档生成器工厂"""
    
    _generators: Dict[str, Type[BaseDocumentGenerator]] = {
        "docx": DocxGenerator,
    }

    @classmethod
    def create(cls, format_type: str, style: StyleConfig) -> BaseDocumentGenerator:
        generator_class = cls._generators.get(format_type.lower())
        if not generator_class:
            raise ValueError(f"不支持的格式: {format_type}。仅支持: docx")
        return generator_class(style)


# =============================================================================
# 对外工具类 (增强版)
# =============================================================================

class ResumeGenerator(BaseTool):
    """生成 Word 格式的专业简历文档。
    
    功能特点：
    - 支持 LLM 内容优化（自动润色简历内容）
    - 多种专业模板样式
    - 技能进度条展示
    - 自动生成个人简介
    """

    RESUME_DATA_SCHEMA = """JSON格式的简历数据，包含以下字段:
{
    "name": "姓名",
    "phone": "手机号",
    "email": "邮箱",
    "location": "所在地",
    "github": "GitHub地址(可选)",
    "linkedin": "LinkedIn地址(可选)",
    "summary": "个人简介",
    "education": [
        {"school": "学校", "degree": "学位", "major": "专业", "start_date": "开始时间", "end_date": "结束时间", "gpa": "GPA(可选)"}
    ],
    "experience": [
        {"company": "公司", "position": "职位", "start_date": "开始时间", "end_date": "结束时间", "description": "工作描述", "highlights": ["亮点1"]}
    ],
    "projects": [
        {"name": "项目名", "role": "角色", "description": "项目描述", "highlights": ["亮点1"], "tech_stack": ["技术栈"]}
    ],
    "skills": ["技能1", "技能2"],
    "skill_levels": [{"name": "Python", "level": 90}],
    "certificates": ["证书1"],
    "awards": ["奖项1"]
}"""

    def __init__(
        self,
        output_dir: str = "./output",
        llm: Optional[Any] = None,
        auto_optimize: bool = True,
        use_multi_agent: bool = True,
    ) -> None:
        """初始化简历生成器。
        
        Args:
            output_dir: 输出目录
            llm: LLM 实例（用于内容优化）
            auto_optimize: 是否自动优化内容
            use_multi_agent: 是否使用多Agent架构（ContentAgent + LayoutAgent）
        """
        super().__init__(
            name="generate_resume",
            description="生成 Word 格式的专业简历文档。可自动优化内容，让简历更加专业。",
            parameters={
                "type": "object",
                "properties": {
                    "resume_data": {
                        "type": "string",
                        "description": self.RESUME_DATA_SCHEMA,
                    },
                    "filename": {
                        "type": "string",
                        "description": "输出文件名（不含扩展名）",
                    },
                    "template_style": {
                        "type": "string",
                        "description": "模板样式: 'classic'(经典), 'modern'(现代), 'minimal'(简约), 'professional'(专业)",
                        "enum": ["classic", "modern", "minimal", "professional"],
                    },
                    "optimize": {
                        "type": "boolean",
                        "description": "是否使用AI优化简历内容（默认开启）",
                    },
                },
                "required": ["resume_data"],
            },
        )
        self.output_dir = output_dir
        self.llm = llm
        self.auto_optimize = auto_optimize
        self.use_multi_agent = use_multi_agent
        self._orchestrator: Optional["ResumeAgentOrchestrator"] = None
        
        os.makedirs(output_dir, exist_ok=True)
        
        # 延迟初始化多Agent协调器
        if llm is not None and use_multi_agent:
            self._init_orchestrator()

    def _init_orchestrator(self) -> None:
        """初始化多Agent协调器"""
        if self.llm is None:
            return
            
        try:
            from agents import ResumeAgentOrchestrator
            self._orchestrator = ResumeAgentOrchestrator(
                llm=self.llm,
                enable_content_optimization=True,
                enable_layout_optimization=True,
            )
        except ImportError:
            pass

    def execute(
        self,
        resume_data: str,
        filename: str = "resume",
        template_style: str = "modern",
        optimize: bool = True,
    ) -> str:
        """生成简历文档。
        
        Args:
            resume_data: JSON 格式的简历数据
            filename: 输出文件名
            template_style: 模板样式
            optimize: 是否优化内容
            
        Returns:
            成功或失败的消息
        """
        # 1. 解析 JSON 数据（支持 @optimized 引用）
        import tempfile
        temp_dir = tempfile.gettempdir()
        
        if isinstance(resume_data, str) and resume_data.strip() == "@optimized":
            # 使用优化后的数据
            optimized_file = os.path.join(temp_dir, "optimized_resume.json")
            if os.path.exists(optimized_file):
                with open(optimized_file, 'r', encoding='utf-8') as f:
                    raw_data = json.load(f)
                print("[ResumeGenerator] 使用优化后的数据")
            else:
                return "❌ 未找到优化后的数据，请先调用 content_optimizer"
        elif isinstance(resume_data, str) and resume_data.strip() == "@layout":
            # 使用布局设计后的数据
            layout_file = os.path.join(temp_dir, "layout_resume.json")
            if os.path.exists(layout_file):
                with open(layout_file, 'r', encoding='utf-8') as f:
                    raw_data = json.load(f)
                print("[ResumeGenerator] 使用布局设计后的数据")
            else:
                return "❌ 未找到布局数据，请先调用 layout_designer"
        else:
            try:
                raw_data = json.loads(resume_data) if isinstance(resume_data, str) else resume_data
            except json.JSONDecodeError as e:
                return f"❌ JSON 解析失败: {e}. 提示：可以使用 \"@optimized\" 或 \"@layout\" 引用之前处理的数据。"
        
        # 2. 提取嵌入的布局配置（由 LayoutDesignerTool 生成）
        layout_config = raw_data.pop("_layout_config", None)
        
        # 3. AI 优化（如果启用且有协调器）
        optimization_result = None
        if optimize and self.auto_optimize:
            raw_data, optimization_result, orchestrator_config = self._run_optimization(raw_data)
            # 协调器的配置优先级低于嵌入的配置
            if orchestrator_config and not layout_config:
                layout_config = orchestrator_config
        
        # 4. 创建数据模型
        try:
            data = ResumeData.from_dict(raw_data)
        except Exception as e:
            return f"❌ 数据解析失败: {type(e).__name__}: {e}"
        
        # 5. 获取样式配置（优先使用 LayoutAgent 的配置）
        try:
            if layout_config:
                # 使用 LayoutAgent 决定的样式
                ai_style = layout_config.get("style", template_style)
                style = StyleConfig.get_style(ai_style)
                # 应用完整的布局配置
                style = self._apply_layout_config(style, layout_config)
                print(f"[ResumeGenerator] 使用 LayoutAgent 配置: {ai_style}")
            else:
                # 回退到默认样式
                style = StyleConfig.get_style(template_style)
                print(f"[ResumeGenerator] 使用默认样式: {template_style}")
                
        except ValueError:
            style = StyleConfig.get_style("modern")
        
        # 5. 生成文档
        try:
            output_path = os.path.join(self.output_dir, f"{filename}.docx")
            generator = DocumentGeneratorFactory.create("docx", style)
            success = generator.generate(data, output_path)
            
            if success:
                abs_path = os.path.abspath(output_path)
                
                # 构建返回消息
                if optimization_result and optimization_result.success:
                    mode = "多Agent" if self._orchestrator else "AI"
                    optimized_msg = f" (已{mode}优化)"
                    suggestions = optimization_result.content_suggestions + optimization_result.layout_suggestions
                    suggestion_text = ""
                    if suggestions:
                        suggestion_text = "\n💡 优化建议:\n" + "\n".join(f"  • {s}" for s in suggestions[:3])
                else:
                    optimized_msg = ""
                    suggestion_text = ""
                
                return (
                    f"✅ 简历已成功生成{optimized_msg}!\n"
                    f"📄 文件路径: {abs_path}\n"
                    f"📋 格式: DOCX\n"
                    f"🎨 样式: {template_style}"
                    f"{suggestion_text}"
                )
            return "❌ 文档生成失败"
            
        except ImportError as e:
            missing_pkg = str(e).split("'")[-2] if "'" in str(e) else "相关包"
            return f"❌ 缺少依赖包: {missing_pkg}\n请运行: pip install python-docx"
        except Exception as e:
            return f"❌ 生成文档时出错: {type(e).__name__}: {e}"
    
    def _run_optimization(self, raw_data: Dict[str, Any]) -> tuple:
        """运行多Agent优化流程
        
        Returns:
            (优化后的数据, 优化结果对象, 布局配置)
        """
        optimization_result = None
        layout_config = None
        
        if self._orchestrator:
            try:
                result = self._orchestrator.optimize(raw_data)
                if result.success:
                    raw_data = result.optimized_resume
                    layout_config = result.layout_config
                    optimization_result = result
                    print(f"[ResumeGenerator] 多Agent优化完成，耗时 {result.execution_time:.2f}s")
            except Exception as e:
                print(f"[ResumeGenerator] 多Agent优化失败: {e}")
        
        return raw_data, optimization_result, layout_config
    
    def _apply_layout_config(self, style: StyleConfig, layout_config: Dict[str, Any]) -> StyleConfig:
        """应用 LayoutAgent 的布局配置到样式
        
        Args:
            style: 基础样式配置
            layout_config: LayoutAgent 生成的配置，包含：
                - font_config: 字体配置
                - spacing_config: 间距配置
                - visual_elements: 视觉元素开关
        """
        try:
            # 应用字体配置
            if "font_config" in layout_config:
                font_cfg = layout_config["font_config"]
                if "title_size" in font_cfg:
                    style.fonts.title_size = font_cfg["title_size"]
                if "heading_size" in font_cfg:
                    style.fonts.heading_size = font_cfg["heading_size"]
                if "body_size" in font_cfg:
                    style.fonts.body_size = font_cfg["body_size"]
                if "subheading_size" in font_cfg:
                    style.fonts.subheading_size = font_cfg["subheading_size"]
                if "small_size" in font_cfg:
                    style.fonts.small_size = font_cfg["small_size"]
            
            # 应用间距配置
            if "spacing_config" in layout_config:
                spacing_cfg = layout_config["spacing_config"]
                if "margin" in spacing_cfg:
                    style.spacing.margin = spacing_cfg["margin"]
                if "section_gap" in spacing_cfg:
                    style.spacing.section_gap = spacing_cfg["section_gap"]
                if "item_gap" in spacing_cfg:
                    style.spacing.item_gap = spacing_cfg["item_gap"]
                if "line_height" in spacing_cfg:
                    style.spacing.line_height = spacing_cfg["line_height"]
            
            # 应用视觉元素配置
            if "visual_elements" in layout_config:
                visual_cfg = layout_config["visual_elements"]
                if "use_icons" in visual_cfg:
                    style.show_icons = visual_cfg["use_icons"]
                if "use_skill_bars" in visual_cfg:
                    style.show_skill_bars = visual_cfg["use_skill_bars"]
                if "use_timeline" in visual_cfg:
                    style.show_timeline = visual_cfg["use_timeline"]
                    
        except Exception as e:
            print(f"[ResumeGenerator] 应用布局配置失败: {e}")
        
        return style
