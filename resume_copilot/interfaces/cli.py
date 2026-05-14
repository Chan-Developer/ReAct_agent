# -*- coding: utf-8 -*-
"""Product CLI for Resume Copilot."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from common import get_logger, set_level, setup_logging
from resume_copilot.application.resume_product_service import ResumeProductService
from resume_copilot.application.resume_workbench_service import ResumeWorkbenchService

setup_logging()
logger = get_logger(__name__)


def create_llm(local: bool = False):
    from llm import ModelScopeOpenAI, VllmLLM

    if local:
        logger.info("Using local vLLM")
        return VllmLLM()
    logger.info("Using ModelScope API")
    try:
        return ModelScopeOpenAI()
    except ValueError as exc:
        logger.error(f"Failed to initialize LLM: {exc}")
        sys.exit(1)


def _load_resume_payload(resume_arg: str) -> dict:
    if resume_arg.startswith("@"):
        return json.loads(Path(resume_arg[1:]).read_text(encoding="utf-8"))
    try:
        return json.loads(resume_arg)
    except json.JSONDecodeError:
        raise ValueError("resume must be @file path or valid JSON string")


def _read_text_file(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def run_resume_mode(args) -> None:
    print("\n" + "=" * 60)
    print("Resume Copilot")
    print("=" * 60)

    try:
        resume_data = _load_resume_payload(args.resume)
    except (json.JSONDecodeError, FileNotFoundError, ValueError) as exc:
        print(f"Error: invalid resume input: {exc}")
        return

    job_description = ""
    if args.jd:
        try:
            job_description = _read_text_file(args.jd)
            print(f"Job description chars: {len(job_description)}")
        except FileNotFoundError:
            print(f"Warning: job description file not found: {args.jd}")

    output_dir = args.output_dir or "./storage/exports"
    os.makedirs(output_dir, exist_ok=True)
    service = ResumeProductService(llm=create_llm(args.local), output_dir=output_dir)
    result = service.generate_resume(
        resume_data=resume_data,
        job_description=job_description,
        template_name=args.template or "",
        page_preference=args.page,
    )

    if result.success:
        print("Resume generation completed")
        print(f"Time: {result.execution_time:.2f}s")
        print(f"Progress: {result.steps_completed}/{result.total_steps}")
        if result.output.get("output_path"):
            print(f"Output: {result.output['output_path']}")
        if result.suggestions:
            print("Highlights:")
            for suggestion in result.suggestions[:5]:
                print(f"  - {suggestion}")
    else:
        print(f"Resume generation failed: {result.error}")
        print(f"Progress: {result.steps_completed}/{result.total_steps}")


def run_evaluate_mode(args) -> None:
    print("\n" + "=" * 60)
    print("Resume Copilot Evaluation")
    print("=" * 60)

    service = ResumeProductService(output_dir=args.output_dir or "./storage/exports")

    if args.resume and args.jd:
        try:
            resume_data = _load_resume_payload(args.resume)
            job_description = _read_text_file(args.jd)
        except (json.JSONDecodeError, FileNotFoundError, ValueError) as exc:
            print(f"Error: invalid evaluation input: {exc}")
            return

        result = service.evaluate_resume(resume_data, job_description)
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return

    summary = service.run_benchmark(args.dataset)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def run_workbench_mode(args) -> None:
    print("\n" + "=" * 60)
    print("Resume Copilot Workbench")
    print("=" * 60)

    try:
        resume_text = _read_text_file(args.resume_text) if args.resume_text else ""
        job_description = _read_text_file(args.jd)
    except FileNotFoundError as exc:
        print(f"Error: invalid workbench input: {exc}")
        return

    payload = ResumeWorkbenchService().build_payload(
        resume_text=resume_text,
        job_description=job_description,
        role=args.role or "Target Role",
        market=args.market or "global",
        tone=args.tone or "precise",
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Resume Copilot CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="mode", help="Product command")

    resume = subparsers.add_parser("resume", help="Optimize and generate a resume")
    resume.add_argument("-r", "--resume", required=True, help="Resume JSON or @file path")
    resume.add_argument("--jd", help="Job description file path")
    resume.add_argument("-t", "--template", help="Template name")
    resume.add_argument("--page", choices=["one_page", "two_pages", "auto"], default="auto")
    resume.add_argument("-o", "--output_dir", default="./storage/exports", help="Output directory")
    resume.add_argument("--local", action="store_true", help="Use local vLLM")
    resume.add_argument("-d", "--debug", action="store_true", help="Debug mode")

    evaluate = subparsers.add_parser("evaluate", help="Run resume product benchmarks")
    evaluate.add_argument(
        "--dataset",
        default="storage/benchmarks/resume_eval_set.json",
        help="Benchmark dataset path",
    )
    evaluate.add_argument("-r", "--resume", help="Resume JSON or @file path")
    evaluate.add_argument("--jd", help="Job description file path")
    evaluate.add_argument("-o", "--output_dir", default="./storage/exports", help="Output directory")
    evaluate.add_argument("-d", "--debug", action="store_true", help="Debug mode")

    workbench = subparsers.add_parser("workbench", help="Run the resume workbench payload builder")
    workbench.add_argument("--resume-text", help="Plain-text resume snapshot file path")
    workbench.add_argument("--jd", required=True, help="Job description file path")
    workbench.add_argument("--role", default="Target Role", help="Target role name")
    workbench.add_argument("--market", default="global", help="Target market")
    workbench.add_argument(
        "--tone",
        choices=["precise", "confident", "technical"],
        default="precise",
        help="Voice preference",
    )
    workbench.add_argument("-d", "--debug", action="store_true", help="Debug mode")

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.mode is None:
        print("Resume Copilot")
        print("Primary commands: resume, evaluate, workbench")
        print(
            'Example: python main.py resume -r @data/sample_resume.json --jd data/sample_job.txt'
        )
        return

    if getattr(args, "debug", False):
        set_level("DEBUG")

    if args.mode == "resume":
        run_resume_mode(args)
    elif args.mode == "evaluate":
        run_evaluate_mode(args)
    elif args.mode == "workbench":
        run_workbench_mode(args)
