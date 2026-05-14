# -*- coding: utf-8 -*-
"""OpenAI-compatible resume optimization helper.

The API key and endpoint are intentionally read from environment variables.
Never commit secrets into this repository.
"""

from __future__ import annotations

import json
import os
from typing import Any
from urllib import error, request


def optimize_resume_with_ai(
    *,
    role: str,
    resume_text: str,
    job_description: str,
    discipline: str = "",
    template_name: str = "",
    timeout: float = 18.0,
) -> dict[str, Any]:
    """Return AI optimization suggestions using an OpenAI-compatible endpoint.

    Environment variables:
    - RESUME_COPILOT_AI_API_KEY or OPENAI_API_KEY
    - RESUME_COPILOT_AI_BASE_URL or OPENAI_BASE_URL
    - RESUME_COPILOT_AI_MODEL, default gpt-5.5
    """

    api_key = os.getenv("RESUME_COPILOT_AI_API_KEY") or os.getenv("OPENAI_API_KEY")
    base_url = (
        os.getenv("RESUME_COPILOT_AI_BASE_URL")
        or os.getenv("OPENAI_BASE_URL")
        or ""
    ).rstrip("/")
    model = os.getenv("RESUME_COPILOT_AI_MODEL", "gpt-5.5")

    if not api_key or not base_url:
        return _fallback_result(
            role=role,
            resume_text=resume_text,
            job_description=job_description,
            template_name=template_name,
        )

    endpoint = base_url
    if not endpoint.endswith("/chat/completions"):
        endpoint = f"{endpoint}/chat/completions"

    prompt = _build_prompt(
        role=role,
        resume_text=resume_text,
        job_description=job_description,
        discipline=discipline,
        template_name=template_name,
    )
    body = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a senior resume coach for Chinese university students. "
                    "Return concise JSON only. Optimize for truthful, role-fit, evidence-led resumes."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    }
    payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        endpoint,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
        data = json.loads(raw)
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        parsed = _parse_content(content)
        parsed["provider"] = "ai"
        parsed["model"] = model
        return parsed
    except (OSError, error.URLError, json.JSONDecodeError, KeyError, IndexError) as exc:
        result = _fallback_result(
            role=role,
            resume_text=resume_text,
            job_description=job_description,
            template_name=template_name,
        )
        result["provider"] = "fallback"
        result["error"] = str(exc)
        return result


def _build_prompt(
    *,
    role: str,
    resume_text: str,
    job_description: str,
    discipline: str,
    template_name: str,
) -> str:
    return f"""
Target role: {role}
Discipline: {discipline or "unknown"}
Preferred template: {template_name or "auto"}

Candidate raw material:
{resume_text[:3000]}

Job description:
{job_description[:3000]}

Return JSON with keys:
- summary: one short Chinese sentence explaining the optimization direction
- improved_bullets: 3 resume bullets in Chinese, each truthful and evidence-led
- missing_questions: 3 follow-up questions that would improve the resume
- template_reason: why this template fits
""".strip()


def _parse_content(content: str) -> dict[str, Any]:
    cleaned = content.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.removeprefix("json").strip()
    parsed = json.loads(cleaned)
    return {
        "summary": str(parsed.get("summary", "")).strip(),
        "improved_bullets": [str(item).strip() for item in parsed.get("improved_bullets", [])][:4],
        "missing_questions": [str(item).strip() for item in parsed.get("missing_questions", [])][:4],
        "template_reason": str(parsed.get("template_reason", "")).strip(),
    }


def _fallback_result(
    *,
    role: str,
    resume_text: str,
    job_description: str,
    template_name: str,
) -> dict[str, Any]:
    lines = [line.strip("- ").strip() for line in resume_text.splitlines() if line.strip()]
    seed = lines[:3] or ["补充一个最能证明岗位能力的项目经历"]
    bullets = [
        f"围绕「{role}」重写经历：{item}，补充任务背景、个人动作和可量化结果。"
        for item in seed
    ]
    return {
        "provider": "local",
        "model": "local-rules",
        "summary": "当前未配置 AI 接口，已使用本地规则生成可编辑优化建议。",
        "improved_bullets": bullets,
        "missing_questions": [
            "这段经历最终影响了多少用户、数据、收入、效率或交付结果？",
            "你在团队里具体负责哪一部分，而不是团队整体做了什么？",
            "岗位描述里最重要的 3 个关键词，是否已经出现在项目表达里？",
        ],
        "template_reason": f"当前选择 {template_name or 'auto'} 模板；建议先保证内容证据清晰，再调整视觉模板。",
    }
