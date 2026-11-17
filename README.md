# Springbase Smart Model Router

**Assignment chosen:** Assignment 1, The Smart Model Router (stretch goal included: confidence score + fallback).

A small, reproducible system that picks one of three LLMs for each task, aiming for the cheapest model that still meets a quality bar. If the router is unsure, it escalates to a stronger model.

## Headline result

On this 60-task benchmark, **no router saved money compared with always using the strongest model.** ML + fallback matched its quality at about the same cost and slightly lower mean latency. See "Results" and "Limitations" below.

## 1. Setup

Requires Python 3.12.

```bash
python -m venv .venv
source .venv/bin/activate        # fish: source .venv/bin/activate.fish
pip install -r requirements.txt
```

Create a `.env` file in the repo root with your own keys (never commit it; it is listed in `.gitignore`):

```
GROQ_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
JUDGE_API_KEY=your_key_here
```

Check the exact variable names in `src/config.py` and `config/models.yaml`.

## 2. Models used and why

| Tier | Model | Provider | Price per 1M tokens (in / out) |
|---|---|---|---|
| cheap | openai/gpt-oss-20b | Groq | $0.075 / $0.30 |
| medium | gemini-3.5-flash-lite | Gemini API | $0.30 / $2.50 |
| strong | openai/gpt-oss-120b | Groq | $0.15 / $0.60 |
| judge | gemini-3.1-flash-lite | Gemini API | $0.25 / $1.50 |

Why these: they are low-cost, fast and accessible on free or low-cost tiers, and they span a range of sizes and vendors. The models were changed partway through because the Gemini free daily quota ran out, so the final set differs from the first plan.

Prices were taken from public pages and recorded in `config/pricing.yaml` (`pricing_checked_at: 2026-11-15`). Check them against the providers' official pricing pages before relying on them.

**Important:** the tier names do not follow price order. The "medium" model costs about 1.75x the "strong" model, so routing to medium raises cost. This is the main reason the router saves nothing here.

## 3. How the benchmark works

- 60 tasks: 20 based on public UN General Debate (session 79) statements and 40 hand-written synthetic scenarios.
- 5 categories, 12 tasks each: meeting summary, email draft, research brief, slide outline, data extraction.
- Each category has 4 easy, 4 medium and 4 hard tasks. Difficulty labels were assigned by the author.
- Public tasks: 8 meeting, 6 research, 4 extraction, 2 slide. The rest are synthetic.
- The public facts come from the statements on gadebate.un.org. The manifest links point to the matching UN Digital Library records. Dataset: UN Dag Hammarskjöld Library, General debate speeches dataset, v3 (Jan 2026). Excerpts are capped at 700 words.
- Task files: `data/benchmark_tasks.jsonl`, `data/public_sources_manifest.yaml`.

Each of the 60 tasks is run on all 3 models, giving 180 responses (`data/responses.jsonl`).

## 4. How evaluation works

- **Rubrics** (`src/evaluation/scoring.py`): each category has 5 or 4 weighted criteria, each rated 1-5. The code computes a weighted total from 20 to 100.
- **LLM judge:** scores every response against the rubric. Responses are shown with shuffled A/B/C labels so the judge cannot tell which model wrote them. Results are in `data/judge_scores.jsonl`.
- **Human validation:** one annotator scored 15 tasks (3 per category) twice (`data/human_scores_pass1.jsonl`, `data/human_scores_pass2.jsonl`). The judge is compared against the mean of the two passes (`scripts/validate_human.py`).
- **Failure definition:** a strategy fails on a task if its chosen model's judge score is more than 5 points below the strongest model's score on that task. By construction, always-strongest has 0 failures.

## 5. How the router works

- **Rule router:** a simple keyword/category rule baseline.
- **ML router:** TF-IDF features of the task description plus logistic regression. Training labels are "the cheapest model within 5 points of the best score" (distribution: cheap 25, medium 12, strong 23). The saved model is `models/router.pkl`.
- **Confidence + fallback:** if the router's confidence is below the threshold (0.55), the request escalates one tier up.
- The router sees only the task description, not the input text.
- The strategy comparison uses out-of-fold predictions, so the router is not scored on tasks it trained on.

## 6. How cached responses are used

Every model call is stored in `cache/benchmark.sqlite`. The cache key includes the model ID, never the API key. Rerunning the benchmark reuses cached answers and only calls a provider for anything missing. Router training and evaluation read the stored responses and scores.

## 7. Rerun and reproduce

```bash
python -m src.main --help              # list all commands
python -m src.main verify-models       # one tiny call per model (needs keys)
python -m src.main run-benchmark       # uses the cache
python -m src.main judge
python -m src.main train-router
python -m src.main evaluate > reports/evaluate_output.txt
python scripts/validate_human.py       # human agreement + judge validation
python scripts/model_costs.py          # per-model cost, tokens, latency
pytest                                 # unit tests
```

Run `python -m src.main <command> --help` for each command's options. Reports are written to `reports/`.

## 8. Results (60 tasks)

| Strategy | Quality | Cost | Mean / p95 latency | Failures |
|---|---:|---:|---:|---:|
| Always cheapest | 89.9 | $0.019 | 1,499 / 2,589 ms | 26 |
| Always strongest | 94.1 | $0.032 | 2,119 / 3,406 ms | 0 (by construction) |
| Rule router | 94.2 | $0.043 | 1,924 / 3,562 ms | 10 |
| ML router | 93.8 | $0.040 | 1,921 / 3,954 ms | 10 |
| ML + fallback | 93.8 | $0.033 | 1,895 / 3,359 ms | 5 |

- Only always-cheapest is cheaper than always-strongest (about 41% lower cost), but it loses about 4.2 quality points and has 26 failures.
- ML + fallback costs about 4.5% more than always-strongest, with the same quality within noise and about 11% lower mean latency.
- Fallback escalates 58.3% of requests, so its final mix is 6.7% cheap, 36.7% medium and 56.7% strong. It mostly rebuilds the strong baseline.
- Quality gaps of about 0.25 points on 60 tasks are noise.

## 9. Validation of the human scores and the judge

- **Human self-agreement** (Pass 1 vs Pass 2, 45 responses): same total score 8 (18%), within 5 points 13 (29%), within 10 points 26 (58%). Mean absolute difference 11.4, Pearson r 0.455. Per criterion (1-5): same score 45.4%, within 1 point 80.1%.
- **Pass 2 timing:** it was done 5.97 hours after Pass 1, so the required 24-hour gap was **not met** (`data/pass2_protocol.json`). Treat the agreement numbers as probably flattering.
- **Judge vs human:** the judge scores about 8.3 points higher than the human. Mean absolute error 11.5, Pearson r 0.53. It ranks response pairs the same way as the human in 18 of 29 comparisons (62%).
- **Reading:** the judge's error against the human is about the same as the human's error against themselves, but 62% pairwise agreement means it cannot reliably separate models.

## 10. Failure analysis

See `reports/error_analysis.md`. Main patterns:

- Confident wrong predictions skip fallback (EMAIL_012: cheap chosen at confidence 0.61, scored 73 against 100 for strong).
- Escalating one level can land on a worse, pricier model (SLIDE_002).
- Fallback helped on low-confidence cases such as SLIDE_008, SLIDE_009 and RES_002.
- The router picked medium on SLIDE_004 (easy), where cheap and strong scored higher.
- Slide and email descriptions look alike whatever the difficulty, so the router often cannot tell hard from easy.

## 11. Limitations

- 60 tasks is too few for production conclusions.
- Human validation uses one annotator on 15 tasks, and the 24-hour gap was not met.
- All quality scores come from an LLM judge with moderate agreement with the human.
- The judge and the medium model are both Gemini models, so the judge may slightly favour its own vendor.
- The router sees only the task description, not the input.
- Difficulty labels were assigned by the author.
- Latency depends on provider load at run time.
- Prices come from public pages, and some Gemini prices came from third-party sites.
- Four public data-extraction reference lists include metadata (speaker, date, session) that is not in the excerpt, although the task asked for null on unstated fields. The benchmark was not modified after seeing results.
- Models were changed after the Gemini free quota ran out.

## 12. Repo layout

```
config/      models, pricing and router settings
data/        tasks, manifest, responses, judge and human scores
cache/       SQLite response cache
models/      trained router (router.pkl)
reports/     evaluation output and error analysis
scripts/     helper scripts (validation, costs, UN source picker)
src/         benchmark, providers, evaluation, router, CLI
tests/       unit tests
demo/        demo app
```

## Secrets

No API keys are stored in this repo. Keep keys in `.env`, which is excluded by `.gitignore`.

## Testing

Run the unit tests (cache, cost calculation, data building and router logic, in `tests/`):

```bash
pytest -q
```

Last run: 12 passed in 0.59s. The tests do not call any model API.