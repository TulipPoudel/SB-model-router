from .base import BaseProvider, GenResult, ProviderConfigError

REGISTRY: dict = {}   # tests can register stub providers here


def get_provider(name: str) -> BaseProvider:
    n = name.lower()
    if n in REGISTRY:
        return REGISTRY[n]()
    if n == "groq":
        from .groq import GroqProvider
        return GroqProvider()
    if n in ("google", "gemini"):
        from .gemini import GeminiProvider
        return GeminiProvider()
    if n == "mock":
        from .mock import MockProvider
        return MockProvider()
    raise ValueError(f"Unknown provider '{name}'. Add it in src/providers/__init__.py.")
