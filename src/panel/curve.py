"""최소 패널 크기별 성능 곡선 (README §17-18).

누출을 피하는 핵심: 패널 유전자는 **각 outer fold 의 training data 에서만**
고른다. 전체 데이터로 상위 유전자를 뽑아 놓고 CV 를 돌리면 §13 위반이다.

따라서 fold 마다 선택되는 유전자가 다를 수 있고, 그 차이 자체가 §18 의
'안정성' 지표가 된다.
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from sklearn.model_selection import GridSearchCV, cross_val_predict

from src.cv.splitters import inner_cv, outer_splits
from src.evaluation.metrics import choose_threshold, evaluate
from src.labels.binarize import LabelBinarizer
from src.models.zoo import ModelSpec, extract_importance


def _fit_best(spec: ModelSpec, X, y, n_jobs: int):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ConvergenceWarning)
        search = GridSearchCV(spec.build(), spec.param_grid, scoring="roc_auc",
                              cv=inner_cv(), n_jobs=n_jobs, refit=True)
        search.fit(X, y)
    return search


def run_panel_curve(
    X: pd.DataFrame,
    y_raw: pd.Series,
    groups: pd.Series,
    spec: ModelSpec,
    target: str,
    sizes: list[int],
    scheme: str = "random",
    n_jobs: int = -1,
    verbose: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """패널 크기별 성능과 fold 별 선택 유전자를 반환한다.

    Returns
    -------
    metrics : fold × panel_size 성능
    picks   : fold × panel_size 에서 선택된 유전자 목록
    """
    X_values = X.to_numpy()
    feature_names = np.asarray(X.columns)
    y_strat = LabelBinarizer(target).fit_transform(y_raw)

    metric_rows, pick_rows = [], []

    for fold, (tr, te) in enumerate(outer_splits(y_strat.to_numpy(), groups, scheme=scheme)):
        binz = LabelBinarizer(target).fit(y_raw.iloc[tr])
        y_tr = binz.transform(y_raw.iloc[tr]).to_numpy()
        y_te = binz.transform(y_raw.iloc[te]).to_numpy()
        X_tr, X_te = X_values[tr], X_values[te]

        # --- 전체 feature 기준 (Reference) ---
        search = _fit_best(spec, X_tr, y_tr, n_jobs)
        best = search.best_estimator_
        kept_mask = best.named_steps["filter"].get_support()
        kept_names = feature_names[kept_mask]

        oof = cross_val_predict(best, X_tr, y_tr, cv=inner_cv(),
                                method="predict_proba", n_jobs=n_jobs)[:, 1]
        thr = choose_threshold(y_tr, oof)
        row = evaluate(y_te, best.predict_proba(X_te)[:, 1], threshold=thr)
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
            # 원본 X 에서 해당 열만 남긴다. 필터는 이미 통과했으므로 그대로 사용.
            cols = np.flatnonzero(np.isin(feature_names, picked))
            Xk_tr, Xk_te = X_values[np.ix_(tr, cols)], X_values[np.ix_(te, cols)]

            search_k = _fit_best(spec, Xk_tr, y_tr, n_jobs)
            best_k = search_k.best_estimator_
            oof_k = cross_val_predict(best_k, Xk_tr, y_tr, cv=inner_cv(),
                                      method="predict_proba", n_jobs=n_jobs)[:, 1]
            thr_k = choose_threshold(y_tr, oof_k)

            row = evaluate(y_te, best_k.predict_proba(Xk_te)[:, 1], threshold=thr_k)
            row.update({"fold": fold, "panel_size": k, "target": target,
                        "model": spec.name, "n_features": len(cols)})
            metric_rows.append(row)
            pick_rows.append(pd.DataFrame({"fold": fold, "panel_size": k,
                                           "target": target, "feature": picked}))

        if verbose:
            got = {r["panel_size"]: r["roc_auc"] for r in metric_rows if r["fold"] == fold}
            desc = " | ".join(f"{k}:{v:.3f}" for k, v in got.items())
            print(f"  fold {fold}: {desc}")

    return pd.DataFrame(metric_rows), pd.concat(pick_rows, ignore_index=True)


def panel_stability(picks: pd.DataFrame, size: int) -> pd.DataFrame:
    """같은 패널 크기에서 fold 간 유전자가 얼마나 일치하는지 (README §18 안정성)."""
    sub = picks[picks.panel_size == size]
    n_folds = sub.fold.nunique()
    counts = sub.groupby("feature").fold.nunique().sort_values(ascending=False)
    return pd.DataFrame({
        "feature": counts.index,
        "n_folds": counts.to_numpy(),
        "freq": counts.to_numpy() / n_folds,
    })


def jaccard_across_folds(picks: pd.DataFrame, size: int) -> float:
    """fold 쌍 간 Jaccard 유사도 평균. 1 에 가까울수록 패널이 안정적이다."""
    sub = picks[picks.panel_size == size]
    sets = [set(g.feature) for _, g in sub.groupby("fold")]
    if len(sets) < 2:
        return np.nan
    scores = [
        len(a & b) / len(a | b)
        for i, a in enumerate(sets) for b in sets[i + 1:]
        if a | b
    ]
    return float(np.mean(scores)) if scores else np.nan
