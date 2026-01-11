# -*- coding: utf-8 -*-
"""智能分页系统。

根据内容量和样式配置，自动决定一页或两页布局，并优化布局参数。

核心组件：
- ContentEstimator: 估算内容占用的页面空间
- LayoutOptimizer: 根据页面目标调整布局参数
- PageSplitter: 将内容拆分到多页
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import copy

from common.logger import get_logger

logger = get_logger(__name__)


# A4 页面参数（单位：点 Pt）
A4_WIDTH_PT = 595.0   # 约 8.27 英寸
A4_HEIGHT_PT = 842.0  # 约 11.69 英寸


@dataclass
class PageMetrics:
    """页面度量配置"""
    page_height: float = A4_HEIGHT_PT  # 页面高度（Pt）
    margin_top: float = 28.8     # 上边距（0.4 inch = 28.8 Pt）
    margin_bottom: float = 28.8  # 下边距
    usable_height: float = 784.4  # 可用高度 = 842 - 28.8*2
    
    @classmethod
    def from_margin_inch(cls, margin: float) -> "PageMetrics":
        """从英寸边距创建度量"""
        margin_pt = margin * 72  # 1 inch = 72 Pt
        usable = A4_HEIGHT_PT - margin_pt * 2
        return cls(
            margin_top=margin_pt,
            margin_bottom=margin_pt,
            usable_height=usable,
        )


class ContentEstimator:
    """内容空间估算器
    
    根据简历数据和样式配置，估算内容占用的页面高度。
    使用启发式方法，基于字符数、条目数和样式参数计算。
    """
    
    # 估算参数（基于经验值）
    LINE_HEIGHT_FACTOR = 1.2  # 行高因子
    CHARS_PER_LINE = 45       # 每行大约字符数（中文）
    
    # 各部分基础高度（Pt）
    SECTION_HEADER_HEIGHT = 20    # 章节标题高度
    HEADER_HEIGHT = 60            # 姓名+联系方式
    SUMMARY_BASE_HEIGHT = 40      # 个人简介基础高度
    ITEM_BASE_HEIGHT = 35         # 经历/项目条目基础高度
    HIGHLIGHT_HEIGHT = 14         # 每条亮点高度
    SKILL_LINE_HEIGHT = 20        # 技能行高度
    
    def __init__(self, metrics: Optional[PageMetrics] = None):
        self.metrics = metrics or PageMetrics()
    
    def estimate_pages(
        self,
        resume_data: Dict[str, Any],
        style_config: Dict[str, Any],
    ) -> float:
        """估算内容占用的页数
        
        Args:
            resume_data: 简历数据
            style_config: 样式配置（包含 font_config, spacing_config）
            
        Returns:
            估算页数（如 1.3 表示略超一页）
        """
        total_height = self._estimate_total_height(resume_data, style_config)
        
        # 计算可用高度
        margin = style_config.get("spacing_config", {}).get("margin", 0.4)
        metrics = PageMetrics.from_margin_inch(margin)
        
        pages = total_height / metrics.usable_height
        
        logger.debug(f"[ContentEstimator] 估算高度: {total_height:.1f}Pt, "
                    f"可用高度: {metrics.usable_height:.1f}Pt, "
                    f"页数: {pages:.2f}")
        
        return pages
    
    def _estimate_total_height(
        self,
        data: Dict[str, Any],
        style: Dict[str, Any],
    ) -> float:
        """估算内容总高度（Pt）"""
        font_config = style.get("font_config", {})
        spacing_config = style.get("spacing_config", {})
        
        body_size = font_config.get("body_size", 9)
        section_gap = spacing_config.get("section_gap", 4)
        item_gap = spacing_config.get("item_gap", 1)
        line_height = spacing_config.get("line_height", 1.0)
        
        total = 0.0
        
        # 1. Header（姓名+联系方式）
        total += self.HEADER_HEIGHT
        
        # 2. Summary（个人简介）
        summary = data.get("summary", "")
        if summary:
            total += self.SECTION_HEADER_HEIGHT + section_gap
            lines = max(1, len(summary) / self.CHARS_PER_LINE)
            total += lines * body_size * line_height * self.LINE_HEIGHT_FACTOR
        
        # 3. Experience（工作经历）
        experiences = data.get("experience", [])
        if experiences:
            total += self.SECTION_HEADER_HEIGHT + section_gap
            for exp in experiences:
                total += self._estimate_item_height(exp, body_size, line_height)
                total += item_gap
        
        # 4. Projects（项目经验）
        projects = data.get("projects", [])
        if projects:
            total += self.SECTION_HEADER_HEIGHT + section_gap
            for proj in projects:
                total += self._estimate_item_height(proj, body_size, line_height)
                total += item_gap
        
        # 5. Education（教育背景）
        education = data.get("education", [])
        if education:
            total += self.SECTION_HEADER_HEIGHT + section_gap
            for edu in education:
                total += self.ITEM_BASE_HEIGHT * 0.8  # 教育经历通常较短
        
        # 6. Skills（技能）
        skills = data.get("skills", [])
        if skills:
            total += self.SECTION_HEADER_HEIGHT + section_gap
            # 假设每行 5-6 个技能
            skill_lines = max(1, len(skills) / 5)
            total += skill_lines * self.SKILL_LINE_HEIGHT
        
        # 7. 其他部分（证书、奖项等）
        for section in ["certificates", "awards", "languages"]:
            items = data.get(section, [])
            if items:
                total += self.SECTION_HEADER_HEIGHT + section_gap
                total += self.SKILL_LINE_HEIGHT
        
        return total
    
    def _estimate_item_height(
        self,
        item: Dict[str, Any],
        body_size: float,
        line_height: float,
    ) -> float:
        """估算单个条目（经历/项目）的高度"""
        height = self.ITEM_BASE_HEIGHT
        
        # 描述文本
        desc = item.get("description", "")
        if desc:
            lines = max(1, len(desc) / self.CHARS_PER_LINE)
            height += lines * body_size * line_height * self.LINE_HEIGHT_FACTOR
        
        # 亮点列表
        highlights = item.get("highlights", [])
        height += len(highlights) * self.HIGHLIGHT_HEIGHT
        
        # 技术栈
        tech_stack = item.get("tech_stack", [])
        if tech_stack:
            height += self.SKILL_LINE_HEIGHT * 0.7
        
        return height
    
    def get_content_density(self, resume_data: Dict[str, Any]) -> str:
        """获取内容密度等级
        
        Returns:
            "low", "medium", "high", "very_high"
        """
        # 计算总条目数
        exp_count = len(resume_data.get("experience", []))
        proj_count = len(resume_data.get("projects", []))
        
        total_highlights = 0
        for exp in resume_data.get("experience", []):
            total_highlights += len(exp.get("highlights", []))
        for proj in resume_data.get("projects", []):
            total_highlights += len(proj.get("highlights", []))
        
        skill_count = len(resume_data.get("skills", []))
        
        # 评估密度
        score = exp_count * 3 + proj_count * 2.5 + total_highlights * 0.5 + skill_count * 0.2
        
        if score < 10:
            return "low"
        elif score < 18:
            return "medium"
        elif score < 28:
            return "high"
        else:
            return "very_high"


class LayoutOptimizer:
    """布局优化器
    
    根据页面目标调整布局参数，使内容适应目标页数。
    
    优化策略（按优先级）：
    1. 调整间距（section_gap, item_gap）
    2. 调整字体大小（body_size, small_size）
    3. 精简内容（减少 highlights 数量）
    """
    
    # 调整范围限制
    MIN_BODY_SIZE = 8
    MAX_BODY_SIZE = 11
    MIN_SECTION_GAP = 2
    MAX_SECTION_GAP = 10
    MIN_MARGIN = 0.3
    MAX_MARGIN = 0.6
    
    def __init__(self):
        self.estimator = ContentEstimator()
    
    def optimize_for_pages(
        self,
        resume_data: Dict[str, Any],
        style_config: Dict[str, Any],
        target: str = "one_page",
        max_iterations: int = 5,
    ) -> Tuple[Dict[str, Any], Dict[str, Any], str]:
        """优化布局以适应目标页数
        
        Args:
            resume_data: 简历数据
            style_config: 样式配置
            target: 目标页数 ("one_page", "two_pages", "auto")
            max_iterations: 最大迭代次数
            
        Returns:
            (优化后的数据, 优化后的样式, 优化说明)
        """
        data = copy.deepcopy(resume_data)
        style = copy.deepcopy(style_config)
        
        # 估算当前页数
        current_pages = self.estimator.estimate_pages(data, style)
        
        logger.info(f"[LayoutOptimizer] 初始估算: {current_pages:.2f}页, 目标: {target}")
        
        # 确定目标范围
        if target == "auto":
            if current_pages <= 1.1:
                target_range = (0.85, 1.0)
                target_desc = "一页"
            elif current_pages <= 1.6:
                target_range = (0.9, 1.05)
                target_desc = "紧凑一页"
            else:
                target_range = (1.5, 2.0)
                target_desc = "两页"
        elif target == "one_page":
            target_range = (0.85, 1.0)
            target_desc = "一页"
        else:  # two_pages
            target_range = (1.5, 2.0)
            target_desc = "两页"
        
        adjustments = []
        
        # 迭代优化
        for i in range(max_iterations):
            current_pages = self.estimator.estimate_pages(data, style)
            
            if target_range[0] <= current_pages <= target_range[1]:
                break
            
            if current_pages > target_range[1]:
                # 需要压缩
                adjustment = self._compress(data, style, current_pages - target_range[1])
            else:
                # 需要扩展（较少见）
                adjustment = self._expand(style, target_range[0] - current_pages)
            
            if adjustment:
                adjustments.append(adjustment)
            else:
                break
        
        # 生成优化说明
        final_pages = self.estimator.estimate_pages(data, style)
        
        if adjustments:
            notes = f"已优化为{target_desc}布局（估算 {final_pages:.1f} 页）\n调整: " + "; ".join(adjustments)
        else:
            notes = f"布局已适合{target_desc}（估算 {final_pages:.1f} 页）"
        
        return data, style, notes
    
    def _compress(
        self,
        data: Dict[str, Any],
        style: Dict[str, Any],
        excess: float,
    ) -> Optional[str]:
        """压缩布局
        
        Args:
            data: 简历数据（会被修改）
            style: 样式配置（会被修改）
            excess: 超出目标的页数
            
        Returns:
            调整说明
        """
        spacing = style.setdefault("spacing_config", {})
        font = style.setdefault("font_config", {})
        
        # 策略1：减小间距
        section_gap = spacing.get("section_gap", 4)
        if section_gap > self.MIN_SECTION_GAP:
            new_gap = max(self.MIN_SECTION_GAP, section_gap - 1)
            spacing["section_gap"] = new_gap
            return f"章节间距 {section_gap}→{new_gap}"
        
        item_gap = spacing.get("item_gap", 1)
        if item_gap > 0:
            spacing["item_gap"] = 0
            return "条目间距→0"
        
        # 策略2：减小边距
        margin = spacing.get("margin", 0.4)
        if margin > self.MIN_MARGIN:
            new_margin = max(self.MIN_MARGIN, margin - 0.05)
            spacing["margin"] = new_margin
            return f"边距 {margin}→{new_margin}"
        
        # 策略3：减小字体
        body_size = font.get("body_size", 9)
        if body_size > self.MIN_BODY_SIZE:
            new_size = body_size - 1
            font["body_size"] = new_size
            font["subheading_size"] = max(new_size, font.get("subheading_size", 9) - 1)
            font["small_size"] = max(7, font.get("small_size", 8) - 1)
            return f"字体 {body_size}→{new_size}"
        
        # 策略4：精简内容
        return self._trim_content(data)
    
    def _trim_content(self, data: Dict[str, Any]) -> Optional[str]:
        """精简内容"""
        trimmed = []
        
        # 减少 highlights
        for exp in data.get("experience", []):
            highlights = exp.get("highlights", [])
            if len(highlights) > 3:
                exp["highlights"] = highlights[:3]
                trimmed.append("经历亮点→3条")
                break
        
        if not trimmed:
            for proj in data.get("projects", []):
                highlights = proj.get("highlights", [])
                if len(highlights) > 3:
                    proj["highlights"] = highlights[:3]
                    trimmed.append("项目亮点→3条")
                    break
        
        # 减少项目数量
        if not trimmed:
            projects = data.get("projects", [])
            if len(projects) > 2:
                data["projects"] = projects[:2]
                trimmed.append(f"项目数→2")
        
        # 减少技能数量
        if not trimmed:
            skills = data.get("skills", [])
            if len(skills) > 12:
                data["skills"] = skills[:12]
                trimmed.append("技能数→12")
        
        return trimmed[0] if trimmed else None
    
    def _expand(self, style: Dict[str, Any], deficit: float) -> Optional[str]:
        """扩展布局（较少使用）"""
        spacing = style.setdefault("spacing_config", {})
        font = style.setdefault("font_config", {})
        
        # 增大间距
        section_gap = spacing.get("section_gap", 4)
        if section_gap < self.MAX_SECTION_GAP:
            new_gap = min(self.MAX_SECTION_GAP, section_gap + 2)
            spacing["section_gap"] = new_gap
            return f"章节间距 {section_gap}→{new_gap}"
        
        # 增大字体
        body_size = font.get("body_size", 9)
        if body_size < self.MAX_BODY_SIZE:
            new_size = body_size + 1
            font["body_size"] = new_size
            return f"字体 {body_size}→{new_size}"
        
        return None


class PageSplitter:
    """页面拆分器
    
    将内容合理地拆分到多个页面，确保不会在奇怪的位置断开。
    """
    
    def __init__(self):
        self.estimator = ContentEstimator()
    
    def split_for_two_pages(
        self,
        resume_data: Dict[str, Any],
        style_config: Dict[str, Any],
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """将简历拆分为两页
        
        Args:
            resume_data: 简历数据
            style_config: 样式配置
            
        Returns:
            (第一页数据, 第二页数据)
        """
        # 第一页：核心信息
        page1 = {
            "name": resume_data.get("name"),
            "phone": resume_data.get("phone"),
            "email": resume_data.get("email"),
            "location": resume_data.get("location"),
            "summary": resume_data.get("summary"),
            "experience": resume_data.get("experience", [])[:2],  # 最近2份经历
            "projects": resume_data.get("projects", [])[:2],      # 最重要2个项目
        }
        
        # 第二页：补充信息
        page2 = {
            "experience": resume_data.get("experience", [])[2:],  # 其余经历
            "projects": resume_data.get("projects", [])[2:],      # 其余项目
            "education": resume_data.get("education", []),
            "skills": resume_data.get("skills", []),
            "certificates": resume_data.get("certificates", []),
            "awards": resume_data.get("awards", []),
        }
        
        return page1, page2
    
    def get_page_break_recommendation(
        self,
        resume_data: Dict[str, Any],
        style_config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """获取分页建议
        
        Returns:
            包含分页建议的字典
        """
        pages = self.estimator.estimate_pages(resume_data, style_config)
        density = self.estimator.get_content_density(resume_data)
        
        if pages <= 1.0:
            recommendation = "single_page"
            notes = "内容适合单页"
        elif pages <= 1.2 and density in ["low", "medium"]:
            recommendation = "compress_to_one"
            notes = "建议压缩到一页"
        elif pages <= 1.5:
            recommendation = "compress_or_two"
            notes = "可压缩到一页，或使用两页"
        else:
            recommendation = "two_pages"
            notes = "建议使用两页"
        
        return {
            "estimated_pages": round(pages, 2),
            "content_density": density,
            "recommendation": recommendation,
            "notes": notes,
        }
