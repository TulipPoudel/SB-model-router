import pytest
from src.cost import estimate_cost

P = {"prices_usd_per_million_tokens": {"m": {"input": 0.30, "output": 2.50}}}


def test_formula():
    assert estimate_cost("m", 1_000_000, 1_000_000, P) == pytest.approx(2.80)
    assert estimate_cost("m", 2000, 500, P) == pytest.approx(0.0006 + 0.00125)


def test_missing_tokens_not_fabricated():
    assert estimate_cost("m", None, 10, P) is None
