from __future__ import annotations
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from src.paths import FIGURES

PAL = {"cheap": "#4C9BE8", "medium": "#F2A541", "strong": "#2E7D5B"}


def _save(fig, name):
    fig.tight_layout(); fig.savefig(FIGURES / name, dpi=150); plt.close(fig)


def make_all_plots(long, by_model, strat, sweep, tiers):
    FIGURES.mkdir(parents=True, exist_ok=True)
    cols = [PAL.get(t, "gray") for t in tiers]
    # 1 quality by model
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.bar(tiers, by_model.mean_quality, color=cols); ax.set_ylabel("Mean judge score (0-100)")
    ax.set_title("Chart 1: Average quality by model"); ax.set_ylim(0, 100)
    _save(fig, "chart1_quality_by_model.png")
    # 2 cost
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.bar(tiers, by_model.cost_per_task_usd, color=cols); ax.set_ylabel("Estimated commercial cost / task (USD)")
    ax.set_title("Chart 2: Estimated cost per task"); _save(fig, "chart2_cost_by_model.png")
    # 3 latency
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.boxplot([long[long.tier == t].latency_ms / 1000 for t in tiers], showfliers=True)
    ax.set_xticks(range(1, len(tiers) + 1)); ax.set_xticklabels(tiers)
    ax.set_ylabel("Latency (s)"); ax.set_title("Chart 3: Latency distribution"); _save(fig, "chart3_latency.png")
    # 4 router vs strongest
    names = [f"always_{tiers[-1]}", "ml_router", "ml_plus_fallback"]
    fig, axs = plt.subplots(1, 2, figsize=(9, 4))
    axs[0].bar(names, strat.loc[names, "mean_quality"], color=["#2E7D5B", "#9467bd", "#d62728"]); axs[0].set_ylim(0, 100)
    axs[0].set_title("Mean quality"); axs[1].bar(names, strat.loc[names, "cost_per_task_usd"], color=["#2E7D5B", "#9467bd", "#d62728"])
    axs[1].set_title("Estimated cost / task (USD)")
    for a in axs: a.tick_params(axis="x", rotation=20)
    fig.suptitle("Chart 4: Router vs strongest model"); _save(fig, "chart4_router_vs_strongest.png")
    # 5 pareto
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    for t in tiers:
        ax.scatter(by_model.loc[t, "cost_per_task_usd"], by_model.loc[t, "mean_quality"], s=90, color=PAL.get(t), label=f"model: {t}")
    for n, r in strat.iterrows():
        if n.startswith("always"): continue
        ax.scatter(r.cost_per_task_usd, r.mean_quality, marker="s", s=70, label=n)
    ax.plot(sweep.cost_per_task_usd, sweep.mean_quality, "k:", lw=1, label="ML+fallback, threshold sweep (OOF)")
    ax.set_xlabel("Estimated cost / task (USD)"); ax.set_ylabel("Mean quality"); ax.legend(fontsize=7)
    ax.set_title("Chart 5: Cost-quality Pareto"); _save(fig, "chart5_pareto.png")
