"""src/models/elastic_net.py 검증.

핵심은 **사전선별 누출**이다. 특징을 전체 데이터로 한 번 고르고 CV 를 돌리면
test fold 정보가 새어 들어가 성능이 부풀려진다. 이건 결과가 좋아 보이는 방향으로
틀리기 때문에 눈으로는 절대 안 잡힌다.

    python3 -m pytest tests/test_elastic_net.py -q
"""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.models.elastic_net import enet_preselect_cv, top_correlated  # noqa: E402
from src.models.metrics import pearson_cols  # noqa: E402


def test_top_correlated_picks_true_signal():
    """참 신호가 실린 특징이 상위에 뽑히는가."""
    rng = np.random.default_rng(0)
    n, p = 200, 50
    X = rng.normal(size=(n, p))
    signal = [3, 17, 41]
    y = X[:, signal] @ np.array([2.0, -1.5, 1.0]) + rng.normal(scale=0.3, size=n)
    keep = top_correlated(X, y, k=5)
    assert set(signal) <= set(keep)


def test_top_correlated_ignores_constant_features():
    """분산 0인 특징은 상관이 정의되지 않으므로 뽑히면 안 된다."""
    rng = np.random.default_rng(1)
    X = rng.normal(size=(60, 10))
    X[:, 4] = 7.0                      # 상수 컬럼
    y = X[:, 0] * 2 + rng.normal(scale=0.1, size=60)
    keep = top_correlated(X, y, k=9)   # 10개 중 9개를 고르면 상수만 남아야 한다
    assert 4 not in keep


def test_top_correlated_returns_k():
    rng = np.random.default_rng(2)
    X, y = rng.normal(size=(40, 30)), rng.normal(size=40)
    for k in (1, 5, 30):
        assert len(top_correlated(X, y, k)) == k


def test_preselection_uses_only_train_rows():
    """선별이 train 행만 보는가 — test 행을 바꿔도 결과가 흔들리면 안 된다."""
    rng = np.random.default_rng(3)
    n, p = 120, 80
    X = rng.normal(size=(n, p))
    y = X[:, 5] * 2 + rng.normal(scale=0.5, size=n)
    tr, te = np.arange(0, 90), np.arange(90, n)

    pred_a, keep_a = enet_preselect_cv(X[tr], y[tr], X[te], top_feat=20, seed=0)

    X2 = X.copy()
    X2[te] = rng.normal(size=(len(te), p))      # test 행만 완전히 교체
    _, keep_b = enet_preselect_cv(X2[tr], y[tr], X2[te], top_feat=20, seed=0)

    assert np.array_equal(keep_a, keep_b), "선별이 test 행에 영향을 받는다 = 누출"


def test_leaky_preselection_inflates_score():
    """전체로 선별하면 점수가 부풀려진다는 것을 실제로 보인다.

    신호가 전혀 없는 순수 잡음 데이터에서, 올바른 방식은 r 이 0 근처여야 하고
    전체 데이터로 선별하면 0보다 뚜렷하게 높아진다.
    """
    rng = np.random.default_rng(4)
    n, p = 100, 3000                       # p >> n 이라 우연한 상관이 많다
    X = rng.normal(size=(n, p))
    y = rng.normal(size=n)                 # X 와 무관한 순수 잡음
    tr, te = np.arange(0, 70), np.arange(70, n)

    honest, _ = enet_preselect_cv(X[tr], y[tr], X[te], top_feat=30, seed=0)

    leak = top_correlated(X, y, 30)        # ← 전체 데이터로 선별 (하면 안 되는 것)
    leaky, _ = enet_preselect_cv(X[tr][:, leak], y[tr], X[te][:, leak],
                                 top_feat=30, seed=0)

    r_honest = pearson_cols(y[te][:, None], honest[:, None], min_n=5)[0]
    r_leaky = pearson_cols(y[te][:, None], leaky[:, None], min_n=5)[0]
    assert r_leaky > r_honest, f"누출판 {r_leaky:.3f} 이 정직판 {r_honest:.3f} 보다 높지 않다"


def test_recovers_sparse_signal():
    """신호가 있으면 실제로 예측이 되는가."""
    rng = np.random.default_rng(5)
    n, p = 200, 400
    X = rng.normal(size=(n, p))
    y = X[:, [1, 2, 3]] @ np.array([3.0, -2.0, 1.5]) + rng.normal(scale=0.5, size=n)
    tr, te = np.arange(0, 150), np.arange(150, n)
    pred, _ = enet_preselect_cv(X[tr], y[tr], X[te], top_feat=50, seed=0)
    r = pearson_cols(y[te][:, None], pred[:, None], min_n=5)[0]
    assert r > 0.9


def test_rejects_nan_target():
    rng = np.random.default_rng(6)
    X, y = rng.normal(size=(40, 20)), rng.normal(size=40)
    y[3] = np.nan
    with pytest.raises(ValueError, match="결측"):
        enet_preselect_cv(X[:30], y[:30], X[30:], top_feat=10)
