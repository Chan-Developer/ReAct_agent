# -*- coding: utf-8 -*-
"""Agent 核心模块。

实现 ReAct 风格的智能代理。
"""
from __future__ import annotations

import os
import platform
from string import Template
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Protocol

from common import get_config, get_logger
from prompts import REACT_SYSTEM_PROMPT

from .message import Conversation
from .parser import parse_tool_calls

if TYPE_CHECKING:
    from tools import ToolRegistry
    from tools.base import BaseTool

logger = get_logger(__name__)

__all__ = ["Agent"]


class LLMProtocol(Protocol):
    """LLM 接口协议"""
    def chat(self, messages: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]: ...


class Agent:
    """ReAct 风格智能代理。
    
    实现"思考 → 行动 → 观察 → 最终答案"的循环。
    
    Example:
        >>> from llm import ModelScopeOpenAI
        >>> from tools import Calculator, ToolRegistry
        >>> 
        >>> llm = ModelScopeOpenAI()
        >>> agent = Agent(llm=llm, tools=[Calculator()])
        >>> response = agent.run("计算 3*7+2")
    """
    
    def __init__(
        self, 
        llm: LLMProtocol,
        tools: Optional[List["BaseTool"]] = None,
        tool_registry: Optional["ToolRegistry"] = None,
        max_rounds: int = 5, 
        project_directory: str = ".",
    ):
        """初始化 Agent。
        
        Args:
            llm: LLM 接口实例
            tools: 工具列表
            tool_registry: 工具注册器（与 tools 二选一）
            max_rounds: 最大迭代轮数
            project_directory: 项目目录
        """
        self.llm = llm
        self.max_rounds = max_rounds
        self.project_directory = project_directory
        
        # 初始化工具注册器
        self.tool_registry = self._init_registry(tools, tool_registry)
        
        # 对话管理
        self.conversation = Conversation()
        self._system_prompt: Optional[str] = None
        
        logger.info(f"Agent 初始化完成，已注册 {len(self.tool_registry)} 个工具")

    def _init_registry(
        self,
        tools: Optional[List["BaseTool"]],
        registry: Optional["ToolRegistry"],
    ) -> "ToolRegistry":
        """初始化工具注册器"""
        from tools import ToolRegistry
        
        if registry is not None:
            return registry
        
        reg = ToolRegistry()
        if tools:
            reg.register_tools(tools)
        else:
            logger.warning("未提供工具，Agent 将在无工具模式下运行")
        return reg

    def run(self, user_input: str) -> str:
        """执行用户请求。
        
        Args:
            user_input: 用户输入
            
        Returns:
            Agent 的最终回答
        """
        logger.info(f"处理用户输入: {user_input}")
        
        self.conversation.add_user(user_input)
        self._system_prompt = self._render_system_prompt()

        for round_num in range(1, self.max_rounds + 1):
            logger.info(f"====== 第 {round_num}/{self.max_rounds} 轮 ======")
            
            try:
                response = self._think()
            except Exception as e:
                logger.error(f"LLM 调用失败: {e}", exc_info=True)
                return f"抱歉，处理过程中出现错误: {e}"

            content = response.get("content", "")
            logger.info(f"LLM 响应: {content[:200]}...")
            
            # 解析工具调用
            tool_calls = parse_tool_calls(response)

            if tool_calls:
                self.conversation.add_assistant(content, [
                    {"name": tc.name, "arguments": tc.arguments}
                    for tc in tool_calls
                ])
                logger.info(f"执行 {len(tool_calls)} 个工具调用")
                self._execute_tools(tool_calls)
                continue  

            # 检查最终答案
            if "final_answer" in content.lower():
                self.conversation.add_assistant(content)
                logger.info("任务完成")
                return content

            self.conversation.add_assistant(content)
            
            if round_num == self.max_rounds:
                return content
            
        return "达到最大迭代次数，任务可能未完成。"
    
    def reset(self) -> None:
        """重置对话历史"""
        self.conversation.clear()
        self._system_prompt = None

    def _think(self) -> Dict[str, Any]:
        """调用 LLM"""
        messages = [{"role": "system", "content": self._system_prompt}]
        messages.extend(self.conversation.to_list())
        return self.llm.chat(messages)

    def _execute_tools(self, tool_calls) -> None:
        """执行工具调用"""
        for tc in tool_calls:
            result = self._execute_single_tool(tc.name, tc.arguments)
            self.conversation.add_tool_result(tc.name, str(result))

    def _execute_single_tool(self, name: str, args: dict) -> str:
        """执行单个工具"""
        logger.info(f"执行工具: {name}")
        
        tool = self.tool_registry.get(name)
        if tool is None:
            return f"❌ 未找到工具 '{name}'"
        
        try:
            return tool.execute(**args)
        except TypeError as e:
            return f"❌ 参数错误: {e}"
        except Exception as e:
            return f"❌ 执行失败: {e}"

    def _render_system_prompt(self) -> str:
        """渲染系统提示"""
        return Template(REACT_SYSTEM_PROMPT).substitute(
            operating_system=self._get_os_name(),
            tool_list=self._format_tools(),
            file_list=self._get_files(),
        )

    def _format_tools(self) -> str:
        """格式化工具列表"""
        tools = self.tool_registry.get_all()
        if not tools:
            return "无可用工具"
        
        lines = []
        for tool in tools:
            spec = tool.as_function_spec()
            params = spec.get('parameters', {}).get('properties', {})
            param_str = ", ".join(
                f"{k}: {v.get('description', '')}" 
                for k, v in params.items()
            ) or "无参数"
            lines.append(f"- {spec['name']}: {spec['description']}\n  参数: {param_str}")
        return "\n".join(lines)

    def _get_files(self) -> str:
        """获取项目文件列表"""
        try:
            files = [f for f in os.listdir(self.project_directory) 
                     if os.path.isfile(os.path.join(self.project_directory, f))]
            return ", ".join(files[:10]) if files else "无文件"
        except Exception:
            return "无法获取"

    @staticmethod
    def _get_os_name() -> str:
        return {"Darwin": "macOS", "Windows": "Windows", "Linux": "Linux"}.get(
            platform.system(), "Unknown"
        )
