# -*- coding: utf-8 -*-
"""LLM 简历内容优化器。

使用 LLM 对简历内容进行专业润色，使其更加符合 HR 的期望。

职责：
- 内容优化（量化成果、动词开头、STAR法则）
- 自动生成个人简介
- 丰富工作经历

依赖：
- llm.LLMProtocol: LLM 接口协议
- prompts.resume_prompts: 提示词模板
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional, TYPE_CHECKING

# 使用 TYPE_CHECKING 避免循环导入
if TYPE_CHECKING:
    from llm import LLMProtocol

# 导入提示词模板
from prompts import (
    RESUME_OPTIMIZER_SYSTEM_PROMPT,
    RESUME_OPTIMIZE_PROMPT,
    RESUME_SUMMARY_PROMPT,
    RESUME_EXPERIENCE_PROMPT,
)

__all__ = ["ResumeOptimizer"]


class ResumeOptimizer:
    """LLM 简历内容优化器。
    
    使用 LLM 对简历内容进行专业润色：
    - 量化成果：将模糊描述改为具体数字
    - 动词开头：使用强有力的动词
    - STAR法则：情境-任务-行动-结果
    - 关键词优化：确保包含行业关键词
    - 精简表达：删除冗余内容
    
    Attributes:
        llm: LLM 实例
        system_prompt: 系统提示词
        
    Example:
        >>> from llm import ModelScopeOpenAI
        >>> optimizer = ResumeOptimizer(ModelScopeOpenAI())
        >>> optimized = optimizer.optimize(resume_data)
    """
    
    def __init__(
        self,
        llm: "LLMProtocol",
        system_prompt: Optional[str] = None,
    ):
        """初始化优化器。
        
        Args:
            llm: LLM 实例，需要实现 chat 方法
            system_prompt: 自定义系统提示词（可选）
        """
        self.llm = llm
        self.system_prompt = system_prompt or RESUME_OPTIMIZER_SYSTEM_PROMPT
    
    def optimize(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """优化简历内容。
        
        使用 LLM 对简历的文字内容进行专业润色，
        保持数据结构不变，只优化文字表达。
        
        Args:
            resume_data: 原始简历数据字典
            
        Returns:
            优化后的简历数据字典
            
        Note:
            如果优化失败，会返回原始数据
        """
        prompt = RESUME_OPTIMIZE_PROMPT.format(
            resume_json=json.dumps(resume_data, ensure_ascii=False, indent=2)
        )
        
        try:
            response = self._call_llm(prompt, temperature=0.7)
            optimized = self._extract_json(response)
            
            if optimized:
                # 保留原始数据中优化器未返回的字段
                for key, value in resume_data.items():
                    if key not in optimized:
                        optimized[key] = value
                return optimized
            
            return resume_data
            
        except Exception as e:
            self._log_error("优化失败", e)
            return resume_data
    
    def generate_summary(self, resume_data: Dict[str, Any]) -> str:
        """根据简历信息自动生成个人简介。
        
        基于教育背景、技能和经历，生成一段专业的个人简介。
        
        Args:
            resume_data: 简历数据字典
            
        Returns:
            生成的个人简介文本，失败返回空字符串
        """
        # 提取教育信息
        education = resume_data.get("education", [])
        first_edu = education[0] if education else {}
        
        prompt = RESUME_SUMMARY_PROMPT.format(
            name=resume_data.get("name", "求职者"),
            school=first_edu.get("school", "未知"),
            major=first_edu.get("major", "未知"),
            degree=first_edu.get("degree", "学士"),
            skills=", ".join(resume_data.get("skills", [])) or "未填写",
            experience_count=len(resume_data.get("experience", [])),
            project_count=len(resume_data.get("projects", [])),
        )
        
        try:
            content = self._call_llm(prompt, temperature=0.8)
            # 清理可能的引号和多余空白
            return content.strip().strip('"\'')
            
        except Exception as e:
            self._log_error("生成简介失败", e)
            return ""
    
    def enrich_experience(
        self,
        resume_data: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """为缺少工作经历的简历生成一段合理的经历。
        
        基于候选人的教育背景和技能，生成一段相关的实习经历。
        
        Args:
            resume_data: 简历数据字典
            
        Returns:
            生成的工作经历字典，失败返回 None
            
        Warning:
            生成的经历仅供参考，用户应根据实际情况修改
        """
        education = resume_data.get("education", [])
        first_edu = education[0] if education else {}
        
        prompt = RESUME_EXPERIENCE_PROMPT.format(
            name=resume_data.get("name", "求职者"),
            school=first_edu.get("school", "未知"),
            major=first_edu.get("major", "未知"),
            skills=", ".join(resume_data.get("skills", [])) or "未填写",
        )
        
        try:
            content = self._call_llm(prompt, temperature=0.9)
            return self._extract_json(content)
            
        except Exception as e:
            self._log_error("生成经历失败", e)
            return None
    
    def _call_llm(self, prompt: str, temperature: float = 0.7) -> str:
        """调用 LLM。
        
        Args:
            prompt: 用户提示词
            temperature: 采样温度
            
        Returns:
            LLM 响应内容
        """
        response = self.llm.chat(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
        )
        return response.get("content", "")
    
    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """从文本中提取 JSON。
        
        支持多种格式：
        - 纯 JSON 文本
        - Markdown 代码块中的 JSON
        - 混合文本中的 JSON
        
        Args:
            text: 包含 JSON 的文本
            
        Returns:
            解析后的字典，失败返回 None
        """
        if not text:
            return None
        
        # 1. 尝试直接解析
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass
        
        # 2. 尝试从代码块中提取
        patterns = [
            r'```json\s*([\s\S]*?)\s*```',  # ```json ... ```
            r'```\s*([\s\S]*?)\s*```',       # ``` ... ```
            r'(\{[\s\S]*\})',                # { ... }
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    json_str = match.group(1)
                    return json.loads(json_str)
                except (json.JSONDecodeError, IndexError):
                    continue
        
        return None
    
    def _log_error(self, action: str, error: Exception) -> None:
        """记录错误日志。
        
        Args:
            action: 操作描述
            error: 异常对象
        """
        # TODO: 接入统一日志系统
        print(f"[ResumeOptimizer] {action}: {error}")
