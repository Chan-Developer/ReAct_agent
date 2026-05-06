#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Manual smoke test for resume generation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from llm import ModelScopeOpenAI
from tools.generators import ResumeGenerator


def main() -> None:
    resume_data = {
        "name": "Test User",
        "phone": "138-1234-5678",
        "email": "test@example.com",
        "location": "Chengdu",
        "github": "github.com/example",
        "education": [
            {
                "school": "UESTC",
                "degree": "Master",
                "major": "Electronic Information",
                "start_date": "2024.09",
                "end_date": "2027.06",
                "gpa": "3.8/4.0",
            }
        ],
        "skills": ["Python", "PyTorch", "Machine Learning", "Deep Learning", "C++", "Linux"],
        "skill_levels": [
            {"name": "Python", "level": 90},
            {"name": "PyTorch", "level": 85},
            {"name": "Machine Learning", "level": 80},
            {"name": "C++", "level": 70},
        ],
        "projects": [
            {
                "name": "Speech Recognition System",
                "role": "Core Developer",
                "start_date": "2024.10",
                "end_date": "2025.01",
                "description": "End-to-end speech recognition system based on Transformer.",
                "highlights": [
                    "Reached 95 percent accuracy on the test set with a Conformer model.",
                    "Reduced single-audio inference time by 40 percent.",
                ],
                "tech_stack": ["Python", "PyTorch", "Whisper", "ONNX"],
            }
        ],
        "certificates": ["CET-6", "National Computer Rank Exam Level 2"],
        "awards": ["Graduate Scholarship First Prize", "Math Modeling Provincial Second Prize"],
    }

    print("=" * 60)
    print("Resume generator smoke test")
    print("=" * 60)

    try:
        generator = ResumeGenerator(
            output_dir="./output",
            llm=ModelScopeOpenAI(),
            auto_optimize=True,
        )
        result = generator.execute(
            resume_data=json.dumps(resume_data, ensure_ascii=False),
            filename="test_resume_word",
            template_style="modern",
        )
        print(result)
    except ValueError as exc:
        print(f"LLM not configured: {exc}")
        print("Hint: set MODELSCOPE_API_KEY or edit configs/config.yaml")

    print("=" * 60)
    print("Smoke test finished")
    print("=" * 60)


if __name__ == "__main__":
    main()
