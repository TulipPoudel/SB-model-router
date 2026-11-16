"""Offline end-to-end smoke test of the whole pipeline with the TEST-ONLY mock provider, in a temp directory.
Produces NO real results and writes nothing into your repo's data/ or cache/. Run: python scripts/smoke_mock.py"""
import json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

repo = Path(__file__).resolve().parents[1]
tmp = Path(tempfile.mkdtemp())
for d in ("config", "data", "cache", "models", "reports/figures"):
    (tmp / d).mkdir(parents=True, exist_ok=True)
shutil.copy(repo / "config/router.yaml", tmp / "config/router.yaml")
(tmp / "config/models.yaml").write_text("""
generation: {temperature: 0.0, max_tokens: 1000, prompt_version: v1}
tiers: [cheap, medium, strong]
models:
  cheap:  {provider: mock, model_id: mock-cheap}
  medium: {provider: mock, model_id: mock-medium}
  strong: {provider: mock, model_id: mock-strong}
judge: {provider: mock, model_id: mock-judge-medium, temperature: 0.0, max_tokens: 1000, prompt_version: judge_v1}
""")
(tmp / "config/pricing.yaml").write_text("""
pricing_checked_at: "UNVERIFIED"
pricing_source: smoke
prices_usd_per_million_tokens:
  mock-cheap: {input: 0.1, output: 0.4}
  mock-medium: {input: 0.3, output: 2.5}
  mock-strong: {input: 0.15, output: 0.6}
  mock-judge-medium: {input: 0.3, output: 2.5}
""")
env = {**os.environ, "ROUTER_ROOT": str(tmp), "PYTHONPATH": str(repo)}


def run(*a):
    r = subprocess.run([sys.executable, "-m", "src.main", *a], cwd=repo, env=env, capture_output=True, text=True)
    print(f"$ {' '.join(a)} -> {r.returncode}")
    if r.returncode:
        print(r.stdout[-1500:], r.stderr[-2500:]); sys.exit(1)
    return r.stdout


run("build-data", "--synthetic-only")
run("run-benchmark"); out = run("run-benchmark"); assert "0 pending" in out, "second run must make zero calls"
run("judge"); run("train-router"); run("evaluate"); out = run("route", "Please summarise this meeting transcript and list action items", "--no-call")
print(out[:400])
for f in ("strategy_comparison.csv", "results_summary.md", "error_analysis.md", "figures/chart5_pareto.png"):
    assert (tmp / "reports" / f).exists(), f
print("SMOKE TEST PASSED (mock data only). Temp dir:", tmp)
shutil.rmtree(tmp)
