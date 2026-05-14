# -*- coding: utf-8 -*-
"""Sanity checks for the product-facing frontend."""

from pathlib import Path


def test_frontend_files_exist():
    root = Path(__file__).resolve().parents[1]
    assert (root / "apps" / "web" / "index.html").exists()
    assert (root / "apps" / "web" / "styles.css").exists()
    assert (root / "apps" / "web" / "app.js").exists()


def test_frontend_mentions_resume_copilot():
    root = Path(__file__).resolve().parents[1]
    html = (root / "apps" / "web" / "index.html").read_text(encoding="utf-8")
    js = (root / "apps" / "web" / "app.js").read_text(encoding="utf-8")

    assert "Resume Copilot" in html
    assert "Resume Lab" in html
    assert "resumeWorkbenchForm" in html
    assert "saveWorkbenchVersionButton" in html
    assert "generateWorkbenchDocumentButton" in html
    assert "rawIntakeForm" in html
    assert "applicationFeedbackForm" in html
    assert "batchOpportunityButton" in html
    assert "profileForm" in html
    assert "opportunityForm" in html
    assert "opportunityBoard" in html
    assert 'data-page="home"' in html
    assert 'data-page="quest"' in html
    assert 'data-page="workspace"' in html
    assert 'data-page="opportunities"' in html
    assert 'data-route="quest"' in html
    assert "questDisciplineSelect" in html
    assert "AI Optimization" in html
    assert "templateSelect" in html
    assert "Generation Plan" in html
    assert "Generation Result" in html
    assert "zh-CN" in js
    assert "Student job-search execution system" in js
    assert "loadDashboard" in js
    assert "/api/resume-workbench" in js
    assert "/api/resume-workbench/save" in js
    assert "/api/intake/raw" in js
    assert "/api/profile" in js
    assert "/api/applications" in js
    assert "/api/applications/feedback" in js
    assert "/api/opportunities" in js
    assert "/api/opportunities/batch" in js
    assert "/api/opportunities/apply" in js
    assert "renderGenerationResult" in js
    assert "setActivePage" in js
    assert "routeFromHash" in js


def test_local_frontend_server_script_exists():
    root = Path(__file__).resolve().parents[1]
    script = root / "scripts" / "dev" / "serve_frontend.py"
    content = script.read_text(encoding="utf-8")

    assert script.exists()
    assert "http.server" in content
