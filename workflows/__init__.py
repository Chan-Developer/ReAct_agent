# -*- coding: utf-8 -*-
"""工作流模块。

存放各种专家流水线工作流。

每个工作流定义一个固定的专家执行顺序，
专家之间通过数据传递协作完成任务。

可用工作流：
- ResumePipeline: 简历生成流水线
  ContentAgent → StyleSelector → LayoutAgent → Generator
"""

from .base import BaseWorkflow, WorkflowResult
from .resume_pipeline import ResumePipeline

__all__ = [
    "BaseWorkflow",
    "WorkflowResult",
    "ResumePipeline",
]
