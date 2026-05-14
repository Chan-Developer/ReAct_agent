# -*- coding: utf-8 -*-
"""Core product domain models for the personal job-search agent."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class UserProfile:
    full_name: str
    target_title: str
    target_markets: list[str] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    preferences: dict[str, str] = field(default_factory=dict)
    education: str = ""
    major: str = ""
    graduation_cycle: str = ""
    raw_materials_summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UserProfile":
        return cls(
            full_name=str(data.get("full_name", "")),
            target_title=str(data.get("target_title", "")),
            target_markets=list(data.get("target_markets", [])),
            strengths=list(data.get("strengths", [])),
            preferences=dict(data.get("preferences", {})),
            education=str(data.get("education", "")),
            major=str(data.get("major", "")),
            graduation_cycle=str(data.get("graduation_cycle", "")),
            raw_materials_summary=str(data.get("raw_materials_summary", "")),
        )


@dataclass
class CareerTarget:
    title: str
    market: str
    seniority: str
    priorities: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CareerTarget":
        return cls(
            title=str(data.get("title", "")),
            market=str(data.get("market", "")),
            seniority=str(data.get("seniority", "")),
            priorities=list(data.get("priorities", [])),
        )


@dataclass
class ResumeVersion:
    label: str
    status: str
    focus: str
    market: str
    role: str = ""
    source: str = ""
    output_path: str = ""
    resume_data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ResumeVersion":
        return cls(
            label=str(data.get("label", "")),
            status=str(data.get("status", "")),
            focus=str(data.get("focus", "")),
            market=str(data.get("market", "")),
            role=str(data.get("role", "")),
            source=str(data.get("source", "")),
            output_path=str(data.get("output_path", "")),
            resume_data=dict(data.get("resume_data", {})),
        )


@dataclass
class ApplicationRecord:
    company: str
    role: str
    stage: str
    next_step: str
    source: str = ""
    resume_label: str = ""
    result: str = ""
    feedback_notes: str = ""
    interview_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ApplicationRecord":
        return cls(
            company=str(data.get("company", "")),
            role=str(data.get("role", "")),
            stage=str(data.get("stage", "")),
            next_step=str(data.get("next_step", "")),
            source=str(data.get("source", "")),
            resume_label=str(data.get("resume_label", "")),
            result=str(data.get("result", "")),
            feedback_notes=str(data.get("feedback_notes", "")),
            interview_count=int(data.get("interview_count", 0) or 0),
        )


@dataclass
class InterviewPrepSession:
    topic: str
    status: str
    focus: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "InterviewPrepSession":
        return cls(
            topic=str(data.get("topic", "")),
            status=str(data.get("status", "")),
            focus=str(data.get("focus", "")),
        )


@dataclass
class JobOpportunity:
    company: str
    title: str
    location: str
    market: str
    source: str
    job_url: str = ""
    description: str = ""
    posted_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "JobOpportunity":
        return cls(
            company=str(data.get("company", "")),
            title=str(data.get("title", "")),
            location=str(data.get("location", "")),
            market=str(data.get("market", "")),
            source=str(data.get("source", "")),
            job_url=str(data.get("job_url", "")),
            description=str(data.get("description", "")),
            posted_at=str(data.get("posted_at", "")),
        )


@dataclass
class MatchedOpportunity:
    company: str
    title: str
    market: str
    fit_score: float
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
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MatchedOpportunity":
        return cls(
            company=str(data.get("company", "")),
            title=str(data.get("title", "")),
            market=str(data.get("market", "")),
            fit_score=float(data.get("fit_score", 0.0) or 0.0),
            match_reasons=list(data.get("match_reasons", [])),
            missing_signals=list(data.get("missing_signals", [])),
            risk_flags=list(data.get("risk_flags", [])),
            recommended_resume_version=str(data.get("recommended_resume_version", "")),
            status=str(data.get("status", "recommended")),
            next_action=str(data.get("next_action", "")),
            source=str(data.get("source", "")),
            location=str(data.get("location", "")),
            description=str(data.get("description", "")),
        )


@dataclass
class AgentWorkspace:
    profile: UserProfile
    targets: list[CareerTarget] = field(default_factory=list)
    resume_versions: list[ResumeVersion] = field(default_factory=list)
    opportunities: list[MatchedOpportunity] = field(default_factory=list)
    applications: list[ApplicationRecord] = field(default_factory=list)
    interviews: list[InterviewPrepSession] = field(default_factory=list)
    memory_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile": self.profile.to_dict(),
            "targets": [item.to_dict() for item in self.targets],
            "resume_versions": [item.to_dict() for item in self.resume_versions],
            "opportunities": [item.to_dict() for item in self.opportunities],
            "applications": [item.to_dict() for item in self.applications],
            "interviews": [item.to_dict() for item in self.interviews],
            "memory_notes": list(self.memory_notes),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentWorkspace":
        return cls(
            profile=UserProfile.from_dict(data.get("profile", {})),
            targets=[CareerTarget.from_dict(item) for item in data.get("targets", [])],
            resume_versions=[
                ResumeVersion.from_dict(item) for item in data.get("resume_versions", [])
            ],
            opportunities=[
                MatchedOpportunity.from_dict(item) for item in data.get("opportunities", [])
            ],
            applications=[
                ApplicationRecord.from_dict(item) for item in data.get("applications", [])
            ],
            interviews=[
                InterviewPrepSession.from_dict(item) for item in data.get("interviews", [])
            ],
            memory_notes=list(data.get("memory_notes", [])),
        )
