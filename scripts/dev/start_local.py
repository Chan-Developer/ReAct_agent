#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Single-machine startup for Resume Copilot."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from resume_copilot.interfaces.http_server import run_server


def main() -> None:
    parser = argparse.ArgumentParser(description="Start Resume Copilot locally")
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
