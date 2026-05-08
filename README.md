# Resume Copilot

Resume Copilot is a vertical AI product focused on one core outcome: helping candidates improve interview conversion through better, job-targeted resumes.

## Core Product

The product keeps only one main business flow:

1. Intake a resume
2. Diagnose weak signals
3. Tailor against a target JD
4. Optimize content and layout
5. Score output quality
6. Export a submission-ready resume

## Main Commands

Generate a resume:

```bash
python main.py resume -r @data/sample_resume.json --jd data/sample_job.txt
```

Run product evaluation:

```bash
python main.py evaluate --dataset storage/benchmarks/resume_eval_set.json
```

## Directory Layout

The repo is now organized around a cleaner product structure:

- [resume_copilot](E:/pyWeb/ReAct_agent/resume_copilot): product package
- [resume_copilot/application](E:/pyWeb/ReAct_agent/resume_copilot/application): product orchestration services
- [resume_copilot/interfaces](E:/pyWeb/ReAct_agent/resume_copilot/interfaces): CLI and external entrypoints
- [resume_copilot/quality](E:/pyWeb/ReAct_agent/resume_copilot/quality): scoring, benchmark, and evaluation logic
- [apps/web](E:/pyWeb/ReAct_agent/apps/web): product frontend prototype
- [storage/benchmarks](E:/pyWeb/ReAct_agent/storage/benchmarks): benchmark datasets
- [storage/exports](E:/pyWeb/ReAct_agent/storage/exports): generated artifacts
- [scripts/dev](E:/pyWeb/ReAct_agent/scripts/dev): local product scripts
- [tests](E:/pyWeb/ReAct_agent/tests): product and regression tests

## Frontend

Serve the product frontend locally:

```bash
python scripts/dev/serve_frontend.py
```

The frontend includes:

- bilingual `English / 简体中文` switching
- globally oriented product positioning
- a studio prototype for market targeting and JD-aware previewing

## Evaluation

Resume Copilot now includes a product-quality benchmark layer:

- [storage/benchmarks/resume_eval_set.json](E:/pyWeb/ReAct_agent/storage/benchmarks/resume_eval_set.json): benchmark cases
- [resume_copilot/quality/metrics.py](E:/pyWeb/ReAct_agent/resume_copilot/quality/metrics.py): quality scoring
- [resume_copilot/quality/benchmark.py](E:/pyWeb/ReAct_agent/resume_copilot/quality/benchmark.py): benchmark runner

Current quality metrics include:

- JD match score
- quantified evidence score
- readability score
- ATS safety score
- keyword coverage score
- overall score

## Notes

The repo still contains some earlier infrastructure and agent modules, but the public product surface is intentionally narrowed to the resume flow and its evaluation path.
