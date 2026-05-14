# -*- coding: utf-8 -*-
"""Checks for local and Docker startup entrypoints."""

from __future__ import annotations

from pathlib import Path


def test_local_start_script_exists():
    root = Path(__file__).resolve().parents[1]
    script = root / "scripts" / "dev" / "start_local.py"
    content = script.read_text(encoding="utf-8")

    assert script.exists()
    assert "run_server" in content
    assert "--output-dir" in content
    assert "--workspace-path" in content


def test_docker_startup_files_exist():
    root = Path(__file__).resolve().parents[1]
    dockerfile = root / "Dockerfile"
    compose = root / "docker-compose.yml"

    docker_content = dockerfile.read_text(encoding="utf-8")
    compose_content = compose.read_text(encoding="utf-8")

    assert dockerfile.exists()
    assert compose.exists()
    assert "resume_copilot.interfaces.http_server" in docker_content
    assert "app:" in compose_content
    assert "redis:" in compose_content
    assert "profiles: [\"memory\"]" in compose_content


def test_http_server_exposes_product_routes():
    root = Path(__file__).resolve().parents[1]
    server = root / "resume_copilot" / "interfaces" / "http_server.py"
    content = server.read_text(encoding="utf-8")

    assert "/api/dashboard" in content
    assert "/api/product-structure" in content
    assert "/api/profile" in content
    assert "/api/intake/raw" in content
    assert "/api/targets" in content
    assert "/api/resume-versions" in content
    assert "/api/applications" in content
    assert "/api/applications/feedback" in content
    assert "/api/opportunities/batch" in content
    assert "/api/resume-workbench" in content
    assert "/api/resume-workbench/save" in content
    assert "/api/studio-preview" in content
    assert "/api/evaluate" in content
    assert "/health" in content
    assert "--workspace-path" in content
