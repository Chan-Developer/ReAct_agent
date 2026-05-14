# -*- coding: utf-8 -*-
"""Tests for structured product reports and canonical resume schema."""

from __future__ import annotations

from resume_copilot.application import ResumeProductService, ResumeWorkbenchService
from resume_copilot.application.reporting import build_resume_workbench_payload
from resume_copilot.domain import normalize_resume_data


def test_normalize_resume_data_converts_legacy_experiences_key():
    normalized = normalize_resume_data(
        {
            "name": "Taylor",
            "experiences": [{"company": "Example", "position": "Intern"}],
            "skills": [{"name": "Python"}],
        }
    )

    assert "experiences" not in normalized
    assert normalized["experience"][0]["company"] == "Example"
    assert normalized["skills"][0]["name"] == "Python"


def test_evaluate_resume_returns_structured_report():
    service = ResumeProductService()
    report = service.evaluate_resume(
        resume_data={
            "name": "Alex Chen",
            "email": "alex@example.com",
            "summary": "Backend engineer with Python and AWS experience.",
            "experiences": [
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
        },
        job_description=(
            "Hiring a backend engineer with Python, API design, reliability, AWS, and "
            "stakeholder communication skills."
        ),
        role="Backend Engineer",
        market="us",
    )

    payload = report.to_dict()

    assert payload["type"] == "resume_diagnosis_report"
    assert payload["role"] == "Backend Engineer"
    assert payload["market"] == "us"
    assert "jd_analysis" in payload
    assert "metrics" in payload
    assert isinstance(payload["diagnosis"], list)
    assert isinstance(payload["recommendations"], list)
    assert payload["metrics"]["jd_match_score"] >= 0
    assert isinstance(payload["jd_analysis"]["keywords"], list)


def test_resume_workbench_payload_contains_interaction_blocks():
    payload = build_resume_workbench_payload(
        resume_text="Built Python services.\nImproved reliability.\nWorked with stakeholders.",
        job_description="Need a backend engineer with Python, reliability, APIs, and mentoring.",
        role="Backend Engineer",
        market="us",
        tone="technical",
    )

    assert payload["type"] == "resume_workbench_payload"
    assert payload["report"]["type"] == "resume_diagnosis_report"
    assert isinstance(payload["focus_areas"], list)
    assert isinstance(payload["rewrite_candidates"], list)
    assert isinstance(payload["command_log"], list)
    assert isinstance(payload["next_actions"], list)
    assert isinstance(payload["generation_plan"], dict)
    assert payload["generation_plan"]["template_hint"]
    assert payload["generation_plan"]["filename_stem"]


def test_resume_workbench_service_wraps_builder():
    payload = ResumeWorkbenchService().build_payload(
        resume_text="Built Python services and improved reliability.",
        job_description="Need a backend engineer with Python and API experience.",
        role="Backend Engineer",
        market="us",
        tone="precise",
    )

    assert payload["type"] == "resume_workbench_payload"
    assert payload["role"] == "Backend Engineer"
