from __future__ import annotations
import json, time
from src.config import load_models, load_pricing, get_model_cfg, gen_config
from src.cost import estimate_cost, warn_if_unverified
from src.paths import DB_PATH, TASKS_FILE, RESPONSES_FILE
from src.providers import get_provider, ProviderConfigError
from src.benchmark.cache import ResponseCache
from src.benchmark.prompts import build_prompt, prompt_hash

_last_call: dict = {}


def load_tasks(path=TASKS_FILE):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def _throttle(provider: str, interval: float):
    if interval:
        wait = interval - (time.time() - _last_call.get(provider, 0))
        if wait > 0:
            time.sleep(wait)


def cached_generate(cache: ResponseCache, mcfg: dict, task_id: str, prompt: str, prompt_version: str,
                    extra_gen: dict | None = None):
    """Check cache -> (if no success) exactly one provider call -> save immediately. Returns (row, was_cached)."""
    gc = gen_config(mcfg)
    if extra_gen:
        gc = {**gc, **extra_gen}
    key = cache.make_key(task_id, mcfg["provider"], mcfg["model_id"], prompt_version, gc, prompt_hash(prompt))
    hit = cache.get_success(key)
    if hit:
        return hit, True
    provider = get_provider(mcfg["provider"])
    _throttle(mcfg["provider"], mcfg.get("min_interval_s", 0))
    result = provider.generate(prompt, mcfg)
    _last_call[mcfg["provider"]] = time.time()
    cache.put(key, task_id, mcfg["provider"], mcfg["model_id"], prompt_version, gc, prompt_hash(prompt), result)
    return cache.get(key), False


def _key_for(cache, mcfg, task, prompt_version):
    p = build_prompt(task)
    return cache.make_key(task["task_id"], mcfg["provider"], mcfg["model_id"], prompt_version, gen_config(mcfg), prompt_hash(p))


def run_benchmark(limit=None, dry_run=False, max_consecutive_errors=5):
    cfg = load_models()
    cache = ResponseCache(DB_PATH)
    tasks = load_tasks()[: limit or None]
    pv = cfg["generation"]["prompt_version"]
    tiers = cfg["tiers"]
    pending = [(t, tier) for t in tasks for tier in tiers
               if not cache.get_success(_key_for(cache, get_model_cfg(cfg, tier), t, pv))]
    print(f"{len(tasks)} tasks x {len(tiers)} models = {len(tasks) * len(tiers)} evaluations; "
          f"{len(pending)} pending (rest already cached).")
    if dry_run or not pending:
        return export_responses(tasks)
    consecutive = 0
    for i, (task, tier) in enumerate(pending, 1):
        mcfg = get_model_cfg(cfg, tier)
        try:
            row, cached = cached_generate(cache, mcfg, task["task_id"], build_prompt(task), pv)
        except ProviderConfigError as e:
            print(f"ABORT: {e}")
            break
        status = row["status"]
        print(f"[{i}/{len(pending)}] {task['task_id']} {tier:<6} {status} "
              f"{'' if status == 'ok' else row['error'][:120]}")
        consecutive = consecutive + 1 if status != "ok" else 0
        if consecutive >= max_consecutive_errors:
            print(f"Stopping after {consecutive} consecutive errors (rate limit / daily quota?). "
                  "Re-run later: successful calls are cached and will not be repeated.")
            break
    return export_responses(tasks)


def export_responses(tasks=None, out=RESPONSES_FILE):
    cfg, pricing = load_models(), load_pricing()
    warn_if_unverified(pricing)
    cache = ResponseCache(DB_PATH)
    tasks = tasks or load_tasks()
    pv = cfg["generation"]["prompt_version"]
    n_ok = 0
    with open(out, "w", encoding="utf-8") as f:
        for t in tasks:
            for tier in cfg["tiers"]:
                m = get_model_cfg(cfg, tier)
                row = cache.get_success(_key_for(cache, m, t, pv))
                rec = {"task_id": t["task_id"], "tier": tier, "model": m["model_id"], "provider": m["provider"],
                       "prompt_version": pv, "status": "ok" if row else "missing", "response": row and row["response"],
                       "input_tokens": row and row["input_tokens"], "output_tokens": row and row["output_tokens"],
                       "latency_ms": row and row["latency_ms"], "created_at": row and row["created_at"],
                       "estimated_cost_usd": row and estimate_cost(m["model_id"], row["input_tokens"],
                                                                   row["output_tokens"], pricing)}
                n_ok += bool(row)
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Wrote {out} ({n_ok} ok / {len(tasks) * len(cfg['tiers'])} total)")
    return out
