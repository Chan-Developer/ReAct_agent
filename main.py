#!/usr/bin/env python
"""简单 CLI，用于演示 agent 思考与工具调用流程。

运行：
    python -m agent.main
或
    python agent/main.py
"""
from __future__ import annotations

import argparse

from core.agent import Agent
from core.tools.builtin import Calculator, Search, FileOperations
from llm_interface import VllmLLM


def build_agent(max_steps: int) -> Agent:
    tools = [Calculator(), Search(), FileOperations()]
    llm = VllmLLM()
    return Agent(tools, llm, max_steps)


def main() -> None:
    parser = argparse.ArgumentParser(description="Simple ReAct agent demo")
    parser.add_argument("--max_steps", help="Max steps for the agent",default=3,type=int)
    parser.add_argument("--prompt", help="User prompt for the agent",default="Hello, how are you?",type=str)
    args = parser.parse_args()

    agent = build_agent(args.max_steps)
    reply = agent.run(args.prompt)
    print("\nAssistant:", reply)


if __name__ == "__main__":
    main()
