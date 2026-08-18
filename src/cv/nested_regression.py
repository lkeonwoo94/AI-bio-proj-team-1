"""CIN/LoHFraction 연속값 예측용 nested CV (§26⑤ 후속).

`src/cv/nested.py` 와 구조는 같지만(outer -> inner GridSearch -> outer 평가),
label 이 연속형이라 StratifiedKFold 대신 KFold 를 쓴다. threshold 결정
단계가 없다는 점만 다르다 — 분류 threshold 자체가 존재하지 않는다.

random split 만 지원한다. 이 비교의 목적은 "같은 random 5-fold 조건에서
분류 대비 회귀가 어떤 신호를 보이는가"이며, lineage 기반 split 까지
회귀로 확장하는 것은 범위 밖이다.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from sklearn.model_selection import GridSearchCV, KFold

from src.config import load_config
from src.evaluation.metrics_regression import evaluate_regression
from src.models.zoo import ModelSpec, extract_importance


@dataclass
class NestedRegressionResult:
    metrics: pd.DataFrame
    importances: pd.DataFrame

    @property
    def summary(self) -> pd.Series:
        return self.metrics.select_dtypes("number").mean(numeric_only=True)


def run_nested_cv_regression(
    X: pd.DataFrame,
    y: pd.Series,
    spec: ModelSpec,
    target: str,
    n_jobs: int = -1,
    outer_folds: int | None = None,
    inner_folds: int | None = None,
    verbose: bool = True,
) -> NestedRegressionResult:
    cfg = load_config("experiment")["cv"]
    seed = load_config("experiment")["seed"]
    outer_folds = outer_folds or cfg["outer_folds"]
    inner_folds = inner_folds or cfg["inner_folds"]

    X_values = X.to_numpy()
    y_values = y.to_numpy()
    feature_names = np.asarray(X.columns)

    outer_kf = KFold(n_splits=outer_folds, shuffle=True, random_state=seed)
    metric_rows, importance_rows = [], []

    for fold, (tr, te) in enumerate(outer_kf.split(X_values)):
        X_tr, X_te = X_values[tr], X_values[te]
        y_tr, y_te = y_values[tr], y_values[te]

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ConvergenceWarning)
            search = GridSearchCV(
                spec.build(), spec.param_grid, scoring="r2",
                cv=KFold(n_splits=inner_folds, shuffle=True, random_state=seed),
                n_jobs=n_jobs, refit=True, error_score="raise",
            )
            search.fit(X_tr, y_tr)
        best = search.best_estimator_

        pred_te = best.predict(X_te)
        row = evaluate_regression(y_te, pred_te)
        row.update({
            "fold": fold, "model": spec.name, "target": target,
            "best_params": str(search.best_params_), "n_train": len(tr),
            "n_features_kept": int(best.named_steps["filter"].n_features_out_),
        })
        metric_rows.append(row)

        imp = extract_importance(best, spec.importance)
        if imp is not None:
            kept = feature_names[best.named_steps["filter"].get_support()]
            importance_rows.append(pd.DataFrame({"fold": fold, "feature": kept, "importance": imp}))

        if verbose:
            print(f"  fold {fold}: R2 {row['r2']:.3f} | rho {row['spearman_rho']:.3f} | "
                  f"RMSE {row['rmse']:.3f} | feature {row['n_features_kept']:,} | "
                  f"{search.best_params_}")

    metrics = pd.DataFrame(metric_rows)
    importances = (
        pd.concat(importance_rows, ignore_index=True)
        if importance_rows else pd.DataFrame(columns=["fold", "feature", "importance"])
    )
    return NestedRegressionResult(metrics=metrics, importances=importances)
