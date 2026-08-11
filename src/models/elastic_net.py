"""Elastic Net — 특징이 표본보다 훨씬 많을 때의 희소 회귀.

릿지(`src/models/ridge.py`)와 역할이 다르다. 릿지는 닫힌 해가 있어 빠르고 모든
타깃을 동시에 풀 수 있지만 계수가 전부 0이 아니어서 「어느 유전자가 기여했나」를
읽기 어렵다. Elastic Net 은 L1 때문에 좌표하강을 타깃마다 돌려야 해서 훨씬 느린
대신 **계수가 희소해 해석이 된다**. DepMap 공식 Predictability 베이스라인이기도 하다.

p ≈ 19,000 을 그대로 넣으면 느리므로 상관 상위 특징만 남기고 적합한다. 이때
**사전선별을 반드시 train fold 안에서만** 해야 한다. 전체 데이터로 한 번 고르고
CV 를 돌리면 test fold 정보가 특징 선택에 새어 들어가 성능이 부풀려진다 —
이 프로젝트에서 가장 빠지기 쉬운 함정이다.
"""
from __future__ import annotations

import numpy as np
from sklearn.linear_model import ElasticNetCV

__all__ = ["top_correlated", "enet_preselect_cv"]


def top_correlated(X: np.ndarray, y: np.ndarray, k: int) -> np.ndarray:
    """|피어슨 상관| 상위 k개 특징의 인덱스.

    분산이 0인 특징은 상관을 정의할 수 없으므로 선택되지 않도록 0으로 둔다.
    """
    Xc = X - X.mean(0)
    yc = y - y.mean()
    denom = np.sqrt((Xc ** 2).sum(0)) * np.sqrt((yc ** 2).sum())
    denom[denom == 0] = np.inf
    corr = np.abs(Xc.T @ yc / denom)
    return np.argsort(-corr)[:k]


def enet_preselect_cv(Xtr: np.ndarray, ytr: np.ndarray, Xte: np.ndarray,
                      top_feat: int = 500, l1_ratio: float = 0.5,
                      n_alphas: int = 20, cv: int = 3, max_iter: int = 3000,
                      tol: float = 1e-4, seed: int = 0) -> tuple[np.ndarray, np.ndarray]:
    """train fold 안에서만 특징을 고른 뒤 ElasticNetCV 로 적합한다.

    Parameters
    ----------
    Xtr, Xte : (n_tr, p), (n_te, p)
    ytr : (n_tr,) 단일 타깃. 결측이 없어야 한다(호출부에서 마스킹할 것).
    top_feat : 사전선별로 남길 특징 수.
    tol, max_iter : 좌표하강 정지 조건. 이 둘이 실행 시간을 직접 좌우한다
        (sklearn 기본은 tol=1e-4). 완화하면 빨라지지만 해가 덜 수렴한다.

    Returns
    -------
    pred : (n_te,) 예측값.
    keep : (top_feat,) 선택된 특징 인덱스. 계수 해석에 쓴다.
    """
    if np.isnan(ytr).any():
        raise ValueError("ytr 에 결측이 있다 — 호출부에서 걸러야 한다")

    keep = top_correlated(Xtr, ytr, top_feat)
    model = ElasticNetCV(l1_ratio=l1_ratio, n_alphas=n_alphas, cv=cv,
                         max_iter=max_iter, tol=tol, random_state=seed, n_jobs=1)
    model.fit(np.asarray(Xtr[:, keep], dtype=np.float64),
              np.asarray(ytr, dtype=np.float64))
    return model.predict(np.asarray(Xte[:, keep], dtype=np.float64)), keep
