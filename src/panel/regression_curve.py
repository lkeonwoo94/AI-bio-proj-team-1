"""회귀 기반 최소 패널 크기별 성능 곡선 (한계 6번 후속).

`src/panel/curve.py:run_panel_curve` 의 회귀 버전이다. 분류 쪽은
LabelBinarizer/threshold/ROC-AUC 를 쓰지만 여기는 label 이 연속형이라
KFold + R²/Spearman rho 로 바뀐다 — 그 외 "패널은 training fold 안에서만
고른다"는 §13 원칙은 동일하게 지킨다.
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from sklearn.model_selection import GridSearchCV, KFold

from src.config import load_config
from src.evaluation.metrics_regression import evaluate_regression
from src.models.zoo import ModelSpec, extract_importance


def _fit_best(spec: ModelSpec, X, y, inner_folds: int, seed: int, n_jobs: int):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ConvergenceWarning)
        search = GridSearchCV(
            spec.build(), spec.param_grid, scoring="r2",
            cv=KFold(n_splits=inner_folds, shuffle=True, random_state=seed),
            n_jobs=n_jobs, refit=True, error_score="raise",
        )
        search.fit(X, y)
    return search


def run_panel_curve_regression(
    X: pd.DataFrame,
    y: pd.Series,
    spec: ModelSpec,
    target: str,
    sizes: list[int],
    n_jobs: int = -1,
    verbose: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """패널 크기별 회귀 성능과 fold 별 선택 feature 목록.

    Returns
    -------
    metrics : fold x panel_size 성능 (r2, spearman_rho, rmse, mae)
    picks   : fold x panel_size 에서 선택된 feature 목록
    """
    cfg = load_config("experiment")["cv"]
    seed = load_config("experiment")["seed"]
    outer_folds = cfg["outer_folds"]
    inner_folds = cfg["inner_folds"]

    X_values = X.to_numpy()
    y_values = y.to_numpy()
    feature_names = np.asarray(X.columns)

    outer_kf = KFold(n_splits=outer_folds, shuffle=True, random_state=seed)
    metric_rows, pick_rows = [], []

    for fold, (tr, te) in enumerate(outer_kf.split(X_values)):
        X_tr, X_te = X_values[tr], X_values[te]
        y_tr, y_te = y_values[tr], y_values[te]

        # --- 전체 feature 기준 (Reference) ---
        search = _fit_best(spec, X_tr, y_tr, inner_folds, seed, n_jobs)
        best = search.best_estimator_
        kept_mask = best.named_steps["filter"].get_support()
        kept_names = feature_names[kept_mask]

        pred_te = best.predict(X_te)
        row = evaluate_regression(y_te, pred_te)
        row.update({"fold": fold, "panel_size": "all", "target": target,
                    "model": spec.name, "n_features": int(kept_mask.sum())})
        metric_rows.append(row)

        # --- training fold 중요도로 상위 k 선택 ---
        imp = extract_importance(best, spec.importance)
        if imp is None:
            raise ValueError(f"{spec.name} 은 중요도를 제공하지 않아 패널 분석에 쓸 수 없습니다.")
        order = np.argsort(imp)[::-1]

        for k in sizes:
            top_idx = order[:k]
            picked = kept_names[top_idx]
            cols = np.flatnonzero(np.isin(feature_names, picked))
            Xk_tr, Xk_te = X_values[np.ix_(tr, cols)], X_values[np.ix_(te, cols)]

            search_k = _fit_best(spec, Xk_tr, y_tr, inner_folds, seed, n_jobs)
            best_k = search_k.best_estimator_
            pred_k = best_k.predict(Xk_te)

            row = evaluate_regression(y_te, pred_k)
            row.update({"fold": fold, "panel_size": k, "target": target,
                        "model": spec.name, "n_features": len(cols)})
            metric_rows.append(row)
            pick_rows.append(pd.DataFrame({"fold": fold, "panel_size": k,
                                           "target": target, "feature": picked}))

        if verbose:
            got = {r["panel_size"]: r["spearman_rho"] for r in metric_rows if r["fold"] == fold}
            desc = " | ".join(f"{k}:{v:.3f}" for k, v in got.items())
            print(f"  fold {fold}: {desc}")

    return pd.DataFrame(metric_rows), pd.concat(pick_rows, ignore_index=True)
