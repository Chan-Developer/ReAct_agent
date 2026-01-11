# -*- coding: utf-8 -*-
"""简历专家 Agent。

使用方式:
    from workflows import ResumePipeline
    
    pipeline = ResumePipeline(llm)
    result = pipeline.run(input_data=resume_data, job_description="...")
"""

from .content_agent import ContentAgent
from .layout_agent import LayoutAgent

__all__ = [
    "ContentAgent",
    "LayoutAgent",
]

