# -*- coding: utf-8 -*-
"""CLI coverage for the resume workbench mode."""

from __future__ import annotations

import sys

from resume_copilot.interfaces.cli import parse_args


def test_cli_workbench_mode_parses_expected_arguments():
    original_argv = sys.argv[:]
    try:
        sys.argv = [
            "main.py",
            "workbench",
            "--jd",
            "job.txt",
            "--role",
            "Backend Engineer",
            "--market",
            "us",
            "--tone",
            "technical",
        ]
        args = parse_args()
    finally:
        sys.argv = original_argv

    assert args.mode == "workbench"
    assert args.jd == "job.txt"
    assert args.role == "Backend Engineer"
    assert args.market == "us"
    assert args.tone == "technical"
