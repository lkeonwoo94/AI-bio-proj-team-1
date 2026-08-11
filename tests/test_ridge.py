"""src/models/ridge.py 검증.

핵심은 leave-one-out 항등식이다. 이건 틀려도 결과가 그럴듯하게 나와서
눈으로는 안 잡히므로, 표본을 실제로 하나씩 빼서 재적합한 값과 대조한다.

    python3 -m pytest tests/test_ridge.py -q
"""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.models.metrics import pearson_cols  # noqa: E402
from src.models.ridge import ridge_kernel_cv, ridge_small  # noqa: E402


def make_data(n=40, p=120, t=3, seed=0):
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n, p))
    B = rng.normal(size=(p, t)) * (rng.random((p, t)) < 0.05)   # 희소한 참 계수
    Y = X @ B + rng.normal(scale=0.5, size=(n, t))
    return X, Y


def ridge_beta(Xc, yc, alpha):
    """정규방정식 직접 풀이 — 비교 기준."""
    p = Xc.shape[1]
    return np.linalg.solve(Xc.T @ Xc + alpha * np.eye(p), Xc.T @ yc)


def test_matches_normal_equations():
    """단일 alpha에서 커널 해가 p×p 정규방정식 해와 같은가."""
    X, Y = make_data()
    Xtr, Ytr, Xte = X[:30], Y[:30], X[30:]
    alpha = 7.5
    got = ridge_kernel_cv(Xtr, Ytr, Xte, np.array([alpha]))

    xm, ym = Xtr.mean(0), Ytr.mean(0)
    want = (Xte - xm) @ ridge_beta(Xtr - xm, Ytr - ym, alpha) + ym
    assert np.allclose(got, want, atol=1e-8)


def test_loo_identity_matches_naive_refit():
    """LOO 항등식이 실제 재적합과 같은 잔차를 주는가 — 이 파일의 핵심."""
    X, Y = make_data(n=25, p=60, t=2, seed=1)
    alpha = 3.0
    xm, ym = X.mean(0), Y.mean(0)
    Xc, Yc = X - xm, Y - ym

    # 항등식 경로 (ridge_kernel_cv 내부와 동일한 계산)
    n = len(X)
    s2, U = np.linalg.eigh(Xc @ Xc.T)
    keep = s2 > s2.max() * 1e-12
    s2, U = s2[keep], U[:, keep]
    shrink = s2 / (s2 + alpha)
    fit = U @ (shrink[:, None] * (U.T @ Yc))
    h = (U ** 2) @ shrink + 1.0 / n      # 절편 항 포함
    fast = (Yc - fit) / (1.0 - h)[:, None]

    # naive: 한 표본씩 빼고 재적합
    naive = np.empty_like(Yc)
    for i in range(len(X)):
        m = np.ones(len(X), bool)
        m[i] = False
        xm_i, ym_i = X[m].mean(0), Y[m].mean(0)
        beta = ridge_beta(X[m] - xm_i, Y[m] - ym_i, alpha)
        naive[i] = Y[i] - ((X[i] - xm_i) @ beta + ym_i)

    # 절편 항까지 맞으면 재적합과 **정확히** 일치한다.
    assert np.allclose(fast, naive, atol=1e-9), \
        f"LOO 잔차가 재적합과 다르다 (최대차 {np.abs(fast - naive).max():.2e})"


def test_alpha_chosen_per_target():
    """타깃마다 다른 alpha 가 선택될 수 있는가 (노이즈 수준을 다르게 준다)."""
    rng = np.random.default_rng(2)
    n, p = 60, 200
    X = rng.normal(size=(n, p))
    b = rng.normal(size=p) * (rng.random(p) < 0.05)
    clean = X @ b
    Y = np.column_stack([clean + rng.normal(scale=0.1, size=n),
                         clean + rng.normal(scale=5.0, size=n)])
    alphas = np.logspace(-1, 5, 25)
    pred = ridge_kernel_cv(X[:45], Y[:45], X[45:], alphas)
    assert pred.shape == (15, 2)
    # 깨끗한 타깃이 노이즈 큰 타깃보다 잘 맞아야 한다
    r = pearson_cols(Y[45:], pred, min_n=5)
    assert r[0] > r[1]


def test_ridge_small_matches_normal_equations():
    X, Y = make_data(n=50, p=8, t=2, seed=3)
    got = ridge_small(X[:40], Y[:40], X[40:], alpha=2.0)
    xm, ym = X[:40].mean(0), Y[:40].mean(0)
    want = (X[40:] - xm) @ ridge_beta(X[:40] - xm, Y[:40] - ym, 2.0) + ym
    assert np.allclose(got, want, atol=1e-10)


def test_pearson_cols_handles_nan_and_constants():
    y = np.array([[1.0, 1.0], [2.0, 1.0], [3.0, 1.0], [np.nan, 1.0]] * 10)
    p = np.array([[1.0, 5.0], [2.0, 6.0], [3.5, 7.0], [4.0, 8.0]] * 10)
    r = pearson_cols(y, p)
    assert r[0] > 0.99          # 결측 쌍은 제외하고 계산
    assert np.isnan(r[1])       # 상수 컬럼은 NaN


def test_pearson_cols_min_n():
    y = np.arange(10.0).reshape(10, 1)
    assert np.isnan(pearson_cols(y, y, min_n=30)[0])
    assert pearson_cols(y, y, min_n=5)[0] == pytest.approx(1.0)
