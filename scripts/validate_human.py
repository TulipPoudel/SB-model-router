import json, statistics as st

def load(p):
    return {r["task_id"]: r for r in map(json.loads, open(p, encoding="utf-8")) if r.get("task_id")}

h1, h2 = load("data/human_scores_pass1.jsonl"), load("data/human_scores_pass2.jsonl")
jd = load("data/judge_scores.jsonl")
TIERS = ("cheap", "medium", "strong")

def htot(r):
    return {t: float(v["total_score"]) for t, v in r["scores"].items() if isinstance(v, dict) and "total_score" in v}

def jtot(r):
    acc = {}
    for p in r["passes"]:
        for label, resp in p["responses"].items():
            tier = p["label_map"][label]
            for k in ("total_score", "weighted_score", "weighted_total", "total"):
                if isinstance(resp.get(k), (int, float)):
                    acc.setdefault(tier, []).append(float(resp[k]))
                    break
    return {t: st.mean(v) for t, v in acc.items()}

ids = sorted(set(h1) & set(h2))
if not any(jtot(jd[t]) for t in ids if t in jd):
    p = jd[ids[0]]["passes"][0]
    print("No judge total found. Judge keys:", list(p.keys()))
    print("One response keys:", list(next(iter(p["responses"].values())).keys()))
    raise SystemExit

def corr(u, v):
    mu, mv = st.mean(u), st.mean(v)
    d = (sum((i-mu)**2 for i in u) * sum((i-mv)**2 for i in v)) ** 0.5
    return sum((i-mu)*(k-mv) for i, k in zip(u, v)) / d if d else float("nan")

def report(title, rows):
    a = [r[2] for r in rows]; b = [r[3] for r in rows]
    d = [abs(x-y) for x, y in zip(a, b)]
    print(f"\n=== {title} ===")
    print(f"n={len(rows)} responses  exact: {sum(x==0 for x in d)}  within5: {sum(x<=5 for x in d)}  within10: {sum(x<=10 for x in d)}")
    print(f"mean signed diff (2nd - 1st): {st.mean([y-x for x, y in zip(a, b)]):+.2f}  MAE: {st.mean(d):.2f}  max: {max(d):.1f}  Pearson r: {corr(a, b):.3f}")
    for t, tier, x, y in sorted(rows, key=lambda r: -abs(r[2]-r[3]))[:5]:
        print(f"  {t} [{tier}]: {x:.1f} vs {y:.1f}")

self_rows, judge_rows, hm = [], [], {}
for t in ids:
    s1, s2 = htot(h1[t]), htot(h2[t])
    jt = jtot(jd[t]) if t in jd else {}
    for tier in TIERS:
        if tier in s1 and tier in s2:
            self_rows.append((t, tier, s1[tier], s2[tier]))
            m = (s1[tier] + s2[tier]) / 2
            hm[(t, tier)] = m
            if tier in jt:
                judge_rows.append((t, tier, m, jt[tier]))
report("HUMAN SELF-AGREEMENT, total score 20-100 (pass1 vs pass2)", self_rows)

# per-criterion (1-5) agreement
ex = w1 = n = 0
for t in ids:
    for tier, v in h1[t]["scores"].items():
        c1 = v.get("criteria", {}); c2 = h2[t]["scores"][tier].get("criteria", {})
        for c in c1:
            if c in c2:
                n += 1; ex += c1[c] == c2[c]; w1 += abs(c1[c]-c2[c]) <= 1
print(f"\nper-criterion 1-5: n={n}  same score: {ex} ({100*ex/n:.1f}%)  within 1 point: {w1} ({100*w1/n:.1f}%)")

report("JUDGE vs HUMAN (human = mean of both passes; 'diff' = judge - human)", [(t, k, h, j) for t, k, h, j in judge_rows])

# does the judge rank responses in the same order as the human?
agree = tot = 0
for t in ids:
    jt = jtot(jd[t]) if t in jd else {}
    for i in range(3):
        for k in range(i+1, 3):
            a, b = TIERS[i], TIERS[k]
            if (t, a) in hm and (t, b) in hm and a in jt and b in jt:
                dh, dj = hm[(t, a)] - hm[(t, b)], jt[a] - jt[b]
                if dh != 0 and dj != 0:
                    tot += 1; agree += (dh > 0) == (dj > 0)
print(f"\npairwise ranking agreement (judge vs human, ties skipped): {agree}/{tot}")