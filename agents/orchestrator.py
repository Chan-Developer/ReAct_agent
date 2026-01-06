"""
Resume Agent Orchestrator - 简历 Agent 协调器

负责：
- 协调 ContentAgent 和 LayoutAgent 的工作流程
- 管理 Agent 间的数据传递
- 提供统一的简历优化入口
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import json
import time

from .base import LLMProtocol, AgentResult
from .content_agent import ContentAgent
from .layout_agent import LayoutAgent, LayoutConfig
from common.logger import get_logger

logger = get_logger(__name__)


@dataclass
class OrchestratorResult:
    """协调器执行结果"""
    success: bool
    optimized_resume: Dict[str, Any]
    layout_config: Dict[str, Any]
    content_suggestions: List[str] = field(default_factory=list)
    layout_suggestions: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    agent_logs: List[str] = field(default_factory=list)
    error: Optional[str] = None


class ResumeAgentOrchestrator:
    """
    简历 Agent 协调器
    
    协调多个专业 Agent 完成简历优化任务：
    1. ContentAgent: 优化内容质量
    2. LayoutAgent: 优化布局编排
    
    工作流程：
    原始简历 -> ContentAgent 优化 -> LayoutAgent 编排 -> 最终简历
    """
    
    def __init__(
        self,
        llm: LLMProtocol,
        enable_content_optimization: bool = True,
        enable_layout_optimization: bool = True,
    ):
        self.llm = llm
        self.enable_content = enable_content_optimization
        self.enable_layout = enable_layout_optimization
        
        # 初始化 Agents
        self.content_agent = ContentAgent(llm) if enable_content_optimization else None
        self.layout_agent = LayoutAgent(llm) if enable_layout_optimization else None
        
        self.execution_logs: List[str] = []
        
        logger.info(
            f"ResumeAgentOrchestrator 初始化完成 "
            f"(内容优化: {enable_content_optimization}, 布局优化: {enable_layout_optimization})"
        )
    
    def _log(self, message: str):
        """记录执行日志"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.execution_logs.append(log_entry)
        logger.info(message)
    
    def optimize(
        self,
        resume_data: Dict[str, Any],
        style_preference: str = "modern",
    ) -> OrchestratorResult:
        """
        执行完整的简历优化流程
        
        Args:
            resume_data: 原始简历数据
            style_preference: 样式偏好 (modern/classic/minimal/creative)
            
        Returns:
            OrchestratorResult: 包含优化后的简历和配置
        """
        start_time = time.time()
        self.execution_logs.clear()
        
        self._log("开始简历优化流程...")
        
        current_data = resume_data.copy()
        content_suggestions = []
        layout_suggestions = []
        layout_config = {}
        
        try:
            # Step 1: 内容优化
            if self.content_agent:
                self._log("Step 1/2: 运行 ContentAgent 进行内容优化...")
                content_result = self.content_agent.run(current_data)
                
                if content_result.success:
                    current_data = content_result.data
                    content_suggestions = content_result.suggestions
                    self._log(f"内容优化完成，获得 {len(content_suggestions)} 条建议")
                else:
                    self._log(f"内容优化失败: {content_result.error}，使用原始内容继续")
            else:
                self._log("Step 1/2: ContentAgent 已禁用，跳过内容优化")
            
            # Step 2: 布局编排
            if self.layout_agent:
                self._log("Step 2/2: 运行 LayoutAgent 进行布局编排...")
                layout_result = self.layout_agent.run(current_data)
                
                if layout_result.success:
                    result_data = layout_result.data
                    current_data = result_data.get("resume_data", current_data)
                    layout_config = result_data.get("layout_config", {})
                    layout_suggestions = layout_result.suggestions
                    self._log(f"布局编排完成，获得 {len(layout_suggestions)} 条建议")
                else:
                    self._log(f"布局编排失败: {layout_result.error}，使用默认配置")
                    layout_config = self.layout_agent._get_default_config(current_data)
            else:
                self._log("Step 2/2: LayoutAgent 已禁用，跳过布局编排")
                layout_config = LayoutConfig().__dict__
            
            execution_time = time.time() - start_time
            self._log(f"优化流程完成，耗时 {execution_time:.2f} 秒")
            
            return OrchestratorResult(
                success=True,
                optimized_resume=current_data,
                layout_config=layout_config,
                content_suggestions=content_suggestions,
                layout_suggestions=layout_suggestions,
                execution_time=execution_time,
                agent_logs=self.execution_logs.copy(),
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"优化流程异常: {str(e)}"
            self._log(error_msg)
            logger.error(error_msg, exc_info=True)
            
            return OrchestratorResult(
                success=False,
                optimized_resume=resume_data,
                layout_config=LayoutConfig().__dict__,
                execution_time=execution_time,
                agent_logs=self.execution_logs.copy(),
                error=str(e),
            )
    
    def optimize_content_only(self, resume_data: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """
        仅执行内容优化
        
        Args:
            resume_data: 原始简历数据
            
        Returns:
            (优化后的数据, 建议列表)
        """
        if not self.content_agent:
            logger.warning("ContentAgent 未启用")
            return resume_data, []
        
        result = self.content_agent.run(resume_data)
        
        if result.success:
            return result.data, result.suggestions
        
        return resume_data, []
    
    def optimize_layout_only(
        self,
        resume_data: Dict[str, Any],
        style_preference: str = "modern"
    ) -> Tuple[Dict[str, Any], Dict[str, Any], List[str]]:
        """
        仅执行布局编排
        
        Args:
            resume_data: 简历数据
            style_preference: 样式偏好
            
        Returns:
            (精简后的数据, 布局配置, 建议列表)
        """
        if not self.layout_agent:
            logger.warning("LayoutAgent 未启用")
            return resume_data, LayoutConfig().__dict__, []
        
        result = self.layout_agent.run(resume_data)
        
        if result.success:
            return (
                result.data.get("resume_data", resume_data),
                result.data.get("layout_config", {}),
                result.suggestions
            )
        
        return resume_data, LayoutConfig().__dict__, []
    
    def get_suggestions(self, resume_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        获取所有 Agent 的改进建议（不执行优化）
        
        Args:
            resume_data: 简历数据
            
        Returns:
            各 Agent 的建议
        """
        suggestions = {
            "content": [],
            "layout": []
        }
        
        if self.content_agent:
            try:
                reasoning = self.content_agent.think(resume_data)
                suggestions["content"] = self.content_agent._extract_suggestions(reasoning)
            except Exception as e:
                logger.error(f"获取内容建议失败: {e}")
        
        if self.layout_agent:
            try:
                suggestions["layout"] = self.layout_agent.suggest_improvements(resume_data)
            except Exception as e:
                logger.error(f"获取布局建议失败: {e}")
        
        return suggestions
    
    def reset(self):
        """重置所有 Agent 状态"""
        if self.content_agent:
            self.content_agent.reset()
        if self.layout_agent:
            self.layout_agent.reset()
        self.execution_logs.clear()
        logger.debug("Orchestrator 状态已重置")

