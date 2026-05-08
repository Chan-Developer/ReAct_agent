# -*- coding: utf-8 -*-
"""Core curation helpers for the resume product."""

from __future__ import annotations

import copy
import re
from typing import Any


PROJECT_PRIORITY_TERMS = {
    "architecture": 6,
    "distributed": 5,
    "platform": 5,
    "scalable": 5,
    "optimization": 4,
    "performance": 4,
    "backend": 4,
    "api": 4,
    "data": 4,
    "ml": 4,
    "ai": 4,
    "kubernetes": 4,
    "cloud": 4,
    "lead": 3,
    "owner": 3,
    "system": 3,
}

AWARD_PRIORITY_PATTERNS = (
    (r"(national|global|international|world|国家级|国家|全国|国际|全球)", 120),
    (r"(champion|winner|gold|一等奖|特等奖|冠军|金奖|top\s*1)", 110),
    (r"(finalist|runner-up|silver|二等奖|亚军|银奖|top\s*3)", 95),
    (r"(provincial|regional|省级|大区|区域)", 80),
    (r"(scholarship|奖学金|优秀毕业生|优秀学生干部)", 72),
    (r"(school|campus|university|college|校级|院级)", 58),
    (r"(nomination|participation|提名|参与)", 40),
)


def curate_resume(resume_data: dict[str, Any], job_description: str = "") -> tuple[dict[str, Any], list[str]]:
    """Apply product curation before layout and export."""
    curated = copy.deepcopy(resume_data)
    suggestions: list[str] = []

    if "experiences" in curated and "experience" not in curated:
        curated["experience"] = curated["experiences"]

    if curated.get("projects"):
        curated["projects"], project_notes = rank_projects_for_job(
            curated.get("projects", []),
            job_description,
        )
        suggestions.extend(project_notes)

    if curated.get("awards"):
        curated["awards"] = sort_awards_by_importance(curated.get("awards", []))

    return curated, suggestions


def rank_projects_for_job(
    projects: list[dict[str, Any]],
    job_description: str,
) -> tuple[list[dict[str, Any]], list[str]]:
    """Reorder and lightly package projects around target role fit."""
    if not projects:
        return [], []

    job_keywords = _extract_keywords(job_description)
    ranked: list[tuple[float, dict[str, Any], str]] = []

    for project in projects:
        project_copy = copy.deepcopy(project)
        score, rationale, focus = _score_project(project_copy, job_keywords)
        if focus:
            project_copy["target_fit_summary"] = focus
        project_copy["relevance_score"] = round(score, 2)
        ranked.append((score, project_copy, rationale))

    ranked.sort(key=lambda item: item[0], reverse=True)

    suggestions: list[str] = []
    if ranked:
        top_project = ranked[0][1].get("name", "Top project")
        suggestions.append(f"Top project surfaced for this role: {top_project}.")
        for _, item, rationale in ranked[:2]:
            name = item.get("name", "Project")
            suggestions.append(f"{name}: {rationale}")

    return [item for _, item, _ in ranked], suggestions[:3]


def sort_awards_by_importance(awards: list[str]) -> list[str]:
    """Sort awards from highest-signal to lowest-signal."""
    return sorted(awards, key=_award_importance_score, reverse=True)


def _score_project(project: dict[str, Any], job_keywords: set[str]) -> tuple[float, str, str]:
    text_parts = [
        str(project.get("name", "")),
        str(project.get("role", "")),
        str(project.get("description", "")),
        " ".join(str(item) for item in project.get("highlights", [])),
        " ".join(str(item) for item in project.get("tech_stack", [])),
    ]
    haystack = " ".join(text_parts).lower()

    overlap = sorted(kw for kw in job_keywords if kw in haystack)
    overlap_score = len(overlap) * 12

    priority_score = 0
    for term, weight in PROJECT_PRIORITY_TERMS.items():
        if term in haystack:
            priority_score += weight

    impact_signals = len(re.findall(r"\d|%|x\b|ms\b|k\b|m\b|亿|万", haystack)) * 2
    leadership_signals = len(
        re.findall(r"lead|owner|architect|mentor|主导|负责|带领|推进|设计", haystack)
    ) * 3
    freshness_score = 4 if project.get("end_date") in {"至今", "Present", "present"} else 0

    total_score = overlap_score + priority_score + impact_signals + leadership_signals + freshness_score

    rationale_bits: list[str] = []
    if overlap:
        rationale_bits.append(f"matched {min(len(overlap), 4)} role keywords")
    if leadership_signals:
        rationale_bits.append("shows ownership")
    if impact_signals:
        rationale_bits.append("contains measurable impact")
    if not rationale_bits:
        rationale_bits.append("supports role narrative")

    focus = ""
    if overlap:
        focus = "Best aligned to target role through " + ", ".join(overlap[:3]) + "."
    elif priority_score:
        focus = "Highlights high-complexity delivery and execution ownership."

    return total_score, ", ".join(rationale_bits), focus


def _extract_keywords(text: str) -> set[str]:
    keywords = {
        token
        for token in re.findall(r"[A-Za-z][A-Za-z0-9\+\#\.\-/]{2,}", text.lower())
        if token not in {"the", "and", "for", "with", "from", "that", "your", "years"}
    }
    return keywords


def _award_importance_score(award: str) -> int:
    lowered = award.lower()
    score = 0
    for pattern, weight in AWARD_PRIORITY_PATTERNS:
        if re.search(pattern, lowered):
            score += weight
    if re.search(r"\d{4}", lowered):
        score += 3
    score += max(0, 30 - len(award)) * 0.2
    return int(score)
