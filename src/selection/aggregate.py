"""Fold 반복 feature selection 집계 (README §16).

단일 fold 에서 한 번 높게 나온 유전자가 아니라, 여러 training fold 에서
반복적으로 선택되는 유전자를 우선한다. 그래서 평균 중요도만이 아니라
선택 빈도와 순위 안정성을 함께 기록한다.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def rank_within_fold(importances: pd.DataFrame, top_k: int = 50) -> pd.DataFrame:
    """fold 별로 중요도 순위를 매기고 상위 top_k 를 '선택됨'으로 표시한다."""
    df = importances.copy()
    df["rank"] = df.groupby("fold")["importance"].rank(ascending=False, method="min")
    df["selected"] = df["rank"] <= top_k
    return df


def aggregate_selection(importances: pd.DataFrame, top_k: int = 50) -> pd.DataFrame:
    """유전자별 선택 빈도·평균 중요도·순위 안정성.

    Returns
    -------
    feature, n_folds_selected, selection_freq, mean_importance,
    mean_rank, rank_std, kind
    """
    if importances.empty:
        return pd.DataFrame()

    ranked = rank_within_fold(importances, top_k=top_k)
    n_folds = ranked["fold"].nunique()

    out = (
        ranked.groupby("feature")
        .agg(
            n_folds_selected=("selected", "sum"),
            mean_importance=("importance", "mean"),
            mean_rank=("rank", "mean"),
            rank_std=("rank", "std"),
        )
        .reset_index()
    )
    out["selection_freq"] = out.n_folds_selected / n_folds
    out["kind"] = np.where(out.feature.str.endswith("_hotspot"), "hotspot", "damaging")
    out["gene"] = out.feature.str.replace(r" \(.*?\)_(hotspot|damaging)$", "", regex=True)

    # 반복 선택이 1순위, 그 안에서 평균 순위가 앞선 것 우선 (§16)
    return out.sort_values(
        ["selection_freq", "mean_rank"], ascending=[False, True]
    ).reset_index(drop=True)


def stable_panel(agg: pd.DataFrame, size: int, min_freq: float = 0.0) -> list[str]:
    """집계 결과에서 상위 size 개 feature 를 뽑는다."""
    pool = agg[agg.selection_freq >= min_freq] if min_freq else agg
    return pool.head(size).feature.tolist()


def cross_phenotype_table(aggs: dict[str, pd.DataFrame], size: int = 20) -> pd.DataFrame:
    """WGD/CIN/LOH 각각의 선택 빈도를 한 표로 (README §16 예시 형태)."""
    frames = []
    for target, agg in aggs.items():
        if agg.empty:
            continue
        frames.append(
            agg.set_index("feature")[["selection_freq", "mean_rank"]]
            .rename(columns={"selection_freq": f"{target}_freq", "mean_rank": f"{target}_rank"})
        )
    if not frames:
        return pd.DataFrame()

    merged = pd.concat(frames, axis=1).fillna({c: 0 for c in
                                               [c for c in
                                                pd.concat(frames, axis=1).columns
                                                if c.endswith("_freq")]})
    freq_cols = [c for c in merged.columns if c.endswith("_freq")]
    merged["mean_freq"] = merged[freq_cols].mean(axis=1)
    merged["n_phenotypes"] = (merged[freq_cols] >= 0.6).sum(axis=1)
    return merged.sort_values("mean_freq", ascending=False).head(size).reset_index()
