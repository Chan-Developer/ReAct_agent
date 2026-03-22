# -*- coding: utf-8 -*-
"""Plan-Execute-Reflect agent implementation."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Protocol

from common import get_logger
from .react_agent import ReactAgent

if TYPE_CHECKING:
    from tools import ToolRegistry
    from tools.base import BaseTool
    from memory import MemoryManager

logger = get_logger(__name__)

__all__ = ["PlanExecuteReflectAgent", "PERAgent"]


class LLMProtocol(Protocol):
    """Protocol for chat-based LLM clients."""

    def chat(self, messages: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        ...


@dataclass
class PlanStep:
    """A single executable step in a plan."""

    id: str
    title: str
    detail: str = ""
    done_criteria: str = ""
    status: str = "pending"
    result: str = ""


@dataclass
class ReflectionResult:
    """Result parsed from reflection stage."""

    status: str = "continue"
    final_answer: str = ""
    feedback: str = ""
    next_steps: List[str] = field(default_factory=list)


class PlanExecuteReflectAgent:
    """A controller agent that plans, executes with ReAct, then reflects."""

    def __init__(
        self,
        llm: LLMProtocol,
        tools: Optional[List["BaseTool"]] = None,
        tool_registry: Optional["ToolRegistry"] = None,
        memory: Optional["MemoryManager"] = None,
        max_cycles: int = 2,
        max_plan_steps: int = 6,
        max_rounds_per_step: int = 5,
        project_directory: str = ".",
        use_memory_context: bool = True,
        carry_step_conversation: bool = False,
    ):
        self.llm = llm
        self.max_cycles = max(1, max_cycles)
        self.max_plan_steps = max(1, max_plan_steps)
        self.carry_step_conversation = carry_step_conversation

        self.executor = ReactAgent(
            llm=llm,
            tools=tools,
            tool_registry=tool_registry,
            memory=memory,
            max_rounds=max_rounds_per_step,
            project_directory=project_directory,
            use_memory_context=use_memory_context,
        )

    def run(self, user_input: str) -> str:
        logger.info("[PER] start task")
        steps = self._build_plan(user_input)
        if not steps:
            steps = [PlanStep(id="S1", title="Solve user request", detail=user_input)]

        for cycle in range(1, self.max_cycles + 1):
            pending = [s for s in steps if s.status != "done"]
            if not pending:
                break

            logger.info(f"[PER] cycle {cycle}/{self.max_cycles}, pending={len(pending)}")
            for step in pending:
                self._execute_step(user_input, steps, step)

            reflection = self._reflect(user_input, steps)
            if reflection.status == "done":
                if reflection.final_answer.strip():
                    return reflection.final_answer.strip()
                break

            self._merge_follow_up_steps(steps, reflection.next_steps)

        return self._fallback_answer(user_input, steps)

    def reset(self, new_session: bool = False) -> None:
        """Reset internal execution state."""
        self.executor.reset(new_session=new_session)

    def _build_plan(self, user_input: str) -> List[PlanStep]:
        prompt = (
            "You are a planning module. Create a concise execution plan.\n"
            "Return STRICT JSON only:\n"
            "{\n"
            '  "steps": [\n'
            '    {"id": "S1", "title": "short title", "detail": "what to do", "done_criteria": "done signal"}\n'
            "  ]\n"
            "}\n"
            f"Task:\n{user_input}"
        )
        data = self._ask_json(prompt)
        raw_steps = data.get("steps", []) if isinstance(data, dict) else []

        steps: List[PlanStep] = []
        for idx, item in enumerate(raw_steps[: self.max_plan_steps], start=1):
            if not isinstance(item, dict):
                continue
            title = str(item.get("title", "")).strip()
            if not title:
                continue
            step_id = str(item.get("id", f"S{idx}")).strip() or f"S{idx}"
            steps.append(
                PlanStep(
                    id=step_id,
                    title=title,
                    detail=str(item.get("detail", "")).strip(),
                    done_criteria=str(item.get("done_criteria", "")).strip(),
                )
            )

        return steps

    def _execute_step(self, user_input: str, steps: List[PlanStep], step: PlanStep) -> None:
        if not self.carry_step_conversation:
            self.executor.reset(new_session=False)

        step_prompt = self._build_step_prompt(user_input, steps, step)
        try:
            result = self.executor.run(step_prompt)
            step.result = (result or "").strip()
            step.status = "done"
        except Exception as exc:
            logger.warning(f"[PER] step failed {step.id}: {exc}")
            step.result = f"Step execution failed: {exc}"
            step.status = "done"

    def _build_step_prompt(self, user_input: str, steps: List[PlanStep], step: PlanStep) -> str:
        finished = [
            f"{s.id} {s.title}: {self._truncate(s.result, 300)}"
            for s in steps
            if s.status == "done" and s.result
        ]
        finished_text = "\n".join(finished) if finished else "None"

        return (
            "You are executing one step in a plan.\n"
            "Complete this step and produce useful output for downstream steps.\n"
            f"Original task:\n{user_input}\n\n"
            f"Current step [{step.id}] {step.title}\n"
            f"Step detail: {step.detail or 'N/A'}\n"
            f"Done criteria: {step.done_criteria or 'N/A'}\n\n"
            f"Completed context:\n{finished_text}\n"
        )

    def _reflect(self, user_input: str, steps: List[PlanStep]) -> ReflectionResult:
        steps_text = "\n".join(
            [
                f"- {s.id} | {s.title} | status={s.status}\n  result={self._truncate(s.result, 500)}"
                for s in steps
            ]
        )
        prompt = (
            "You are a reflection module.\n"
            "Decide whether task is done or needs more steps.\n"
            "Return STRICT JSON only:\n"
            "{\n"
            '  "status": "done|continue",\n'
            '  "final_answer": "answer for user when done",\n'
            '  "feedback": "short reflection",\n'
            '  "next_steps": ["optional extra step title"]\n'
            "}\n"
            f"Original task:\n{user_input}\n\n"
            f"Execution summary:\n{steps_text}"
        )
        data = self._ask_json(prompt)
        if not isinstance(data, dict):
            return ReflectionResult(status="continue")

        status = str(data.get("status", "continue")).strip().lower()
        if status not in {"done", "continue"}:
            status = "continue"

        next_steps = data.get("next_steps", [])
        if not isinstance(next_steps, list):
            next_steps = []

        return ReflectionResult(
            status=status,
            final_answer=str(data.get("final_answer", "")).strip(),
            feedback=str(data.get("feedback", "")).strip(),
            next_steps=[str(s).strip() for s in next_steps if str(s).strip()],
        )

    def _merge_follow_up_steps(self, steps: List[PlanStep], next_steps: List[str]) -> None:
        if not next_steps:
            return

        existing_titles = {s.title.strip().lower() for s in steps}
        next_index = len(steps) + 1
        for title in next_steps:
            normalized = title.strip().lower()
            if not normalized or normalized in existing_titles:
                continue
            if len(steps) >= self.max_plan_steps:
                break
            steps.append(PlanStep(id=f"S{next_index}", title=title))
            existing_titles.add(normalized)
            next_index += 1

    def _fallback_answer(self, user_input: str, steps: List[PlanStep]) -> str:
        completed = "\n".join(
            [f"- {s.id} {s.title}: {self._truncate(s.result, 400)}" for s in steps if s.result]
        )
        if not completed:
            return f"Unable to complete task: {user_input}"
        return (
            "Task processed with Plan-Execute-Reflect. Consolidated result:\n"
            f"{completed}"
        )

    def _ask_json(self, user_prompt: str) -> Dict[str, Any]:
        messages = [
            {"role": "system", "content": "Return valid JSON only. No markdown, no extra text."},
            {"role": "user", "content": user_prompt},
        ]
        response = self.llm.chat(messages)
        text = response.get("content", "") if isinstance(response, dict) else str(response)
        return self._parse_json_text(text)

    def _parse_json_text(self, text: str) -> Dict[str, Any]:
        text = (text or "").strip()
        if not text:
            return {}

        try:
            data = json.loads(text)
            return data if isinstance(data, dict) else {}
        except json.JSONDecodeError:
            pass

        fenced = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
        if fenced:
            try:
                data = json.loads(fenced.group(1))
                return data if isinstance(data, dict) else {}
            except json.JSONDecodeError:
                pass

        extracted = self._extract_json_object(text)
        if extracted:
            try:
                data = json.loads(extracted)
                return data if isinstance(data, dict) else {}
            except json.JSONDecodeError:
                return {}
        return {}

    @staticmethod
    def _extract_json_object(text: str) -> Optional[str]:
        start = text.find("{")
        if start < 0:
            return None

        depth = 0
        in_str = False
        escape = False
        for idx, char in enumerate(text[start:], start=start):
            if escape:
                escape = False
                continue
            if char == "\\":
                escape = True
                continue
            if char == '"':
                in_str = not in_str
                continue
            if in_str:
                continue
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return text[start : idx + 1]
        return None

    @staticmethod
    def _truncate(text: str, limit: int) -> str:
        text = (text or "").strip()
        if len(text) <= limit:
            return text
        return text[: max(0, limit - 3)] + "..."


PERAgent = PlanExecuteReflectAgent

