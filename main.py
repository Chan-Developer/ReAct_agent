#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unified CLI entry for the agent framework."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from typing import Callable, List, Tuple

from common import get_logger, set_level, setup_logging
from agents import PlanExecuteReflectAgent, ReactAgent
from llm import ModelScopeOpenAI, VllmLLM
from tools import AddFile, Calculator, ReadFile, Search
from tools.agent_wrappers import ContentOptimizerTool, LayoutDesignerTool, StyleSelectorTool
from tools.generators import ResumeGenerator

setup_logging()
logger = get_logger(__name__)


def create_llm(local: bool = False):
    """Create LLM instance."""
    if local:
        logger.info("Using local vLLM")
        return VllmLLM()
    logger.info("Using ModelScope API")
    try:
        return ModelScopeOpenAI()
    except ValueError as exc:
        logger.error(f"Failed to initialize LLM: {exc}")
        sys.exit(1)


def create_default_tools(output_dir: str = "./output", llm=None) -> list:
    """Create default tools."""
    return [Calculator(), Search(), AddFile(), ReadFile()]


def create_resume_tools(output_dir: str = "./output", llm=None) -> list:
    """Create resume-specific tools."""
    return [
        ContentOptimizerTool(llm),
        StyleSelectorTool(llm),
        LayoutDesignerTool(llm),
        ResumeGenerator(output_dir=output_dir, llm=None, auto_optimize=False),
    ]


def _load_resume_payload(resume_arg: str) -> dict:
    """Load resume payload from @file or inline JSON."""
    if resume_arg.startswith("@"):
        with open(resume_arg[1:], "r", encoding="utf-8") as f:
            return json.load(f)
    try:
        return json.loads(resume_arg)
    except json.JSONDecodeError:
        raise ValueError("resume must be @file path or valid JSON string")


def _read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _prepare_prompt_and_tools(args, llm) -> Tuple[List[object], str]:
    """Prepare tools and final prompt for solo/per modes."""
    os.makedirs(args.output_dir, exist_ok=True)

    if not getattr(args, "resume", None):
        tools = create_default_tools(args.output_dir, llm=llm)
        return tools, args.prompt

    tools = create_resume_tools(args.output_dir, llm=llm)

    resume_data = _load_resume_payload(args.resume)
    temp_dir = tempfile.gettempdir()
    with open(os.path.join(temp_dir, "original_resume.json"), "w", encoding="utf-8") as f:
        json.dump(resume_data, f, ensure_ascii=False, indent=2)

    job_description = ""
    if getattr(args, "jd", None):
        try:
            job_description = _read_text_file(args.jd)
            with open(os.path.join(temp_dir, "job_description.txt"), "w", encoding="utf-8") as f:
                f.write(job_description)
        except FileNotFoundError:
            logger.warning(f"job description file not found: {args.jd}")

    prompt_parts = [args.prompt]
    prompt_parts.append(
        '\nResume data has been cached. Use resume_json="@original" for tool calls when needed.'
    )
    if job_description:
        prompt_parts.append(
            "\nJob description is available. Pass job_description to content/style tools when needed."
        )
    if getattr(args, "template", None):
        prompt_parts.append(f"\nPreferred template: {args.template}")
    if getattr(args, "page", "auto") != "auto":
        prompt_parts.append(f"\nPage preference: {args.page}")

    return tools, "".join(prompt_parts)


def _run_single_agent_mode(
    args,
    mode_name: str,
    builder: Callable[[object, list], object],
) -> None:
    print("\n" + "=" * 60)
    print(mode_name)
    print("=" * 60)

    llm = create_llm(args.local)
    try:
        tools, prompt = _prepare_prompt_and_tools(args, llm)
    except FileNotFoundError as exc:
        print(f"Error: file not found: {exc}")
        return
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"Error: invalid input: {exc}")
        return

    print(f"Loaded tools: {[t.name for t in tools]}")
    logger.info(f"User input: {prompt[:120]}...")

    agent = builder(llm, tools)
    try:
        reply = agent.run(prompt)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        return
    except Exception as exc:
        logger.error(f"Execution error: {exc}", exc_info=getattr(args, "debug", False))
        print(f"Error: {exc}")
        return

    print("\n" + "=" * 60)
    print("Assistant:", reply)
    print("=" * 60)


def run_solo_mode(args) -> None:
    """Run solo ReAct mode."""

    def build(llm, tools):
        return ReactAgent(llm=llm, tools=tools, max_rounds=args.max_steps)

    _run_single_agent_mode(args, "Solo Mode", build)


def run_per_mode(args) -> None:
    """Run Plan-Execute-Reflect mode."""

    def build(llm, tools):
        return PlanExecuteReflectAgent(
            llm=llm,
            tools=tools,
            max_cycles=args.max_cycles,
            max_rounds_per_step=args.max_steps,
        )

    _run_single_agent_mode(args, "Plan-Execute-Reflect Mode", build)


def run_workflow_mode(args) -> None:
    """Run fixed workflow mode."""
    print("\n" + "=" * 60)
    print("Workflow Mode")
    print("=" * 60)

    try:
        if args.input.startswith("@"):
            with open(args.input[1:], "r", encoding="utf-8") as f:
                input_data = json.load(f)
        else:
            input_data = json.loads(args.input)
    except (json.JSONDecodeError, FileNotFoundError) as exc:
        print(f"Error: invalid workflow input: {exc}")
        return

    job_description = ""
    if getattr(args, "jd", None):
        try:
            job_description = _read_text_file(args.jd)
            print(f"Job description chars: {len(job_description)}")
        except FileNotFoundError:
            print(f"Warning: job description file not found: {args.jd}")

    llm = create_llm(args.local)

    if args.workflow_name != "resume":
        print(f"Unknown workflow: {args.workflow_name}")
        print("Available workflow: resume")
        return

    from workflows import ResumePipeline

    pipeline = ResumePipeline(llm=llm, output_dir=args.output_dir)
    print(f"Workflow: {pipeline.WORKFLOW_NAME}")
    print(f"Steps: {' -> '.join(pipeline.WORKFLOW_STEPS)}")

    result = pipeline.run(
        input_data=input_data,
        job_description=job_description,
        template_name=getattr(args, "template", ""),
        page_preference=getattr(args, "page", "auto"),
        output_dir=args.output_dir,
    )

    if result.success:
        print("Workflow completed")
        print(f"Time: {result.execution_time:.2f}s")
        print(f"Progress: {result.steps_completed}/{result.total_steps}")
        if result.output.get("output_path"):
            print(f"Output: {result.output['output_path']}")
    else:
        print(f"Workflow failed: {result.error}")
        print(f"Progress: {result.steps_completed}/{result.total_steps}")


def run_multi_mode(args) -> None:
    """Placeholder for future multi-agent orchestrator."""
    print("\n" + "=" * 60)
    print("Multi Mode (TODO)")
    print("=" * 60)
    print("This mode is not implemented yet.")
    print("Please use one of:")
    print("  - solo")
    print("  - per")
    print("  - workflow")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Agent Framework CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="mode", help="Run mode")

    solo = subparsers.add_parser("solo", help="Single agent ReAct mode")
    solo.add_argument("-p", "--prompt", required=True, help="Task prompt")
    solo.add_argument("-r", "--resume", help="Resume JSON or @file path")
    solo.add_argument("--jd", help="Job description file path")
    solo.add_argument("-t", "--template", help="Template name")
    solo.add_argument("--page", choices=["one_page", "two_pages", "auto"], default="auto")
    solo.add_argument("-m", "--max_steps", type=int, default=10, help="Max ReAct rounds")
    solo.add_argument("-o", "--output_dir", default="./output", help="Output directory")
    solo.add_argument("--local", action="store_true", help="Use local vLLM")
    solo.add_argument("-d", "--debug", action="store_true", help="Debug mode")

    per = subparsers.add_parser("per", help="Plan-Execute-Reflect mode")
    per.add_argument("-p", "--prompt", required=True, help="Task prompt")
    per.add_argument("-r", "--resume", help="Resume JSON or @file path")
    per.add_argument("--jd", help="Job description file path")
    per.add_argument("-t", "--template", help="Template name")
    per.add_argument("--page", choices=["one_page", "two_pages", "auto"], default="auto")
    per.add_argument("-m", "--max_steps", type=int, default=8, help="Max ReAct rounds per step")
    per.add_argument("--max_cycles", type=int, default=2, help="Max plan/reflect cycles")
    per.add_argument("-o", "--output_dir", default="./output", help="Output directory")
    per.add_argument("--local", action="store_true", help="Use local vLLM")
    per.add_argument("-d", "--debug", action="store_true", help="Debug mode")

    workflow = subparsers.add_parser("workflow", help="Fixed workflow mode")
    workflow.add_argument("-n", "--workflow_name", required=True, help="Workflow name")
    workflow.add_argument("-i", "--input", required=True, help="Input JSON or @file path")
    workflow.add_argument("--jd", help="Job description file path")
    workflow.add_argument("-t", "--template", help="Template name")
    workflow.add_argument("--page", choices=["one_page", "two_pages", "auto"], default="auto")
    workflow.add_argument("-o", "--output_dir", default="./output", help="Output directory")
    workflow.add_argument("--local", action="store_true", help="Use local vLLM")
    workflow.add_argument("-d", "--debug", action="store_true", help="Debug mode")

    multi = subparsers.add_parser("multi", help="Multi-agent mode (TODO)")
    multi.add_argument("-i", "--input", help="Input JSON or @file path")
    multi.add_argument("-d", "--debug", action="store_true", help="Debug mode")

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.mode is None:
        print("Agent Framework CLI")
        print("Available modes: solo, per, workflow, multi")
        print('Example: python main.py solo -p "compute 1+1"')
        return

    if getattr(args, "debug", False):
        set_level("DEBUG")

    if args.mode == "solo":
        run_solo_mode(args)
    elif args.mode == "per":
        run_per_mode(args)
    elif args.mode == "workflow":
        run_workflow_mode(args)
    elif args.mode == "multi":
        run_multi_mode(args)


if __name__ == "__main__":
    main()

