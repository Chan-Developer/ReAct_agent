# -*- coding: utf-8 -*-
"""简历生成工作流。

专家流水线：
1. ContentAgent - 内容优化专家（调用 LLM，支持职位匹配）
2. StyleSelector - 模板选择（根据 JD 自动匹配或手动指定）
3. LayoutAgent - 布局设计专家（调用 LLM）+ 智能分页优化
4. Generator - 生成 Word 文档
"""
from __future__ import annotations

import os
from typing import Any, Dict, Optional

from .base import BaseWorkflow, WorkflowResult, WorkflowContext
from common.logger import get_logger

logger = get_logger(__name__)


class ResumePipeline(BaseWorkflow):
    """简历生成流水线
    
    完整的简历生成工作流，包含：
    - 内容优化（支持职位匹配）
    - 模板选择（自动匹配或手动指定）
    - 布局设计（智能分页）
    - 文档生成
    
    Example:
        >>> from workflows import ResumePipeline
        >>> from llm import ModelScopeOpenAI
        >>> 
        >>> pipeline = ResumePipeline(llm=ModelScopeOpenAI())
        >>> result = pipeline.run(
        ...     input_data=resume_json,
        ...     job_description="招聘Python工程师...",
        ...     page_preference="one_page",
        ... )
    """
    
    WORKFLOW_NAME = "resume_pipeline"
    WORKFLOW_STEPS = [
        "内容优化",
        "模板选择", 
        "布局设计",
        "分页优化",
        "生成文档",
    ]
    
    def __init__(self, llm=None, output_dir: str = "./output"):
        super().__init__(llm=llm)
        self.output_dir = output_dir
        
        # 延迟初始化的组件
        self._content_agent = None
        self._layout_agent = None
        self._generator = None
    
    @property
    def content_agent(self):
        """延迟加载 ContentAgent"""
        if self._content_agent is None and self.llm:
            from agents.crews.resume.content_agent import ContentAgent
            self._content_agent = ContentAgent(self.llm)
        return self._content_agent
    
    @property
    def layout_agent(self):
        """延迟加载 LayoutAgent"""
        if self._layout_agent is None and self.llm:
            from agents.crews.resume.layout_agent import LayoutAgent
            self._layout_agent = LayoutAgent(self.llm)
        return self._layout_agent
    
    @property
    def generator(self):
        """延迟加载 ResumeGenerator"""
        if self._generator is None:
            from tools.generators import ResumeGenerator
            self._generator = ResumeGenerator(
                output_dir=self.output_dir,
                llm=None,
                auto_optimize=False,
            )
        return self._generator
    
    def _execute_steps(self, ctx: WorkflowContext) -> WorkflowResult:
        """执行完整流水线"""
        suggestions = []
        data = ctx.input_data.copy()
        
        # =====================================================================
        # Step 1: 内容优化（ContentAgent 专家）
        # =====================================================================
        self._step("内容优化 (ContentAgent)")
        
        if self.content_agent:
            try:
                result = self.content_agent.run(data, job_description=ctx.job_description)
                
                if result.success:
                    data = result.data
                    suggestions.extend(result.suggestions)
                    self._log(f"内容优化完成，{len(result.suggestions)} 条建议")
                    
                    # 记录职位匹配信息
                    keywords = self.content_agent.get_job_keywords()
                    if keywords:
                        self._log(f"提取关键词: {', '.join(keywords[:5])}")
                else:
                    self._log(f"内容优化失败: {result.error}")
            except Exception as e:
                self._log(f"ContentAgent 异常: {e}")
        else:
            self._log("跳过（无 LLM）")
        
        ctx.optimized_data = data
        
        # =====================================================================
        # Step 2: 模板选择
        # =====================================================================
        self._step("模板选择")
        
        template_config = self._select_template(ctx)
        ctx.template_config = template_config
        
        if template_config:
            self._log(f"使用模板配置")
        
        # =====================================================================
        # Step 3: 布局设计（LayoutAgent 专家）
        # =====================================================================
        self._step("布局设计 (LayoutAgent)")
        
        layout_config = template_config or {}
        
        if self.layout_agent:
            try:
                result = self.layout_agent.run(data)
                
                if result.success:
                    result_data = result.data
                    data = result_data.get("resume_data", data)
                    agent_layout = result_data.get("layout_config", {})
                    
                    # 合并配置（模板配置优先）
                    layout_config = {**agent_layout, **layout_config}
                    suggestions.extend(result.suggestions)
                    self._log(f"布局设计完成")
                else:
                    self._log(f"布局设计失败: {result.error}")
            except Exception as e:
                self._log(f"LayoutAgent 异常: {e}")
        else:
            self._log("跳过（无 LLM）")
        
        # =====================================================================
        # Step 4: 智能分页优化
        # =====================================================================
        self._step("分页优化")
        
        data, layout_config = self._optimize_pagination(
            data, layout_config, ctx.page_preference
        )
        
        ctx.layout_config = layout_config
        
        # =====================================================================
        # Step 5: 生成文档
        # =====================================================================
        self._step("生成文档")
        
        # 嵌入布局配置
        data["_layout_config"] = layout_config
        
        # 生成文件名
        name = data.get("name", "resume")
        filename = f"{name}_resume"
        
        # 保存数据到临时文件
        import tempfile
        import json
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, "layout_resume.json")
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # 生成文档
        try:
            gen_result = self.generator.execute(
                resume_data="@layout",
                filename=filename,
                optimize=False,
            )
            
            if "成功" in gen_result:
                self._log(f"文档生成成功: {filename}.docx")
                output_path = os.path.join(self.output_dir, f"{filename}.docx")
            else:
                self._log(f"文档生成失败: {gen_result}")
                output_path = None
        except Exception as e:
            self._log(f"生成器异常: {e}")
            output_path = None
        
        # =====================================================================
        # 返回结果
        # =====================================================================
        return WorkflowResult(
            success=output_path is not None,
            output={
                "resume_data": data,
                "layout_config": layout_config,
                "output_path": output_path,
            },
            suggestions=suggestions,
            steps_completed=len(self.WORKFLOW_STEPS),
        )
    
    def _select_template(self, ctx: WorkflowContext) -> Optional[Dict[str, Any]]:
        """选择模板配置"""
        from tools.templates import get_registry
        
        registry = get_registry()
        
        # 1. 如果指定了模板名称
        if ctx.template_name:
            config = registry.get(ctx.template_name)
            if config:
                self._log(f"使用指定模板: {config.display_name}")
                layout_config = config.to_layout_config()
                
                # 应用页面偏好
                if ctx.page_preference != "auto":
                    layout_config["page_preference"] = ctx.page_preference
                
                return layout_config
            else:
                self._log(f"模板 '{ctx.template_name}' 不存在，使用自动匹配")
        
        # 2. 根据职位描述自动匹配
        if ctx.job_description:
            matches = registry.match_job(ctx.job_description, top_k=1)
            if matches and matches[0][1] > 0.1:
                best_name, score = matches[0]
                config = registry.get(best_name)
                if config:
                    self._log(f"自动匹配模板: {config.display_name} ({score:.0%})")
                    layout_config = config.to_layout_config()
                    
                    if ctx.page_preference != "auto":
                        layout_config["page_preference"] = ctx.page_preference
                    
                    return layout_config
        
        # 3. 使用默认模板
        config = registry.get("tech_modern")
        if config:
            self._log("使用默认模板: tech_modern")
            return config.to_layout_config()
        
        return None
    
    def _optimize_pagination(
        self,
        data: Dict[str, Any],
        layout_config: Dict[str, Any],
        page_preference: str,
    ) -> tuple:
        """执行分页优化"""
        from tools.generators.pagination import ContentEstimator, LayoutOptimizer
        
        estimator = ContentEstimator()
        optimizer = LayoutOptimizer()
        
        # 估算页数
        pages = estimator.estimate_pages(data, layout_config)
        self._log(f"估算页数: {pages:.2f}")
        
        # 判断是否需要优化
        if page_preference == "one_page" and pages > 1.0:
            # 需要压缩
            data, layout_config, notes = optimizer.optimize_for_pages(
                data, layout_config, target="one_page"
            )
            self._log(f"优化为一页: {notes}")
        elif page_preference == "auto" and pages > 1.1:
            # 自动优化
            data, layout_config, notes = optimizer.optimize_for_pages(
                data, layout_config, target="one_page"
            )
            self._log(f"自动优化: {notes}")
        else:
            self._log("无需优化")
        
        return data, layout_config
