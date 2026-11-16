from __future__ import annotations
import os
from .base import BaseProvider, GenResult, ProviderConfigError

URL = "https://api.groq.com/openai/v1/chat/completions"


class GroqProvider(BaseProvider):
    name = "groq"

    def __init__(self):
        self.key = os.environ.get("GROQ_API_KEY")
        if not self.key:
            raise ProviderConfigError("GROQ_API_KEY is not set (see .env.example).")

    def generate(self, prompt, model_config):
        payload = {
            "model": model_config["model_id"],
            "messages": [{"role": "user", "content": prompt}],
            "temperature": model_config["temperature"],
            "max_completion_tokens": model_config["max_tokens"],
        }
        effort = model_config.get("extra", {}).get("reasoning_effort")
        if effort:
            payload["reasoning_effort"] = effort
        data, latency, err = self.post_json(URL, {"Authorization": f"Bearer {self.key}"}, payload)
        if data is None:
            return GenResult(None, None, None, latency, "error", err)
        try:
            ch = data["choices"][0]
            text = ch["message"].get("content")
            usage = data.get("usage") or {}
            if not text or not text.strip():
                return GenResult(None, usage.get("prompt_tokens"), usage.get("completion_tokens"), latency,
                                 "error", f"empty content (finish_reason={ch.get('finish_reason')})")
            return GenResult(text, usage.get("prompt_tokens"), usage.get("completion_tokens"), latency, "ok",
                             meta={"finish_reason": ch.get("finish_reason")})
        except (KeyError, IndexError) as e:
            return GenResult(None, None, None, latency, "error", f"unexpected response shape: {e}")
