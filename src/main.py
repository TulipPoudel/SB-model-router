"""CLI:  python -m src.main <command>   (see README for the order)"""
from __future__ import annotations
import argparse, json


def main():
    ap = argparse.ArgumentParser(prog="router")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("fetch-public", help="download/ingest UN sources from the manifest")
    p = sub.add_parser("build-data"); p.add_argument("--synthetic-only", action="store_true")
    sub.add_parser("verify-models", help="one tiny call per model to check keys/IDs")
    p = sub.add_parser("run-benchmark"); p.add_argument("--limit", type=int); p.add_argument("--dry-run", action="store_true")
    sub.add_parser("export-responses")
    p = sub.add_parser("judge"); p.add_argument("--passes", type=int, default=1)
    sub.add_parser("human-select")
    p = sub.add_parser("human-score"); p.add_argument("--pass", dest="pass_no", type=int, choices=[1, 2], required=True)
    sub.add_parser("validate-judge")
    sub.add_parser("train-router")
    sub.add_parser("evaluate")
    p = sub.add_parser("route"); p.add_argument("text"); p.add_argument("--no-call", action="store_true")
    a = ap.parse_args()

    if a.cmd == "fetch-public":
        from src.data.fetch_public import fetch_public; fetch_public()
    elif a.cmd == "build-data":
        from src.data.build import build_data; build_data(a.synthetic_only)
    elif a.cmd == "verify-models":
        from src.benchmark.run import cached_generate
        from src.benchmark.cache import ResponseCache
        from src.config import load_models, get_model_cfg
        from src.paths import DB_PATH
        cfg, cache = load_models(), ResponseCache(DB_PATH)
        for k in [*cfg["tiers"], "judge"]:
            m = get_model_cfg(cfg, k); m["max_tokens"] = min(m["max_tokens"], 512) if k != "judge" else m["max_tokens"]
            row, cached = cached_generate(cache, m, "VERIFY", "Reply with the single word: ready", "verify")
            print(f"{k:<7} {m['provider']}/{m['model_id']}: {row['status']} {'(cached)' if cached else ''} {row['error'] or (row['response'] or '')[:40]!r}")
    elif a.cmd == "run-benchmark":
        from src.benchmark.run import run_benchmark; run_benchmark(a.limit, a.dry_run)
    elif a.cmd == "export-responses":
        from src.benchmark.run import export_responses; export_responses()
    elif a.cmd == "judge":
        from src.evaluation.judge import run_judge; run_judge(passes=a.passes)
    elif a.cmd == "human-select":
        from src.evaluation.human import select_validation_tasks; select_validation_tasks()
    elif a.cmd == "human-score":
        from src.evaluation.human import score_pass; score_pass(a.pass_no)
    elif a.cmd == "validate-judge":
        from src.evaluation.metrics import validate_judge
        from src.paths import REPORTS
        r = validate_judge(); json.dump(r, open(REPORTS / "judge_validation.json", "w"), indent=2); print(json.dumps(r, indent=2))
    elif a.cmd == "train-router":
        from src.analysis.results import train_router; train_router()
    elif a.cmd == "evaluate":
        from src.analysis.results import run_evaluation; run_evaluation()
    elif a.cmd == "route":
        from src.router.routing import route_and_run
        print(json.dumps(route_and_run(a.text, call=not a.no_call), indent=2, default=str))


if __name__ == "__main__":
    main()
