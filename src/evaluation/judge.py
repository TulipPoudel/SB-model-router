from __future__ import annotations
import json, random, re
from src.benchmark.cache import ResponseCache
from src.benchmark.run import cached_generate, load_tasks
from src.config import load_models, get_model_cfg
from src.paths import DB_PATH, JUDGE_FILE, RESPONSES_FILE
from src.evaluation.scoring import RUBRICS, weighted_score, criteria_keys

LABELS = ["A", "B", "C"]

JUDGE_TEMPLATE = """You are an impartial expert evaluator. Score three anonymous responses to the same task.

TASK DESCRIPTION:
{task_description}

SOURCE INPUT:
{input}

REQUIREMENTS GIVEN TO THE MODELS:
{requirements}

REFERENCE - FACTS A GOOD RESPONSE SHOULD REFLECT:
{facts}

RUBRIC (score every criterion from 1 to 5; 1 = very poor, 3 = adequate, 5 = excellent):
{rubric}
Criteria keys: {keys}

{responses}

EVALUATION RULES:
- Compare every response against the SOURCE INPUT and the reference facts, not against each other's claims.
- Score each response independently, using the rubric only.
- Do NOT reward unnecessary length; verbosity that breaks a stated length limit should be penalised.
- Penalise unsupported claims, invented details and violated requirements.
- Do not try to guess which provider or model wrote a response.
- Keep each justification to one short sentence.

Return ONLY strict JSON (no markdown, no commentary) in exactly this shape:
{{"responses": {{"A": {{"criteria": {{"<criterion_key>": {{"score": <int 1-5>, "justification": "<short>"}}}}}}, "B": {{...}}, "C": {{...}}}}}}"""


def build_judge_prompt(task: dict, labelled: dict, rubric_id: str) -> str:
    rub = "\n".join(f"- {k} (weight {int(w * 100)}%): {d}" for k, (w, d) in RUBRICS[rubric_id]["criteria"].items())
    resp = "\n\n".join(f"=== RESPONSE {lab} ===\n{txt}\n=== END RESPONSE {lab} ===" for lab, txt in labelled.items())
    return JUDGE_TEMPLATE.format(
        task_description=task["task_description"], input=task["input"],
        requirements="\n".join(f"- {r}" for r in task["requirements"]),
        facts="\n".join(f"- {f}" for f in task["expected_facts"]), rubric=rub,
        keys=", ".join(criteria_keys(rubric_id)), responses=resp)


def parse_judge_json(text: str, rubric_id: str) -> dict:
    t = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    data = json.loads(t[t.index("{"): t.rindex("}") + 1])["responses"]
    keys = criteria_keys(rubric_id)
    out = {}
    for lab in LABELS:
        crit = {}
        just = {}
        for k in keys:
            s = data[lab]["criteria"][k]
            sc = int(s["score"] if isinstance(s, dict) else s)
            if not 1 <= sc <= 5:
                raise ValueError(f"score out of range: {lab}/{k}={sc}")
            crit[k] = sc
            just[k] = s.get("justification", "") if isinstance(s, dict) else ""
        out[lab] = {"criteria": crit, "justifications": just, "total_score": weighted_score(rubric_id, crit)}
    return out


def _load_responses(path=RESPONSES_FILE):
    by_task = {}
    for l in open(path, encoding="utf-8"):
        r = json.loads(l)
        by_task.setdefault(r["task_id"], {})[r["tier"]] = r
    return by_task


def run_judge(passes=1, seed=42, max_attempts=3):
    cfg = load_models()
    tiers = cfg["tiers"]
    jcfg = get_model_cfg(cfg, "judge")
    contestants = {get_model_cfg(cfg, t)["model_id"] for t in tiers}
    if jcfg["model_id"] in contestants:
        raise SystemExit(f"Judge model {jcfg['model_id']} is also a contestant; pick a different judge.")
    cache = ResponseCache(DB_PATH)
    tasks = load_tasks()
    resp = _load_responses()
    n_done = n_skip = 0
    with open(JUDGE_FILE, "w", encoding="utf-8") as f:
        for t in tasks:
            r = resp.get(t["task_id"], {})
            if any(r.get(x, {}).get("status") != "ok" for x in tiers):
                print(f"skip {t['task_id']}: incomplete model responses"); n_skip += 1
                continue
            per_pass = []
            for p in range(passes):
                order = list(tiers)
                random.Random(f"{seed}-{t['task_id']}-{p}").shuffle(order)   # randomised labels, reproducible
                label_map = dict(zip(LABELS, order))
                prompt = build_judge_prompt(t, {lab: r[tier]["response"] for lab, tier in label_map.items()}, t["rubric_id"])
                parsed = None
                for attempt in range(max_attempts):
                    row, _ = cached_generate(cache, jcfg, f"JUDGE::{t['task_id']}", prompt, jcfg["prompt_version"],
                                             extra_gen={"attempt": attempt})
                    if row["status"] != "ok":
                        print(f"judge error {t['task_id']}: {row['error'][:100]}"); continue
                    try:
                        parsed = parse_judge_json(row["response"], t["rubric_id"]); break
                    except (ValueError, KeyError, json.JSONDecodeError) as e:
                        print(f"judge JSON invalid {t['task_id']} attempt {attempt}: {e}")
                if parsed:
                    per_pass.append({"label_map": label_map, "responses": parsed})
            if not per_pass:
                n_skip += 1; continue
            keys = criteria_keys(t["rubric_id"])
            scores = {}
            for tier in tiers:
                crit = {k: sum(pp["responses"][lab]["criteria"][k] for pp in per_pass
                               for lab, tr in pp["label_map"].items() if tr == tier) / len(per_pass) for k in keys}
                scores[tier] = {"criteria": crit, "total_score": weighted_score(t["rubric_id"], crit)}
            f.write(json.dumps({"task_id": t["task_id"], "rubric_id": t["rubric_id"], "judge_model": jcfg["model_id"],
                                "n_passes": len(per_pass), "passes": per_pass, "scores": scores}) + "\n")
            n_done += 1
    print(f"Judged {n_done} tasks ({n_skip} skipped) -> {JUDGE_FILE}")


