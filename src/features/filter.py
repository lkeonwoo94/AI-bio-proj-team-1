"""희귀 mutation 제거 (README §9.3).

빈도는 training fold 에서만 계산한다. 전체 데이터에서 빈도를 구하면
test 세포주의 변이 분포를 미리 본 것이 되어 누출이다.

sklearn Pipeline 안에 넣어 fold 마다 자동으로 다시 적합되도록 만든다.
"""

from __future__ import annotations

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

from src.config import load_config


class RareMutationFilter(BaseEstimator, TransformerMixin):
    """training fold 에서 일정 빈도 이상 관측된 mutation 만 남긴다.

    Parameters
    ----------
    min_count : 최소 관측 세포주 수 (절대 개수)
    min_freq : 최소 관측 비율. 지정하면 min_count 대신 사용한다.
    """

    def __init__(self, min_count: int | None = None, min_freq: float | None = None):
        self.min_count = min_count
        self.min_freq = min_freq

    def _resolve(self, n_samples: int) -> int:
        if self.min_freq is not None:
            return max(1, int(np.ceil(self.min_freq * n_samples)))
        if self.min_count is not None:
            return int(self.min_count)
        cfg = load_config("experiment")["features"]
        if cfg.get("min_mutation_freq") is not None:
            return max(1, int(np.ceil(cfg["min_mutation_freq"] * n_samples)))
        return int(cfg["min_mutation_count"])

    def fit(self, X, y=None):
        X = np.asarray(X)
        threshold = self._resolve(X.shape[0])
        counts = (X > 0).sum(axis=0)

        self.support_ = counts >= threshold
        # 전부 걸러지면 학습이 불가능하므로 가장 흔한 변이라도 남긴다.
        if not self.support_.any():
            self.support_ = counts >= np.sort(counts)[-min(10, len(counts))]

        self.threshold_ = threshold
        self.n_features_in_ = X.shape[1]
        self.n_features_out_ = int(self.support_.sum())
        return self

    def transform(self, X):
        return np.asarray(X)[:, self.support_]

    def get_support(self, indices: bool = False):
        return np.flatnonzero(self.support_) if indices else self.support_
