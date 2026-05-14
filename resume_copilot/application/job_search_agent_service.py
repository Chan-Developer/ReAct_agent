# -*- coding: utf-8 -*-
"""Application service for the broader personal job-search agent."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .resume_product_service import ResumeProductService
from .resume_workbench_service import ResumeWorkbenchService
from .student_intake_service import StudentIntakeService
from resume_copilot.domain import (
    AgentWorkspace,
    ApplicationRecord,
    CareerTarget,
    InterviewPrepSession,
    MatchedOpportunity,
    OpportunityScoreReport,
    ResumeVersion,
    UserProfile,
)


class PersonalJobSearchService:
    """Product-facing service for a personal job-search agent workspace."""

    def __init__(
        self,
        llm=None,
        output_dir: str = "./storage/exports",
        workspace_path: str = "./storage/runtime/agent_workspace.json",
    ):
        self.resume_service = ResumeProductService(llm=llm, output_dir=output_dir)
        self.workbench_service = ResumeWorkbenchService()
        self.intake_service = StudentIntakeService()
        self.workspace_path = Path(workspace_path)
        self.workspace_path.parent.mkdir(parents=True, exist_ok=True)

    def get_workspace(self) -> AgentWorkspace:
        """Return the persisted single-user workspace."""
        if self.workspace_path.exists():
            payload = json.loads(self.workspace_path.read_text(encoding="utf-8"))
            return AgentWorkspace.from_dict(payload)

        workspace = self._build_default_workspace()
        self._save_workspace(workspace)
        return workspace

    def update_profile(self, payload: dict[str, Any]) -> dict[str, Any]:
        workspace = self.get_workspace()
        markets = self._split_list_field(payload.get("target_markets", []))
        strengths = self._split_list_field(payload.get("strengths", []))
        tone = str(payload.get("tone", workspace.profile.preferences.get("tone", "technical"))).strip()
        layout = str(
            payload.get(
                "layout_preference",
                workspace.profile.preferences.get("layout", "one-page first"),
            )
        ).strip()

        workspace.profile = UserProfile(
            full_name=str(payload.get("full_name", workspace.profile.full_name)).strip()
            or workspace.profile.full_name,
            target_title=str(payload.get("target_title", workspace.profile.target_title)).strip()
            or workspace.profile.target_title,
            target_markets=markets or workspace.profile.target_markets,
            strengths=strengths or workspace.profile.strengths,
            preferences={"tone": tone, "layout": layout},
            education=workspace.profile.education,
            major=workspace.profile.major,
            graduation_cycle=workspace.profile.graduation_cycle,
            raw_materials_summary=workspace.profile.raw_materials_summary,
        )
        self._prepend_memory(
            workspace,
            f"Profile updated for {workspace.profile.full_name}: targeting "
            f"{workspace.profile.target_title} in {', '.join(workspace.profile.target_markets) or 'selected markets'}.",
        )
        self._save_workspace(workspace)
        return self.get_dashboard_snapshot()

    def add_target(self, payload: dict[str, Any]) -> dict[str, Any]:
        workspace = self.get_workspace()
        target = CareerTarget(
            title=str(payload.get("title", "")).strip(),
            market=str(payload.get("market", "")).strip(),
            seniority=str(payload.get("seniority", "")).strip(),
            priorities=self._split_list_field(payload.get("priorities", [])),
        )
        if target.title:
            workspace.targets.insert(0, target)
            self._prepend_memory(
                workspace,
                f"New target added: {target.title} ({target.market}) with priorities "
                f"{', '.join(target.priorities[:3]) or 'not specified'}.",
            )
            self._save_workspace(workspace)
        return self.get_dashboard_snapshot()

    def add_resume_version(self, payload: dict[str, Any]) -> dict[str, Any]:
        workspace = self.get_workspace()
        version = ResumeVersion(
            label=str(payload.get("label", "")).strip(),
            status=str(payload.get("status", "Draft")).strip() or "Draft",
            focus=str(payload.get("focus", "")).strip(),
            market=str(payload.get("market", "Global")).strip() or "Global",
            role=str(payload.get("role", "")).strip(),
            source=str(payload.get("source", "manual")).strip(),
            output_path=str(payload.get("output_path", "")).strip(),
            resume_data=dict(payload.get("resume_data", {}) or {}),
        )
        if version.label:
            workspace.resume_versions.insert(0, version)
            self._prepend_memory(
                workspace,
                f"Resume version created: {version.label} focused on "
                f"{version.focus or 'general positioning'}.",
            )
            self._save_workspace(workspace)
        return self.get_dashboard_snapshot()

    def intake_raw_materials(self, payload: dict[str, Any]) -> dict[str, Any]:
        workspace = self.get_workspace()
        intake_payload = self.intake_service.build_intake_payload(
            raw_text=str(payload.get("raw_text", "")).strip(),
            target_title=str(payload.get("target_title", workspace.profile.target_title)).strip()
            or workspace.profile.target_title,
            target_markets=self._split_list_field(
                payload.get("target_markets", workspace.profile.target_markets)
            ),
            full_name=str(payload.get("full_name", workspace.profile.full_name)).strip()
            or workspace.profile.full_name,
            education=str(payload.get("education", workspace.profile.education)).strip(),
            major=str(payload.get("major", workspace.profile.major)).strip(),
            graduation_cycle=str(
                payload.get("graduation_cycle", workspace.profile.graduation_cycle)
            ).strip(),
        )
        profile_update = intake_payload["profile_update"]
        workspace.profile = UserProfile(
            full_name=profile_update["full_name"],
            target_title=profile_update["target_title"],
            target_markets=list(profile_update["target_markets"]),
            strengths=list(profile_update["strengths"]),
            preferences=workspace.profile.preferences,
            education=profile_update.get("education", ""),
            major=profile_update.get("major", ""),
            graduation_cycle=profile_update.get("graduation_cycle", ""),
            raw_materials_summary=profile_update.get("raw_materials_summary", ""),
        )
        workspace.resume_versions.insert(
            0,
            ResumeVersion(
                label="Raw intake master draft",
                status="Draft",
                focus="Structured from messy student materials",
                market=(
                    workspace.profile.target_markets[0]
                    if workspace.profile.target_markets
                    else "Global"
                ),
                role=workspace.profile.target_title,
                source="raw_intake",
                resume_data=intake_payload["resume_seed"],
            ),
        )
        self._prepend_memory(
            workspace,
            "Raw candidate materials were converted into a first structured resume draft.",
        )
        self._save_workspace(workspace)
        snapshot = self.get_dashboard_snapshot()
        snapshot["intake_payload"] = intake_payload
        return snapshot

    def create_resume_version_from_workbench(self, payload: dict[str, Any]) -> dict[str, Any]:
        workspace = self.get_workspace()
        workbench_payload = self.workbench_service.build_payload(
            resume_text=str(payload.get("resume", "")).strip(),
            job_description=str(payload.get("jd", "")).strip(),
            role=str(payload.get("role", workspace.profile.target_title)).strip()
            or workspace.profile.target_title,
            market=str(payload.get("market", "global")).strip() or "global",
            tone=str(payload.get("tone", "precise")).strip() or "precise",
            discipline=str(payload.get("discipline", "")).strip(),
            template_name=str(payload.get("template", "")).strip(),
        )
        report = workbench_payload["report"]
        generation_plan = workbench_payload["generation_plan"]
        label = str(payload.get("label", "")).strip() or (
            f"{workbench_payload['role']} {workbench_payload['market']} draft"
        )
        version = ResumeVersion(
            label=label,
            status="Generated",
            focus=report["recommendations"][0]
            if report["recommendations"]
            else generation_plan["summary_focus"],
            market=workbench_payload["market"],
            role=workbench_payload["role"],
            source="resume_lab",
            resume_data=workbench_payload["resume_seed"],
        )
        workspace.resume_versions.insert(0, version)

        generation_result = None
        if bool(payload.get("generate_document", False)):
            pipeline_result = self.resume_service.generate_resume(
                resume_data=workbench_payload["resume_seed"],
                job_description=str(payload.get("jd", "")).strip(),
                template_name=str(payload.get("template", "")).strip()
                or generation_plan["template_hint"],
                page_preference=generation_plan["page_preference"],
                output_format=str(payload.get("output_format", "docx")).strip() or "docx",
            )
            generation_result = {
                "success": pipeline_result.success,
                "output_path": pipeline_result.output.get("output_path", ""),
                "output_format": pipeline_result.output.get("output_format", ""),
                "suggestions": pipeline_result.suggestions[:5],
                "error": pipeline_result.error,
            }
            if pipeline_result.success:
                version.output_path = generation_result["output_path"]
                version.status = "Ready"

        self._prepend_memory(
            workspace,
            f"Resume Lab created version '{version.label}' for {version.role or workspace.profile.target_title}.",
        )
        self._save_workspace(workspace)
        snapshot = self.get_dashboard_snapshot()
        snapshot["workbench_payload"] = workbench_payload
        snapshot["created_resume_version"] = version.to_dict()
        snapshot["generation_result"] = generation_result
        return snapshot

    def add_application(self, payload: dict[str, Any]) -> dict[str, Any]:
        workspace = self.get_workspace()
        application = ApplicationRecord(
            company=str(payload.get("company", "")).strip(),
            role=str(payload.get("role", "")).strip(),
            stage=str(payload.get("stage", "Discovery")).strip() or "Discovery",
            next_step=str(payload.get("next_step", "")).strip(),
            source=str(payload.get("source", "")).strip(),
            resume_label=str(payload.get("resume_label", "")).strip(),
        )
        if application.company and application.role:
            workspace.applications.insert(0, application)
            workspace.interviews.insert(
                0,
                InterviewPrepSession(
                    topic=f"{application.company} interview prep",
                    status="Queued",
                    focus=f"Prepare stories and evidence for {application.role}.",
                ),
            )
            self._prepend_memory(
                workspace,
                f"Application tracked for {application.company} / {application.role}. "
                f"Next step: {application.next_step or 'follow up soon'}.",
            )
            self._save_workspace(workspace)
        return self.get_dashboard_snapshot()

    def import_opportunity(self, payload: dict[str, Any]) -> dict[str, Any]:
        workspace = self.get_workspace()
        opportunity = self._score_opportunity(workspace, payload)
        if opportunity.company and opportunity.title:
            workspace.opportunities.insert(0, opportunity)
            self._prepend_memory(
                workspace,
                f"Opportunity reviewed: {opportunity.company} / {opportunity.title} scored "
                f"{opportunity.fit_score:.0f}.",
            )
            self._save_workspace(workspace)
        return self.get_dashboard_snapshot()

    def import_opportunity_batch(self, payload: dict[str, Any]) -> dict[str, Any]:
        workspace = self.get_workspace()
        rows = payload.get("opportunities", [])
        imported: list[MatchedOpportunity] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            opportunity = self._score_opportunity(workspace, row)
            if opportunity.company and opportunity.title:
                imported.append(opportunity)

        if imported:
            workspace.opportunities = sorted(
                imported + workspace.opportunities,
                key=lambda item: item.fit_score,
                reverse=True,
            )[:30]
            self._prepend_memory(
                workspace,
                f"Batch opportunity import completed with {len(imported)} roles scored and ranked.",
            )
            self._save_workspace(workspace)

        snapshot = self.get_dashboard_snapshot()
        snapshot["batch_summary"] = {
            "imported_count": len(imported),
            "top_recommendations": [
                {"company": item.company, "title": item.title, "fit_score": item.fit_score}
                for item in workspace.opportunities[:5]
            ],
        }
        return snapshot

    def apply_from_opportunity(self, payload: dict[str, Any]) -> dict[str, Any]:
        workspace = self.get_workspace()
        company = str(payload.get("company", "")).strip()
        title = str(payload.get("title", "")).strip()

        for opportunity in workspace.opportunities:
            if opportunity.company != company or opportunity.title != title:
                continue

            opportunity.status = "tracked"
            workspace.applications.insert(
                0,
                ApplicationRecord(
                    company=opportunity.company,
                    role=opportunity.title,
                    stage="Planned",
                    next_step=opportunity.next_action or "Tailor resume and submit",
                    source=opportunity.source,
                    resume_label=opportunity.recommended_resume_version,
                ),
            )
            workspace.interviews.insert(
                0,
                InterviewPrepSession(
                    topic=f"{opportunity.company} interview prep",
                    status="Queued",
                    focus=f"Prepare stories tied to {opportunity.title} and its top match reasons.",
                ),
            )
            self._prepend_memory(
                workspace,
                f"Opportunity converted to application: {opportunity.company} / {opportunity.title}.",
            )
            self._save_workspace(workspace)
            break

        return self.get_dashboard_snapshot()

    def record_application_feedback(self, payload: dict[str, Any]) -> dict[str, Any]:
        workspace = self.get_workspace()
        company = str(payload.get("company", "")).strip()
        role = str(payload.get("role", "")).strip()
        result = str(payload.get("result", "")).strip() or "No response"
        feedback_notes = str(payload.get("feedback_notes", "")).strip()
        interview_count = int(payload.get("interview_count", 0) or 0)

        for application in workspace.applications:
            if application.company != company or application.role != role:
                continue
            application.result = result
            application.feedback_notes = feedback_notes
            application.interview_count = interview_count
            lowered = result.lower()
            if lowered in {"interview", "interviewing"}:
                application.stage = "Interviewing"
                application.next_step = "Prepare role-specific interview stories"
            elif lowered in {"rejected", "rejection"}:
                application.stage = "Closed"
                application.next_step = "Review weak signals and retarget the next applications"
            elif lowered == "offer":
                application.stage = "Offer"
                application.next_step = "Review final package and decision criteria"
            break

        feedback_summary = {
            "result": result,
            "recommended_actions": self._build_feedback_actions(result, feedback_notes),
        }
        self._prepend_memory(
            workspace,
            f"Application feedback recorded for {company} / {role}: {result}.",
        )
        self._save_workspace(workspace)
        snapshot = self.get_dashboard_snapshot()
        snapshot["feedback_summary"] = feedback_summary
        return snapshot

    def get_dashboard_snapshot(self) -> dict[str, Any]:
        workspace = self.get_workspace()
        payload = workspace.to_dict()
        payload["opportunities"] = [
            self._serialize_opportunity(item) for item in workspace.opportunities
        ]
        payload["north_star"] = (
            "Help one student turn messy campus experience into interviews through a repeatable resume-first job-search loop."
        )
        payload["positioning"] = {
            "audience": "Students entering the job market with scattered but under-packaged experience.",
            "wedge": "Resume Lab is the first wedge: diagnose, align to JD, generate, and learn from outcomes.",
            "promise": "Move from raw materials to tracked applications, interview prep, and reusable winning patterns.",
        }
        payload["modules"] = [
            {
                "name": "Student Profile Agent",
                "status": "active",
                "description": "Captures school, major, target roles, strengths, constraints, and writing preferences.",
            },
            {
                "name": "Resume Agent",
                "status": "active",
                "description": "Turns rough student materials into JD-aligned resume versions and export-ready files.",
            },
            {
                "name": "Targeting Agent",
                "status": "active" if workspace.targets else "next",
                "description": "Clarifies which roles deserve focus and what evidence each role needs.",
            },
            {
                "name": "Opportunity Agent",
                "status": "active" if workspace.opportunities else "next",
                "description": "Scores roles, flags weak signals, recommends a resume version, and avoids blind mass-apply.",
            },
            {
                "name": "Application Agent",
                "status": "active" if workspace.applications else "next",
                "description": "Keeps applications, resume variants, next actions, and outcomes in one execution queue.",
            },
            {
                "name": "Interview Agent",
                "status": "active" if workspace.interviews else "next",
                "description": "Converts the strongest resume evidence into project walkthroughs and interview stories.",
            },
        ]
        payload["journeys"] = [
            "Onboard a student from messy campus materials.",
            "Build a master resume and tailor it to a target JD.",
            "Score opportunities before spending energy on them.",
            "Convert high-fit opportunities into tracked applications.",
            "Use feedback and interviews to improve the next resume version.",
        ]
        return payload

    def _serialize_opportunity(self, opportunity: MatchedOpportunity) -> dict[str, Any]:
        payload = opportunity.to_dict()
        payload["score_report"] = OpportunityScoreReport(
            report_type="opportunity_score_report",
            company=opportunity.company,
            title=opportunity.title,
            market=opportunity.market,
            fit_score=opportunity.fit_score,
            matched_keywords=[],
            match_reasons=opportunity.match_reasons,
            missing_signals=opportunity.missing_signals,
            risk_flags=opportunity.risk_flags,
            recommended_resume_version=opportunity.recommended_resume_version,
            status=opportunity.status,
            next_action=opportunity.next_action,
            source=opportunity.source,
            location=opportunity.location,
            description=opportunity.description,
        ).to_dict()
        return payload

    def _build_feedback_actions(self, result: str, feedback_notes: str) -> list[str]:
        actions = []
        normalized = result.lower()
        if normalized in {"rejected", "rejection"}:
            actions.append(
                "Inspect the role-fit gaps and rewrite the weakest two bullets before the next similar application."
            )
            actions.append("Choose a tighter target list instead of broad reapplication.")
        elif normalized in {"interview", "interviewing"}:
            actions.append(
                "Generate role-specific interview preparation from the strongest matching project."
            )
            actions.append("Prepare one ownership story and one failure-recovery story.")
        elif normalized == "offer":
            actions.append(
                "Capture what worked in the final resume version and preserve it as a reusable winning pattern."
            )
        else:
            actions.append(
                "Follow up with a clearer application queue and keep monitoring role-fit patterns."
            )
        if feedback_notes:
            actions.append(f"Use this note as the next optimization clue: {feedback_notes}")
        return actions[:4]

    def _save_workspace(self, workspace: AgentWorkspace) -> None:
        self.workspace_path.write_text(
            json.dumps(workspace.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _build_default_workspace(self) -> AgentWorkspace:
        return AgentWorkspace(
            profile=UserProfile(
                full_name="Primary Candidate",
                target_title="Senior Backend Engineer",
                target_markets=["US", "UK", "Remote"],
                strengths=["Distributed systems", "Python backend", "Project packaging"],
                preferences={"tone": "technical", "layout": "one-page first"},
            ),
            targets=[
                CareerTarget(
                    title="Senior Backend Engineer",
                    market="US",
                    seniority="Senior IC",
                    priorities=["Scale", "Reliability", "Ownership"],
                ),
                CareerTarget(
                    title="Platform Engineer",
                    market="Remote",
                    seniority="Senior IC",
                    priorities=["Systems thinking", "Infra depth", "Async collaboration"],
                ),
            ],
            resume_versions=[
                ResumeVersion(
                    label="Core master resume",
                    status="Ready",
                    focus="General backend positioning",
                    market="Global",
                ),
                ResumeVersion(
                    label="JD-tailored version",
                    status="In progress",
                    focus="Python + distributed systems",
                    market="US",
                ),
            ],
            opportunities=[
                MatchedOpportunity(
                    company="Signal Stack",
                    title="Senior Backend Engineer",
                    market="US",
                    fit_score=89.0,
                    match_reasons=[
                        "Direct title alignment with the candidate's primary target.",
                        "Matches the candidate's preferred hiring market.",
                        "Overlaps with strengths and target priorities: python, reliability, ownership.",
                    ],
                    missing_signals=["Explicit mentoring depth"],
                    risk_flags=["Needs one stronger leadership bullet"],
                    recommended_resume_version="JD-tailored version",
                    status="recommended",
                    next_action="Use the JD-tailored version and add one stronger leadership example.",
                    source="Imported",
                    location="Remote / US",
                    description="Backend platform role focused on Python services, reliability, and systems scale.",
                )
            ],
            applications=[
                ApplicationRecord(
                    company="Atlas Cloud",
                    role="Senior Backend Engineer",
                    stage="Tailoring",
                    next_step="Finalize role-specific resume",
                    source="Referral",
                    resume_label="JD-tailored version",
                ),
                ApplicationRecord(
                    company="Northstar Labs",
                    role="Platform Engineer",
                    stage="Interview prep",
                    next_step="Prepare project deep-dive stories",
                    source="Inbound",
                    resume_label="Core master resume",
                ),
            ],
            interviews=[
                InterviewPrepSession(
                    topic="Project storytelling",
                    status="Queued",
                    focus="Turn strongest project into a 2-minute narrative",
                ),
                InterviewPrepSession(
                    topic="Behavioral answers",
                    status="Needs refresh",
                    focus="Rewrite STAR examples around ownership and mentorship",
                ),
            ],
            memory_notes=[
                "Prefer evidence-led writing over broad self-description.",
                "Keep US submissions to one page unless role scope clearly requires two.",
                "Lead with platform and distributed systems projects for backend roles.",
            ],
        )

    def _prepend_memory(self, workspace: AgentWorkspace, note: str) -> None:
        workspace.memory_notes.insert(0, note)
        workspace.memory_notes = workspace.memory_notes[:10]

    def _split_list_field(self, value: Any) -> list[str]:
        if isinstance(value, list):
            items = value
        else:
            items = str(value).replace(";", ",").split(",")
        return [str(item).strip() for item in items if str(item).strip()]

    def _score_opportunity(
        self,
        workspace: AgentWorkspace,
        payload: dict[str, Any],
    ) -> MatchedOpportunity:
        company = str(payload.get("company", "")).strip()
        title = str(payload.get("title", "")).strip()
        market = str(payload.get("market", "")).strip() or "Global"
        location = str(payload.get("location", "")).strip()
        source = str(payload.get("source", "Manual import")).strip()
        description = str(payload.get("description", "")).strip()
        lowered = f"{title} {description} {location} {market}".lower()

        keyword_pool = (
            workspace.profile.strengths
            + [workspace.profile.target_title]
            + [target.title for target in workspace.targets]
            + [priority for target in workspace.targets for priority in target.priorities]
        )
        keywords = {token.lower() for token in keyword_pool if token}
        matched_keywords = sorted({kw for kw in keywords if kw in lowered})

        score = 35 + len(matched_keywords) * 8
        preferred_markets = {item.upper() for item in workspace.profile.target_markets}
        if market.upper() in preferred_markets:
            score += 15
        if workspace.profile.target_title.lower() in title.lower():
            score += 18
        if re.search(r"python|backend|platform|distributed|reliability|api|infra", lowered):
            score += 12
        fit_score = float(max(18, min(98, score)))

        match_reasons: list[str] = []
        if workspace.profile.target_title.lower() in title.lower():
            match_reasons.append("Direct title alignment with the candidate's primary target.")
        if market.upper() in preferred_markets:
            match_reasons.append("Matches the candidate's preferred hiring market.")
        if matched_keywords:
            match_reasons.append(
                "Overlaps with strengths and target priorities: "
                + ", ".join(matched_keywords[:3])
                + "."
            )
        if not match_reasons:
            match_reasons.append("General adjacency to the current target profile.")

        missing_signals = [
            signal
            for signal in ("leadership", "mentor", "architecture", "ownership")
            if signal in lowered and signal not in keywords
        ]

        risk_flags: list[str] = []
        if fit_score < 60:
            risk_flags.append("Role fit is moderate; review before applying.")
        if not workspace.resume_versions:
            risk_flags.append("No saved resume versions available yet.")
        if not location:
            risk_flags.append("Location details are incomplete.")

        recommended_resume = self._pick_resume_version(workspace, title, description, market)
        next_action = (
            f"Use {recommended_resume or 'the best matching resume'} and tailor project bullets for {title}."
        )

        status = "recommended" if fit_score >= 65 else "review"

        return MatchedOpportunity(
            company=company,
            title=title,
            market=market,
            fit_score=fit_score,
            match_reasons=match_reasons,
            missing_signals=missing_signals[:3],
            risk_flags=risk_flags[:3],
            recommended_resume_version=recommended_resume,
            status=status,
            next_action=next_action,
            source=source,
            location=location,
            description=description,
        )

    def _pick_resume_version(
        self,
        workspace: AgentWorkspace,
        title: str,
        description: str,
        market: str,
    ) -> str:
        if not workspace.resume_versions:
            return ""

        search_text = f"{title} {description} {market}".lower()
        best_label = workspace.resume_versions[0].label
        best_score = -1
        for version in workspace.resume_versions:
            version_score = 0
            if version.market and version.market.lower() in search_text:
                version_score += 2
            focus_tokens = [token for token in version.focus.lower().split() if token]
            if any(token in search_text for token in focus_tokens):
                version_score += 3
            if version.status.lower() == "ready":
                version_score += 2
            if version_score > best_score:
                best_score = version_score
                best_label = version.label
        return best_label
