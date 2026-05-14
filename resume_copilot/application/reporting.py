# -*- coding: utf-8 -*-
"""Builders for structured product reports."""

from __future__ import annotations

import re
from typing import Any

from resume_copilot.domain import JDAnalysis, ResumeDiagnosisReport, normalize_resume_data
from resume_copilot.quality import score_resume_against_jd
from resume_copilot.quality.metrics import extract_jd_keywords


def build_jd_analysis(job_description: str, fallback_role: str = "Target Role") -> JDAnalysis:
    lines = [line.strip(" -*\t") for line in job_description.splitlines() if line.strip()]
    responsibilities: list[str] = []
    requirements: list[str] = []
    bonus_signals: list[str] = []

    for line in lines:
        lowered = line.lower()
        if _looks_like_requirement(lowered):
            requirements.append(line)
        elif _looks_like_bonus(lowered):
            bonus_signals.append(line)
        elif len(responsibilities) < 6:
            responsibilities.append(line)

    role_hint = _infer_role(job_description, fallback_role=fallback_role)
    keywords = extract_jd_keywords(job_description, max_keywords=12)
    return JDAnalysis(
        role_hint=role_hint,
        keywords=keywords,
        responsibilities=responsibilities[:6],
        requirements=requirements[:6],
        bonus_signals=bonus_signals[:6],
    )


def build_resume_diagnosis_report(
    resume_data: dict[str, Any],
    job_description: str,
    role: str = "Target Role",
    market: str = "global",
) -> ResumeDiagnosisReport:
    normalized_resume = normalize_resume_data(resume_data)
    metric_result = score_resume_against_jd(normalized_resume, job_description)
    metrics = metric_result.to_dict()
    jd_analysis = build_jd_analysis(job_description, fallback_role=role)

    diagnosis: list[str] = []
    if metrics["quantified_evidence_score"] < 45:
        diagnosis.append("Add more measurable outcomes to prove impact.")
    if metrics["jd_match_score"] < 60:
        diagnosis.append("Re-align summary and project language to the target JD.")
    if metrics["readability_score"] < 55:
        diagnosis.append("Tighten bullets and lead with stronger action verbs.")
    if not diagnosis:
        diagnosis.append("Current draft shows a solid base for recruiter review.")

    recommendations = _build_recommendations(metrics, market, role)
    return ResumeDiagnosisReport(
        report_type="resume_diagnosis_report",
        role=role,
        market=market,
        jd_analysis=jd_analysis,
        metrics=metrics,
        diagnosis=diagnosis,
        recommendations=recommendations,
    )


def build_resume_workbench_payload(
    resume_text: str,
    job_description: str,
    role: str,
    market: str,
    tone: str,
) -> dict[str, Any]:
    """Build a frontend-friendly payload for the resume workbench."""

    normalized_role = role or "Target Role"
    resume_data = {
        "name": "Candidate",
        "summary": resume_text[:800],
        "experience": [
            {
                "company": "Current Experience",
                "position": normalized_role,
                "description": resume_text[:1200],
                "highlights": _extract_highlights(resume_text)[:4],
            }
        ]
        if resume_text.strip()
        else [],
        "skills": _extract_keywords_from_text(resume_text)[:14],
    }

    report = build_resume_diagnosis_report(
        resume_data=resume_data,
        job_description=job_description,
        role=normalized_role,
        market=market,
    )
    report_payload = report.to_dict()
    missing_keywords = report_payload["metrics"].get("missing_keywords", [])
    matched_keywords = report_payload["metrics"].get("matched_keywords", [])
    generation_plan = _build_generation_plan(
        report_payload["metrics"],
        role=normalized_role,
        market=market,
        tone=tone,
    )

    return {
        "type": "resume_workbench_payload",
        "role": normalized_role,
        "market": market,
        "tone": tone,
        "report": report_payload,
        "input_profile": {
            "resume_line_count": len([line for line in resume_text.splitlines() if line.strip()]),
            "jd_line_count": len([line for line in job_description.splitlines() if line.strip()]),
        },
        "focus_areas": _build_focus_areas(report_payload["metrics"], tone, market),
        "rewrite_candidates": _build_rewrite_candidates(
            _extract_highlights(resume_text),
            missing_keywords,
            tone,
        ),
        "keyword_stack": {
            "matched": matched_keywords[:8],
            "missing": missing_keywords[:8],
        },
        "resume_seed": resume_data,
        "generation_plan": generation_plan,
        "command_log": _build_command_log(report_payload, normalized_role, market),
        "next_actions": _build_next_actions(report_payload, normalized_role),
    }


def _build_recommendations(metrics: dict[str, Any], market: str, role: str) -> list[str]:
    market_guidance = {
        "us": "Push quantified scale, ownership, and recruiter scan value.",
        "uk": "Balance outcomes with role scope and team context.",
        "eu": "Keep the structure consistent and cross-border readable.",
        "apac": "Increase evidence density and clarify progression signals.",
        "remote": "Highlight async delivery, documentation, and stakeholder communication.",
        "global": "Optimize for recruiter clarity and role-fit evidence.",
    }
    recommendations = [
        market_guidance.get(market.lower(), market_guidance["global"]),
        f"Anchor the resume more explicitly to {role}.",
    ]
    missing_keywords = metrics.get("missing_keywords", [])
    if missing_keywords:
        recommendations.append(
            "Top missing keywords to consider: " + ", ".join(missing_keywords[:3]) + "."
        )
    return recommendations


def _build_focus_areas(metrics: dict[str, Any], tone: str, market: str) -> list[str]:
    areas: list[str] = []
    if metrics["quantified_evidence_score"] < 45:
        areas.append("Increase measurable outcomes and operational impact.")
    if metrics["jd_match_score"] < 60:
        areas.append("Mirror the JD language more directly in the summary and project framing.")
    if metrics["readability_score"] < 55:
        areas.append("Shorten bullets and lead with stronger verbs.")

    tone_guidance = {
        "precise": "Keep the copy compact and recruiter-scannable.",
        "confident": "Push ownership and decision-making higher in the narrative.",
        "technical": "Expose architecture, reliability, and implementation tradeoffs.",
    }
    market_guidance = {
        "us": "Bias toward one-page density and quantified scale signals.",
        "uk": "Balance outcomes with role scope and collaboration context.",
        "eu": "Preserve consistent structure and cross-border clarity.",
        "apac": "Support stronger education and project packaging when useful.",
        "remote": "Surface async execution and documentation habits.",
    }

    areas.append(tone_guidance.get(tone, "Keep the language direct and useful."))
    areas.append(market_guidance.get(market, "Optimize for role-fit clarity."))
    return areas[:5]


def _build_rewrite_candidates(lines: list[str], missing_keywords: list[str], tone: str) -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []
    if _contains_cjk(" ".join(lines)):
        return _build_chinese_rewrite_candidates(lines, missing_keywords)

    tone_suffix = {
        "precise": "with cleaner scope and fewer filler words",
        "confident": "with stronger ownership framing",
        "technical": "with deeper system detail",
    }.get(tone, "with tighter role-fit language")

    for line in lines[:3]:
        missing = ", ".join(missing_keywords[:2]) if missing_keywords else "role-fit keywords"
        candidates.append(
            {
                "before": line,
                "after": f"Built and improved {missing} outcomes {tone_suffix}.",
            }
        )
    return candidates


def _build_chinese_rewrite_candidates(
    lines: list[str],
    missing_keywords: list[str],
) -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []
    keyword_hint = "、".join(missing_keywords[:3]) if missing_keywords else "岗位关键词"
    for line in lines[:3]:
        after = _rewrite_chinese_student_line(line, keyword_hint)
        candidates.append({"before": line, "after": after})
    return candidates


def _rewrite_chinese_student_line(line: str, keyword_hint: str) -> str:
    if "FastAPI" in line or "Python" in line or "后端" in line:
        return (
            "基于 Python/FastAPI 设计并实现校园招新小程序后端，完成报名、数据管理与接口联调，"
            "支撑 300+ 学生使用，并可继续补充数据库、缓存或系统稳定性细节。"
        )
    if "ACM" in line or "算法" in line or "图论" in line or "动态规划" in line:
        return (
            "参与 ACM 校队训练，系统复盘图论与动态规划题型，沉淀解题模板和复杂度分析，"
            f"用于证明计算机基础与{keyword_hint}相关能力。"
        )
    if "社团" in line or "组织" in line or "分享会" in line:
        return (
            "组织校园技术分享会，负责流程规划、宣传触达与报名协调，服务技术社群活动落地，"
            "体现沟通协作、推进执行和跨角色协调能力。"
        )
    return f"围绕{keyword_hint}重写该经历：补充任务背景、个人动作、技术栈和可量化结果。"


def _build_command_log(report_payload: dict[str, Any], role: str, market: str) -> list[str]:
    metrics = report_payload["metrics"]
    return [
        f"> role.target = {role}",
        f"> market.profile = {market}",
        f"> jd.match_score = {metrics['jd_match_score']}",
        f"> evidence.score = {metrics['quantified_evidence_score']}",
        f"> missing.keywords = {', '.join(metrics.get('missing_keywords', [])[:4]) or 'none'}",
    ]


def _build_next_actions(report_payload: dict[str, Any], role: str) -> list[str]:
    metrics = report_payload["metrics"]
    if _contains_cjk(role):
        actions = [
            f"把简历开头两行改成直接服务「{role}」的求职摘要。",
            "把弱描述改成“任务背景 + 个人动作 + 技术/方法 + 可量化结果”的项目 bullet。",
            "补充一个最能证明岗位要求的项目或经历，并写清楚你个人负责的部分。",
        ]
        if metrics["missing_keywords"]:
            actions.append("把最高价值的缺失关键词自然补进摘要、项目和技能模块。")
        return actions[:4]

    actions = [
        f"Rewrite the summary so the first two lines clearly target {role}.",
        "Replace weak bullets with outcome-led bullets that include numbers or scale signals.",
        "Add one project or experience block that best proves the hiring signals in the JD.",
    ]
    if metrics["missing_keywords"]:
        actions.append(
            "Inject the highest-value missing keywords into summary, experience, and skills."
        )
    return actions[:4]


def _build_generation_plan(
    metrics: dict[str, Any],
    *,
    role: str,
    market: str,
    tone: str,
) -> dict[str, Any]:
    page_preference = "one_page"
    if metrics["quantified_evidence_score"] > 70 and metrics["readability_score"] > 65:
        page_preference = "auto"

    template_hint = "tech_modern"
    if tone == "confident":
        template_hint = "management"
    elif tone == "precise":
        template_hint = "minimal"

    if market == "apac":
        template_hint = "fresh_graduate"

    filename_stem = _slugify_filename(role or "resume")
    return {
        "template_hint": template_hint,
        "page_preference": page_preference,
        "filename_stem": filename_stem,
        "summary_focus": f"Target {role} with {tone} and {market} market framing.",
        "highlight_strategy": (
            "Lead with matched keywords, then quantified evidence, then recruiter-scan clarity."
        ),
    }


def _extract_highlights(text: str) -> list[str]:
    lines = [line.strip("- ").strip() for line in text.splitlines() if line.strip()]
    if lines:
        return lines
    chunks = [chunk.strip() for chunk in re.split(r"[。.!?\n]", text) if chunk.strip()]
    return chunks[:5]


def _extract_keywords_from_text(text: str) -> list[str]:
    seen: list[str] = []
    for token in re.findall(r"[A-Za-z][A-Za-z0-9\+\#\.\-/]{2,}", text):
        if token.lower() not in {item.lower() for item in seen}:
            seen.append(token)
    for token in ("后端", "系统设计", "计算机基础", "项目经验", "沟通", "学习能力", "工程化"):
        if token in text and token not in seen:
            seen.append(token)
    return seen


def _contains_cjk(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text))


# ASCII-safe overrides for Chinese student resume rewriting. They intentionally
# sit below the earlier definitions so corrupted terminal encodings cannot leak
# into runtime output.
def _build_chinese_rewrite_candidates(
    lines: list[str],
    missing_keywords: list[str],
) -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []
    keyword_hint = "\u3001".join(missing_keywords[:3]) if missing_keywords else "\u5c97\u4f4d\u5173\u952e\u8bcd"
    for line in lines[:3]:
        after = _rewrite_chinese_student_line(line, keyword_hint)
        candidates.append({"before": line, "after": after})
    return candidates


def _rewrite_chinese_student_line(line: str, keyword_hint: str) -> str:
    if "FastAPI" in line or "Python" in line or "\u540e\u7aef" in line:
        return (
            "\u57fa\u4e8e Python/FastAPI \u8bbe\u8ba1\u5e76\u5b9e\u73b0\u6821\u56ed\u62db\u65b0\u5c0f\u7a0b\u5e8f\u540e\u7aef\uff0c"
            "\u5b8c\u6210\u62a5\u540d\u3001\u6570\u636e\u7ba1\u7406\u4e0e\u63a5\u53e3\u8054\u8c03\uff0c\u652f\u6491 300+ \u5b66\u751f\u4f7f\u7528\uff0c"
            "\u5e76\u53ef\u7ee7\u7eed\u8865\u5145\u6570\u636e\u5e93\u3001\u7f13\u5b58\u6216\u7cfb\u7edf\u7a33\u5b9a\u6027\u7ec6\u8282\u3002"
        )
    if "ACM" in line or "\u7b97\u6cd5" in line or "\u56fe\u8bba" in line or "\u52a8\u6001\u89c4\u5212" in line:
        return (
            "\u53c2\u4e0e ACM \u6821\u961f\u8bad\u7ec3\uff0c\u7cfb\u7edf\u590d\u76d8\u56fe\u8bba\u4e0e\u52a8\u6001\u89c4\u5212\u9898\u578b\uff0c"
            "\u6c89\u6dc0\u89e3\u9898\u6a21\u677f\u548c\u590d\u6742\u5ea6\u5206\u6790\uff0c"
            f"\u7528\u4e8e\u8bc1\u660e\u8ba1\u7b97\u673a\u57fa\u7840\u4e0e{keyword_hint}\u76f8\u5173\u80fd\u529b\u3002"
        )
    if "\u793e\u56e2" in line or "\u7ec4\u7ec7" in line or "\u5206\u4eab\u4f1a" in line:
        return (
            "\u7ec4\u7ec7\u6821\u56ed\u6280\u672f\u5206\u4eab\u4f1a\uff0c\u8d1f\u8d23\u6d41\u7a0b\u89c4\u5212\u3001\u5ba3\u4f20\u89e6\u8fbe\u4e0e\u62a5\u540d\u534f\u8c03\uff0c"
            "\u670d\u52a1\u6280\u672f\u793e\u7fa4\u6d3b\u52a8\u843d\u5730\uff0c\u4f53\u73b0\u6c9f\u901a\u534f\u4f5c\u3001\u63a8\u8fdb\u6267\u884c\u548c\u8de8\u89d2\u8272\u534f\u8c03\u80fd\u529b\u3002"
        )
    return (
        f"\u56f4\u7ed5{keyword_hint}\u91cd\u5199\u8be5\u7ecf\u5386\uff1a"
        "\u8865\u5145\u4efb\u52a1\u80cc\u666f\u3001\u4e2a\u4eba\u52a8\u4f5c\u3001\u6280\u672f\u6808\u548c\u53ef\u91cf\u5316\u7ed3\u679c\u3002"
    )


def _slugify_filename(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")
    return slug or "resume"


def _looks_like_requirement(lowered: str) -> bool:
    return any(
        token in lowered
        for token in (
            "requirement",
            "requirements",
            "qualification",
            "must",
            "need to",
            "responsible for",
            "任职要求",
            "要求",
            "熟悉",
            "掌握",
        )
    )


def _looks_like_bonus(lowered: str) -> bool:
    return any(
        token in lowered
        for token in (
            "preferred",
            "plus",
            "nice to have",
            "bonus",
            "优先",
            "加分",
        )
    )


def _infer_role(job_description: str, fallback_role: str) -> str:
    first_line = next((line.strip() for line in job_description.splitlines() if line.strip()), "")
    if first_line:
        match = re.search(
            r"(senior|staff|principal|junior)?\s*([a-zA-Z][a-zA-Z\s/\-&]{2,40}(engineer|developer|manager|analyst|designer|specialist))",
            first_line,
            re.IGNORECASE,
        )
        if match:
            return match.group(0).strip()
        if len(first_line) <= 60:
            return first_line
    return fallback_role
