import os
from pathlib import Path

ROOT = Path(os.environ.get("ROUTER_ROOT", Path(__file__).resolve().parents[1]))
CONFIG = ROOT / "config"
DATA = ROOT / "data"
CACHE = ROOT / "cache"
MODELS = ROOT / "models"
REPORTS = ROOT / "reports"
FIGURES = REPORTS / "figures"
DB_PATH = CACHE / "benchmark.sqlite"

TASKS_FILE = DATA / "benchmark_tasks.jsonl"
RESPONSES_FILE = DATA / "responses.jsonl"
JUDGE_FILE = DATA / "judge_scores.jsonl"
HUMAN1_FILE = DATA / "human_scores_pass1.jsonl"
HUMAN2_FILE = DATA / "human_scores_pass2.jsonl"
HUMAN_TASKS_FILE = DATA / "human_validation_tasks.json"
PUBLIC_MANIFEST = DATA / "public_sources_manifest.yaml"
PUBLIC_SOURCES_DIR = DATA / "public_sources"
