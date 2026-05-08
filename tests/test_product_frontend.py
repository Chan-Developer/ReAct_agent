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
    assert "Product studio" in html
    assert "zh-CN" in js
    assert "Global resume intelligence" in js


def test_local_frontend_server_script_exists():
    root = Path(__file__).resolve().parents[1]
    script = root / "scripts" / "dev" / "serve_frontend.py"
    content = script.read_text(encoding="utf-8")

    assert script.exists()
    assert "http.server" in content
