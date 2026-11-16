import pandas as pd, numpy as np
from src.router.classifier import best_value_labels, oof_proba, _splits, select_threshold
from src.router.fallback import apply_fallback
from src.router.rules import rule_route, infer_category
from src.evaluation.scoring import weighted_score, RUBRICS

T = ["cheap", "medium", "strong"]


def test_label_example_from_spec():
    w = pd.DataFrame({"q_cheap": [88], "q_medium": [91], "q_strong": [95], "c_cheap": [1.0], "c_medium": [2.0], "c_strong": [3.0]}, index=["t"])
    assert best_value_labels(w, T, 5)["t"] == "medium"          # A is 7 below -> out, B in, cheaper than C


def test_label_prefers_cheap_when_within_tolerance():
    w = pd.DataFrame({"q_cheap": [93], "q_medium": [91], "q_strong": [95], "c_cheap": [1.0], "c_medium": [2.0], "c_strong": [3.0]}, index=["t"])
    assert best_value_labels(w, T, 5)["t"] == "cheap"


def test_fallback_policy():
    assert apply_fallback("strong", 0.1, 0.7, T) == "strong"
    assert apply_fallback("cheap", 0.9, 0.7, T) == "cheap"
    assert apply_fallback("cheap", 0.5, 0.7, T) == "medium"
    assert apply_fallback("medium", 0.5, 0.7, T) == "strong"


def test_grouped_split_has_no_group_leakage():
    groups = np.array([f"g{i // 3}" for i in range(30)])
    y = np.array((["cheap", "medium", "strong"] * 10))
    for tr, te in _splits(np.arange(30), y, groups, 5, 0):
        assert not set(groups[tr]) & set(groups[te])


def test_oof_runs_and_rows_sum_to_one():
    texts = [f"summarise meeting notes item {i}" if i % 2 else f"extract json fields invoice {i}" for i in range(24)]
    y = ["cheap" if i % 2 == 0 else "strong" for i in range(24)]
    P = oof_proba(texts, y, [f"g{i}" for i in range(24)], T, 4, 0)
    assert np.allclose(P.sum(axis=1), 1.0)


def test_rules_and_scoring():
    assert infer_category("Please write an email to my supplier") == "email_draft"
    assert rule_route({"category": "data_extraction", "input": "short invoice", "requirements": ["a"], "task_description": "x"}) == "cheap"
    assert weighted_score("email_v1", {k: 5 for k in RUBRICS["email_v1"]["criteria"]}) == 100
    assert all(abs(sum(w for w, _ in r["criteria"].values()) - 1) < 1e-9 for r in RUBRICS.values())
