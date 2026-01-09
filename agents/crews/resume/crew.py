# -*- coding: utf-8 -*-
"""简历优化 Crew - 适配通用框架。"""
from typing import TYPE_CHECKING

from ..base import BaseCrew
from .content_agent import ContentAgent
from .layout_agent import LayoutAgent

if TYPE_CHECKING:
    from core.task import Task, TaskResult


class ResumeCrew(BaseCrew):
    """简历优化团队
    
    包含两个专业 Agent：
    - ContentAgent: 内容优化
    - LayoutAgent: 布局编排
    """
    
    CREW_NAME = "resume"
    
    def _init_agents(self):
        """初始化团队成员"""
        self.content_agent = ContentAgent(self.llm)
        self.layout_agent = LayoutAgent(self.llm)
        self.agents = [self.content_agent, self.layout_agent]
    
    def _execute(self, task: "Task") -> "TaskResult":
        """执行简历优化流程"""
        from core.task import TaskResult
        
        data = task.input_data
        suggestions = []
        
        # 将 RAG 检索的参考传给 content agent
        references = task.context.get("references", [])
        if references:
            self._log(f"使用 {len(references)} 条参考案例进行优化")
        
        # Step 1: 内容优化
        self._log("Step 1/2: ContentAgent 优化内容...")
        content_result = self.content_agent.run(data)
        
        if content_result.success:
            data = content_result.data
            suggestions.extend(content_result.suggestions)
            self._log(f"内容优化完成，{len(content_result.suggestions)} 条建议")
        else:
            self._log(f"内容优化失败: {content_result.error}")
        
        # Step 2: 布局编排
        self._log("Step 2/2: LayoutAgent 编排布局...")
        layout_result = self.layout_agent.run(data)
        
        layout_config = {}
        if layout_result.success:
            result_data = layout_result.data
            data = result_data.get("resume_data", data)
            layout_config = result_data.get("layout_config", {})
            suggestions.extend(layout_result.suggestions)
            self._log(f"布局编排完成，{len(layout_result.suggestions)} 条建议")
        else:
            self._log(f"布局编排失败: {layout_result.error}")
        
        return TaskResult(
            success=True,
            output={
                "resume_data": data,
                "layout_config": layout_config,
            },
            suggestions=suggestions,
        )
    
    def _build_retrieval_query(self, task: "Task") -> str:
        """构建简历相关的检索查询"""
        data = task.input_data
        if isinstance(data, dict):
            # 优先使用项目描述
            projects = data.get("projects", [])
            if projects and isinstance(projects[0], dict):
                return projects[0].get("description", "")[:300]
            
            # 其次使用工作经历
            exp = data.get("experience", [])
            if exp and isinstance(exp[0], dict):
                return exp[0].get("description", "")[:300]
            
            # 最后使用技能
            skills = data.get("skills", [])
            if skills:
                return " ".join(skills[:10])
        
        return "简历优化"

