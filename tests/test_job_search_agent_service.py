# -*- coding: utf-8 -*-
"""Tests for the personal job-search agent application skeleton."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from resume_copilot.application import PersonalJobSearchService


def test_dashboard_snapshot_contains_workspace_structure(tmp_path: Path):
    workspace_path = tmp_path / "agent_workspace.json"
    service = PersonalJobSearchService(workspace_path=str(workspace_path))
    snapshot = service.get_dashboard_snapshot()

    assert snapshot["profile"]["full_name"] == "Primary Candidate"
    assert snapshot["modules"]
    assert snapshot["targets"]
    assert snapshot["opportunities"]
    assert snapshot["applications"]
    assert snapshot["interviews"]
    assert snapshot["memory_notes"]
    assert snapshot["journeys"]
    assert snapshot["opportunities"][0]["score_report"]["type"] == "opportunity_score_report"


def test_dashboard_snapshot_includes_resume_agent(tmp_path: Path):
    workspace_path = tmp_path / "agent_workspace.json"
    service = PersonalJobSearchService(workspace_path=str(workspace_path))
    snapshot = service.get_dashboard_snapshot()

    module_names = [item["name"] for item in snapshot["modules"]]
    assert "Resume Agent" in module_names
    assert "Opportunity Agent" in module_names
    assert "Application Agent" in module_names


def test_workspace_updates_persist(tmp_path: Path):
    workspace_path = tmp_path / "agent_workspace.json"
    service = PersonalJobSearchService(workspace_path=str(workspace_path))

    snapshot = service.update_profile(
        {
            "full_name": "Jane Candidate",
            "target_title": "Platform Engineer",
            "target_markets": "US, Remote",
            "strengths": "Python, reliability, mentorship",
        }
    )

    assert snapshot["profile"]["full_name"] == "Jane Candidate"
    assert workspace_path.exists()

    service.add_target(
        {
            "title": "Staff Platform Engineer",
            "market": "US",
            "seniority": "Staff",
            "priorities": "scale, architecture",
        }
    )
    service.add_resume_version(
        {
            "label": "US platform v1",
            "status": "Ready",
            "focus": "Platform systems",
            "market": "US",
        }
    )
    service.import_opportunity(
        {
            "company": "Orbit Works",
            "title": "Staff Platform Engineer",
            "market": "US",
            "location": "Remote / US",
            "source": "LinkedIn import",
            "description": "Platform role focused on Python, architecture, reliability, and ownership.",
        }
    )
    service.apply_from_opportunity({"company": "Orbit Works", "title": "Staff Platform Engineer"})
    final_snapshot = service.add_application(
        {
            "company": "Northstar",
            "role": "Staff Platform Engineer",
            "stage": "Submitted",
            "next_step": "Prepare system design stories",
        }
    )

    assert final_snapshot["targets"][0]["title"] == "Staff Platform Engineer"
    assert final_snapshot["resume_versions"][0]["label"] == "US platform v1"
    assert final_snapshot["applications"][0]["company"] == "Northstar"
    assert final_snapshot["applications"][1]["company"] == "Orbit Works"
    assert final_snapshot["applications"][1]["resume_label"] == "US platform v1"
    assert final_snapshot["opportunities"][0]["company"] == "Orbit Works"
    assert final_snapshot["opportunities"][0]["status"] == "tracked"
    assert final_snapshot["opportunities"][0]["score_report"]["status"] == "tracked"


def test_raw_intake_creates_master_draft_and_profile_fields(tmp_path: Path):
    workspace_path = tmp_path / "agent_workspace.json"
    service = PersonalJobSearchService(workspace_path=str(workspace_path))

    snapshot = service.intake_raw_materials(
        {
            "full_name": "Chen Student",
            "target_title": "Backend Engineer",
            "target_markets": "CN, Remote",
            "education": "Tsinghua University",
            "major": "Computer Science",
            "graduation_cycle": "2026",
            "raw_text": (
                "Competition: ACM contest finalist.\n"
                "Course project: built a campus app with Python backend.\n"
                "Student club: organized a recruiting event for 300 participants."
            ),
        }
    )

    assert snapshot["profile"]["full_name"] == "Chen Student"
    assert snapshot["profile"]["education"] == "Tsinghua University"
    assert snapshot["profile"]["graduation_cycle"] == "2026"
    assert snapshot["resume_versions"][0]["label"] == "Raw intake master draft"
    assert snapshot["resume_versions"][0]["source"] == "raw_intake"
    assert snapshot["resume_versions"][0]["resume_data"]["projects"]
    assert snapshot["intake_payload"]["type"] == "student_intake_payload"
    assert snapshot["intake_payload"]["packaged_signals"]


def test_resume_workbench_save_creates_version(tmp_path: Path):
    workspace_path = tmp_path / "agent_workspace.json"
    service = PersonalJobSearchService(workspace_path=str(workspace_path))

    snapshot = service.create_resume_version_from_workbench(
        {
            "role": "Backend Engineer",
            "market": "cn",
            "tone": "precise",
            "resume": "Built Python APIs and improved release reliability.",
            "jd": "Looking for backend engineers with Python, reliability, and APIs.",
            "generate_document": False,
        }
    )

    assert snapshot["created_resume_version"]["source"] == "resume_lab"
    assert snapshot["created_resume_version"]["role"] == "Backend Engineer"
    assert snapshot["resume_versions"][0]["source"] == "resume_lab"
    assert snapshot["workbench_payload"]["generation_plan"]["template_hint"]
    assert snapshot["generation_result"] is None


def test_resume_workbench_generate_document_updates_output_path(tmp_path: Path):
    workspace_path = tmp_path / "agent_workspace.json"
    service = PersonalJobSearchService(workspace_path=str(workspace_path))
    service.resume_service.generate_resume = lambda **kwargs: SimpleNamespace(
        success=True,
        output={"output_path": "storage/exports/backend_engineer_resume.docx"},
        suggestions=["Keep the summary sharper."],
        error="",
    )

    snapshot = service.create_resume_version_from_workbench(
        {
            "role": "Backend Engineer",
            "market": "cn",
            "tone": "technical",
            "resume": "Built Python APIs and improved release reliability.",
            "jd": "Looking for backend engineers with Python, reliability, and APIs.",
            "generate_document": True,
        }
    )

    assert snapshot["generation_result"]["success"] is True
    assert snapshot["generation_result"]["output_path"].endswith(".docx")
    assert snapshot["resume_versions"][0]["status"] == "Ready"
    assert snapshot["resume_versions"][0]["output_path"].endswith(".docx")


def test_batch_opportunity_import_ranks_results(tmp_path: Path):
    workspace_path = tmp_path / "agent_workspace.json"
    service = PersonalJobSearchService(workspace_path=str(workspace_path))

    snapshot = service.import_opportunity_batch(
        {
            "opportunities": [
                {
                    "company": "Strong Fit",
                    "title": "Senior Backend Engineer",
                    "market": "US",
                    "location": "Remote / US",
                    "description": "Python backend role with distributed systems, reliability, ownership.",
                },
                {
                    "company": "Weaker Fit",
                    "title": "Marketing Analyst",
                    "market": "US",
                    "location": "Remote / US",
                    "description": "Brand, campaigns, and reporting.",
                },
            ]
        }
    )

    top_two = snapshot["batch_summary"]["top_recommendations"][:2]
    assert snapshot["batch_summary"]["imported_count"] == 2
    assert top_two[0]["company"] == "Strong Fit"
    assert top_two[0]["fit_score"] >= top_two[1]["fit_score"]


def test_application_feedback_updates_stage_and_notes(tmp_path: Path):
    workspace_path = tmp_path / "agent_workspace.json"
    service = PersonalJobSearchService(workspace_path=str(workspace_path))

    snapshot = service.record_application_feedback(
        {
            "company": "Atlas Cloud",
            "role": "Senior Backend Engineer",
            "result": "Rejected",
            "feedback_notes": "Needs stronger architecture depth.",
            "interview_count": 1,
        }
    )

    application = snapshot["applications"][0]
    assert application["company"] == "Atlas Cloud"
    assert application["stage"] == "Closed"
    assert application["result"] == "Rejected"
    assert application["feedback_notes"] == "Needs stronger architecture depth."
    assert application["interview_count"] == 1
    assert snapshot["feedback_summary"]["result"] == "Rejected"
    assert snapshot["feedback_summary"]["recommended_actions"]
