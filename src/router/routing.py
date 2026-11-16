"""End-to-end routing of a free-text request (used by the CLI and the Streamlit demo)."""
from __future__ import annotations
from src.benchmark.cache import ResponseCache
from src.benchmark.run import cached_generate
from src.config import load_models, load_pricing, get_model_cfg
from src.cost import estimate_cost
from src.paths import DB_PATH
from src.router import classifier as clf
from src.router.rules import infer_category, extract_features


def estimate_difficulty(text: str) -> str:
    f = extract_features({"task_description": text, "input": text, "requirements": []})
    w = len(text.split())
    return "hard" if f["ambiguity_hits"] >= 3 or w > 500 else "medium" if w > 150 or f["ambiguity_hits"] >= 1 else "easy"


def route_and_run(text: str, call=True):
    bundle = clf.load_router()
    cat, diff = infer_category(text), estimate_difficulty(text)
    task = {"category": cat, "difficulty": diff, "task_description": text, "requirements": []}
    final, pred, conf, escalated = clf.route_text(bundle, clf.task_text(task))
    out = {"category": cat, "difficulty_estimate": diff, "predicted_model": pred, "confidence": round(conf, 3),
           "threshold": bundle["threshold"], "escalated": escalated, "selected_tier": final}
    cfg = load_models()
    m = get_model_cfg(cfg, final)
    out["selected_model"] = f"{m['provider']}/{m['model_id']}"
    if call:
        prompt = f"{text}\n\nRespond with the final deliverable only."
        row, cached = cached_generate(ResponseCache(DB_PATH), m, "DEMO", prompt, cfg["generation"]["prompt_version"])
        out.update(status=row["status"], response=row["response"], error=row["error"], latency_ms=row["latency_ms"],
                   estimated_cost_usd=estimate_cost(m["model_id"], row["input_tokens"], row["output_tokens"], load_pricing()),
                   from_cache=cached)
    return out
