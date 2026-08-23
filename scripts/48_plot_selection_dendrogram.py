"""Day 48 — fold별 feature selection 패턴 dendrogram (psh03 탐색 분석 adapt).

원본: docs/research/2026-08-22/depmap_viz/시각화 코드_1.py, 이미지_subplot
코드_2.py (팀원 psh03 제공). `day12_panel_picks_{model}.csv`(§16, 이미 계산된
outer-fold panel 결과)를 그대로 재사용해 fold 간 선택 패턴 유사도를
계층군집화(Jaccard distance)로 본다 — 새 모델 학습 없이 기존 산출물만 읽는다.

Figure 25. WGD/CIN/LOH 3개 표현형을 한 그림에 나란히 배치(행=유전자, 열=fold).
Figure 25b. 같은 3열(WGD/CIN/LOH) 구성이지만 행이 암종(lineage) —
패널 유전자들에 대한 암종별 평균 mutation 빈도 프로파일로 암종을
계층군집화한다. 표본이 적은 암종(<10)은 제외한다.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import pandas as pd
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import pdist

from src.config import REPO_ROOT
from src.data.merge import load_cohort
from src.viz.style import save, use_style

TABLES = REPO_ROOT / "results" / "tables"
TARGETS = {"wgd": "WGD", "cin": "CIN", "loh": "LOH"}
MODEL_LABEL = {"random_forest": "Random Forest", "elastic_net": "Elastic Net"}
MIN_LINEAGE_N = 10


def selection_matrix(model: str, target: str, panel_size: int) -> pd.DataFrame:
    path = TABLES / f"day12_panel_picks_{model}.csv"
    if not path.exists():
        raise SystemExit(f"{path.name} 없음 — 먼저 day12 패널 계산을 실행하세요.")
    picks = pd.read_csv(path)
    picks = picks[(picks.target == target) & (picks.panel_size == panel_size)]
    if picks.empty:
        raise ValueError(f"{target}, panel size {panel_size}의 fold별 panel pick이 없습니다.")
    return pd.crosstab(picks.feature, picks.fold).reindex(
        columns=sorted(picks.fold.unique()), fill_value=0)


def panel_genes(model: str, target: str, panel_size: int) -> list[str]:
    """fold마다 다른 패널 구성의 합집합 — 표현형별로 한 번이라도 뽑힌 유전자 전체."""
    path = TABLES / f"day12_panel_picks_{model}.csv"
    picks = pd.read_csv(path)
    picks = picks[(picks.target == target) & (picks.panel_size == panel_size)]
    return sorted(picks.feature.unique())


def lineage_profile_matrix(genes: list[str], min_n: int = MIN_LINEAGE_N) -> pd.DataFrame:
    """암종별 패널 유전자 평균 mutation 빈도 — row=lineage, col=gene."""
    cohort = load_cohort()
    counts = cohort.groups.value_counts()
    keep_lineages = counts[counts >= min_n].index
    X = cohort.X.loc[:, genes]
    profile = X.groupby(cohort.groups).mean()
    return profile.loc[profile.index.isin(keep_lineages)]


def plot_lineage_dendrogram(model: str, panel_size: int) -> Path:
    """Figure 25b. Figure 25와 같은 3열(WGD/CIN/LOH), 행은 암종."""
    fig, axes = plt.subplots(1, 3, figsize=(20, 9))

    for ax, target in zip(axes, TARGETS):
        genes = panel_genes(model, target, panel_size)
        profile = lineage_profile_matrix(genes)
        profile.to_csv(TABLES / f"day48b_lineage_profile_{model}_{target}_panel{panel_size}.csv")
        distances = pdist(profile.to_numpy(), metric="euclidean")
        if len(profile) > 1:
            dendrogram(linkage(distances, method="average"), labels=profile.index.tolist(),
                       orientation="right", ax=ax)
        else:
            ax.text(0.5, 0.5, profile.index[0], ha="center", va="center")
        ax.set_title(f"{TARGETS[target]} — {panel_size}-gene 패널 기준 암종 군집", fontsize=13)
        ax.set_xlabel("Euclidean distance (패널 유전자 평균 mutation 빈도)")
        ax.tick_params(axis="y", labelsize=8)

    fig.suptitle(f"Figure 25b. 암종(lineage)별 패널 유전자 mutation 프로파일 군집 "
                 f"({MODEL_LABEL.get(model, model)}, {panel_size}-gene 패널, "
                 f"n≥{MIN_LINEAGE_N} 암종만)", y=1.0, fontsize=14)
    fig.tight_layout()
    return save(fig, f"fig25b_lineage_dendrogram_{model}_panel{panel_size}.png")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="random_forest")
    p.add_argument("--panel-size", type=int, default=10)
    args = p.parse_args()

    use_style()
    fig, axes = plt.subplots(1, 3, figsize=(20, 8))

    for ax, target in zip(axes, TARGETS):
        matrix = selection_matrix(args.model, target, args.panel_size)
        matrix.to_csv(TABLES / f"day48_selection_matrix_{args.model}_{target}_panel{args.panel_size}.csv")
        distances = pdist(matrix.to_numpy(), metric="jaccard")
        if len(matrix) > 1:
            dendrogram(linkage(distances, method="average"), labels=matrix.index.tolist(),
                       orientation="right", ax=ax)
        else:
            ax.text(0.5, 0.5, matrix.index[0], ha="center", va="center")
        ax.set_title(f"{TARGETS[target]} — {args.panel_size}-gene 패널 fold 선택 패턴", fontsize=13)
        ax.set_xlabel("Jaccard distance")
        ax.set_xlim(0, 1)

    fig.suptitle(f"Figure 25. Fold별 feature selection 안정성 "
                 f"({MODEL_LABEL.get(args.model, args.model)}, {args.panel_size}-gene 패널)",
                 y=1.0, fontsize=14)
    fig.tight_layout()
    path1 = save(fig, f"fig25_selection_dendrogram_{args.model}_panel{args.panel_size}.png")

    use_style()
    path2 = plot_lineage_dendrogram(args.model, args.panel_size)

    print(f"저장: {path1.name}, {path2.name}, day48*_*.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
