from __future__ import annotations
import json
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import cohen_kappa_score
from src.paths import JUDGE_FILE, HUMAN1_FILE, HUMAN2_FILE


def _spearman(a, b):
    if len(a) < 3 or np.std(a) == 0 or np.std(b) == 0:
        return float("nan")
    return float(spearmanr(a, b).correlation)


def _flatten(path, key="scores"):
    rows = []
    for l in open(path, encoding="utf-8"):
        r = json.loads(l)
        for tier, s in r[key].items():
            rows.append({"task_id": r["task_id"], "tier": tier, "criterion": "__total__", "score": s["total_score"]})
            for c, v in s["criteria"].items():
                rows.append({"task_id": r["task_id"], "tier": tier, "criterion": c, "score": v})
    return pd.DataFrame(rows)


def agreement_stats(a: pd.Series, b: pd.Series) -> dict:
    a, b = np.asarray(a, float), np.asarray(b, float)
    return {"n": int(len(a)), "mae": float(np.mean(np.abs(a - b))), "spearman": _spearman(a, b),
            "within_1_pct": float(np.mean(np.abs(a - b) <= 1) * 100), "exact_pct": float(np.mean(a == b) * 100)}


def _tot(d: dict) -> dict:
    d = dict(d); d.pop("within_1_pct", None); d.pop("exact_pct", None)   # not meaningful on a 0-100 scale
    return d


def validate_judge() -> dict:
    h1, h2, j = _flatten(HUMAN1_FILE), _flatten(HUMAN2_FILE), _flatten(JUDGE_FILE)
    keys = ["task_id", "tier", "criterion"]
    df = h1.merge(h2, on=keys, suffixes=("_h1", "_h2")).merge(j.rename(columns={"score": "score_j"}), on=keys)
    crit, tot = df[df.criterion != "__total__"], df[df.criterion == "__total__"]
    crit = crit.assign(score_hm=(crit.score_h1 + crit.score_h2) / 2)
    tot = tot.assign(score_hm=(tot.score_h1 + tot.score_h2) / 2)
    out = {
        "n_tasks": int(df.task_id.nunique()), "n_criterion_scores": int(len(crit)), "n_response_totals": int(len(tot)),
        "human_vs_human_criterion_1to5": agreement_stats(crit.score_h1, crit.score_h2),
        "human_vs_human_cohen_kappa_quadratic": float(cohen_kappa_score(crit.score_h1.astype(int), crit.score_h2.astype(int), weights="quadratic")),
        "human_vs_human_total_0to100": _tot(agreement_stats(tot.score_h1, tot.score_h2)),
        "judge_vs_human_pass1_criterion": agreement_stats(crit.score_j, crit.score_h1),
        "judge_vs_human_pass2_criterion": agreement_stats(crit.score_j, crit.score_h2),
        "judge_vs_human_mean_criterion": agreement_stats(crit.score_j, crit.score_hm),
        "judge_vs_human_mean_total_0to100": _tot(agreement_stats(tot.score_j, tot.score_hm)),
        "note": "criterion-level stats are on the 1-5 scale (judge scores may be fractional when judge passes>1); "
                "within_1_pct = share of |diff|<=1; totals are on 0-100.",
    }
    # within-task ranking agreement (does the judge order the 3 models like humans do?)
    rk = [(_spearman(g.score_j.values, g.score_hm.values)) for _, g in tot.groupby("task_id")]
    out["judge_vs_human_within_task_ranking_mean_spearman"] = float(np.nanmean(rk)) if len(rk) else float("nan")
    return out
