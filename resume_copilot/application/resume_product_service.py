# -*- coding: utf-8 -*-
"""Product application service for Resume Copilot."""

from __future__ import annotations

from typing import Any

from workflows import ResumePipeline

from resume_copilot.quality import ResumeBenchmarkRunner, score_resume_against_jd


class ResumeProductService:
    """Single product service around the core resume pipeline."""

    def __init__(self, llm=None, output_dir: str = "./storage/exports"):
        self.llm = llm
        self.output_dir = output_dir

    def generate_resume(
        self,
        resume_data: dict[str, Any],
        job_description: str = "",
        template_name: str = "",
        page_preference: str = "auto",
    ):
        pipeline = ResumePipeline(llm=self.llm, output_dir=self.output_dir)
        return pipeline.run(
            input_data=resume_data,
            job_description=job_description,
            template_name=template_name,
            page_preference=page_preference,
            output_dir=self.output_dir,
        )

    def evaluate_resume(self, resume_data: dict[str, Any], job_description: str):
        return score_resume_against_jd(resume_data, job_description)

    def run_benchmark(self, dataset_path: str = "storage/benchmarks/resume_eval_set.json"):
        runner = ResumeBenchmarkRunner()
        return runner.run(dataset_path)
