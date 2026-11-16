"""Category-specific rubrics (weights from the project plan). Each criterion is scored 1-5.
Total (0-100) = sum(weight * score / 5) * 100  ->  all-5s = 100, all-1s = 20."""
from __future__ import annotations

RUBRICS = {
    "meeting_v1": {"category": "meeting_summary", "criteria": {
        "factual_accuracy": (0.35, "Facts, numbers, names and dates match the source; corrected figures are used."),
        "decisions_action_items": (0.25, "Decisions and action items (owner + due date) are captured; unassigned items are flagged."),
        "organisation": (0.15, "Clear structure; decisions, open issues and actions are easy to find."),
        "conciseness": (0.15, "Respects length limits; no padding or irrelevant detail."),
        "unsupported_claims": (0.10, "5 = nothing invented or over-stated; 1 = several unsupported claims."),
    }},
    "email_v1": {"category": "email_draft", "criteria": {
        "intent_details": (0.30, "Conveys the intended message and includes every required detail, without inventing any."),
        "tone": (0.25, "Tone fits the relationship and situation described."),
        "clarity": (0.20, "Clear, well organised, easy to act on."),
        "call_to_action": (0.15, "States the needed next step/deadline unambiguously (where one is required)."),
        "grammar": (0.10, "Correct grammar, spelling and professional formatting."),
    }},
    "research_v1": {"category": "research_brief", "criteria": {
        "factual_accuracy": (0.30, "Claims are supported by the provided evidence; numbers are right."),
        "completeness": (0.25, "Covers all key evidence and answers what was asked."),
        "evidence_uncertainty": (0.20, "Separates facts from inference; flags conflicts, weak data and gaps."),
        "synthesis": (0.15, "Integrates the evidence into conclusions rather than listing it."),
        "structure": (0.10, "Logical sections and readable format."),
    }},
    "slides_v1": {"category": "slide_outline", "criteria": {
        "narrative_flow": (0.25, "Slides build a coherent story from start to finish."),
        "completeness": (0.25, "Covers all required content and obeys slide-count/format constraints."),
        "audience_suitability": (0.20, "Language, depth and emphasis fit the stated audience."),
        "visual_recommendations": (0.15, "Concrete, appropriate visual suggestions per slide."),
        "conciseness": (0.15, "Bullets are tight; respects per-slide limits."),
    }},
    "extraction_v1": {"category": "data_extraction", "criteria": {
        "field_accuracy": (0.45, "Extracted values exactly match the source (types, formats, normalisation)."),
        "completeness": (0.25, "All requested fields/items are present."),
        "schema_correctness": (0.20, "Valid JSON that follows the requested schema; no extra commentary."),
        "missing_value_handling": (0.10, "Uses null/[] for information not in the source instead of guessing."),
    }},
}

CATEGORY_TO_RUBRIC = {v["category"]: k for k, v in RUBRICS.items()}


def criteria_keys(rubric_id):
    return list(RUBRICS[rubric_id]["criteria"])


def weighted_score(rubric_id: str, criteria_scores: dict) -> float:
    crit = RUBRICS[rubric_id]["criteria"]
    missing = set(crit) - set(criteria_scores)
    if missing:
        raise ValueError(f"missing criteria: {sorted(missing)}")
    return round(sum(w * criteria_scores[k] / 5 for k, (w, _) in crit.items()) * 100, 2)
