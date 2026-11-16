from __future__ import annotations
import hashlib

FORMAT_HINTS = {
    "bullet_points": "Bullet points.",
    "email": "A complete email with a subject line, greeting, body and sign-off.",
    "brief": "A short structured research brief in prose with clear section headings.",
    "slide_outline": "A slide-by-slide outline. For each slide give: title, key bullets, and a visual recommendation.",
    "json": "A single valid JSON object or array and nothing else (no commentary, no code fences).",
}

TEMPLATE = """You are completing a professional task. Follow every requirement exactly.

TASK:
{task_description}

INPUT:
{input}

REQUIREMENTS:
{requirements}

OUTPUT FORMAT:
{output_format}

Respond with the final deliverable only."""


def build_prompt(task: dict) -> str:
    reqs = "\n".join(f"- {r}" for r in task["requirements"])
    return TEMPLATE.format(task_description=task["task_description"], input=task["input"], requirements=reqs,
                           output_format=FORMAT_HINTS.get(task["output_format"], task["output_format"]))


def prompt_hash(prompt: str) -> str:
    return hashlib.sha256(prompt.encode()).hexdigest()
