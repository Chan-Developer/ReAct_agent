# -*- coding: utf-8 -*-
"""内容优化工具。

将 ContentAgent 包装为 Tool，供 ReactAgent 调用。
内部保留完整的 Think-Execute-Reflect 流程。

新增功能：
- 支持职位描述匹配优化
- 自动提取职位关键词
"""
from __future__ import annotations

import json
import os
import tempfile
from typing import TYPE_CHECKING, Any, Dict

from tools.base import BaseTool
from common.logger import get_logger

if TYPE_CHECKING:
    from agents.base import LLMProtocol

logger = get_logger(__name__)


class ContentOptimizerTool(BaseTool):
    """简历内容优化工具。
    
    包装 ContentAgent，保留完整的 Think-Execute-Reflect 流程。
    
    工作流程：
        1. Think: 分析简历内容，识别优化点
        2. Execute: 执行内容优化（量化成就、STAR 法则等）
        3. Reflect: 生成改进建议
        4. （如有职位描述）计算关键词匹配度
    
    Example:
        >>> from llm import ModelScopeOpenAI
        >>> llm = ModelScopeOpenAI()
        >>> tool = ContentOptimizerTool(llm)
        >>> # 基础优化
        >>> result = tool.execute(resume_json='{"name": "张三", ...}')
        >>> # 带职位匹配
        >>> result = tool.execute(
        ...     resume_json='@original',
        ...     job_description='招聘Python后端工程师...'
        ... )
    """
    
    def __init__(self, llm: "LLMProtocol"):
        """初始化工具。
        
        Args:
            llm: LLM 实例，用于初始化内部 Agent
        """
        super().__init__(
            name="content_optimizer",
            description="优化简历内容，支持职位匹配。包括：量化成就、STAR法则重构、关键词优化",
            parameters={
                "type": "object",
                "properties": {
                    "resume_json": {
                        "type": "string",
                        "description": "JSON 格式的简历数据，或使用 @original 引用原始数据",
                    },
                    "job_description": {
                        "type": "string",
                        "description": "目标职位描述（可选）。提供后会根据职位要求调整内容侧重点",
                        "default": "",
                    },
                },
                "required": ["resume_json"],
            },
        )
        self.llm = llm
        self._agent = None  # 延迟初始化
    
    @property
    def agent(self):
        """延迟加载 ContentAgent。"""
        if self._agent is None:
            from agents.crews.resume.content_agent import ContentAgent
            self._agent = ContentAgent(self.llm)
        return self._agent
    
    def execute(self, resume_json: str, job_description: str = "") -> str:
        """执行内容优化。
        
        Args:
            resume_json: JSON 格式的简历数据或引用
            job_description: 目标职位描述（可选）
            
        Returns:
            优化结果和建议
        """
        temp_dir = tempfile.gettempdir()
        
        # 加载简历数据
        resume_data, error = self._load_resume_data(resume_json, temp_dir)
        if error:
            return error
        
        # 保存原始数据（供后续工具引用）
        self._save_original(resume_data, temp_dir)
        
        # 如果有职位描述，也保存它
        if job_description:
            self._save_job_description(job_description, temp_dir)
            logger.info("[ContentOptimizerTool] 使用职位匹配模式")
        
        logger.info("[ContentOptimizerTool] 开始内容优化...")
        
        # 调用 Agent 的完整流程（Think -> Execute -> Reflect）
        try:
            result = self.agent.run(resume_data, job_description=job_description)
        except Exception as e:
            logger.error(f"[ContentOptimizerTool] 执行失败: {e}")
            return f"❌ 内容优化失败: {e}"
        
        if not result.success:
            return f"❌ 内容优化失败: {result.error}"
        
        # 保存优化结果
        self._save_optimized(result.data, temp_dir)
        
        logger.info(f"[ContentOptimizerTool] 优化完成，{len(result.suggestions)} 条建议")
        
        # 构建返回消息
        suggestions_text = "\n".join(f"- {s}" for s in result.suggestions[:4])
        
        job_match_info = ""
        if job_description:
            keywords = self.agent.get_job_keywords()
            if keywords:
                job_match_info = f"\n\n🎯 目标职位关键词: {', '.join(keywords[:8])}"
        
        return f"""✅ 简历内容优化完成！

📝 优化建议：
{suggestions_text}{job_match_info}

优化后的数据已保存，后续步骤：
1. 调用 style_selector 选择模板（可选）
2. 调用 layout_designer 设计布局
3. 调用 generate_resume 生成文档

使用 resume_json="@optimized" 引用优化后的数据。"""
    
    def _load_resume_data(self, resume_json: str, temp_dir: str) -> tuple:
        """加载简历数据
        
        Returns:
            (数据字典, 错误消息) - 成功时错误消息为 None
        """
        ref = resume_json.strip()
        
        # 支持引用
        ref_map = {
            "@original": "original_resume.json",
            "@optimized": "optimized_resume.json",
        }
        
        if ref in ref_map:
            temp_file = os.path.join(temp_dir, ref_map[ref])
            if os.path.exists(temp_file):
                with open(temp_file, 'r', encoding='utf-8') as f:
                    return json.load(f), None
            else:
                return None, f"❌ 未找到数据文件 ({ref})"
        
        # 解析 JSON
        try:
            return json.loads(resume_json), None
        except json.JSONDecodeError as e:
            logger.error(f"[ContentOptimizerTool] JSON 解析失败: {e}")
            return None, f"❌ JSON 解析失败。请使用 resume_json=\"@original\" 引用原始数据。"
    
    def _save_original(self, data: Dict[str, Any], temp_dir: str) -> None:
        """保存原始数据"""
        temp_file = os.path.join(temp_dir, "original_resume.json")
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.debug(f"[ContentOptimizerTool] 原始数据已保存: {temp_file}")
    
    def _save_optimized(self, data: Dict[str, Any], temp_dir: str) -> None:
        """保存优化后的数据"""
        temp_file = os.path.join(temp_dir, "optimized_resume.json")
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"[ContentOptimizerTool] 优化数据已保存: {temp_file}")
    
    def _save_job_description(self, job_description: str, temp_dir: str) -> None:
        """保存职位描述（供其他工具使用）"""
        temp_file = os.path.join(temp_dir, "job_description.txt")
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(job_description)
        logger.debug(f"[ContentOptimizerTool] 职位描述已保存")
