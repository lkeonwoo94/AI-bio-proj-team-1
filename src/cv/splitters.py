"""CV split 생성 (README §12, §15).

random split 과 lineage 기반 split 을 같은 인터페이스로 제공해
Day 13 의 비교가 코드 변경 없이 가능하도록 한다.
"""

from __future__ import annotations

from typing import Iterator

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold, LeaveOneGroupOut, StratifiedKFold

from src.config import load_config


def outer_splits(
    y: np.ndarray,
    groups: pd.Series,
    scheme: str = "random",
    n_splits: int | None = None,
    seed: int | None = None,
) -> Iterator[tuple[np.ndarray, np.ndarray]]:
    """outer CV split.

    scheme
        random  : StratifiedKFold — 표준 성능 평가 (§12)
        group   : lineage GroupKFold — 같은 암종이 train/test 에 겹치지 않음 (§15)
        lolo    : Leave-One-Lineage-Out — 암종 하나를 통째로 test 로 (§15)
    """
    cfg = load_config("experiment")
    n_splits = n_splits or cfg["cv"]["outer_folds"]
    seed = cfg["seed"] if seed is None else seed
    g = groups.to_numpy()

    if scheme == "random":
        yield from StratifiedKFold(
            n_splits=n_splits, shuffle=True, random_state=seed
        ).split(np.zeros(len(y)), y)
    elif scheme == "group":
        yield from GroupKFold(n_splits=n_splits).split(np.zeros(len(y)), y, groups=g)
    elif scheme == "lolo":
        yield from LeaveOneGroupOut().split(np.zeros(len(y)), y, groups=g)
    else:
        raise ValueError(f"알 수 없는 scheme: {scheme!r}")


def inner_cv(seed: int | None = None, n_splits: int | None = None) -> StratifiedKFold:
    """inner CV — hyperparameter, feature selection, threshold 결정용 (§12)."""
    cfg = load_config("experiment")
    return StratifiedKFold(
        n_splits=n_splits or cfg["cv"]["inner_folds"],
        shuffle=True,
        random_state=cfg["seed"] if seed is None else seed,
    )


def eligible_lineages(groups: pd.Series, min_size: int = 20) -> list[str]:
    """Leave-One-Lineage-Out 대상 lineage.

    세포주가 너무 적은 lineage 는 test fold 가 되면 성능 추정이 불안정하고
    양성/음성 한쪽만 남는 경우도 생긴다. 결과 해석에서 제외할 수 있도록
    미리 목록을 만들어 둔다.
    """
    counts = groups.value_counts()
    return sorted(counts[counts >= min_size].index)
