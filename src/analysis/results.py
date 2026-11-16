from __future__ import annotations
import json
import numpy as np
import pandas as pd
from src.benchmark.run import load_tasks
from src.config import load_models, load_pricing, load_router_cfg
from src.cost import estimate_cost, warn_if_unverified, pricing_is_verified
from src.paths import RESPONSES_FILE, JUDGE_FILE, REPORTS, FIGURES, MODELS
from src.router import classifier as clf
from src.router.fallback import apply_fallback
from src.router.rules import rule_route


# ------------------------------------------------------------------ data assembly
def load_long() -> pd.DataFrame:
    cfg, pricing = load_models(), load_pricing()
    warn_if_unverified(pricing)
    rows = [json.loads(l) for l in open(RESPONSES_FILE, encoding="utf-8")]
    r = pd.DataFrame(rows)
    r = r[r.status == "ok"].copy()
    r["cost_usd"] = [estimate_cost(m, i, o, pricing) for m, i, o in zip(r.model, r.input_tokens, r.output_tokens)]
    j = []
    for l in open(JUDGE_FILE, encoding="utf-8"):
        d = json.loads(l)
        for tier, s in d["scores"].items():
            j.append({"task_id": d["task_id"], "tier": tier, "quality": s["total_score"]})
    return r.merge(pd.DataFrame(j), on=["task_id", "tier"])[
        ["task_id", "tier", "model", "quality", "cost_usd", "latency_ms", "input_tokens", "output_tokens"]]


def build_wide(long: pd.DataFrame, tiers, tasks) -> pd.DataFrame:
    meta = pd.DataFrame(tasks).set_index("task_id")
    wide = pd.DataFrame(index=sorted(long.task_id.unique()))
    for p, col in (("q", "quality"), ("c", "cost_usd"), ("l", "latency_ms")):
        pv = long.pivot(index="task_id", columns="tier", values=col)
        for t in tiers:
            wide[f"{p}_{t}"] = pv[t]
    wide = wide.dropna()
    wide = wide.join(meta[["category", "difficulty", "source_group", "scenario_family"]])
    return wide


def evaluate_strategy(wide, chosen, tiers, tol) -> dict:
    q, c, l = clf.realise(wide, chosen, tiers)
    ref = wide[f"q_{tiers[-1]}"].values
    share = pd.Series(chosen).value_counts(normalize=True)
    out = {"mean_quality": q.mean(), "median_quality": np.median(q), "cost_per_task_usd": c.mean(),
           "total_cost_usd": c.sum(), "mean_latency_ms": l.mean(), "median_latency_ms": np.median(l),
           "p95_latency_ms": np.percentile(l, 95), "quality_failures": int((q < ref - tol).sum())}
    for t in tiers:
        out[f"pct_{t}"] = 100 * share.get(t, 0.0)
    return out


# ------------------------------------------------------------------ router training
def _prepare(tol=None):
    cfg, rcfg = load_models(), load_router_cfg()
    tiers, tol = cfg["tiers"], rcfg["quality_tolerance"] if tol is None else tol
    tasks = load_tasks()
    long = load_long()
    wide = build_wide(long, tiers, tasks)
    tmap = {t["task_id"]: t for t in tasks}
    wide = wide[wide.index.isin(tmap)]
    if wide[[f"c_{t}" for t in tiers]].isna().any().any():
        raise SystemExit("Missing token counts for some responses; cannot compute cost-based labels.")
    tl = [tmap[i] for i in wide.index]
    return cfg, rcfg, tiers, tol, tl, wide


def train_router():
    """Nested grouped CV (honest OOF predictions) + final fit on all data. Saves models/router.pkl."""
    cfg, rcfg, tiers, tol, tl, wide = _prepare()
    labels = clf.best_value_labels(wide, tiers, tol)
    texts = [clf.task_text(t) for t in tl]
    groups = [t["source_group"] for t in tl]
    oof = clf.nested_cv(texts, list(labels.values), groups, wide.reset_index(drop=True), tiers, tol,
                        rcfg["thresholds"], rcfg["outer_folds"], rcfg["inner_folds"], rcfg["seed"])
    oof.index = wide.index
    oof["label"] = labels
    oof.to_csv(REPORTS / "oof_predictions.csv")
    # final model: threshold chosen on grouped-OOF over all data (validation-style), then fit on everything
    ip = clf.oof_proba(texts, list(labels.values), groups, tiers, rcfg["outer_folds"], rcfg["seed"])
    thr = clf.select_threshold(ip, wide.reset_index(drop=True), rcfg["thresholds"], tiers, tol)
    model = clf.fit(texts, list(labels.values), rcfg["seed"])
    clf.save_router(model, tiers, thr, tol, extra={"n_train": len(texts), "label_counts": labels.value_counts().to_dict()})
    print(f"Label distribution: {labels.value_counts().to_dict()} | final threshold {thr} | saved models/router.pkl")
    return oof


# ------------------------------------------------------------------ evaluation
def run_evaluation():
    cfg, rcfg, tiers, tol, tl, wide = _prepare()
    oof_path = REPORTS / "oof_predictions.csv"
    oof = pd.read_csv(oof_path, index_col=0) if oof_path.exists() else train_router()
    oof = oof.loc[wide.index]
    pricing = load_pricing()
    REPORTS.mkdir(exist_ok=True); FIGURES.mkdir(parents=True, exist_ok=True)

    chosen = {
        f"always_{tiers[0]}": [tiers[0]] * len(wide),
        f"always_{tiers[-1]}": [tiers[-1]] * len(wide),
        "rule_router": [rule_route(t) for t in tl],
        "ml_router": list(oof.pred),
        "ml_plus_fallback": [apply_fallback(p, c, th, tiers) for p, c, th in zip(oof.pred, oof.conf, oof.threshold)],
    }
    strat = pd.DataFrame({k: evaluate_strategy(wide, v, tiers, tol) for k, v in chosen.items()}).T
    ref = strat.loc[f"always_{tiers[-1]}"]
    strat["cost_saving_vs_strongest_pct"] = 100 * (1 - strat.cost_per_task_usd / ref.cost_per_task_usd)
    strat["quality_delta_vs_strongest"] = strat.mean_quality - ref.mean_quality
    strat["escalated_pct"] = np.nan
    strat.loc["ml_plus_fallback", "escalated_pct"] = 100 * np.mean(np.array(chosen["ml_plus_fallback"]) != oof.pred.values)
    strat.to_csv(REPORTS / "strategy_comparison.csv")

    # model-level tables
    long = load_long()
    long = long[long.task_id.isin(wide.index)].merge(wide[["category", "difficulty"]], left_on="task_id", right_index=True)
    by_model = long.groupby("tier").agg(mean_quality=("quality", "mean"), median_quality=("quality", "median"),
                                        cost_per_task_usd=("cost_usd", "mean"), total_cost_usd=("cost_usd", "sum"),
                                        mean_latency_ms=("latency_ms", "mean"),
                                        p95_latency_ms=("latency_ms", lambda s: np.percentile(s, 95))).loc[tiers]
    by_cat = long.pivot_table(index="category", columns="tier", values="quality", aggfunc="mean")[tiers]
    by_cat["best_tier"] = by_cat.idxmax(axis=1)
    by_diff = long.pivot_table(index="difficulty", columns="tier", values="quality", aggfunc="mean")[tiers]
    by_model.to_csv(REPORTS / "model_summary.csv"); by_cat.to_csv(REPORTS / "quality_by_category.csv")
    by_diff.to_csv(REPORTS / "quality_by_difficulty.csv")

    # router diagnostics
    labels = oof.label
    acc = float((oof.pred == labels).mean())
    majority = float(labels.value_counts(normalize=True).max())
    qs = {t: wide[f"q_{t}"] for t in tiers}
    ok_pred = float(np.mean([qs[p][i] >= wide[[f"q_{t}" for t in tiers]].loc[i].max() - tol for i, p in zip(oof.index, oof.pred)]))
    cheap_ok = {t: float((qs[t] >= qs[tiers[-1]] - tol).mean()) for t in tiers}
    ml, fb = strat.loc["ml_router"], strat.loc["ml_plus_fallback"]
    diag = {"tolerance": tol, "routing_accuracy_vs_best_value_label": acc, "majority_class_baseline": majority,
            "pred_within_tol_of_best_pct": 100 * ok_pred,
            "pct_tasks_where_model_within_tol_of_strong": {t: 100 * v for t, v in cheap_ok.items()},
            "label_distribution": labels.value_counts().to_dict(),
            "fallback_escalated_pct": float(strat.loc["ml_plus_fallback", "escalated_pct"]),
            "fallback_quality_gain": float(fb.mean_quality - ml.mean_quality),
            "fallback_extra_cost_per_task_usd": float(fb.cost_per_task_usd - ml.cost_per_task_usd),
            "fallback_latency_increase_ms": float(fb.mean_latency_ms - ml.mean_latency_ms),
            "failures_ml": int(ml.quality_failures), "failures_ml_fallback": int(fb.quality_failures),
            "pricing_verified": pricing_is_verified(pricing)}
    json.dump(diag, open(REPORTS / "router_diagnostics.json", "w"), indent=2)

    # threshold sweep for the Pareto plot (OOF probabilities; plotting only)
    sweep = []
    P = oof[tiers].astype(float)
    for thr in rcfg["thresholds"]:
        s = evaluate_strategy(wide, clf.choose_chosen(P, thr, tiers), tiers, tol)
        sweep.append({"threshold": thr, **s})
    sweep = pd.DataFrame(sweep); sweep.to_csv(REPORTS / "threshold_sweep.csv", index=False)

    write_error_analysis(wide, tl, oof, tiers, tol, chosen["ml_plus_fallback"])
    from src.analysis.plots import make_all_plots
    make_all_plots(long, by_model, strat, sweep, tiers)
    write_summary(by_model, by_cat, by_diff, strat, diag, tiers, tol, pricing)
    print(strat.round(3).T.to_string())
    return {"by_model": by_model, "by_cat": by_cat, "strategies": strat, "diagnostics": diag}


def write_error_analysis(wide, tl, oof, tiers, tol, chosen_fb):
    try:
        bundle = clf.load_router(MODELS / "router.pkl")
    except FileNotFoundError:
        bundle = None
    tmap = {t["task_id"]: t for t in tl}
    lines = ["# Error analysis (measured results only)\n",
             f"Failure = chosen model's judge score is more than {tol} points below the strongest model's score on that task.\n",
             "Term explanations come from the final router fitted on all data (so they illustrate, not test).\n"]
    rows = []
    for k, tid in enumerate(wide.index):
        q = {t: wide.loc[tid, f"q_{t}"] for t in tiers}
        gap = q[tiers[-1]] - q[oof.loc[tid, "pred"]]
        rows.append((tid, gap, chosen_fb[k]))
    fails = sorted([r for r in rows if r[1] > tol], key=lambda r: -r[1])[:8]
    lines.append(f"## Routing failures of the ML router ({sum(r[1] > tol for r in rows)} total; worst {len(fails)} shown)\n")
    for tid, gap, ch in fails:
        t, o = tmap[tid], oof.loc[tid]
        q = {x: round(wide.loc[tid, f"q_{x}"], 1) for x in tiers}
        fixed = wide.loc[tid, f"q_{ch}"] >= q[tiers[-1]] - tol
        terms = clf.explain(bundle["pipeline"], clf.task_text(t), o.pred) if bundle else []
        lines += [f"### {tid} - {t['category']} / {t['difficulty']}",
                  f"- scores: {q}", f"- router predicted **{o.pred}** (confidence {float(o.conf):.2f}, threshold {float(o.threshold)})",
                  f"- fallback chose **{ch}** -> {'corrected' if fixed else 'NOT corrected'}",
                  f"- terms that pushed the prediction: {', '.join(f'{a}' for a, _ in terms) or 'n/a'}",
                  "- limitation to examine: the router only sees the task description/requirements, not the input text or "
                  "the model's actual difficulty; check whether the input is long/conflicting while the description looks simple.\n"]
    wins = [tid for tid in wide.index if wide.loc[tid, f"q_{tiers[0]}"] > wide.loc[tid, f"q_{tiers[-1]}"]]
    lines.append(f"## Cases where the cheapest model beat the strongest ({len(wins)})\n")
    for tid in wins[:10]:
        t = tmap[tid]
        lines.append(f"- {tid} ({t['category']}/{t['difficulty']}): " + ", ".join(f"{x}={wide.loc[tid, f'q_{x}']:.1f}" for x in tiers))
    (REPORTS / "error_analysis.md").write_text("\n".join(lines), encoding="utf-8")


def write_summary(by_model, by_cat, by_diff, strat, diag, tiers, tol, pricing):
    s, f = strat, lambda x: f"{x:.3f}"
    best = by_model.mean_quality.idxmax()
    st = f"always_{tiers[-1]}"
    L = ["# Results summary (auto-generated from measured data)\n"]
    if not diag["pricing_verified"]:
        L.append("> **WARNING:** config/pricing.yaml is UNVERIFIED; all dollar figures below are placeholders.\n")
    L += [f"Quality tolerance: {tol} points. Pricing source: {pricing.get('pricing_source')} (checked {pricing.get('pricing_checked_at')}). "
          f"Actual expenditure recorded: ${pricing.get('actual_expenditure_usd', 0)}.\n",
          "## Model-level\n", by_model.round(4).to_markdown(), "\n## Mean quality by category\n", by_cat.round(1).to_markdown(),
          "\n## Mean quality by difficulty\n", by_diff.round(1).to_markdown(), "\n## Router strategies\n",
          s.round(4).to_markdown(),
          "\n## Questions\n",
          f"1. **Best overall:** {best} (mean quality {by_model.mean_quality.max():.1f}).",
          f"2. **Best model by category:** " + "; ".join(f"{c}: {r.best_tier}" for c, r in by_cat.iterrows()) + ".",
          f"3. **Quality vs cost:** " + "; ".join(f"{t}: {by_model.loc[t,'mean_quality']:.1f} @ ${by_model.loc[t,'cost_per_task_usd']:.5f}/task" for t in tiers) + ".",
          f"4. **Can a simpler model suffice?** Share of tasks within {tol} pts of the strongest model: " +
          ", ".join(f"{t}: {v:.0f}%" for t, v in diag["pct_tasks_where_model_within_tol_of_strong"].items()) + ".",
          f"5. **Does the ML router learn the pattern?** Routing accuracy vs best-value label (grouped OOF): {diag['routing_accuracy_vs_best_value_label']:.2f} "
          f"(majority-class baseline {diag['majority_class_baseline']:.2f}). n is small; treat as indicative.",
          f"6-8. **ML+fallback vs always-strongest:** quality {s.loc['ml_plus_fallback','mean_quality']:.1f} vs {s.loc[st,'mean_quality']:.1f} "
          f"(delta {s.loc['ml_plus_fallback','quality_delta_vs_strongest']:+.2f}); cost/task saving {s.loc['ml_plus_fallback','cost_saving_vs_strongest_pct']:.1f}%; "
          f"quality failures {int(s.loc['ml_plus_fallback','quality_failures'])}. ML router alone: delta {s.loc['ml_router','quality_delta_vs_strongest']:+.2f}, "
          f"saving {s.loc['ml_router','cost_saving_vs_strongest_pct']:.1f}%, failures {int(s.loc['ml_router','quality_failures'])}.",
          f"9. **Fallback:** escalated {diag['fallback_escalated_pct']:.0f}% of requests; quality {diag['fallback_quality_gain']:+.2f}; "
          f"extra cost ${diag['fallback_extra_cost_per_task_usd']:.5f}/task; extra latency {diag['fallback_latency_increase_ms']:+.0f} ms; "
          f"failures {diag['failures_ml']} -> {diag['failures_ml_fallback']}.",
          "10. **Where it fails:** see reports/error_analysis.md.\n"]
    (REPORTS / "results_summary.md").write_text("\n".join(L), encoding="utf-8")
