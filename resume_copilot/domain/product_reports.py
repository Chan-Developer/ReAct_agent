# -*- coding: utf-8 -*-
"""Structured product reports for evaluation and scoring flows."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class JDAnalysis:
    role_hint: str
    keywords: list[str] = field(default_factory=list)
    responsibilities: list[str] = field(default_factory=list)
    requirements: list[str] = field(default_factory=list)
    bonus_signals: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "role_hint": self.role_hint,
            "keywords": self.keywords,
            "responsibilities": self.responsibilities,
            "requirements": self.requirements,
            "bonus_signals": self.bonus_signals,
        }


@dataclass
class ResumeDiagnosisReport:
    report_type: str
    role: str
    market: str
    jd_analysis: JDAnalysis
    metrics: dict[str, Any]
    diagnosis: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    @property
    def jd_match_score(self) -> float:
        return float(self.metrics.get("jd_match_score", 0.0))

    @property
    def quantified_evidence_score(self) -> float:
        return float(self.metrics.get("quantified_evidence_score", 0.0))

    @property
    def readability_score(self) -> float:
        return float(self.metrics.get("readability_score", 0.0))

    @property
    def ats_safety_score(self) -> float:
        return float(self.metrics.get("ats_safety_score", 0.0))

    @property
    def keyword_coverage_score(self) -> float:
        return float(self.metrics.get("keyword_coverage_score", 0.0))

    @property
    def overall_score(self) -> float:
        return float(self.metrics.get("overall_score", 0.0))

    @property
    def matched_keywords(self) -> list[str]:
        return list(self.metrics.get("matched_keywords", []))

    @property
    def missing_keywords(self) -> list[str]:
        return list(self.metrics.get("missing_keywords", []))

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "type": self.report_type,
            "role": self.role,
            "market": self.market,
            "jd_analysis": self.jd_analysis.to_dict(),
            "metrics": self.metrics,
            "diagnosis": self.diagnosis,
            "recommendations": self.recommendations,
        }
        payload.update(self.metrics)
        return payload


@dataclass
class OpportunityScoreReport:
    report_type: str
    company: str
    title: str
    market: str
    fit_score: float
    matched_keywords: list[str] = field(default_factory=list)
    match_reasons: list[str] = field(default_factory=list)
    missing_signals: list[str] = field(default_factory=list)
    risk_flags: list[str] = field(default_factory=list)
    recommended_resume_version: str = ""
    status: str = "recommended"
    next_action: str = ""
    source: str = ""
    location: str = ""
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.report_type,
            "company": self.company,
            "title": self.title,
            "market": self.market,
            "fit_score": round(self.fit_score, 2),
            "matched_keywords": self.matched_keywords,
            "match_reasons": self.match_reasons,
            "missing_signals": self.missing_signals,
            "risk_flags": self.risk_flags,
            "recommended_resume_version": self.recommended_resume_version,
            "status": self.status,
            "next_action": self.next_action,
            "source": self.source,
            "location": self.location,
            "description": self.description,
        }
