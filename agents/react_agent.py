# -*- coding: utf-8 -*-
"""ReAct agent implementation (Reasoning + Acting)."""

from __future__ import annotations

import os
import platform
from string import Template
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Protocol

from common import get_logger
from prompts import REACT_SYSTEM_PROMPT
from core.message import Conversation
from core.parser import parse_tool_calls

if TYPE_CHECKING:
    from tools import ToolRegistry
    from tools.base import BaseTool
    from memory import MemoryManager

logger = get_logger(__name__)

__all__ = ["ReactAgent"]


class LLMProtocol(Protocol):
    """Protocol for chat-based LLM clients."""

    def chat(self, messages: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        ...


class ReactAgent:
    """Single-agent ReAct loop with optional tool use and memory context."""

    def __init__(
        self,
        llm: LLMProtocol,
        tools: Optional[List["BaseTool"]] = None,
        tool_registry: Optional["ToolRegistry"] = None,
        memory: Optional["MemoryManager"] = None,
        max_rounds: int = 5,
        project_directory: str = ".",
        use_memory_context: bool = True,
        auto_finish: bool = True,
        max_stall_rounds: int = 2,
    ):
        self.llm = llm
        self.max_rounds = max(1, max_rounds)
        self.project_directory = project_directory
        self.memory = memory
        self.use_memory_context = use_memory_context
        self.auto_finish = auto_finish
        self.max_stall_rounds = max(1, max_stall_rounds)

        self.tool_registry = self._init_registry(tools, tool_registry)
        self.conversation = Conversation()
        self._system_prompt: Optional[str] = None

        memory_status = "enabled" if memory else "disabled"
        logger.info(
            f"ReactAgent initialized, tools={len(self.tool_registry)}, memory={memory_status}"
        )

    def _init_registry(
        self,
        tools: Optional[List["BaseTool"]],
        registry: Optional["ToolRegistry"],
    ) -> "ToolRegistry":
        from tools import ToolRegistry

        if registry is not None:
            return registry

        reg = ToolRegistry()
        if tools:
            reg.register_tools(tools)
        else:
            logger.warning("No tools provided. Agent will run in no-tool mode.")
        return reg

    def run(self, user_input: str) -> str:
        """Run one request through ReAct loop."""
        logger.info(f"Handling user input: {user_input}")

        if self.memory:
            self.memory.add_conversation("user", user_input, importance=0.4)

        self.conversation.add_user(user_input)
        self._system_prompt = self._render_system_prompt(user_input)

        previous_non_tool_content = ""
        stall_rounds = 0

        for round_num in range(1, self.max_rounds + 1):
            logger.info(f"Round {round_num}/{self.max_rounds}")

            try:
                response = self._think()
            except Exception as exc:
                logger.error(f"LLM call failed: {exc}", exc_info=True)
                if self.memory:
                    self.memory.add_task_result(
                        task=user_input[:100],
                        result=str(exc),
                        success=False,
                        importance=0.6,
                    )
                return f"Error while processing request: {exc}"

            content = response.get("content", "")
            logger.info(f"LLM response: {content[:200]}...")

            tool_calls = parse_tool_calls(response)
            if tool_calls:
                self.conversation.add_assistant(
                    content,
                    [{"name": tc.name, "arguments": tc.arguments} for tc in tool_calls],
                )
                logger.info(f"Executing {len(tool_calls)} tool call(s)")
                self._execute_tools(tool_calls)
                previous_non_tool_content = ""
                stall_rounds = 0
                continue

            if self._is_final_answer(content):
                self.conversation.add_assistant(content)
                if self.memory:
                    self.memory.add_conversation("assistant", content[:500], importance=0.5)
                    self.memory.add_task_result(
                        task=user_input[:100],
                        result="Task completed",
                        success=True,
                        importance=0.5,
                    )
                logger.info("Task completed by explicit final marker")
                return content

            self.conversation.add_assistant(content)
            if self.memory:
                self.memory.add_conversation("assistant", content[:500], importance=0.3)

            normalized = (content or "").strip()
            if normalized and normalized == previous_non_tool_content:
                stall_rounds += 1
            elif normalized:
                stall_rounds = 0
                previous_non_tool_content = normalized

            if self._should_auto_finish(round_num, normalized, stall_rounds):
                logger.info("Task completed by auto-finish strategy")
                return content

            if round_num == self.max_rounds:
                return content

        return "Reached max rounds; task may be incomplete."

    def _is_final_answer(self, content: str) -> bool:
        return "final_answer" in (content or "").lower()

    def _should_auto_finish(self, round_num: int, content: str, stall_rounds: int) -> bool:
        if not self.auto_finish:
            return False
        if not content:
            return False
        if "action:" in content.lower():
            return False
        if stall_rounds >= self.max_stall_rounds - 1:
            return True
        if len(self.tool_registry) == 0:
            return True
        return round_num > 1

    def reset(self, new_session: bool = False) -> None:
        """Reset in-memory conversation state."""
        self.conversation.clear()
        self._system_prompt = None
        if new_session and self.memory:
            self.memory.new_session()
            logger.info("Started a new memory session")

    def _think(self) -> Dict[str, Any]:
        messages = [{"role": "system", "content": self._system_prompt}]
        messages.extend(self.conversation.to_list())
        return self.llm.chat(messages)

    def _execute_tools(self, tool_calls) -> None:
        for tc in tool_calls:
            result = self._execute_single_tool(tc.name, tc.arguments)
            self.conversation.add_tool_result(tc.name, str(result))

    def _execute_single_tool(self, name: str, args: dict) -> str:
        logger.info(f"Executing tool: {name}")
        tool = self.tool_registry.get(name)
        if tool is None:
            return f"Tool not found: '{name}'"

        try:
            result = tool.execute(**args)
            logger.debug(f"Tool result: {str(result)[:200]}...")
            return result
        except TypeError as exc:
            logger.error(f"Tool argument error: {exc}")
            return f"Tool argument error: {exc}"
        except Exception as exc:
            logger.error(f"Tool execution error: {type(exc).__name__}: {exc}", exc_info=True)
            return f"Tool execution error: {exc}"

    def _render_system_prompt(self, user_input: str = "") -> str:
        base_prompt = Template(REACT_SYSTEM_PROMPT).substitute(
            operating_system=self._get_os_name(),
            tool_list=self._format_tools(),
            file_list=self._get_files(),
        )

        if self.memory and self.use_memory_context and user_input:
            memory_context = self.memory.get_context(query=user_input, max_items=3, include_recent=2)
            if memory_context:
                base_prompt += f"\n\n## 记忆上下文\n{memory_context}"

        return base_prompt

    def _format_tools(self) -> str:
        tools = self.tool_registry.get_all()
        if not tools:
            return "No tools available."

        lines: List[str] = []
        for tool in tools:
            spec = tool.as_function_spec()
            params = spec.get("parameters", {}).get("properties", {})
            param_str = ", ".join(f"{k}: {v.get('description', '')}" for k, v in params.items()) or "none"
            lines.append(f"- {spec['name']}: {spec['description']}\n  params: {param_str}")
        return "\n".join(lines)

    def _get_files(self) -> str:
        try:
            files = [
                f
                for f in os.listdir(self.project_directory)
                if os.path.isfile(os.path.join(self.project_directory, f))
            ]
            return ", ".join(files[:10]) if files else "No files."
        except Exception:
            return "Unavailable"

    @staticmethod
    def _get_os_name() -> str:
        return {
            "Darwin": "macOS",
            "Windows": "Windows",
            "Linux": "Linux",
        }.get(platform.system(), "Unknown")


Agent = ReactAgent

