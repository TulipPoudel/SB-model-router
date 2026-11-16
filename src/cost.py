from __future__ import annotations
import warnings


def pricing_is_verified(pricing: dict) -> bool:
    return not str(pricing.get("pricing_checked_at", "")).upper().startswith("UNVERIFIED")


def warn_if_unverified(pricing: dict):
    if not pricing_is_verified(pricing):
        warnings.warn("config/pricing.yaml is marked UNVERIFIED: estimated costs are placeholders until "
                      "you check the providers' pricing pages and set pricing_checked_at.", stacklevel=2)


def estimate_cost(model_id: str, input_tokens, output_tokens, pricing: dict):
    """USD estimated at published prices. Returns None if token counts are unavailable (never fabricated)."""
    if input_tokens is None or output_tokens is None:
        return None
    p = pricing["prices_usd_per_million_tokens"][model_id]
    return (input_tokens / 1_000_000) * p["input"] + (output_tokens / 1_000_000) * p["output"]
