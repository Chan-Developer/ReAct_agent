# -*- coding: utf-8 -*-
"""Crew 基类 - Agent 团队抽象。"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TYPE_CHECKING
import time

from common.logger import get_logger

if TYPE_CHECKING:
    from core.task import Task, TaskResult
    from core.knowledge import BaseKnowledgeBase
    from agents.base import BaseLLMAgent

logger = get_logger(__name__)


class BaseCrew(ABC):
    """Agent 团队基类
    
    定义一组协作的 Agent，共同完成特定类型的任务。
    
    子类需要：
    1. 设置 CREW_NAME
    2. 实现 _init_agents() 初始化团队成员
    3. 实现 _execute() 定义工作流
    """
    
    CREW_NAME: str = "BaseCrew"
    
    def __init__(
        self,
        llm,
        knowledge_base: Optional["BaseKnowledgeBase"] = None,
    ):
        self.llm = llm
        self.kb = knowledge_base
        self.agents: List["BaseLLMAgent"] = []
        self._logs: List[str] = []
        
        self._init_agents()
        logger.info(f"[{self.CREW_NAME}] 初始化完成，共 {len(self.agents)} 个 Agent")
    
    @abstractmethod
    def _init_agents(self):
        """初始化团队成员（子类实现）"""
        pass
    
    @abstractmethod
    def _execute(self, task: "Task") -> "TaskResult":
        """执行任务的具体流程（子类实现）"""
        pass
    
    def run(self, task: "Task") -> "TaskResult":
        """执行任务（完整流程）"""
        from core.task import TaskResult
        
        self._logs.clear()
        start_time = time.time()
        
        self._log(f"开始执行任务: {task.name}")
        
        # 1. RAG: 检索上下文
        if self.kb and not task.context.get("references"):
            self._log("从知识库检索参考...")
            query = self._build_retrieval_query(task)
            references = self.kb.retrieve_context(query, top_k=3)
            task.context["references"] = references
            self._log(f"检索到 {len(references)} 条参考")
        
        # 2. 执行具体流程
        try:
            result = self._execute(task)
            result.logs = self._logs.copy()
            
            elapsed = time.time() - start_time
            self._log(f"任务完成，耗时 {elapsed:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"[{self.CREW_NAME}] 执行失败: {e}", exc_info=True)
            return TaskResult(
                success=False,
                output=None,
                logs=self._logs.copy(),
                error=str(e),
            )
    
    def _build_retrieval_query(self, task: "Task") -> str:
        """构建检索查询（子类可重写）"""
        if isinstance(task.input_data, dict):
            # 尝试从常见字段构建查询
            for key in ["description", "summary", "content", "text"]:
                if key in task.input_data:
                    return str(task.input_data[key])[:500]
        return task.name
    
    def _log(self, message: str):
        """记录日志"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{self.CREW_NAME}] {message}"
        self._logs.append(log_entry)
        logger.info(f"[{self.CREW_NAME}] {message}")
    
    def reset(self):
        """重置所有 Agent 状态"""
        for agent in self.agents:
            agent.reset()
        self._logs.clear()

