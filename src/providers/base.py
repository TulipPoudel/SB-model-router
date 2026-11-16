from __future__ import annotations
import time
from dataclasses import dataclass, field
import requests


class ProviderConfigError(RuntimeError):
    """Raised for missing API keys etc. Aborts a run cleanly (nothing is cached)."""


@dataclass
class GenResult:
    text: str | None
    input_tokens: int | None
    output_tokens: int | None
    latency_ms: float | None
    status: str                    # "ok" | "error"
    error: str | None = None
    meta: dict = field(default_factory=dict)


class BaseProvider:
    name = "base"

    def generate(self, prompt: str, model_config: dict) -> GenResult:
        raise NotImplementedError

    @staticmethod
    def post_json(url, headers, payload, timeout=180, max_retries=5):
        """POST with backoff on 429/5xx. Returns (json|None, latency_ms_of_last_attempt|None, error|None).
        Latency is that of the final (successful) HTTP request only, so backoff sleeps are excluded."""
        err = None
        for attempt in range(max_retries):
            t0 = time.perf_counter()
            try:
                r = requests.post(url, headers=headers, json=payload, timeout=timeout)
            except requests.RequestException as e:
                err = f"network error: {e}"
                time.sleep(2 ** attempt)
                continue
            dt = (time.perf_counter() - t0) * 1000
            if r.status_code == 200:
                return r.json(), dt, None
            err = f"HTTP {r.status_code}: {r.text[:300]}"
            if r.status_code in (429, 500, 502, 503, 504):
                try:
                    wait = float(r.headers.get("retry-after", 0))
                except ValueError:
                    wait = 0
                time.sleep(min(max(wait, 2 ** attempt * 2), 90))
                continue
            return None, dt, err
        return None, None, err
