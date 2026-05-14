# Resume Copilot

Resume Copilot is not trying to be another generic chatbot.

It is being shaped into a job-search operating system for one real candidate:
start from a rough resume, wire it to a target JD, expose the gaps, generate a stronger version, track opportunities, and keep the whole search loop in one workspace.

## Why This Project Exists

Most students do not fail because they have zero ability.
They fail because their signal is weak:

- their resume does not match the JD
- their strongest project is buried
- their bullets are vague
- they do not know which jobs are worth applying to
- they do not build a repeatable search workflow

Resume Copilot is built to fix that.

## The Product Direction

The current product direction is:

1. Resume diagnosis
2. JD-aware tailoring
3. Resume generation
4. Opportunity scoring
5. Application tracking
6. Interview-prep expansion

The public surface is intentionally narrow:
resume first, then full job-search execution.

## Where The Product Really Stands

Resume Copilot is no longer just an experiment, but it is not yet a full business-ready job-search system either.

The most honest current assessment is:

- strong product prototype
- early practical tool
- incomplete business loop

What is already real:

- Resume Lab for diagnosis and JD-aware workbench interaction
- resume generation pipeline
- opportunity scoring
- application workspace

What is still missing:

- onboarding from messy raw student materials
- stronger campus-oriented experience packaging
- batch job prioritization
- feedback loop from application results and interviews

For the detailed gap breakdown, see:

- [Business Gap Checklist](/E:/pyWeb/ReAct_agent/docs/plans/business_gap_checklist.md)
- [Student Employment Execution Plan](/E:/pyWeb/ReAct_agent/docs/plans/student_employment_execution_plan.md)

## What Makes It Interesting

- `Resume Lab`: a more hacker-style workbench for running the resume workflow
- structured product reports instead of loose prompt output
- canonical resume schema across scoring, curation, layout, and export
- workspace model for one candidate instead of a vague “chat session”
- simple local startup path and Docker startup path

## Current Experience

### Resume Lab

The new `Resume Lab` is the main product interaction layer.
Instead of only showing a form, it returns:

- diagnosis
- signal matrix
- matched and missing keywords
- rewrite candidates
- next-step queue
- generation plan for the next resume version

### Candidate Workspace

The workspace keeps:

- profile
- target roles
- resume versions
- opportunities
- applications
- interview-prep queue
- memory notes

### Output Layer

The system can already:

- analyze a resume against a JD
- rank projects for job fit
- recommend a template hint
- optimize for one-page output
- export a `.docx` resume

## What Still Needs To Happen

To become a real business-facing product for students, the next major jumps are:

1. accept messy raw input, not just structured resume data
2. move from Resume Lab directly into generated resume versions
3. help users choose which jobs to apply to first
4. close the loop with interview and application feedback

That is the difference between a smart analyzer and a true job-search execution system.

## Quick Start

### Local startup

```bash
pip install .[docs]
python scripts/dev/start_local.py
```

Then open:

```text
http://127.0.0.1:8000
```

### Docker startup

```bash
docker compose up --build
```

Then open:

```text
http://127.0.0.1:8000
```

### Docker startup with memory stack

```bash
docker compose --profile memory up --build
```

## Main Commands

### Generate a resume

```bash
python main.py resume -r @data/sample_resume.json --jd data/sample_job.txt
```

### Evaluate a resume against a JD

```bash
python main.py evaluate -r @data/sample_resume.json --jd data/sample_job.txt
```

### Run the Resume Lab payload from CLI

```bash
python main.py workbench --resume-text data/sample_resume.txt --jd data/sample_job.txt --role "Backend Engineer" --market us --tone technical
```

## Product Structure

The codebase is being pulled toward a cleaner product architecture:

- [resume_copilot](/E:/pyWeb/ReAct_agent/resume_copilot): product package
- [resume_copilot/application](/E:/pyWeb/ReAct_agent/resume_copilot/application): product services and workbench/report orchestration
- [resume_copilot/domain](/E:/pyWeb/ReAct_agent/resume_copilot/domain): canonical domain models and product reports
- [resume_copilot/interfaces](/E:/pyWeb/ReAct_agent/resume_copilot/interfaces): CLI and HTTP entrypoints
- [resume_copilot/quality](/E:/pyWeb/ReAct_agent/resume_copilot/quality): scoring and benchmark logic
- [workflows](/E:/pyWeb/ReAct_agent/workflows): resume generation workflow
- [tools/generators](/E:/pyWeb/ReAct_agent/tools/generators): export and pagination layer
- [apps/web](/E:/pyWeb/ReAct_agent/apps/web): product frontend
- [tests](/E:/pyWeb/ReAct_agent/tests): regression and product tests

## Development Priorities

What we are optimizing for now:

- make the resume workflow tighter
- make the product interaction simpler and more distinctive
- make the core schema and service boundaries stable
- make local and deploy flows less fragile

What the product is still chasing:

- better student onboarding
- stronger execution after diagnosis
- tighter business loop from resume to offer

What we are not optimizing for now:

- generic multi-agent theater
- broad “AI platform” positioning
- overbuilt infra before the product loop is sharp

## Quality Layer

Resume Copilot includes a product-quality benchmark layer:

- [storage/benchmarks/resume_eval_set.json](/E:/pyWeb/ReAct_agent/storage/benchmarks/resume_eval_set.json)
- [resume_copilot/quality/metrics.py](/E:/pyWeb/ReAct_agent/resume_copilot/quality/metrics.py)
- [resume_copilot/quality/benchmark.py](/E:/pyWeb/ReAct_agent/resume_copilot/quality/benchmark.py)

Current scoring dimensions include:

- JD match score
- quantified evidence score
- readability score
- ATS safety score
- keyword coverage score
- overall score

## Current Reality

This repo is still in transition.
Some older agent infrastructure is still present.

But the product direction is now much clearer:

`Resume Lab -> resume generation -> opportunity scoring -> application workflow`

That is the lane.

## Vision

The long game is bigger than resume polishing.

The goal is to help a student move from:

- “I do not know how to package myself”

to:

- “I know what to target, how to present it, what to apply to next, and how to improve after each loop”

If that works for one real user, the product has a future.

If it works for many students with messy starting points, repeated applications, and real interview pressure, then it becomes a real business.
