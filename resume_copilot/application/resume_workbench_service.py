# -*- coding: utf-8 -*-
"""Application service for the Resume Lab workbench."""

from __future__ import annotations

from .ai_optimizer import optimize_resume_with_ai
from .reporting import build_resume_workbench_payload


class ResumeWorkbenchService:
    """Build frontend-ready payloads for the resume workbench."""

    def build_payload(
        self,
        *,
        resume_text: str,
        job_description: str,
        role: str = "Target Role",
        market: str = "global",
        tone: str = "precise",
        discipline: str = "",
        template_name: str = "",
    ) -> dict:
        payload = build_resume_workbench_payload(
            resume_text=resume_text,
            job_description=job_description,
            role=role,
            market=market,
            tone=tone,
        )
        if template_name:
            payload["generation_plan"]["template_hint"] = template_name
        payload["discipline"] = discipline
        payload["ai_optimization"] = optimize_resume_with_ai(
            role=role,
            resume_text=resume_text,
            job_description=job_description,
            discipline=discipline,
            template_name=payload["generation_plan"].get("template_hint", template_name),
        )
        return payload
