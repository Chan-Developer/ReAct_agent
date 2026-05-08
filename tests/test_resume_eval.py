# -*- coding: utf-8 -*-
"""Tests for resume product evaluation utilities."""

from __future__ import annotations

from pathlib import Path


def test_score_resume_against_jd_returns_all_metrics():
    from evaluation import score_resume_against_jd

    resume_data = {
        "name": "Alex Chen",
        "email": "alex@example.com",
        "summary": "Backend engineer with Python and AWS experience.",
        "experience": [
            {
                "company": "DataLoop",
                "position": "Backend Engineer",
                "description": "Built API services.",
                "highlights": [
                    "Built Python APIs for analytics workflows",
                    "Reduced release rollback incidents by 35%",
                ],
            }
        ],
        "skills": ["Python", "AWS", "Redis"],
    }
    job_description = (
        "Hiring a backend engineer with Python, API design, reliability, AWS, and"
        " stakeholder communication skills."
    )

    result = score_resume_against_jd(resume_data, job_description)

    assert 0 <= result.jd_match_score <= 100
    assert 0 <= result.quantified_evidence_score <= 100
    assert 0 <= result.readability_score <= 100
    assert 0 <= result.ats_safety_score <= 100
    assert 0 <= result.overall_score <= 100
    assert isinstance(result.matched_keywords, list)
    assert isinstance(result.missing_keywords, list)


def test_benchmark_runner_loads_dataset_and_returns_summary():
    from evaluation import ResumeBenchmarkRunner

    dataset = Path(__file__).resolve().parents[1] / "storage" / "benchmarks" / "resume_eval_set.json"
    runner = ResumeBenchmarkRunner()

    summary = runner.run(dataset)

    assert summary["case_count"] >= 3
    assert "average_overall_score" in summary
    assert len(summary["results"]) == summary["case_count"]


def test_cli_evaluate_help_stays_available():
    from core.cli import parse_args
    import sys

    original_argv = sys.argv[:]
    try:
        sys.argv = ["main.py", "evaluate", "--dataset", "storage/benchmarks/resume_eval_set.json"]
        args = parse_args()
    finally:
        sys.argv = original_argv

    assert args.mode == "evaluate"
    assert args.dataset.endswith("resume_eval_set.json")
