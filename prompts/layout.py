# -*- coding: utf-8 -*-
"""简历布局提示词模板。

包含布局 Agent 所需的所有提示词模板。
"""

# =============================================================================
# 系统提示词
# =============================================================================

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


# =============================================================================
# 布局分析提示词
# =============================================================================

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


# =============================================================================
# 布局执行提示词
# =============================================================================

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


# =============================================================================
# 内容精简提示词
# =============================================================================

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

