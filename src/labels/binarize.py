"""연속형 표현형의 high / low 이진화 (README §10).

핵심 규칙: threshold 는 **training fold 에서만** 계산하고,
validation / test 에는 그 값을 그대로 적용한다.

이를 강제하기 위해 fit 과 transform 을 분리했다. 전체 데이터를 받아
한 번에 이진화하는 함수는 의도적으로 제공하지 않는다.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.config import load_config


class LabelBinarizer:
    """연속형 label 을 high(1) / low(0) 로 나눈다.

    binary 타입 label 은 threshold 없이 그대로 통과시킨다.
    """

    def __init__(self, label: str):
        cfg = load_config("experiment")["labels"][label]
        self.label = label
        self.type_ = cfg["type"]
        self.method = cfg.get("binarize", "median")
        self.quantile = cfg.get("quantile", 0.75)
        self.threshold_: float | None = None

    def fit(self, y_train: pd.Series) -> LabelBinarizer:
        """training fold 의 값만 보고 threshold 를 정한다."""
        if self.type_ == "binary":
            self.threshold_ = None
            return self

        q = 0.5 if self.method == "median" else self.quantile
        self.threshold_ = float(np.quantile(y_train.astype(float), q))
        return self

    def transform(self, y: pd.Series) -> pd.Series:
        if self.type_ == "binary":
            return y.astype(int)
        if self.threshold_ is None:
            raise RuntimeError(f"{self.label}: fit 을 먼저 호출해야 합니다.")
        return (y.astype(float) > self.threshold_).astype(int)

    def fit_transform(self, y_train: pd.Series) -> pd.Series:
        """training fold 전용. test 에 쓰면 누출이다."""
        return self.fit(y_train).transform(y_train)
