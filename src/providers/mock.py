"""TEST-ONLY provider. Produces fake, deterministic outputs so the pipeline can be smoke-tested offline.
Never use it for real results (it is not referenced by config/models.yaml)."""
from __future__ import annotations
import hashlib, json, random, re
from .base import BaseProvider, GenResult

_BASE = {"cheap": 62, "medium": 75, "strong": 85}


def _tier(model_id):
    for t in _BASE:
        if t in model_id:
            return t
    return "medium"


class MockProvider(BaseProvider):
    name = "mock"

    def generate(self, prompt, model_config):
        rng = random.Random(hashlib.sha256((prompt + model_config["model_id"]).encode()).hexdigest())
        tier = _tier(model_config["model_id"])
        if "Criteria keys:" in prompt:
            keys = re.search(r"Criteria keys: (.*)", prompt).group(1).split(", ")
            labels = re.findall(r"=== RESPONSE (\w) ===", prompt)
            out = {"responses": {}}
            for lab in labels:
                seg = prompt.split(f"=== RESPONSE {lab} ===")[1]
                t = re.search(r"\[mock:(\w+)\]", seg)
                base = _BASE.get(t.group(1) if t else "medium", 70)
                out["responses"][lab] = {"criteria": {
                    k: {"score": max(1, min(5, round(base / 20 + rng.uniform(-1.2, 1.2)))), "justification": "mock"}
                    for k in keys}}
            text = "```json\n" + json.dumps(out) + "\n```"
        else:
            text = f"[mock:{tier}] " + "lorem ipsum " * rng.randint(20, 60)
        return GenResult(text, len(prompt) // 4, len(text) // 4, rng.uniform(300, 900) * (1 + 2 * (tier == "strong")), "ok")
