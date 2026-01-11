# -*- coding: utf-8 -*-
"""工作流基类。

定义工作流的通用接口和行为。
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import time

from common.logger import get_logger

logger = get_logger(__name__)


@dataclass
class WorkflowResult:
    """工作流执行结果"""
    success: bool
    output: Dict[str, Any]
    suggestions: List[str] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)
    error: Optional[str] = None
    execution_time: float = 0.0
    steps_completed: int = 0
    total_steps: int = 0


@dataclass
class WorkflowContext:
    """工作流上下文（在步骤间传递）"""
    input_data: Dict[str, Any]
    job_description: str = ""
    template_name: str = ""
    page_preference: str = "auto"
    output_dir: str = "./output"
    
    # 中间结果
    optimized_data: Optional[Dict[str, Any]] = None
    template_config: Optional[Dict[str, Any]] = None
    layout_config: Optional[Dict[str, Any]] = None
    
    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseWorkflow(ABC):
    """工作流基类
    
    定义专家流水线的通用行为。
    
    子类需要：
    1. 设置 WORKFLOW_NAME 和 WORKFLOW_STEPS
    2. 实现 _execute_steps() 定义具体流程
    """
    
    WORKFLOW_NAME: str = "base"
    WORKFLOW_STEPS: List[str] = []
    
    def __init__(self, llm=None):
        """初始化工作流
        
        Args:
            llm: LLM 实例（用于专家 Agent）
        """
        self.llm = llm
        self._logs: List[str] = []
        self._current_step: int = 0
        
        logger.info(f"[{self.WORKFLOW_NAME}] 工作流初始化完成")
    
    @abstractmethod
    def _execute_steps(self, ctx: WorkflowContext) -> WorkflowResult:
        """执行工作流步骤（子类实现）"""
        pass
    
    def run(
        self,
        input_data: Dict[str, Any],
        job_description: str = "",
        template_name: str = "",
        page_preference: str = "auto",
        output_dir: str = "./output",
        **kwargs,
    ) -> WorkflowResult:
        """执行工作流
        
        Args:
            input_data: 输入数据
            job_description: 职位描述（可选）
            template_name: 模板名称（可选）
            page_preference: 页面偏好
            output_dir: 输出目录
            
        Returns:
            WorkflowResult
        """
        self._logs.clear()
        self._current_step = 0
        start_time = time.time()
        
        # 创建上下文
        ctx = WorkflowContext(
            input_data=input_data,
            job_description=job_description,
            template_name=template_name,
            page_preference=page_preference,
            output_dir=output_dir,
            metadata=kwargs,
        )
        
        self._log(f"开始执行工作流: {self.WORKFLOW_NAME}")
        self._log(f"总步骤: {len(self.WORKFLOW_STEPS)}")
        
        if job_description:
            self._log(f"职位描述: {len(job_description)} 字符")
        if template_name:
            self._log(f"指定模板: {template_name}")
        
        try:
            result = self._execute_steps(ctx)
            result.logs = self._logs.copy()
            result.execution_time = time.time() - start_time
            result.total_steps = len(self.WORKFLOW_STEPS)
            
            self._log(f"工作流完成，耗时 {result.execution_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"[{self.WORKFLOW_NAME}] 执行失败: {e}", exc_info=True)
            return WorkflowResult(
                success=False,
                output={},
                logs=self._logs.copy(),
                error=str(e),
                execution_time=time.time() - start_time,
                steps_completed=self._current_step,
                total_steps=len(self.WORKFLOW_STEPS),
            )
    
    def _log(self, message: str):
        """记录日志"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{self.WORKFLOW_NAME}] {message}"
        self._logs.append(log_entry)
        logger.info(f"[{self.WORKFLOW_NAME}] {message}")
    
    def _step(self, step_name: str):
        """标记进入新步骤"""
        self._current_step += 1
        self._log(f"Step {self._current_step}/{len(self.WORKFLOW_STEPS)}: {step_name}")
