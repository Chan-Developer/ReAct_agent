# -*- coding: utf-8 -*-
"""Plan-Execute-Reflect agent tests."""

from agents import PlanExecuteReflectAgent
from tools import Calculator


class MockPERLLM:
    """Simple rule-based mock for PER tests."""

    def chat(self, messages, **kwargs):
        user_text = messages[-1]["content"]

        if "Create a concise execution plan" in user_text:
            return {
                "content": (
                    '{"steps": ['
                    '{"id": "S1", "title": "Compute value", "detail": "calculate 1+1", "done_criteria": "have result"}'
                    "]}"
                )
            }

        if "You are a reflection module." in user_text:
            return {
                "content": (
                    '{"status": "done", "final_answer": "All done from reflection.", '
                    '"feedback": "ok", "next_steps": []}'
                )
            }

        return {"content": "final_answer: 2"}


def test_per_agent_finishes_with_reflection_answer():
    llm = MockPERLLM()
    agent = PlanExecuteReflectAgent(
        llm=llm,
        tools=[Calculator()],
        max_cycles=2,
        max_rounds_per_step=3,
    )

    result = agent.run("calculate 1+1")

    assert result == "All done from reflection."


def test_per_agent_fallback_when_reflection_missing():
    class FallbackLLM(MockPERLLM):
        def chat(self, messages, **kwargs):
            user_text = messages[-1]["content"]
            if "You are a reflection module." in user_text:
                return {"content": "{}"}
            return super().chat(messages, **kwargs)

    llm = FallbackLLM()
    agent = PlanExecuteReflectAgent(llm=llm, tools=[Calculator()], max_cycles=1, max_rounds_per_step=2)

    result = agent.run("calculate 1+1")

    assert "Consolidated result" in result
