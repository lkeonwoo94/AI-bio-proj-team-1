"""평가 지표.

이 프로젝트에서 지표를 잘못 잡으면 결과가 통째로 무의미해진다. 세포×유전자 쌍을
전부 모아 R² 나 상관을 계산하면 「유전자별 평균」만 맞춰도 0.9 가 넘는다.
따라서 **반드시 유전자(컬럼)마다, 세포주 축을 따라** 계산한다.
"""
from __future__ import annotations

import numpy as np

__all__ = ["pearson_cols"]


def pearson_cols(Ytrue: np.ndarray, Ypred: np.ndarray,
                 min_n: int = 30) -> np.ndarray:
    """컬럼(유전자)마다 세포주 축을 따라 Pearson r 을 계산한다.

    결측은 쌍 단위로 제외한다. 유효 표본이 `min_n` 미만이거나 한쪽 분산이 0이면
    NaN 을 돌려준다 — 표본이 적을 때 우연히 높게 나온 r 이 분포를 오염시키는 것을
    막기 위해서다.

    Parameters
    ----------
    Ytrue, Ypred : (n_samples, n_targets)

    Returns
    -------
    (n_targets,) 각 컬럼의 r. 계산 불가한 컬럼은 NaN.
    """
    if Ytrue.shape != Ypred.shape:
        raise ValueError(f"shape 불일치: {Ytrue.shape} vs {Ypred.shape}")
    out = np.full(Ytrue.shape[1], np.nan)
    for j in range(Ytrue.shape[1]):
        a, b = Ytrue[:, j], Ypred[:, j]
        m = ~(np.isnan(a) | np.isnan(b))
        if m.sum() >= min_n and a[m].std() > 0 and b[m].std() > 0:
            out[j] = np.corrcoef(a[m], b[m])[0, 1]
    return out
