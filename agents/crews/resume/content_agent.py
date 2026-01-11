"""
Content Agent - 简历内容优化专家

负责：
- 优化简历文案，使其更专业
- 量化工作成果和项目成就
- 使用 STAR 法则重构经历描述
- 关键词优化，提升 ATS 通过率
- 根据目标职位调整内容侧重点（新增）
"""

from typing import Any, Dict, List, Optional
import json
import re

from agents.base import BaseLLMAgent, AgentResult, LLMProtocol
from common.logger import get_logger
from prompts.content import (
    CONTENT_AGENT_SYSTEM_PROMPT,
    CONTENT_THINK_PROMPT,
    CONTENT_EXECUTE_PROMPT,
    JOB_CONTEXT_TEMPLATE,
    JOB_MATCH_DIMENSION,
    JOB_MATCH_SCORE,
    JOB_KEYWORDS_FIELD,
    JOB_SUMMARY_NOTE,
    JOB_EXP_NOTE,
    JOB_SKILLS_NOTE,
)

logger = get_logger(__name__)


class ContentAgent(BaseLLMAgent):
    """
    简历内容优化 Agent
    
    专注于简历文案的专业性提升，包括：
    - 成就量化
    - 文案润色
    - 关键词植入
    - STAR 法则重构
    - 职位匹配优化（新增）
    """
    
    def __init__(self, llm: LLMProtocol, max_retries: int = 2):
        super().__init__(
            llm=llm,
            name="ContentAgent",
            role="简历内容优化专家",
            system_prompt=CONTENT_AGENT_SYSTEM_PROMPT,
            max_retries=max_retries,
        )
        self._job_description: str = ""
        self._extracted_keywords: List[str] = []
    
    def run(
        self,
        resume_data: Dict[str, Any],
        job_description: str = "",
    ) -> AgentResult:
        """执行内容优化流程
        
        Args:
            resume_data: 简历数据字典
            job_description: 目标职位描述（可选）
            
        Returns:
            AgentResult 包含优化后的数据和建议
        """
        self._job_description = job_description
        
        # 如果有职位描述，先提取关键词
        if job_description:
            self._extracted_keywords = self._extract_job_keywords(job_description)
            logger.info(f"[{self.name}] 提取到 {len(self._extracted_keywords)} 个目标关键词")
        
        # 调用父类的 run 方法
        return super().run(resume_data)
    
    def think(self, input_data: Dict[str, Any]) -> str:
        """分析简历内容，识别优化点"""
        resume_json = json.dumps(input_data, ensure_ascii=False, indent=2)
        
        # 构建提示词（根据是否有职位描述）
        if self._job_description:
            job_context = JOB_CONTEXT_TEMPLATE.format(job_description=self._job_description)
            job_match_dimension = JOB_MATCH_DIMENSION
            job_match_score = JOB_MATCH_SCORE
            job_keywords_field = JOB_KEYWORDS_FIELD
        else:
            job_context = ""
            job_match_dimension = ""
            job_match_score = ""
            job_keywords_field = ""
        
        prompt = CONTENT_THINK_PROMPT.format(
            resume_json=resume_json,
            job_context=job_context,
            job_match_dimension=job_match_dimension,
            job_match_score=job_match_score,
            job_keywords_field=job_keywords_field,
        )
        
        response = self._call_llm(prompt)
        logger.debug(f"[{self.name}] 分析完成")
        
        return response
    
    def execute(self, input_data: Dict[str, Any], reasoning: str) -> AgentResult:
        """执行内容优化"""
        resume_json = json.dumps(input_data, ensure_ascii=False, indent=2)
        
        # 构建提示词
        if self._job_description:
            job_context = JOB_CONTEXT_TEMPLATE.format(job_description=self._job_description)
            job_summary_note = JOB_SUMMARY_NOTE
            job_exp_note = JOB_EXP_NOTE
            job_skills_note = JOB_SKILLS_NOTE
        else:
            job_context = ""
            job_summary_note = ""
            job_exp_note = ""
            job_skills_note = ""
        
        prompt = CONTENT_EXECUTE_PROMPT.format(
            resume_json=resume_json,
            reasoning=reasoning,
            job_context=job_context,
            job_summary_note=job_summary_note,
            job_exp_note=job_exp_note,
            job_skills_note=job_skills_note,
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
        
        # 提取建议
        suggestions = self._extract_suggestions(reasoning)
        
        # 如果有职位描述，添加匹配度信息
        if self._job_description and self._extracted_keywords:
            match_info = self._calculate_keyword_match(merged_data)
            suggestions.insert(0, match_info)
        
        return AgentResult(
            success=True,
            data=merged_data,
            reasoning=reasoning,
            suggestions=suggestions
        )
    
    def _extract_job_keywords(self, job_description: str) -> List[str]:
        """从职位描述中提取关键词
        
        Args:
            job_description: 职位描述文本
            
        Returns:
            关键词列表
        """
        # 使用 LLM 提取关键词
        prompt = f"""请从以下职位描述中提取关键技能和要求词汇，每个关键词用逗号分隔：

职位描述：
{job_description}

只返回关键词列表，格式如：Python, 机器学习, 数据分析, ..."""
        
        try:
            response = self._call_llm(prompt)
            keywords = [kw.strip() for kw in response.split(",") if kw.strip()]
            return keywords[:20]  # 限制数量
        except Exception as e:
            logger.warning(f"[{self.name}] 关键词提取失败: {e}")
            # 简单的关键词提取回退方案
            return self._simple_keyword_extract(job_description)
    
    def _simple_keyword_extract(self, text: str) -> List[str]:
        """简单关键词提取（回退方案）"""
        # 常见技术关键词
        tech_keywords = [
            "Python", "Java", "JavaScript", "Go", "C++", "Rust",
            "React", "Vue", "Angular", "Node.js", "Django", "Flask",
            "MySQL", "PostgreSQL", "MongoDB", "Redis", "Kafka",
            "Docker", "Kubernetes", "AWS", "Azure", "GCP",
            "机器学习", "深度学习", "NLP", "CV", "AI",
            "数据分析", "数据挖掘", "大数据", "Spark", "Hadoop",
        ]
        
        found = []
        text_lower = text.lower()
        for kw in tech_keywords:
            if kw.lower() in text_lower:
                found.append(kw)
        
        return found
    
    def _calculate_keyword_match(self, resume_data: Dict[str, Any]) -> str:
        """计算简历与职位关键词的匹配度"""
        if not self._extracted_keywords:
            return ""
        
        # 将简历内容转为文本
        resume_text = json.dumps(resume_data, ensure_ascii=False).lower()
        
        matched = []
        for kw in self._extracted_keywords:
            if kw.lower() in resume_text:
                matched.append(kw)
        
        match_rate = len(matched) / len(self._extracted_keywords) * 100
        
        return f"职位关键词匹配度: {match_rate:.0f}% ({len(matched)}/{len(self._extracted_keywords)})"
    
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
        job_note = ""
        if self._job_description:
            job_note = f"\n- 目标职位要求：{self._job_description[:200]}..."
        
        prompt = f"""请优化以下个人简介，使其更有吸引力和专业感：

原始简介：{summary}

背景信息：
- 目标职位：{context.get('title', '未知')}
- 教育背景：{context.get('education', '未知')}
- 工作年限：{context.get('years', '未知')}{job_note}

要求：
1. 2-3 句话，控制在 100 字内
2. 突出核心竞争力和独特价值
3. 使用有力的动词和具体的成就
4. 如有目标职位，需呼应岗位要求

直接返回优化后的简介文本，不要加任何解释。"""
        
        return self._call_llm(prompt).strip()
    
    def optimize_experience(self, experience: Dict[str, Any]) -> Dict[str, Any]:
        """单独优化一条工作经历"""
        job_note = ""
        if self._job_description:
            job_note = f"\n5. 突出与目标职位相关的经验"
        
        prompt = f"""请优化以下工作经历，使用 STAR 法则重构：

```json
{json.dumps(experience, ensure_ascii=False, indent=2)}
```

要求：
1. 每条 highlight 以强动词开头
2. 包含具体的量化指标
3. 突出技术深度和业务价值
4. 控制在 3-4 条核心成就{job_note}

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
    
    def get_job_keywords(self) -> List[str]:
        """获取提取的职位关键词"""
        return self._extracted_keywords.copy()
