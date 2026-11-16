from __future__ import annotations
import warnings
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold, StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from src.paths import MODELS
from src.router.fallback import apply_fallback


def task_text(t: dict, with_meta=True) -> str:
    """Router input: task description + requirements (+ category/difficulty tokens). Never any quality score."""
    meta = f"category_{t['category']} difficulty_{t['difficulty']} " if with_meta else ""
    return meta + t["task_description"] + " " + " ".join(t["requirements"])


# ---------- labels ----------
def best_value_labels(wide: pd.DataFrame, tiers, tol: float) -> pd.Series:
    """Cheapest model whose quality is within `tol` points of the best model on that task."""
    labels = {}
    for tid, r in wide.iterrows():
        q = {t: r[f"q_{t}"] for t in tiers}
        best = max(q.values())
        eligible = [t for t in tiers if q[t] >= best - tol]
        labels[tid] = min(eligible, key=lambda t: (r[f"c_{t}"], tiers.index(t)))
    return pd.Series(labels, name="label")


# ---------- model ----------
class _Const:
    def __init__(self, c): self.classes_ = np.array([c])
    def predict_proba(self, X): return np.ones((len(X), 1))


def make_pipeline(seed=42):
    return Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=3000, min_df=2, sublinear_tf=True)),
        ("clf", LogisticRegression(max_iter=2000, class_weight="balanced", random_state=seed)),
    ])


def fit(texts, y, seed=42):
    if len(set(y)) < 2:
        return _Const(y[0])
    return make_pipeline(seed).fit(texts, y)


def proba_frame(model, texts, tiers) -> pd.DataFrame:
    P = model.predict_proba(texts)
    df = pd.DataFrame(0.0, index=range(len(texts)), columns=tiers)
    for j, c in enumerate(model.classes_):
        df[c] = P[:, j]
    return df


def _splits(texts, y, groups, n_splits, seed):
    k = max(2, min(n_splits, len(set(groups))))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            return list(StratifiedGroupKFold(n_splits=k, shuffle=True, random_state=seed).split(texts, y, groups))
        except ValueError:
            return list(GroupKFold(n_splits=k).split(texts, y, groups))


def oof_proba(texts, y, groups, tiers, n_splits, seed) -> pd.DataFrame:
    """Out-of-fold probabilities; a group is never in train and test together (anti-leakage)."""
    out = pd.DataFrame(0.0, index=range(len(texts)), columns=tiers)
    texts, y = np.asarray(texts, dtype=object), np.asarray(y, dtype=object)
    for tr, te in _splits(texts, y, groups, n_splits, seed):
        m = fit(list(texts[tr]), list(y[tr]), seed)
        out.iloc[te] = proba_frame(m, list(texts[te]), tiers).values
    return out


# ---------- threshold selection (validation data only) ----------
def realise(wide: pd.DataFrame, chosen, tiers):
    idx = {t: i for i, t in enumerate(tiers)}
    pick = np.array([idx[c] for c in chosen])
    Q, C, L = (wide[[f"{p}_{t}" for t in tiers]].values for p in "qcl")
    r = np.arange(len(wide))
    return Q[r, pick], C[r, pick], L[r, pick]


def choose_chosen(proba: pd.DataFrame, thr: float, tiers):
    pred = proba.idxmax(axis=1)
    conf = proba.max(axis=1)
    return [apply_fallback(p, c, thr, tiers) for p, c in zip(pred, conf)]


def select_threshold(proba, wide, thresholds, tiers, tol):
    """Lowest mean cost among thresholds whose mean quality >= always-strongest mean quality - tol.
    If none qualifies, the threshold with the highest mean quality. Uses validation (inner OOF) data only."""
    ref = wide[f"q_{tiers[-1]}"].mean() - tol
    stats = []
    for thr in thresholds:
        q, c, _ = realise(wide, choose_chosen(proba, thr, tiers), tiers)
        stats.append((thr, q.mean(), c.mean()))
    ok = [s for s in stats if s[1] >= ref]
    return min(ok, key=lambda s: (s[2], -s[0]))[0] if ok else max(stats, key=lambda s: (s[1], s[0]))[0]


def nested_cv(texts, y, groups, wide, tiers, tol, thresholds, outer, inner, seed) -> pd.DataFrame:
    """Outer grouped CV gives an honest prediction for every task; the threshold is chosen by inner grouped CV
    on the outer-training portion only, so the outer test fold never influences it."""
    texts, y = np.asarray(texts, dtype=object), np.asarray(y, dtype=object)
    groups = np.asarray(groups)
    res = pd.DataFrame(index=range(len(texts)), columns=[*tiers, "pred", "conf", "threshold", "fold"], dtype=object)
    for f, (tr, te) in enumerate(_splits(texts, y, groups, outer, seed)):
        ip = oof_proba(list(texts[tr]), list(y[tr]), groups[tr], tiers, inner, seed)
        thr = select_threshold(ip, wide.iloc[tr].reset_index(drop=True), thresholds, tiers, tol)
        m = fit(list(texts[tr]), list(y[tr]), seed)
        P = proba_frame(m, list(texts[te]), tiers)
        for k, i in enumerate(te):
            res.loc[i, tiers] = P.iloc[k].values
            res.loc[i, "pred"], res.loc[i, "conf"] = P.iloc[k].idxmax(), P.iloc[k].max()
            res.loc[i, "threshold"], res.loc[i, "fold"] = thr, f
    return res


def save_router(model, tiers, threshold, tol, path=MODELS / "router.pkl", extra=None):
    joblib.dump({"pipeline": model, "tiers": tiers, "threshold": threshold, "tolerance": tol,
                 "trained_at": datetime.now().isoformat(timespec="seconds"), **(extra or {})}, path)


def load_router(path=MODELS / "router.pkl"):
    return joblib.load(path)


def route_text(bundle: dict, text: str):
    """Returns (final_tier, predicted_tier, confidence, escalated)."""
    tiers = bundle["tiers"]
    P = proba_frame(bundle["pipeline"], [text], tiers).iloc[0]
    pred, conf = P.idxmax(), float(P.max())
    final = apply_fallback(pred, conf, bundle["threshold"], tiers)
    return final, pred, conf, final != pred


def explain(model, text: str, cls: str, k=6):
    """Top TF-IDF terms pushing toward `cls` (None for constant models)."""
    if isinstance(model, _Const):
        return []
    vec, clf = model.named_steps["tfidf"], model.named_steps["clf"]
    x = vec.transform([text]).toarray()[0]
    j = list(clf.classes_).index(cls) if cls in clf.classes_ else None
    if j is None:
        return []
    coef = clf.coef_[j] if len(clf.classes_) > 2 else (clf.coef_[0] if j == 1 else -clf.coef_[0])
    contrib = x * coef
    names = np.array(vec.get_feature_names_out())
    top = np.argsort(-contrib)[:k]
    return [(names[i], float(contrib[i])) for i in top if contrib[i] > 0]
