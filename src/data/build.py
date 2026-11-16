from __future__ import annotations
import collections, json
from src.paths import TASKS_FILE
from src.data.synthetic_tasks import TASKS as SYN

PREFIX = {"meeting_summary": "MEET", "email_draft": "EMAIL", "research_brief": "RES", "slide_outline": "SLIDE", "data_extraction": "DATA"}
REQUIRED = ["task_id", "category", "difficulty", "source_type", "source_id", "source_group", "scenario_family",
            "task_template", "task_description", "input", "requirements", "expected_facts", "output_format", "rubric_id"]
CATS, DIFFS = set(PREFIX), {"easy", "medium", "hard"}


def validate_task(t: dict):
    for k in REQUIRED:
        assert t.get(k) not in (None, "", []), f"{t.get('task_id')}: missing {k}"
    assert t["category"] in CATS and t["difficulty"] in DIFFS and t["source_type"] in ("public", "synthetic")


def _union_groups(tasks):
    """Public tasks that share any source id are merged into one group (union-find) - anti-leakage."""
    parent = {}
    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for t in tasks:
        ids = t["source_ids"]
        for a in ids[1:]:
            parent[find(a)] = find(ids[0])
        find(ids[0])
    for t in tasks:
        t["source_group"] = "un_grp_" + min(x for x in parent if find(x) == find(t["source_ids"][0]))


def build_data(synthetic_only=False):
    tasks = [dict(t) for t in SYN]
    pub = []
    if not synthetic_only:
        from src.data.public_tasks import build_public_tasks
        pub = build_public_tasks()
        _union_groups(pub)
    else:
        print("WARNING: building synthetic-only benchmark (40 tasks). This deviates from the 20+40 design; document it.")
    counters = collections.Counter()
    final = []
    for t in pub + tasks:
        counters[t["category"]] += 1
        t = {**t, "task_id": f"{PREFIX[t['category']]}_{counters[t['category']]:03d}"}
        t = {"task_id": t.pop("task_id"), **t}
        validate_task(t)
        final.append(t)
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        for t in final:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")
    c = collections.Counter((t["category"], t["difficulty"], t["source_type"]) for t in final)
    print(f"Wrote {len(final)} tasks -> {TASKS_FILE}")
    for k in sorted(c):
        print(" ", k, c[k])
    return final
