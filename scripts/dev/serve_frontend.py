#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Serve the Resume Copilot frontend locally."""

from __future__ import annotations

import http.server
import socketserver
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[2] / "apps" / "web"
    port = 4173
    handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(  # noqa: E731
        *args,
        directory=str(root),
        **kwargs,
    )

    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Resume Copilot frontend available at http://127.0.0.1:{port}")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
