# -*- coding: utf-8 -*-
"""通用协调器 - 自动路由任务到合适的 Crew。"""
from typing import Dict, List, Optional, Type, TYPE_CHECKING

from common.logger import get_logger

if TYPE_CHECKING:
    from .task import Task, TaskResult
    from .knowledge import BaseKnowledgeBase
    from agents.crews.base import BaseCrew

logger = get_logger(__name__)


class Orchestrator:
    """通用任务协调器
    
    根据任务名自动选择合适的 Crew 执行。
    
    Usage:
        orchestrator = Orchestrator(llm, kb)
        orchestrator.register(ResumeCrew)
        orchestrator.register(CodeReviewCrew)
        
        result = orchestrator.run(task)
    """
    
    def __init__(
        self,
        llm,
        knowledge_base: Optional["BaseKnowledgeBase"] = None,
    ):
        self.llm = llm
        self.kb = knowledge_base
        self._crew_registry: Dict[str, Type["BaseCrew"]] = {}
        self._crew_instances: Dict[str, "BaseCrew"] = {}
    
    def register(self, crew_class: Type["BaseCrew"], task_names: Optional[List[str]] = None):
        """注册 Crew
        
        Args:
            crew_class: Crew 类
            task_names: 该 Crew 支持的任务名列表，默认使用 CREW_NAME
        """
        names = task_names or [crew_class.CREW_NAME]
        for name in names:
            self._crew_registry[name.lower()] = crew_class
            logger.info(f"[Orchestrator] 注册 Crew: {name} -> {crew_class.__name__}")
    
    def get_crew(self, task_name: str) -> Optional["BaseCrew"]:
        """获取或创建 Crew 实例"""
        key = task_name.lower()
        
        # 已有实例
        if key in self._crew_instances:
            return self._crew_instances[key]
        
        # 查找注册的 Crew
        crew_class = self._crew_registry.get(key)
        if crew_class is None:
            # 尝试模糊匹配
            for registered_name, cls in self._crew_registry.items():
                if registered_name in key or key in registered_name:
                    crew_class = cls
                    break
        
        if crew_class is None:
            return None
        
        # 创建实例
        crew = crew_class(self.llm, self.kb)
        self._crew_instances[key] = crew
        return crew
    
    def run(self, task: "Task") -> "TaskResult":
        """执行任务"""
        from .task import TaskResult
        
        crew = self.get_crew(task.name)
        
        if crew is None:
            logger.warning(f"[Orchestrator] 未找到能处理 '{task.name}' 的 Crew")
            return TaskResult(
                success=False,
                output=None,
                error=f"未找到能处理 '{task.name}' 的 Crew，已注册: {list(self._crew_registry.keys())}"
            )
        
        logger.info(f"[Orchestrator] 使用 {crew.CREW_NAME} 处理任务: {task.name}")
        return crew.run(task)
    
    def list_crews(self) -> List[str]:
        """列出已注册的 Crew"""
        return list(self._crew_registry.keys())

