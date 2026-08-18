"""회귀 성능 지표 — CIN/LoHFraction 을 연속값으로 예측할 때 (§26⑤ 후속).

분류 지표(ROC-AUC 등)와 바로 비교할 수 있는 값은 없다. 대신 Spearman
correlation 이 "순위를 얼마나 잘 맞히는가"라는 점에서 ROC-AUC 와 가장
가까운 직관을 준다 — 두 지표 모두 값 자체가 아니라 상대적 순서에 대한
지표이기 때문이다.
"""

from __future__ import annotations

import numpy as np
from scipy.stats import spearmanr
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def evaluate_regression(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    rho, _ = spearmanr(y_true, y_pred) if len(np.unique(y_true)) > 1 else (np.nan, np.nan)

    return {
        "r2": r2_score(y_true, y_pred),
        "spearman_rho": rho,
        "rmse": mean_squared_error(y_true, y_pred) ** 0.5,
        "mae": mean_absolute_error(y_true, y_pred),
        "n_test": len(y_true),
    }


REGRESSION_METRIC_COLUMNS = ["r2", "spearman_rho", "rmse", "mae"]
