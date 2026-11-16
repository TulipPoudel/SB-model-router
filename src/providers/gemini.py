from __future__ import annotations
import os
from .base import BaseProvider, GenResult, ProviderConfigError

URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


class GeminiProvider(BaseProvider):
    name = "google"

    def __init__(self):
        pass

    def _key(self, model_config):
        env = model_config.get("api_key_env", "GEMINI_API_KEY")
        key = os.environ.get(env)
        if not key:
            raise ProviderConfigError(f"{env} is not set (see .env.example).")
        return key

    def generate(self, prompt, model_config):
        gc = {"temperature": model_config["temperature"], "maxOutputTokens": model_config["max_tokens"]}
        budget = model_config.get("extra", {}).get("thinking_budget")
        if budget is not None:
            gc["thinkingConfig"] = {"thinkingBudget": budget}
        payload = {"contents": [{"role": "user", "parts": [{"text": prompt}]}], "generationConfig": gc}
        data, latency, err = self.post_json(URL.format(model=model_config["model_id"]),
                                            {"x-goog-api-key": self._key(model_config)}, payload)
        if data is None:
            return GenResult(None, None, None, latency, "error", err)
        try:
            cand = data["candidates"][0]
            parts = cand.get("content", {}).get("parts", [])
            text = "".join(p.get("text", "") for p in parts)
            u = data.get("usageMetadata") or {}
            in_tok = u.get("promptTokenCount")
            # thinking tokens are billed as output tokens
            out_tok = None if u.get("candidatesTokenCount") is None and u.get("thoughtsTokenCount") is None \
                else (u.get("candidatesTokenCount") or 0) + (u.get("thoughtsTokenCount") or 0)
            if not text.strip():
                return GenResult(None, in_tok, out_tok, latency, "error",
                                 f"empty content (finishReason={cand.get('finishReason')})")
            return GenResult(text, in_tok, out_tok, latency, "ok", meta={"finish_reason": cand.get("finishReason")})
        except (KeyError, IndexError) as e:
            return GenResult(None, None, None, latency, "error", f"unexpected response shape: {e}")
