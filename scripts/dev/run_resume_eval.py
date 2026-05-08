#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Run Resume Copilot's benchmark set."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from resume_copilot.quality import ResumeBenchmarkRunner, score_resume_against_jd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run resume product benchmarks")
    parser.add_argument(
        "--dataset",
        default="storage/benchmarks/resume_eval_set.json",
        help="Benchmark dataset path",
    )
    parser.add_argument(
        "--resume",
        help="Optional resume JSON file to score directly",
    )
    parser.add_argument(
        "--jd",
        help="Optional job description text file to score directly",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.resume and args.jd:
        resume_data = json.loads(Path(args.resume).read_text(encoding="utf-8"))
        job_description = Path(args.jd).read_text(encoding="utf-8")
        result = score_resume_against_jd(resume_data, job_description)
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return

    runner = ResumeBenchmarkRunner()
    summary = runner.run(args.dataset)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
