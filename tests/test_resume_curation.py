# -*- coding: utf-8 -*-
"""Tests for product curation behavior."""

from __future__ import annotations

from resume_copilot.product import curate_resume, rank_projects_for_job, sort_awards_by_importance
from tools.generators.resume import ResumeData


def test_rank_projects_for_target_job():
    projects = [
        {
            "name": "Campus Club Mini Program",
            "role": "Developer",
            "description": "Built a student activity mini app.",
            "highlights": ["Implemented registration flow for 2k students."],
            "tech_stack": ["Vue", "Node.js"],
        },
        {
            "name": "Distributed Recommendation Platform",
            "role": "Project Lead",
            "description": "Designed backend APIs and ranking services for personalized recommendations.",
            "highlights": ["Improved p95 latency by 37%.", "Led 4 engineers across backend modules."],
            "tech_stack": ["Python", "Redis", "Kubernetes"],
        },
    ]

    ranked, notes = rank_projects_for_job(
        projects,
        "Senior backend engineer with Python, Redis, Kubernetes, API design and distributed systems experience.",
    )

    assert ranked[0]["name"] == "Distributed Recommendation Platform"
    assert ranked[0]["target_fit_summary"]
    assert notes


def test_sort_awards_by_importance():
    awards = [
        "校级优秀学生干部",
        "国家奖学金",
        "省级数学建模一等奖",
    ]

    sorted_awards = sort_awards_by_importance(awards)

    assert sorted_awards[0] == "国家奖学金"
    assert sorted_awards[-1] == "校级优秀学生干部"


def test_curate_resume_applies_project_and_award_order():
    resume_data = {
        "projects": [
            {
                "name": "B",
                "description": "Student project",
                "tech_stack": ["HTML"],
            },
            {
                "name": "A",
                "description": "Built distributed backend APIs with Python and Redis.",
                "tech_stack": ["Python", "Redis"],
            },
        ],
        "awards": ["校级三好学生", "国际大学生竞赛金奖"],
    }

    curated, notes = curate_resume(
        resume_data,
        "Backend engineer role requiring Python Redis API experience.",
    )

    assert curated["projects"][0]["name"] == "A"
    assert curated["awards"][0] == "国际大学生竞赛金奖"
    assert notes


def test_resume_data_accepts_curated_project_fields():
    data = ResumeData.from_dict(
        {
            "projects": [
                {
                    "name": "Search Platform",
                    "target_fit_summary": "Best aligned to target role through Python, API.",
                    "relevance_score": 88.5,
                }
            ]
        }
    )

    assert data.projects[0].target_fit_summary.startswith("Best aligned")
    assert data.projects[0].relevance_score == 88.5
