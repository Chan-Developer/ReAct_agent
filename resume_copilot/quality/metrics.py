# -*- coding: utf-8 -*-
"""Heuristic resume quality metrics for product iteration."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from resume_copilot.domain import normalize_resume_data


ACTION_VERBS = {
    "built",
    "designed",
    "led",
    "improved",
    "reduced",
    "increased",
    "launched",
    "delivered",
    "optimized",
    "scaled",
    "owned",
    "implemented",
    "developed",
    "architected",
    "managed",
    "mentored",
    "created",
    "drove",
}

STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "from",
    "have",
    "has",
    "had",
    "will",
    "into",
    "about",
    "your",
    "their",
    "were",
    "been",
    "than",
    "then",
    "also",
    "using",
    "used",
    "able",
    "team",
    "work",
}

TECH_KEYWORD_ALIASES = {
    "python/java/c++": ["python", "java", "c++"],
    "go/golang": ["go", "golang"],
}

CHINESE_KEYWORDS = [
    "后端",
    "项目经验",
    "系统设计",
    "计算机基础",
    "数据库",
    "缓存",
    "消息队列",
    "稳定性",
    "沟通",
    "学习能力",
    "工程化",
    "算法",
    "数据结构",
    "实习",
    "校招",
]

# Keep Chinese product signals ASCII-safe so PowerShell/codepage issues do not corrupt them.
CHINESE_KEYWORDS = [
    "\u540e\u7aef",
    "\u9879\u76ee\u7ecf\u9a8c",
    "\u7cfb\u7edf\u8bbe\u8ba1",
    "\u8ba1\u7b97\u673a\u57fa\u7840",
    "\u6570\u636e\u5e93",
    "\u7f13\u5b58",
    "\u6d88\u606f\u961f\u5217",
    "\u7a33\u5b9a\u6027",
    "\u6c9f\u901a",
    "\u5b66\u4e60\u80fd\u529b",
    "\u5de5\u7a0b\u5316",
    "\u7b97\u6cd5",
    "\u6570\u636e\u7ed3\u6784",
    "\u5b9e\u4e60",
    "\u6821\u62db",
]


@dataclass
class ResumeMetricResult:
    jd_match_score: float
    quantified_evidence_score: float
    readability_score: float
    ats_safety_score: float
    keyword_coverage_score: float
    overall_score: float
    matched_keywords: list[str]
    missing_keywords: list[str]
    notes: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "jd_match_score": round(self.jd_match_score, 2),
            "quantified_evidence_score": round(self.quantified_evidence_score, 2),
            "readability_score": round(self.readability_score, 2),
            "ats_safety_score": round(self.ats_safety_score, 2),
            "keyword_coverage_score": round(self.keyword_coverage_score, 2),
            "overall_score": round(self.overall_score, 2),
            "matched_keywords": self.matched_keywords,
            "missing_keywords": self.missing_keywords,
            "notes": self.notes,
        }


def _extract_resume_lines(resume_data: dict[str, Any]) -> list[str]:
    resume_data = normalize_resume_data(resume_data)
    lines: list[str] = []

    summary = resume_data.get("summary")
    if summary:
        lines.append(str(summary))

    for section in ("experience", "projects"):
        for item in resume_data.get(section, []):
            if not isinstance(item, dict):
                continue
            for key in ("company", "position", "name", "role", "description"):
                value = item.get(key)
                if value:
                    lines.append(str(value))
            for highlight in item.get("highlights", []):
                lines.append(str(highlight))

    for skill in resume_data.get("skills", []):
        if isinstance(skill, dict):
            skill = skill.get("name", "")
        if skill:
            lines.append(str(skill))

    return lines


def _extract_keywords(text: str) -> list[str]:
    seen: list[str] = []
    for token in re.findall(r"[A-Za-z][A-Za-z0-9\+\#\.\-/]{2,}", text.lower()):
        if token in STOPWORDS:
            continue
        for normalized in TECH_KEYWORD_ALIASES.get(token, [token]):
            if normalized not in seen:
                seen.append(normalized)
    for keyword in CHINESE_KEYWORDS:
        if keyword in text and keyword not in seen:
            seen.append(keyword)
    return seen


def extract_jd_keywords(job_description: str, max_keywords: int = 20) -> list[str]:
    keywords = _extract_keywords(job_description)
    priority = [
        kw
        for kw in keywords
        if any(ch.isdigit() for ch in kw)
        or kw in ACTION_VERBS
        or kw
        in {
            "python",
            "java",
            "golang",
            "backend",
            "distributed",
            "reliability",
            "kubernetes",
            "aws",
            "sql",
            "redis",
            "api",
            "leadership",
            "mentor",
        }
    ]
    ordered = priority + [kw for kw in keywords if kw not in priority]
    return ordered[:max_keywords]


def _score_keyword_match(resume_text: str, keywords: list[str]) -> tuple[float, list[str], list[str]]:
    if not keywords:
        return 0.0, [], []

    lowered = resume_text.lower()
    matched = [kw for kw in keywords if kw.lower() in lowered or kw in resume_text]
    missing = [kw for kw in keywords if kw not in matched]
    score = (len(matched) / len(keywords)) * 100
    return score, matched, missing


def _score_quantified_evidence(lines: list[str]) -> float:
    bullet_like = [line for line in lines if len(line.split()) >= 4]
    if not bullet_like:
        return 0.0
    quantified = [
        line
        for line in bullet_like
        if re.search(r"\d", line) or re.search(r"%|percent|x\b|ms\b|k\b|m\b", line.lower())
    ]
    return (len(quantified) / len(bullet_like)) * 100


def _score_readability(lines: list[str]) -> float:
    bullet_like = [line.strip() for line in lines if len(line.split()) >= 4]
    if not bullet_like:
        return 40.0

    concise = sum(1 for line in bullet_like if 6 <= len(line.split()) <= 28)
    action_led = sum(1 for line in bullet_like if line.split()[0].lower().strip(",:-") in ACTION_VERBS)
    concise_score = (concise / len(bullet_like)) * 70
    action_score = (action_led / len(bullet_like)) * 30
    return concise_score + action_score


def _score_ats_safety(resume_data: dict[str, Any]) -> tuple[float, list[str]]:
    resume_data = normalize_resume_data(resume_data)
    notes: list[str] = []
    score = 100.0

    if not resume_data.get("name"):
        score -= 20
        notes.append("Missing candidate name.")
    if not resume_data.get("email"):
        score -= 15
        notes.append("Missing email contact.")
    if not resume_data.get("summary"):
        score -= 10
        notes.append("Missing summary section.")
    if not resume_data.get("experience"):
        score -= 25
        notes.append("Missing experience section.")
    if not resume_data.get("skills"):
        score -= 10
        notes.append("Missing skills section.")
    if len(json.dumps(resume_data, ensure_ascii=False)) < 280:
        score -= 15
        notes.append("Resume content is too sparse for recruiter review.")

    return max(score, 0.0), notes


def score_resume_against_jd(
    resume_data: dict[str, Any],
    job_description: str,
) -> ResumeMetricResult:
    resume_data = normalize_resume_data(resume_data)
    lines = _extract_resume_lines(resume_data)
    resume_text = "\n".join(lines)

    jd_keywords = extract_jd_keywords(job_description)
    jd_match_score, matched, missing = _score_keyword_match(resume_text, jd_keywords)
    quantified_score = _score_quantified_evidence(lines)
    readability_score = _score_readability(lines)
    ats_score, ats_notes = _score_ats_safety(resume_data)
    keyword_coverage_score = min(jd_match_score * 1.1, 100.0)

    overall = (
        jd_match_score * 0.3
        + quantified_score * 0.25
        + readability_score * 0.2
        + ats_score * 0.15
        + keyword_coverage_score * 0.1
    )

    notes = ats_notes[:]
    if missing[:3]:
        notes.append(f"Top missing keywords: {', '.join(missing[:3])}")
    if quantified_score < 40:
        notes.append("Add more quantified outcomes to improve credibility.")
    if readability_score < 55:
        notes.append("Shorten bullets and start more lines with action verbs.")

    return ResumeMetricResult(
        jd_match_score=jd_match_score,
        quantified_evidence_score=quantified_score,
        readability_score=readability_score,
        ats_safety_score=ats_score,
        keyword_coverage_score=keyword_coverage_score,
        overall_score=overall,
        matched_keywords=matched,
        missing_keywords=missing,
        notes=notes,
    )
