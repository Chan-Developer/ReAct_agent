# -*- coding: utf-8 -*-
"""内容优化工具。

将 ContentAgent 包装为 Tool，供 ReactAgent 调用。
内部保留完整的 Think-Execute-Reflect 流程。
"""
from __future__ import annotations

import json
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
    
    Example:
        >>> from llm import ModelScopeOpenAI
        >>> llm = ModelScopeOpenAI()
        >>> tool = ContentOptimizerTool(llm)
        >>> result = tool.execute(resume_json='{"name": "张三", ...}')
    """
    
    def __init__(self, llm: "LLMProtocol"):
        """初始化工具。
        
        Args:
            llm: LLM 实例，用于初始化内部 Agent
        """
        super().__init__(
            name="content_optimizer",
            description="优化简历内容，包括：量化成就、STAR法则重构、关键词优化",
            parameters={
                "type": "object",
                "properties": {
                    "resume_json": {
                        "type": "string",
                        "description": "JSON 格式的简历数据",
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
    
    def execute(self, resume_json: str) -> str:
        """执行内容优化。
        
        Args:
            resume_json: JSON 格式的简历数据
            
        Returns:
            优化后的 JSON 数据和建议
        """
        # 解析输入
        try:
            resume_data = json.loads(resume_json)
        except json.JSONDecodeError as e:
            return f"❌ JSON 解析失败: {e}"
        
        logger.info("[ContentOptimizerTool] 开始内容优化...")
        
        # 调用 Agent 的完整流程（Think -> Execute -> Reflect）
        try:
            result = self.agent.run(resume_data)
        except Exception as e:
            logger.error(f"[ContentOptimizerTool] 执行失败: {e}")
            return f"❌ 内容优化失败: {e}"
        
        if not result.success:
            return f"❌ 内容优化失败: {result.error}"
        
        # 保存优化结果到临时文件（避免 LLM 传递长 JSON）
        import tempfile
        import os
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, "optimized_resume.json")
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(result.data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"[ContentOptimizerTool] 优化完成，{len(result.suggestions)} 条建议")
        logger.info(f"[ContentOptimizerTool] 结果已保存到: {temp_file}")
        
        # 返回简短的成功消息（不包含完整 JSON）
        return f"""✅ 简历内容优化完成！

优化建议：
{chr(10).join(f"- {s}" for s in result.suggestions[:3])}

优化后的数据已保存，调用 layout_designer 或 generate_resume 时可使用 resume_json="@optimized" 来使用优化后的数据。"""
