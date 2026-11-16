"""Human validation: 15 tasks (3 per category), two blind passes >= 24h apart. Run in a terminal (VS Code)."""
from __future__ import annotations
import json, random, time
from datetime import datetime, timedelta
from src.benchmark.run import load_tasks
from src.config import load_models, load_router_cfg
from src.paths import HUMAN_TASKS_FILE, HUMAN1_FILE, HUMAN2_FILE, RESPONSES_FILE
from src.evaluation.scoring import RUBRICS, weighted_score
from src.evaluation.judge import _load_responses, LABELS


def select_validation_tasks():
    if HUMAN_TASKS_FILE.exists():
        print(f"{HUMAN_TASKS_FILE} already exists - keeping the original selection."); return json.load(open(HUMAN_TASKS_FILE))
    n = load_router_cfg()["human_validation_per_category"]
    seed = load_router_cfg()["seed"]
    tasks = load_tasks()
    chosen = []
    for cat in sorted({t["category"] for t in tasks}):
        pool = [t for t in tasks if t["category"] == cat]
        rng = random.Random(f"{seed}-{cat}")
        picked = []
        for diff in ["easy", "medium", "hard"][:n]:       # one per difficulty -> 3 per category
            c = [t for t in pool if t["difficulty"] == diff]
            picked.append(rng.choice(c)["task_id"])
        chosen += picked
    json.dump({"selected_at": datetime.now().isoformat(timespec="seconds"), "seed": seed, "task_ids": chosen},
              open(HUMAN_TASKS_FILE, "w"), indent=2)
    print(f"Selected {len(chosen)} tasks -> {HUMAN_TASKS_FILE}")
    return chosen


def _ask(prompt, lo=1, hi=5):
    while True:
        s = input(prompt).strip().lower()
        if s == "q":
            raise KeyboardInterrupt
        if s.isdigit() and lo <= int(s) <= hi:
            return int(s)
        print("  enter an integer 1-5 (or q to save & quit)")


def score_pass(pass_no: int):
    out = HUMAN1_FILE if pass_no == 1 else HUMAN2_FILE
    if not HUMAN_TASKS_FILE.exists():
        select_validation_tasks()
    ids = json.load(open(HUMAN_TASKS_FILE))["task_ids"]
    if pass_no == 2:
        if not HUMAN1_FILE.exists():
            raise SystemExit("Pass 1 file not found.")
        p1 = [json.loads(l) for l in open(HUMAN1_FILE)]
        if {r["task_id"] for r in p1} != set(ids):
            raise SystemExit("Pass 1 is incomplete - finish it first.")
        last = max(datetime.fromisoformat(r["timestamp"]) for r in p1)
        if datetime.now() - last < timedelta(hours=24):
            import os, json as _json
            if os.environ.get("ALLOW_EARLY") != "1":
                ready = last + timedelta(hours=24)
                raise SystemExit(f"Pass 2 is locked until {ready:%Y-%m-%d %H:%M} (>=24h after Pass 1). Not faking it.")
            _gap = (datetime.now() - last).total_seconds() / 3600
            print(f"WARNING: running Pass 2 EARLY ({_gap:.1f} h after Pass 1). The 24h protocol is NOT met.")
            _json.dump({"pass1_last_timestamp": last.isoformat(timespec="seconds"),
                        "pass2_started": datetime.now().isoformat(timespec="seconds"),
                        "gap_hours_at_start": round(_gap, 2), "protocol_met": False},
                       open("data/pass2_protocol.json", "w"), indent=2)
    done = {json.loads(l)["task_id"] for l in open(out)} if out.exists() else set()
    tasks = {t["task_id"]: t for t in load_tasks()}
    resp = _load_responses()
    tiers = load_models()["tiers"]
    todo = [i for i in ids if i not in done]
    random.Random(f"human-order-{pass_no}").shuffle(todo)          # task order differs per pass
    print(f"Pass {pass_no}: {len(todo)} tasks left. Score blind - do NOT look at judge_scores.jsonl. 'q' saves & quits.\n")
    for tid in todo:
        t = tasks[tid]
        order = list(tiers)
        random.Random(f"human-labels-{pass_no}-{tid}").shuffle(order)   # response order differs per pass
        label_map = dict(zip(LABELS, order))
        print("=" * 80, f"\nTASK {tid} [{t['category']}]\n{t['task_description']}\n\nINPUT:\n{t['input']}\n\nREQUIREMENTS:")
        print("\n".join(f"- {r}" for r in t["requirements"]))
        print("\nREFERENCE FACTS:\n" + "\n".join(f"- {f}" for f in t["expected_facts"]))
        for lab, tier in label_map.items():
            print(f"\n----- RESPONSE {lab} -----\n{resp[tid][tier]['response']}\n")
        rub = RUBRICS[t["rubric_id"]]["criteria"]
        try:
            scores = {}
            for lab, tier in label_map.items():
                print(f"\nScoring RESPONSE {lab}")
                scores[tier] = {k: _ask(f"  {k} ({int(w*100)}%) - {d}\n    score 1-5: ") for k, (w, d) in rub.items()}
        except KeyboardInterrupt:
            print("\nSaved progress. Re-run to continue."); return
        rec = {"task_id": tid, "pass": pass_no, "timestamp": datetime.now().isoformat(timespec="seconds"),
               "label_map": label_map, "scores": {tr: {"criteria": c, "total_score": weighted_score(t["rubric_id"], c)}
                                                  for tr, c in scores.items()}}
        with open(out, "a", encoding="utf-8") as f:           # append-only; never edit earlier records
            f.write(json.dumps(rec) + "\n")
    print(f"Pass {pass_no} complete -> {out}")
