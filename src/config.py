from __future__ import annotations
import yaml
from dotenv import load_dotenv
from src.paths import ROOT, CONFIG

load_dotenv(ROOT / ".env")


def _load(name):
    return yaml.safe_load((CONFIG / name).read_text())


def load_models():
    return _load("models.yaml")


def load_pricing():
    return _load("pricing.yaml")


def load_router_cfg():
    return _load("router.yaml")["router"]


def get_model_cfg(cfg, key: str) -> dict:
    """key is a tier name ('cheap'...) or 'judge'. Returns a flat config dict."""
    if key == "judge":
        m = dict(cfg["judge"])
    else:
        m = dict(cfg["models"][key])
        m["temperature"] = cfg["generation"]["temperature"]
        m["max_tokens"] = cfg["generation"]["max_tokens"]
    m["tier"] = key
    m.setdefault("extra", {})
    return m


def gen_config(mcfg: dict) -> dict:
    """The part of the config that affects the output -> part of the cache key."""
    return {"temperature": mcfg["temperature"], "max_tokens": mcfg["max_tokens"], "extra": mcfg.get("extra", {})}
