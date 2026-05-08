# -*- coding: utf-8 -*-
"""Dataset-based benchmark runner for resume product quality."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .metrics import ResumeMetricResult, score_resume_against_jd


@dataclass
class BenchmarkCase:
    case_id: str
    market: str
    target_role: str
    resume_data: dict[str, Any]
    job_description: str
    target_thresholds: dict[str, float]


@dataclass
class BenchmarkResult:
    case_id: str
    market: str
    target_role: str
    metrics: ResumeMetricResult
    passed: bool
    failed_thresholds: dict[str, dict[str, float]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "market": self.market,
            "target_role": self.target_role,
            "passed": self.passed,
            "failed_thresholds": self.failed_thresholds,
            "metrics": self.metrics.to_dict(),
        }


class ResumeBenchmarkRunner:
    """Run product benchmarks over a fixed resume evaluation set."""

    def load_cases(self, path: str | Path) -> list[BenchmarkCase]:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        cases: list[BenchmarkCase] = []
        for row in payload.get("cases", []):
            cases.append(
                BenchmarkCase(
                    case_id=row["case_id"],
                    market=row["market"],
                    target_role=row["target_role"],
                    resume_data=row["resume_data"],
                    job_description=row["job_description"],
                    target_thresholds=row.get("target_thresholds", {}),
                )
            )
        return cases

    def evaluate_case(self, case: BenchmarkCase) -> BenchmarkResult:
        metrics = score_resume_against_jd(case.resume_data, case.job_description)
        failed: dict[str, dict[str, float]] = {}

        for metric_name, expected in case.target_thresholds.items():
            actual = getattr(metrics, metric_name)
            if actual < expected:
                failed[metric_name] = {"expected": expected, "actual": round(actual, 2)}

        return BenchmarkResult(
            case_id=case.case_id,
            market=case.market,
            target_role=case.target_role,
            metrics=metrics,
            passed=not failed,
            failed_thresholds=failed,
        )

    def run(self, path: str | Path) -> dict[str, Any]:
        cases = self.load_cases(path)
        results = [self.evaluate_case(case) for case in cases]
        passed = sum(1 for result in results if result.passed)
        avg_overall = (
            sum(result.metrics.overall_score for result in results) / len(results)
            if results
            else 0.0
        )
        return {
            "case_count": len(results),
            "passed": passed,
            "failed": len(results) - passed,
            "average_overall_score": round(avg_overall, 2),
            "results": [result.to_dict() for result in results],
        }
