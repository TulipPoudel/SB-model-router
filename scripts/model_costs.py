import json
import statistics as st
from collections import defaultdict

rows = [json.loads(l) for l in open("data/responses.jsonl", encoding="utf-8")]
by = defaultdict(list)
for r in rows:
    if r["status"] == "ok":
        by[(r["tier"], r["model"])].append(r)

for (tier, model), rs in sorted(by.items()):
    cost = sum(r["estimated_cost_usd"] for r in rs)
    print(f"{tier:7} {model:28} n={len(rs):3} total=${cost:.4f} "
          f"per_task=${cost/len(rs):.5f} "
          f"mean_out_tokens={st.mean(r['output_tokens'] for r in rs):.0f} "
          f"median_latency_ms={st.median(r['latency_ms'] for r in rs):.0f}")