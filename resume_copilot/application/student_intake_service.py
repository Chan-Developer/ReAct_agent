# -*- coding: utf-8 -*-
"""Raw material intake and campus-signal packaging helpers."""

from __future__ import annotations

from typing import Any


class StudentIntakeService:
    """Turn messy student materials into a first structured candidate draft."""

    def build_intake_payload(
        self,
        *,
        raw_text: str,
        target_title: str = "Target Role",
        target_markets: list[str] | None = None,
        full_name: str = "Candidate",
        education: str = "",
        major: str = "",
        graduation_cycle: str = "",
    ) -> dict[str, Any]:
        lines = [line.strip(" -*\t") for line in raw_text.splitlines() if line.strip()]
        highlights = self._extract_highlights(lines)
        packaged_signals = self._package_student_signals(lines)
        strengths = self._infer_strengths(lines, packaged_signals)
        resume_seed = {
            "name": full_name,
            "summary": self._build_summary(target_title, strengths, packaged_signals),
            "experience": self._build_experience_entries(packaged_signals),
            "projects": self._build_project_entries(packaged_signals),
            "skills": strengths[:8],
            "education": [
                {
                    "school": education,
                    "major": major,
                    "end_date": graduation_cycle,
                }
            ]
            if education or major or graduation_cycle
            else [],
        }
        return {
            "type": "student_intake_payload",
            "profile_update": {
                "full_name": full_name,
                "target_title": target_title,
                "target_markets": target_markets or ["Global"],
                "strengths": strengths[:6],
                "education": education,
                "major": major,
                "graduation_cycle": graduation_cycle,
                "raw_materials_summary": " | ".join(highlights[:5]),
            },
            "resume_seed": resume_seed,
            "packaged_signals": packaged_signals,
            "highlight_lines": highlights[:8],
            "next_actions": [
                "Review the packaged campus signals and delete anything untrue or too weak.",
                "Select the strongest two projects or activities for the first tailored version.",
                f"Run Resume Lab against a target {target_title} JD before generating the final version.",
            ],
        }

    def _extract_highlights(self, lines: list[str]) -> list[str]:
        return lines if lines else []

    def _infer_strengths(
        self,
        lines: list[str],
        packaged_signals: list[dict[str, str]],
    ) -> list[str]:
        text = " ".join(lines).lower()
        strengths: list[str] = []
        keyword_map = [
            ("python", "Python"),
            ("java", "Java"),
            ("backend", "Backend development"),
            ("api", "API design"),
            ("data", "Data analysis"),
            ("research", "Research"),
            ("product", "Product thinking"),
            ("operations", "Operations execution"),
            ("algorithm", "Algorithm practice"),
            ("machine learning", "Machine learning"),
        ]
        for token, label in keyword_map:
            if token in text and label not in strengths:
                strengths.append(label)

        for signal in packaged_signals:
            label = signal.get("signal", "")
            if label and label not in strengths:
                strengths.append(label)
        if not strengths:
            strengths = ["Structured problem solving", "Execution", "Project delivery"]
        return strengths

    def _package_student_signals(self, lines: list[str]) -> list[dict[str, str]]:
        packaged: list[dict[str, str]] = []
        for line in lines[:12]:
            lowered = line.lower()
            if any(token in lowered for token in ("competition", "contest", "hackathon")):
                packaged.append(
                    {
                        "source": line,
                        "signal": "Competitive execution",
                        "packaged": "Translate the competition into a delivery story with constraints, ranking, and measurable outcome.",
                        "bucket": "competition",
                    }
                )
            elif any(token in lowered for token in ("course", "curriculum", "project", "capstone")):
                packaged.append(
                    {
                        "source": line,
                        "signal": "Project implementation",
                        "packaged": "Promote the course or side project into a product or system delivery narrative with stack and result.",
                        "bucket": "project",
                    }
                )
            elif any(
                token in lowered
                for token in ("club", "society", "student union", "association", "community")
            ):
                packaged.append(
                    {
                        "source": line,
                        "signal": "Leadership and coordination",
                        "packaged": "Frame the activity as coordination, ownership, and event execution rather than participation.",
                        "bucket": "leadership",
                    }
                )
            elif any(token in lowered for token in ("research", "lab", "paper", "thesis")):
                packaged.append(
                    {
                        "source": line,
                        "signal": "Research and analysis",
                        "packaged": "Convert research work into problem framing, method, and result-oriented evidence.",
                        "bucket": "research",
                    }
                )
        return packaged[:8]

    def _build_summary(
        self,
        target_title: str,
        strengths: list[str],
        packaged_signals: list[dict[str, str]],
    ) -> str:
        signal_text = ", ".join(strengths[:3]) or "execution"
        proof_text = (
            " with experience across projects, campus activities, and early delivery work"
            if packaged_signals
            else ""
        )
        return f"Early-career candidate targeting {target_title}, strongest in {signal_text}{proof_text}."

    def _build_experience_entries(self, packaged_signals: list[dict[str, str]]) -> list[dict[str, Any]]:
        experience: list[dict[str, Any]] = []
        for signal in packaged_signals:
            if signal["bucket"] not in {"leadership", "research"}:
                continue
            experience.append(
                {
                    "company": "Campus Experience",
                    "position": signal["signal"],
                    "description": signal["source"],
                    "highlights": [signal["packaged"]],
                }
            )
        return experience[:3]

    def _build_project_entries(self, packaged_signals: list[dict[str, str]]) -> list[dict[str, Any]]:
        projects: list[dict[str, Any]] = []
        for signal in packaged_signals:
            if signal["bucket"] not in {"project", "competition", "research"}:
                continue
            projects.append(
                {
                    "name": signal["signal"],
                    "role": "Primary contributor",
                    "description": signal["source"],
                    "highlights": [signal["packaged"]],
                    "tech_stack": self._extract_stack(signal["source"]),
                }
            )
        return projects[:4]

    def _extract_stack(self, text: str) -> list[str]:
        found: list[str] = []
        for token in ("Python", "Java", "C++", "SQL", "Redis", "Vue", "React", "TensorFlow"):
            if token.lower() in text.lower():
                found.append(token)
        return found
