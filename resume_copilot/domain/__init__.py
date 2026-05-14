# -*- coding: utf-8 -*-
"""Domain models for the personal job-search agent."""

from .models import (
    AgentWorkspace,
    ApplicationRecord,
    CareerTarget,
    InterviewPrepSession,
    JobOpportunity,
    MatchedOpportunity,
    ResumeVersion,
    UserProfile,
)
from .product_reports import JDAnalysis, OpportunityScoreReport, ResumeDiagnosisReport
from .resume_schema import normalize_resume_data

__all__ = [
    "AgentWorkspace",
    "ApplicationRecord",
    "CareerTarget",
    "InterviewPrepSession",
    "JobOpportunity",
    "MatchedOpportunity",
    "ResumeVersion",
    "UserProfile",
    "JDAnalysis",
    "ResumeDiagnosisReport",
    "OpportunityScoreReport",
    "normalize_resume_data",
]
