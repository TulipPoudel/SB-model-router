"""Transparent hand-written router. Rules were fixed BEFORE looking at benchmark scores and are not tuned."""
from __future__ import annotations
import re

AMBIGUITY_WORDS = ("conflict", "ambiguous", "unclear", "unassigned", "not decided", "disagree", "discrepan",
                   "correct", "contradict", "outdated", "distinguish", "flag")
KEYWORDS = {
    "email_draft": ("email", "draft a reply", "write to", "reply to", "message to"),
    "slide_outline": ("slide", "deck", "presentation"),
    "data_extraction": ("extract", "json", "fields", "schema", "parse"),
    "research_brief": ("research", "brief", "compare", "evidence", "report on"),
    "meeting_summary": ("meeting", "summar", "action items", "minutes", "transcript"),
}


def infer_category(text: str) -> str:
    t = text.lower()
    scores = {c: sum(k in t for k in kws) for c, kws in KEYWORDS.items()}
    return max(scores, key=scores.get) if max(scores.values()) > 0 else "meeting_summary"


def extract_features(task: dict) -> dict:
    full = " ".join([task.get("task_description", ""), task.get("input", ""), " ".join(task.get("requirements", []))])
    return {"category": task.get("category") or infer_category(full),
            "input_words": len(task.get("input", "").split()),
            "n_requirements": len(task.get("requirements", [])),
            "ambiguity_hits": sum(w in full.lower() for w in AMBIGUITY_WORDS)}


def rule_route(task: dict) -> str:
    f = extract_features(task)
    cat, words, nreq, amb = f["category"], f["input_words"], f["n_requirements"], f["ambiguity_hits"]
    if amb >= 3:
        return "strong"                                  # high ambiguity -> strong
    if cat == "data_extraction":
        return "cheap" if words < 150 and nreq <= 4 else "medium" if words < 300 else "strong"
    if cat == "email_draft":
        return "cheap" if nreq <= 4 else "medium"
    if cat == "slide_outline":
        return "medium" if nreq <= 5 else "strong"
    if cat == "meeting_summary":
        return "cheap" if words < 120 else "medium" if words < 350 else "strong"
    if cat == "research_brief":
        return "medium" if words < 250 and nreq <= 4 else "strong"
    return "medium"
