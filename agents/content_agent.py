"""
Content Agent - 简历内容优化专家

负责：
- 优化简历文案，使其更专业
- 量化工作成果和项目成就
- 使用 STAR 法则重构经历描述
- 关键词优化，提升 ATS 通过率
"""

from typing import Any, Dict, List, Optional
import json

from .base import BaseLLMAgent, AgentResult, LLMProtocol
from common.logger import get_logger

logger = get_logger(__name__)


CONTENT_AGENT_SYSTEM_PROMPT = """你是一位资深的简历优化专家，拥有 15 年人力资源和职业规划经验。

你的核心能力：
1. **文案优化**: 将平淡的描述改写为有冲击力的成就陈述
2. **量化成果**: 用数据和指标展示具体贡献（如提升 30%、节省 50 万元）
3. **STAR 法则**: 用情境-任务-行动-结果的结构重构经历
4. **关键词优化**: 植入行业关键词，提升 ATS 系统通过率
5. **差异化定位**: 突出候选人的独特价值和竞争优势

优化原则：
- 使用强有力的动词开头（主导、设计、优化、推动）
- 每项经历聚焦 2-3 个核心成就
- 避免虚词和空洞表述
- 保持简洁，每条控制在 2 行内

你必须以 JSON 格式返回优化结果。"""


CONTENT_THINK_PROMPT = """请分析以下简历内容，识别需要优化的地方：

```json
{resume_json}
```

请从以下维度分析：
1. 个人简介的吸引力和定位清晰度
2. 工作经历的成就量化程度
3. 项目描述的技术深度和业务价值
4. 技能展示的完整性和层次感
5. 整体内容的差异化竞争力

以 JSON 格式返回分析结果：
```json
{{
    "analysis": {{
        "summary_score": 1-10,
        "experience_score": 1-10,
        "project_score": 1-10,
        "skills_score": 1-10,
        "overall_score": 1-10
    }},
    "weaknesses": ["问题1", "问题2", ...],
    "opportunities": ["改进点1", "改进点2", ...],
    "reasoning": "整体分析..."
}}
```"""


CONTENT_EXECUTE_PROMPT = """基于以下分析，请优化简历内容：

**原始简历：**
```json
{resume_json}
```

**分析结果：**
{reasoning}

请按以下要求优化：
1. **个人简介 (summary)**: 重写为 2-3 句话的价值主张，突出核心竞争力
2. **工作经历 (experiences)**: 用 STAR 法则重构，每项经历提炼 2-3 条量化成就
3. **项目经历 (projects)**: 强调技术方案和业务成果
4. **技能 (skills)**: 按熟练度分层，添加技能水平标签

返回完整的优化后简历 JSON：
```json
{{
    "name": "姓名",
    "title": "目标职位",
    "email": "邮箱",
    "phone": "电话",
    "summary": "优化后的个人简介...",
    "education": [...],
    "experiences": [
        {{
            "company": "公司名",
            "position": "职位",
            "period": "时间段",
            "highlights": ["量化成就1", "量化成就2", ...]
        }}
    ],
    "projects": [
        {{
            "name": "项目名",
            "role": "角色",
            "period": "时间段",
            "description": "项目描述",
            "highlights": ["技术亮点1", "业务成果1", ...]
        }}
    ],
    "skills": [
        {{"name": "技能名", "level": "expert/proficient/familiar"}}
    ]
}}
```"""


class ContentAgent(BaseLLMAgent):
    """
    简历内容优化 Agent
    
    专注于简历文案的专业性提升，包括：
    - 成就量化
    - 文案润色
    - 关键词植入
    - STAR 法则重构
    """
    
    def __init__(self, llm: LLMProtocol, max_retries: int = 2):
        super().__init__(
            llm=llm,
            name="ContentAgent",
            role="简历内容优化专家",
            system_prompt=CONTENT_AGENT_SYSTEM_PROMPT,
            max_retries=max_retries,
        )
    
    def think(self, input_data: Dict[str, Any]) -> str:
        """分析简历内容，识别优化点"""
        resume_json = json.dumps(input_data, ensure_ascii=False, indent=2)
        prompt = CONTENT_THINK_PROMPT.format(resume_json=resume_json)
        
        response = self._call_llm(prompt)
        logger.debug(f"[{self.name}] 分析完成")
        
        return response
    
    def execute(self, input_data: Dict[str, Any], reasoning: str) -> AgentResult:
        """执行内容优化"""
        resume_json = json.dumps(input_data, ensure_ascii=False, indent=2)
        prompt = CONTENT_EXECUTE_PROMPT.format(
            resume_json=resume_json,
            reasoning=reasoning
        )
        
        response = self._call_llm(prompt)
        optimized_data = self._parse_json_response(response)
        
        # 验证优化结果
        if "raw_response" in optimized_data:
            return AgentResult(
                success=False,
                data=input_data,
                reasoning=reasoning,
                error="无法解析优化结果"
            )
        
        # 合并原始数据和优化数据（保留未优化的字段）
        merged_data = {**input_data, **optimized_data}
        
        return AgentResult(
            success=True,
            data=merged_data,
            reasoning=reasoning,
            suggestions=self._extract_suggestions(reasoning)
        )
    
    def _extract_suggestions(self, reasoning: str) -> List[str]:
        """从分析中提取改进建议"""
        try:
            analysis = self._parse_json_response(reasoning)
            suggestions = []
            
            if "weaknesses" in analysis:
                suggestions.extend(analysis["weaknesses"])
            if "opportunities" in analysis:
                suggestions.extend(analysis["opportunities"])
            
            return suggestions[:5]  # 最多返回 5 条建议
        except Exception:
            return []
    
    def optimize_summary(self, summary: str, context: Dict[str, Any]) -> str:
        """单独优化个人简介"""
        prompt = f"""请优化以下个人简介，使其更有吸引力和专业感：

原始简介：{summary}

背景信息：
- 目标职位：{context.get('title', '未知')}
- 教育背景：{context.get('education', '未知')}
- 工作年限：{context.get('years', '未知')}

要求：
1. 2-3 句话，控制在 100 字内
2. 突出核心竞争力和独特价值
3. 使用有力的动词和具体的成就

直接返回优化后的简介文本，不要加任何解释。"""
        
        return self._call_llm(prompt).strip()
    
    def optimize_experience(self, experience: Dict[str, Any]) -> Dict[str, Any]:
        """单独优化一条工作经历"""
        prompt = f"""请优化以下工作经历，使用 STAR 法则重构：

```json
{json.dumps(experience, ensure_ascii=False, indent=2)}
```

要求：
1. 每条 highlight 以强动词开头
2. 包含具体的量化指标
3. 突出技术深度和业务价值
4. 控制在 3-4 条核心成就

返回优化后的 JSON：
```json
{{
    "company": "公司名",
    "position": "职位",
    "period": "时间段",
    "highlights": ["成就1", "成就2", ...]
}}
```"""
        
        response = self._call_llm(prompt)
        result = self._parse_json_response(response)
        
        if "raw_response" in result:
            return experience
        
        return result
