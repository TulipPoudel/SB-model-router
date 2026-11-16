import tempfile
from src.benchmark.cache import ResponseCache
from src.benchmark.run import cached_generate
from src.providers import REGISTRY, GenResult


class Stub:
    calls = 0
    def generate(self, prompt, cfg):
        Stub.calls += 1
        return GenResult("hello", 10, 5, 100.0, "ok")


class Fail:
    def generate(self, prompt, cfg):
        return GenResult(None, None, None, 5.0, "error", "boom")


CFG = {"provider": "stub", "model_id": "m", "temperature": 0, "max_tokens": 10, "extra": {}}


def test_key_is_stable_and_sensitive():
    k = ResponseCache.make_key
    a = k("T1", "p", "m", "v1", {"t": 0}, "h")
    assert a == k("T1", "p", "m", "v1", {"t": 0}, "h")
    assert a != k("T1", "p", "m", "v2", {"t": 0}, "h") and a != k("T1", "p", "m", "v1", {"t": 0.5}, "h")


def test_success_is_cached_exactly_once():
    REGISTRY["stub"] = Stub; Stub.calls = 0
    c = ResponseCache(tempfile.mkdtemp() + "/c.sqlite")
    r1, hit1 = cached_generate(c, CFG, "T1", "prompt", "v1")
    r2, hit2 = cached_generate(c, CFG, "T1", "prompt", "v1")
    assert (hit1, hit2, Stub.calls) == (False, True, 1) and r2["response"] == "hello"


def test_errors_are_retried_and_never_overwrite_success():
    c = ResponseCache(tempfile.mkdtemp() + "/c.sqlite")
    REGISTRY["stub"] = Fail
    row, _ = cached_generate(c, CFG, "T1", "p", "v1"); assert row["status"] == "error"
    REGISTRY["stub"] = Stub; Stub.calls = 0
    row, hit = cached_generate(c, CFG, "T1", "p", "v1"); assert row["status"] == "ok" and not hit
    key = c.make_key("T1", "stub", "m", "v1", {"temperature": 0, "max_tokens": 10, "extra": {}},
                     __import__("src.benchmark.prompts", fromlist=["x"]).prompt_hash("p"))
    c.put(key, "T1", "stub", "m", "v1", {}, "h", Fail().generate("", {}))   # late error must not clobber
    assert c.get(key)["status"] == "ok"
