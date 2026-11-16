from __future__ import annotations


def apply_fallback(pred: str, conf: float, threshold: float, tiers: list[str]) -> str:
    """strong predicted -> strong; confident -> predicted; unsure -> escalate exactly one level."""
    if pred == tiers[-1] or conf >= threshold:
        return pred
    return tiers[tiers.index(pred) + 1]
