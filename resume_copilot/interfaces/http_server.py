# -*- coding: utf-8 -*-
"""Lightweight product web server for local and container startup."""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
from functools import partial
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from resume_copilot.application import (
    PersonalJobSearchService,
    ResumeProductService,
    ResumeWorkbenchService,
)
from resume_copilot.application.reporting import build_resume_diagnosis_report

WEB_ROOT = Path(__file__).resolve().parents[2] / "apps" / "web"
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _build_preview_payload(payload: dict[str, Any]) -> dict[str, Any]:
    resume_text = str(payload.get("resume", "")).strip()
    job_description = str(payload.get("jd", "")).strip()
    role = str(payload.get("role", "Target Role")).strip() or "Target Role"
    market = str(payload.get("market", "global")).strip() or "global"
    tone = str(payload.get("tone", "precise")).strip() or "precise"

    resume_data = {
        "name": "Candidate",
        "summary": resume_text[:800],
        "experience": [
            {
                "company": "Current Experience",
                "position": role,
                "description": resume_text[:1200],
                "highlights": [line.strip("- ").strip() for line in resume_text.splitlines() if line.strip()][:4],
            }
        ]
        if resume_text
        else [],
        "skills": _extract_tokens(resume_text)[:12],
    }

    report = build_resume_diagnosis_report(
        resume_data,
        job_description,
        role=role,
        market=market,
    ).to_dict()

    return {
        "role": role,
        "market": market,
        "tone": tone,
        "jd_analysis": report["jd_analysis"],
        "metrics": report["metrics"],
        "diagnosis": report["diagnosis"],
        "recommendations": report["recommendations"],
    }


def _extract_tokens(text: str) -> list[str]:
    seen: list[str] = []
    for raw in text.replace("/", " ").replace(",", " ").split():
        token = raw.strip().strip(".:;()[]{}")
        if len(token) < 3:
            continue
        if token.lower() in {item.lower() for item in seen}:
            continue
        seen.append(token)
    return seen


class ResumeCopilotHandler(SimpleHTTPRequestHandler):
    """Serve static product pages and a small JSON API."""

    server_version = "ResumeCopilotHTTP/0.1"

    def __init__(
        self,
        *args,
        service: ResumeProductService,
        workspace_service: PersonalJobSearchService,
        workbench_service: ResumeWorkbenchService,
        **kwargs,
    ):
        self.service = service
        self.workspace_service = workspace_service
        self.workbench_service = workbench_service
        super().__init__(*args, directory=str(WEB_ROOT), **kwargs)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)

        if parsed.path in {"/health", "/api/health"}:
            self._write_json(
                {
                    "status": "ok",
                    "product": "resume-copilot",
                    "frontend": "/",
                    "api": [
                        "/api/health",
                        "/api/dashboard",
                        "/api/product-structure",
                        "/api/intake/raw",
                        "/api/resume-workbench/save",
                        "/api/download",
                        "/api/opportunities",
                        "/api/opportunities/batch",
                        "/api/applications/feedback",
                        "/api/resume-workbench",
                        "/api/studio-preview",
                        "/api/evaluate",
                    ],
                }
            )
            return

        if parsed.path == "/api/dashboard":
            self._write_json(self.workspace_service.get_dashboard_snapshot())
            return

        if parsed.path == "/api/product-structure":
            snapshot = self.workspace_service.get_dashboard_snapshot()
            self._write_json(
                {
                    "north_star": snapshot["north_star"],
                    "modules": snapshot["modules"],
                    "journeys": snapshot["journeys"],
                }
            )
            return

        if parsed.path == "/api/download":
            self._send_generated_file(parsed)
            return

        if parsed.path == "/api/benchmark":
            summary = self.service.run_benchmark("storage/benchmarks/resume_eval_set.json")
            self._write_json(summary)
            return
            return

        if parsed.path == "/":
            self.path = "/index.html"

        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        payload = self._read_json_body()
        if payload is None:
            return

        if parsed.path == "/api/studio-preview":
            self._write_json(_build_preview_payload(payload))
            return

        if parsed.path == "/api/resume-workbench":
            resume_text = str(payload.get("resume", "")).strip()
            job_description = str(payload.get("jd", "")).strip()
            role = str(payload.get("role", "Target Role")).strip() or "Target Role"
            market = str(payload.get("market", "global")).strip() or "global"
            tone = str(payload.get("tone", "precise")).strip() or "precise"
            discipline = str(payload.get("discipline", "")).strip()
            template_name = str(payload.get("template", "")).strip()
            self._write_json(
                self.workbench_service.build_payload(
                    resume_text=resume_text,
                    job_description=job_description,
                    role=role,
                    market=market,
                    tone=tone,
                    discipline=discipline,
                    template_name=template_name,
                )
            )
            return

        if parsed.path == "/api/evaluate":
            resume_data = payload.get("resume_data") or {}
            job_description = str(payload.get("job_description", ""))
            role = str(payload.get("role", "Target Role")).strip() or "Target Role"
            market = str(payload.get("market", "global")).strip() or "global"
            result = self.service.evaluate_resume(
                resume_data,
                job_description,
                role=role,
                market=market,
            )
            self._write_json(result.to_dict())
            return

        if parsed.path == "/api/profile":
            self._write_json(self.workspace_service.update_profile(payload))
            return

        if parsed.path == "/api/intake/raw":
            self._write_json(self.workspace_service.intake_raw_materials(payload))
            return

        if parsed.path == "/api/targets":
            self._write_json(self.workspace_service.add_target(payload))
            return

        if parsed.path == "/api/resume-versions":
            self._write_json(self.workspace_service.add_resume_version(payload))
            return

        if parsed.path == "/api/applications":
            self._write_json(self.workspace_service.add_application(payload))
            return

        if parsed.path == "/api/applications/feedback":
            self._write_json(self.workspace_service.record_application_feedback(payload))
            return

        if parsed.path == "/api/opportunities":
            self._write_json(self.workspace_service.import_opportunity(payload))
            return

        if parsed.path == "/api/opportunities/batch":
            self._write_json(self.workspace_service.import_opportunity_batch(payload))
            return

        if parsed.path == "/api/opportunities/apply":
            self._write_json(self.workspace_service.apply_from_opportunity(payload))
            return

        if parsed.path == "/api/resume-workbench/save":
            self._write_json(self.workspace_service.create_resume_version_from_workbench(payload))
            return

        self._write_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)

    def _read_json_body(self) -> dict[str, Any] | None:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._write_json({"error": "Invalid Content-Length"}, status=HTTPStatus.BAD_REQUEST)
            return None

        try:
            raw = self.rfile.read(length).decode("utf-8") if length else "{}"
            return json.loads(raw or "{}")
        except json.JSONDecodeError:
            self._write_json({"error": "Invalid JSON body"}, status=HTTPStatus.BAD_REQUEST)
            return None

    def _write_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status.value)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _send_generated_file(self, parsed) -> None:
        query = parse_qs(parsed.query)
        raw_path = (query.get("path") or [""])[0]
        if not raw_path:
            self._write_json({"error": "Missing path"}, status=HTTPStatus.BAD_REQUEST)
            return

        requested = Path(raw_path)
        if not requested.is_absolute():
            requested = PROJECT_ROOT / requested
        try:
            resolved = requested.resolve()
            exports_root = (PROJECT_ROOT / "storage" / "exports").resolve()
            resolved.relative_to(exports_root)
        except (OSError, ValueError):
            self._write_json({"error": "Invalid download path"}, status=HTTPStatus.BAD_REQUEST)
            return

        if not resolved.exists() or not resolved.is_file():
            self._write_json({"error": "File not found"}, status=HTTPStatus.NOT_FOUND)
            return

        content_type = mimetypes.guess_type(resolved.name)[0] or "application/octet-stream"
        data = resolved.read_bytes()
        self.send_response(HTTPStatus.OK.value)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Content-Disposition", f'attachment; filename="{resolved.name}"')
        self.end_headers()
        self.wfile.write(data)


def run_server(
    host: str = "127.0.0.1",
    port: int = 8000,
    output_dir: str = "./storage/exports",
    workspace_path: str = "./storage/runtime/agent_workspace.json",
) -> None:
    service = ResumeProductService(output_dir=output_dir)
    workspace_service = PersonalJobSearchService(
        output_dir=output_dir,
        workspace_path=workspace_path,
    )
    workbench_service = ResumeWorkbenchService()
    handler = partial(
        ResumeCopilotHandler,
        service=service,
        workspace_service=workspace_service,
        workbench_service=workbench_service,
    )
    server = ThreadingHTTPServer((host, port), handler)
    print(f"Resume Copilot running at http://{host}:{port}")
    print("Health check available at /health")
    print(f"Output dir: {output_dir}")
    print(f"Workspace path: {workspace_path}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down Resume Copilot...")
    finally:
        server.server_close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Resume Copilot web product server")
    parser.add_argument("--host", default=os.getenv("RESUME_COPILOT_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "8000")))
    parser.add_argument(
        "--output-dir",
        default=os.getenv("RESUME_COPILOT_OUTPUT_DIR", "./storage/exports"),
    )
    parser.add_argument(
        "--workspace-path",
        default=os.getenv(
            "RESUME_COPILOT_WORKSPACE_PATH",
            "./storage/runtime/agent_workspace.json",
        ),
    )
    args = parser.parse_args()
    run_server(
        host=args.host,
        port=args.port,
        output_dir=args.output_dir,
        workspace_path=args.workspace_path,
    )


if __name__ == "__main__":
    main()
