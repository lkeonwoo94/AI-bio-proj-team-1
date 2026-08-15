"""성능 지표 (README §14).

단일 metric 으로 모델을 고르지 않기 위해 항상 한 묶음으로 계산한다.
positive class 는 항상 1 (WGD+, CIN-high, LOH-high) 이다.
WGD 는 양성이 다수 클래스(65%)라는 점을 해석에서 감안해야 한다.
"""

from __future__ import annotations

import numpy as np
from sklearn.metrics import (
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    f1_score,
    recall_score,
    roc_auc_score,
)


def choose_threshold(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    """balanced accuracy 를 최대화하는 분류 threshold.

    반드시 training fold 안의 out-of-fold 예측으로만 호출한다 (README §13).
    """
    candidates = np.unique(np.round(y_prob, 3))
    if len(candidates) < 2:
        return 0.5
    scores = [balanced_accuracy_score(y_true, (y_prob >= t).astype(int)) for t in candidates]
    return float(candidates[int(np.argmax(scores))])


def evaluate(y_true: np.ndarray, y_prob: np.ndarray, threshold: float = 0.5) -> dict:
    """확률 예측에 대한 성능 한 묶음."""
    y_true = np.asarray(y_true)
    y_pred = (np.asarray(y_prob) >= threshold).astype(int)

    # test fold 에 한 클래스만 있으면 AUC 가 정의되지 않는다 (LOLO 에서 발생).
    single_class = len(np.unique(y_true)) < 2

    return {
        "roc_auc": np.nan if single_class else roc_auc_score(y_true, y_prob),
        "pr_auc": np.nan if single_class else average_precision_score(y_true, y_prob),
        "balanced_accuracy": balanced_accuracy_score(y_true, y_pred),
        "sensitivity": recall_score(y_true, y_pred, pos_label=1, zero_division=0),
        "specificity": recall_score(y_true, y_pred, pos_label=0, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "brier": brier_score_loss(y_true, y_prob),
        "n_test": len(y_true),
        "positive_rate": float(y_true.mean()),
        "threshold": threshold,
    }


METRIC_COLUMNS = [
    "roc_auc", "pr_auc", "balanced_accuracy",
    "sensitivity", "specificity", "f1", "brier",
]
