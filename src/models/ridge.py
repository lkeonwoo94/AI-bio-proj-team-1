"""릿지 회귀 — n ≪ p 인 상황에 맞춘 커널(Gram) 기반 구현.

DepMap 은 세포주 n ≈ 1,100, 유전자 p ≈ 19,000 으로 표본보다 특징이 훨씬 많다.
이때 p×p 정규방정식 대신 n×n 그램 행렬의 고유분해를 쓰면 같은 해를 얻으면서
연산이 n 에만 좌우된다. 게다가 분해를 한 번 해두면

  * 모든 alpha 의 해가 대각 스케일링만으로 나오고,
  * 모든 타깃(유전자)의 해가 행렬곱 한 번으로 동시에 나오며,
  * alpha 선택에 쓰는 leave-one-out 오차도 hat 행렬 대각으로 공짜로 얻는다.

수식:

    ridge:  beta(alpha) = V diag(s / (s^2 + alpha)) U^T y
    LOO  :  (y_i - yhat_i) / (1 - H_ii)
            H_ii = sum_k U_ik^2 s_k^2 / (s_k^2 + alpha) + 1/n

마지막 `+ 1/n` 은 절편 항이다. 중심화로 X_c^T 1 = 0 이 되어 H1 = 0 이므로
절편까지 포함한 평활자는 H + 11^T/n 이 된다. 이 항을 빠뜨리면 LOO 오차가
과소평가된다.

LOO 항등식은 릿지처럼 예측이 y 에 선형인 모델에서만 성립한다. 표본을 실제로
하나씩 빼서 재적합한 것과 정확히 같은 값이며, tests/test_ridge.py 에서
naive 구현과 대조해 검증한다.
"""
from __future__ import annotations

import numpy as np

__all__ = ["ridge_kernel_cv", "ridge_lowrank_cv", "ridge_small"]


def ridge_kernel_cv(Xtr: np.ndarray, Ytr: np.ndarray, Xte: np.ndarray,
                    alphas: np.ndarray) -> np.ndarray:
    """train 을 한 번 분해해 모든 alpha·모든 타깃의 예측을 만든다.

    alpha 는 train 내부 leave-one-out 오차로 **타깃마다 따로** 고른다.

    Parameters
    ----------
    Xtr, Xte : (n_tr, p), (n_te, p) 설계행렬. 중심화는 내부에서 한다.
    Ytr : (n_tr, n_targets) 타깃. 결측이 없어야 한다(호출부에서 채울 것).
    alphas : 후보 정규화 강도.

    Returns
    -------
    (n_te, n_targets) 예측값.
    """
    xm, ym = Xtr.mean(0), Ytr.mean(0)
    Xc, Yc = Xtr - xm, Ytr - ym

    K = Xc @ Xc.T                                    # (n_tr, n_tr)
    s2, U = np.linalg.eigh(K)
    keep = s2 > s2.max() * 1e-12                     # 수치적 0 성분 제거
    s2, U = s2[keep], U[:, keep]
    s = np.sqrt(s2)

    Kte = (Xte - xm) @ Xc.T                          # (n_te, n_tr)
    UtY = U.T @ Yc                                   # (k, n_targets)
    A = (Kte @ U) / s                                # (n_te, k) = Xte_c V

    # --- alpha 선택: leave-one-out ---
    # 중심화로 X_c^T 1 = 0 이므로 H1 = 0 이고, 절편까지 포함한 실제 평활자는
    # H + 11^T/n 이다. 따라서 hat 대각은 h_ii 가 아니라 h_ii + 1/n 이다.
    # 이 항을 빼면 LOO 오차가 과소평가되어 alpha 가 작게 선택되는 쪽으로 치우친다.
    n_tr = Xtr.shape[0]
    best_err = np.full(Yc.shape[1], np.inf)
    best_a = np.zeros(Yc.shape[1], dtype=int)
    for ai, a in enumerate(alphas):
        shrink = s2 / (s2 + a)                       # (k,)
        fit = U @ (shrink[:, None] * UtY)            # (n_tr, n_targets)
        h = (U ** 2) @ shrink + 1.0 / n_tr           # (n_tr,) hat 대각
        resid = (Yc - fit) / (1.0 - h)[:, None]
        err = (resid ** 2).mean(0)
        better = err < best_err
        best_err[better] = err[better]
        best_a[better] = ai

    # --- 선택된 alpha 로 test 예측 ---
    pred = np.empty((Xte.shape[0], Yc.shape[1]))
    for ai in np.unique(best_a):
        cols = np.flatnonzero(best_a == ai)
        d = s / (s2 + alphas[ai])
        pred[:, cols] = A @ (d[:, None] * UtY[:, cols]) + ym[cols]
    return pred


def ridge_lowrank_cv(Xtr: np.ndarray, Ytr: np.ndarray, Xte: np.ndarray,
                     alphas: np.ndarray, rank: int) -> np.ndarray:
    """저랭크 멀티태스크 릿지 (reduced-rank regression).

    타깃 665개는 서로 독립이 아니다 — 같은 경로에 속한 유전자들이 함께 움직인다.
    타깃 축을 rank 개 주성분으로 축약해 그 잠재 변수만 예측하고 되돌리면,
    타깃끼리 통계적 강도를 빌려주는 효과를 기대할 수 있다. n ≪ p 인 상황에서
    흔히 쓰이는 정규화 방식이다.

    ⚠️ **DepMap 에서는 효과가 없었다.** rank 50/150/300 모두 유전자별 중앙 r 이
    베이스라인(0.404)보다 낮았다. 근거는 Q5 E-2 및
    `results/tables/q5_ceiling_ablation.csv`. 재현·반증용으로 남겨둔다.

    주성분은 **train fold 안에서만** 구한다. 전체 Y 로 구하면 test 의 타깃
    공분산 구조가 새어 들어간다.

    Parameters
    ----------
    Xtr, Xte : (n_tr, p), (n_te, p) 설계행렬.
    Ytr : (n_tr, n_targets) 타깃. 결측이 없어야 한다.
    alphas : 후보 정규화 강도.
    rank : 유지할 타깃 축 주성분 수.

    Returns
    -------
    (n_te, n_targets) 예측값.
    """
    ym = Ytr.mean(0)
    Yc = Ytr - ym
    _, _, Vt = np.linalg.svd(Yc, full_matrices=False)
    W = Vt[:rank].T                                  # (n_targets, rank)
    Z = Yc @ W                                       # (n_tr, rank) 잠재 타깃
    Zpred = ridge_kernel_cv(Xtr, Z, Xte, alphas)     # 잠재 축에서 릿지
    return Zpred @ W.T + ym                          # 원래 타깃 축으로 복원


def ridge_small(Xtr: np.ndarray, Ytr: np.ndarray, Xte: np.ndarray,
                alpha: float = 1.0) -> np.ndarray:
    """저차원 설계행렬(암종 원핫 등)용 고정 alpha 릿지.

    특징 수가 적어 p×p 정규방정식을 직접 푸는 편이 빠르다.
    """
    xm, ym = Xtr.mean(0), Ytr.mean(0)
    Xc = Xtr - xm
    G = Xc.T @ Xc + alpha * np.eye(Xc.shape[1])
    B = np.linalg.solve(G, Xc.T @ (Ytr - ym))
    return (Xte - xm) @ B + ym
