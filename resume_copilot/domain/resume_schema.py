# -*- coding: utf-8 -*-
"""Canonical schema helpers for resume product data."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


def normalize_resume_data(resume_data: dict[str, Any]) -> dict[str, Any]:
    """Return a canonical resume payload for product services.

    The repo historically accepted a few legacy aliases such as
    ``experiences`` vs ``experience``. Product-facing flows should operate on
    one stable shape so downstream scoring, curation, layout, and export all
    see the same structure.
    """

    normalized = deepcopy(resume_data or {})

    if "experiences" in normalized and "experience" not in normalized:
        normalized["experience"] = normalized["experiences"]
    normalized.pop("experiences", None)

    if "projects" not in normalized or normalized["projects"] is None:
        normalized["projects"] = []
    if "experience" not in normalized or normalized["experience"] is None:
        normalized["experience"] = []
    if "skills" not in normalized or normalized["skills"] is None:
        normalized["skills"] = []
    if "education" not in normalized or normalized["education"] is None:
        normalized["education"] = []

    normalized["skills"] = [_normalize_skill(skill) for skill in normalized["skills"]]
    return normalized


def _normalize_skill(skill: Any) -> Any:
    if not isinstance(skill, dict):
        return skill
    if "name" in skill:
        return {"name": str(skill.get("name", "")).strip()}
    return skill
