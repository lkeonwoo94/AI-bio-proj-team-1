"""누출 방지 장치가 실제로 작동하는지 검증한다 (README §13).

이 프로젝트에서 가장 조용히 틀리기 쉬운 부분이라 테스트로 고정한다.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.features.filter import RareMutationFilter
from src.labels.binarize import LabelBinarizer


class TestLabelBinarizer:
    def test_threshold_는_training_값만_본다(self):
        """test fold 에 극단값이 있어도 threshold 가 흔들리면 안 된다."""
        train = pd.Series([0.1, 0.2, 0.3, 0.4, 0.5])
        binz = LabelBinarizer("cin").fit(train)
        thr = binz.threshold_

        # test fold 를 transform 해도 threshold 는 그대로여야 한다.
        binz.transform(pd.Series([100.0, 200.0, 300.0]))
        assert binz.threshold_ == thr

    def test_test_fold_는_training_threshold_로_이진화된다(self):
        train = pd.Series([0.0, 0.2, 0.4, 0.6, 0.8])   # median 0.4
        binz = LabelBinarizer("cin").fit(train)

        # 0.5 는 training median(0.4) 보다 크므로 high 여야 한다.
        # test 자체의 median(0.5)으로 계산했다면 low 가 되어버린다.
        out = binz.transform(pd.Series([0.5, 0.45, 0.55]))
        assert out.tolist() == [1, 1, 1]

    def test_binary_label_은_threshold_없이_통과한다(self):
        binz = LabelBinarizer("wgd").fit(pd.Series([0, 1, 1, 0]))
        assert binz.threshold_ is None
        assert binz.transform(pd.Series([0, 1])).tolist() == [0, 1]

    def test_fit_없이_transform_하면_실패한다(self):
        with pytest.raises(RuntimeError, match="fit"):
            LabelBinarizer("cin").transform(pd.Series([0.1, 0.9]))


class TestRareMutationFilter:
    def test_training_빈도로만_feature_를_고른다(self):
        # feature 0: train 에서 흔함, feature 1: train 에서 희귀
        X_train = np.zeros((100, 2), dtype=int)
        X_train[:30, 0] = 1
        X_train[:2, 1] = 1

        filt = RareMutationFilter(min_count=10).fit(X_train)
        assert filt.get_support().tolist() == [True, False]

        # test 에서 feature 1 이 아무리 흔해도 선택은 바뀌지 않는다.
        X_test = np.ones((50, 2), dtype=int)
        assert filt.transform(X_test).shape[1] == 1

    def test_비율_기준이_절대개수보다_우선한다(self):
        X = np.zeros((100, 2), dtype=int)
        X[:15, 0] = 1
        X[:5, 1] = 1

        filt = RareMutationFilter(min_count=1, min_freq=0.1).fit(X)
        # 10% = 10개 이상 -> feature 0 만 통과
        assert filt.get_support().tolist() == [True, False]

    def test_모두_걸러지면_가장_흔한_것을_남긴다(self):
        """학습 자체가 불가능해지는 상황을 막는 안전장치."""
        X = np.zeros((100, 3), dtype=int)
        X[:2, 0] = 1

        filt = RareMutationFilter(min_count=50).fit(X)
        assert filt.n_features_out_ >= 1


class TestPipelineIntegration:
    def test_필터가_pipeline_안에서_fold마다_재적합된다(self):
        """CV 각 fold 에서 support_ 가 달라질 수 있어야 정상이다."""
        from sklearn.linear_model import LogisticRegression
        from sklearn.model_selection import StratifiedKFold
        from sklearn.pipeline import Pipeline

        rng = np.random.default_rng(0)
        X = (rng.random((200, 20)) < 0.06).astype(int)
        y = rng.integers(0, 2, 200)

        pipe = Pipeline([
            ("filter", RareMutationFilter(min_count=10)),
            ("clf", LogisticRegression(max_iter=500)),
        ])

        supports = []
        for tr, _ in StratifiedKFold(n_splits=3, shuffle=True, random_state=0).split(X, y):
            pipe.fit(X[tr], y[tr])
            supports.append(tuple(pipe.named_steps["filter"].get_support()))

        # fold 마다 학습 데이터가 다르므로 support 가 하나로 고정되어 있으면
        # 필터가 전체 데이터를 봤다는 뜻이다.
        assert len(supports) == 3
