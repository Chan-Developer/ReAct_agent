"""
Layout Agent - 简历布局编排专家

负责：
- 分析内容密度，决定最佳布局
- 优化章节顺序和视觉层次
- 选择合适的样式配置（字体、颜色、间距）
- 生成高端、简洁、专业的视觉方案
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import json

from .base import BaseLLMAgent, AgentResult, LLMProtocol
from common.logger import get_logger

logger = get_logger(__name__)


@dataclass
class LayoutConfig:
    """布局配置"""
    # 章节顺序
    section_order: List[str] = field(default_factory=lambda: [
        "header", "summary", "experience", "projects", "education", "skills"
    ])
    
    # 布局风格
    style: str = "modern"  # modern, classic, minimal, creative
    
    # 颜色方案
    color_scheme: str = "professional"  # professional, vibrant, elegant, monochrome
    
    # 字体配置
    font_family: str = "Microsoft YaHei"
    title_size: int = 18
    heading_size: int = 11
    body_size: int = 9
    
    # 间距配置
    margin: float = 0.5
    section_gap: int = 8
    item_gap: int = 3
    
    # 特殊效果
    use_icons: bool = True
    use_skill_bars: bool = True
    use_timeline: bool = False
    highlight_keywords: bool = True
    
    # 内容密度调整
    compact_mode: bool = False
    max_experiences: int = 4
    max_projects: int = 3
    max_highlights_per_item: int = 4


LAYOUT_AGENT_SYSTEM_PROMPT = """你是一位顶尖的简历设计专家，专注于创建高端、专业的简历布局。

你的设计理念：
1. **Less is More**: 简洁是高级感的核心，留白比填满更有力量
2. **视觉层次**: 通过字号、间距、颜色建立清晰的信息层级
3. **重点突出**: 让关键信息一眼可见，次要信息不干扰阅读
4. **专业美感**: 平衡功能性和美观度，让简历既好看又实用

布局原则：
- 应届生：教育优先，突出校园经历和潜力
- 3-5 年：经验优先，强调项目成果和专业技能
- 资深人士：成就优先，展示领导力和行业影响力

你必须以 JSON 格式返回布局配置。"""


LAYOUT_THINK_PROMPT = """请分析以下简历内容，确定最佳布局策略：

```json
{resume_json}
```

分析维度：
1. **内容量评估**: 各章节的内容多少，是否需要精简
2. **职业阶段判断**: 应届生/初级/中级/资深
3. **重点章节识别**: 哪些内容是核心卖点
4. **视觉权重分配**: 各章节应该占多大篇幅
5. **特殊处理建议**: 是否需要技能条、时间轴等

返回分析结果：
```json
{{
    "content_analysis": {{
        "total_items": 数量,
        "experiences_count": 数量,
        "projects_count": 数量,
        "education_count": 数量,
        "skills_count": 数量,
        "content_density": "sparse/normal/dense"
    }},
    "career_stage": "freshman/junior/mid/senior",
    "key_sections": ["最重要章节1", "次重要章节2"],
    "visual_weight": {{
        "header": 0.1,
        "summary": 0.1,
        "experience": 0.35,
        "projects": 0.25,
        "education": 0.1,
        "skills": 0.1
    }},
    "special_suggestions": ["建议1", "建议2"],
    "reasoning": "整体分析..."
}}
```"""


LAYOUT_EXECUTE_PROMPT = """基于以下分析，请生成最优布局配置：

**简历内容：**
```json
{resume_json}
```

**分析结果：**
{reasoning}

请生成详细的布局配置，确保：
1. 章节顺序符合职业阶段（应届生教育优先，资深者经验优先）
2. 选择合适的样式风格（modern/classic/minimal）
3. 根据内容密度调整间距和紧凑模式
4. 配置合适的视觉元素（图标、技能条等）

返回完整配置：
```json
{{
    "section_order": ["header", "summary", ...],
    "style": "modern/classic/minimal/creative",
    "color_scheme": "professional/vibrant/elegant/monochrome",
    "font_config": {{
        "family": "字体名",
        "title_size": 18,
        "heading_size": 11,
        "body_size": 9
    }},
    "spacing_config": {{
        "margin": 0.5,
        "section_gap": 8,
        "item_gap": 3
    }},
    "visual_elements": {{
        "use_icons": true/false,
        "use_skill_bars": true/false,
        "use_timeline": true/false,
        "highlight_keywords": true/false
    }},
    "content_limits": {{
        "compact_mode": true/false,
        "max_experiences": 4,
        "max_projects": 3,
        "max_highlights_per_item": 4
    }},
    "section_styles": {{
        "header": {{"alignment": "center/left", "show_photo": false}},
        "skills": {{"layout": "grid/list/bars", "columns": 3}}
    }},
    "design_notes": "设计说明..."
}}
```"""


LAYOUT_CONTENT_TRIM_PROMPT = """根据布局配置，请精简以下简历内容：

**布局配置：**
```json
{layout_config}
```

**原始内容：**
```json
{resume_json}
```

请按照配置的限制精简内容：
- 最多 {max_experiences} 条工作经历（保留最重要的）
- 最多 {max_projects} 个项目（保留最亮眼的）
- 每项经历最多 {max_highlights} 条亮点
- 如果是紧凑模式，进一步精简描述

返回精简后的完整简历 JSON。"""


class LayoutAgent(BaseLLMAgent):
    """
    简历布局编排 Agent
    
    专注于创建高端、简洁、专业的简历布局，包括：
    - 章节排序优化
    - 视觉层次设计
    - 内容密度调整
    - 样式配置生成
    """
    
    def __init__(self, llm: LLMProtocol, max_retries: int = 2):
        super().__init__(
            llm=llm,
            name="LayoutAgent",
            role="简历布局编排专家",
            system_prompt=LAYOUT_AGENT_SYSTEM_PROMPT,
            max_retries=max_retries,
        )
    
    def think(self, input_data: Dict[str, Any]) -> str:
        """分析简历内容，确定布局策略"""
        resume_json = json.dumps(input_data, ensure_ascii=False, indent=2)
        prompt = LAYOUT_THINK_PROMPT.format(resume_json=resume_json)
        
        response = self._call_llm(prompt)
        logger.debug(f"[{self.name}] 布局分析完成")
        
        return response
    
    def execute(self, input_data: Dict[str, Any], reasoning: str) -> AgentResult:
        """生成布局配置"""
        resume_json = json.dumps(input_data, ensure_ascii=False, indent=2)
        prompt = LAYOUT_EXECUTE_PROMPT.format(
            resume_json=resume_json,
            reasoning=reasoning
        )
        
        response = self._call_llm(prompt)
        layout_config = self._parse_json_response(response)
        
        if "raw_response" in layout_config:
            # 使用默认配置
            layout_config = self._get_default_config(input_data)
        
        # 根据配置精简内容
        trimmed_data = self._trim_content(input_data, layout_config)
        
        return AgentResult(
            success=True,
            data={
                "resume_data": trimmed_data,
                "layout_config": layout_config
            },
            reasoning=reasoning,
            suggestions=self._extract_design_notes(layout_config)
        )
    
    def _get_default_config(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """根据简历内容生成默认配置"""
        # 判断职业阶段
        experiences = resume_data.get("experiences", [])
        education = resume_data.get("education", [])
        
        is_fresh_grad = len(experiences) == 0 or (
            len(experiences) == 1 and "实习" in str(experiences)
        )
        
        if is_fresh_grad:
            section_order = ["header", "summary", "education", "projects", "experience", "skills"]
        else:
            section_order = ["header", "summary", "experience", "projects", "education", "skills"]
        
        return {
            "section_order": section_order,
            "style": "modern",
            "color_scheme": "professional",
            "font_config": {
                "family": "Microsoft YaHei",
                "title_size": 18,
                "heading_size": 11,
                "body_size": 9
            },
            "spacing_config": {
                "margin": 0.5,
                "section_gap": 8,
                "item_gap": 3
            },
            "visual_elements": {
                "use_icons": True,
                "use_skill_bars": True,
                "use_timeline": False,
                "highlight_keywords": True
            },
            "content_limits": {
                "compact_mode": False,
                "max_experiences": 4,
                "max_projects": 3,
                "max_highlights_per_item": 4
            },
            "design_notes": "默认专业风格配置"
        }
    
    def _trim_content(
        self,
        resume_data: Dict[str, Any],
        layout_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """根据配置精简内容"""
        limits = layout_config.get("content_limits", {})
        max_exp = limits.get("max_experiences", 4)
        max_proj = limits.get("max_projects", 3)
        max_highlights = limits.get("max_highlights_per_item", 4)
        
        trimmed = resume_data.copy()
        
        # 精简经历
        if "experiences" in trimmed:
            trimmed["experiences"] = trimmed["experiences"][:max_exp]
            for exp in trimmed["experiences"]:
                if "highlights" in exp:
                    exp["highlights"] = exp["highlights"][:max_highlights]
        
        # 精简项目
        if "projects" in trimmed:
            trimmed["projects"] = trimmed["projects"][:max_proj]
            for proj in trimmed["projects"]:
                if "highlights" in proj:
                    proj["highlights"] = proj["highlights"][:max_highlights]
        
        return trimmed
    
    def _extract_design_notes(self, layout_config: Dict[str, Any]) -> List[str]:
        """提取设计说明"""
        notes = []
        
        if "design_notes" in layout_config:
            notes.append(layout_config["design_notes"])
        
        if "section_styles" in layout_config:
            for section, style in layout_config["section_styles"].items():
                if isinstance(style, dict) and "note" in style:
                    notes.append(f"{section}: {style['note']}")
        
        return notes
    
    def suggest_improvements(self, resume_data: Dict[str, Any]) -> List[str]:
        """为简历布局提供改进建议"""
        prompt = f"""请为以下简历的布局和视觉呈现提供 5 条专业改进建议：

```json
{json.dumps(resume_data, ensure_ascii=False, indent=2)}
```

关注点：
1. 信息层次是否清晰
2. 重点是否突出
3. 留白是否合理
4. 视觉元素是否恰当
5. 整体是否简洁高级

直接返回 5 条建议，每条一行，不要编号和额外解释。"""
        
        response = self._call_llm(prompt)
        suggestions = [s.strip() for s in response.strip().split("\n") if s.strip()]
        
        return suggestions[:5]
    
    def generate_style_config(self, style_preference: str = "modern") -> Dict[str, Any]:
        """根据偏好生成样式配置"""
        style_presets = {
            "modern": {
                "color_scheme": "professional",
                "font_config": {"family": "Microsoft YaHei", "title_size": 18, "heading_size": 11, "body_size": 9},
                "spacing_config": {"margin": 0.5, "section_gap": 8, "item_gap": 3},
                "visual_elements": {"use_icons": True, "use_skill_bars": True}
            },
            "classic": {
                "color_scheme": "monochrome",
                "font_config": {"family": "SimSun", "title_size": 16, "heading_size": 12, "body_size": 10},
                "spacing_config": {"margin": 0.75, "section_gap": 10, "item_gap": 4},
                "visual_elements": {"use_icons": False, "use_skill_bars": False}
            },
            "minimal": {
                "color_scheme": "elegant",
                "font_config": {"family": "Microsoft YaHei", "title_size": 16, "heading_size": 10, "body_size": 9},
                "spacing_config": {"margin": 0.6, "section_gap": 6, "item_gap": 2},
                "visual_elements": {"use_icons": False, "use_skill_bars": True}
            },
            "creative": {
                "color_scheme": "vibrant",
                "font_config": {"family": "Microsoft YaHei", "title_size": 20, "heading_size": 12, "body_size": 9},
                "spacing_config": {"margin": 0.5, "section_gap": 10, "item_gap": 4},
                "visual_elements": {"use_icons": True, "use_skill_bars": True, "use_timeline": True}
            }
        }
        
        return style_presets.get(style_preference, style_presets["modern"])

