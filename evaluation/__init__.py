# -*- coding: utf-8 -*-
"""Compatibility wrapper for product-quality evaluation utilities."""

from resume_copilot.quality import (
    BenchmarkCase,
    BenchmarkResult,
    ResumeBenchmarkRunner,
    ResumeMetricResult,
    score_resume_against_jd,
)

__all__ = [
    "BenchmarkCase",
    "BenchmarkResult",
    "ResumeBenchmarkRunner",
    "ResumeMetricResult",
    "score_resume_against_jd",
]
