"""Day 48 — fold별 feature selection 패턴 dendrogram (psh03 탐색 분석 adapt).

원본: docs/research/2026-08-22/depmap_viz/시각화 코드_1.py, 이미지_subplot
코드_2.py (팀원 psh03 제공). `day12_panel_picks_{model}.csv`(§16, 이미 계산된
outer-fold panel 결과)를 그대로 재사용해 fold 간 선택 패턴 유사도를
계층군집화(Jaccard distance)로 본다 — 새 모델 학습 없이 기존 산출물만 읽는다.

Figure 25. WGD/CIN/LOH 3개 표현형을 한 그림에 나란히 배치(행=유전자, 열=fold).
Figure 25b. 같은 3열(WGD/CIN/LOH) 구성이지만 행이 암종(lineage) —
패널 유전자들에 대한 암종별 평균 mutation 빈도 프로파일로 암종을
계층군집화한다. 표본이 적은 암종(<10)은 제외한다.
Figure 25c. Figure 25와 같은 축 구성(y=feature, x=Jaccard distance)을
암종별로 반복 — 열은 WGD/CIN/LOH, 행은 표본 수 상위 암종. 셀 하나는
'그 암종 샘플들 안에서 패널 유전자들이 서로 같이 mutated 되는 패턴'의
Jaccard 기반 dendrogram (fold 대신 암종 내 샘플이 관측 단위). 유전자
순서(y축)는 표현형(열)마다 알파벳순으로 고정 — scipy 기본 dendrogram은
군집 결과에 따라 매번 잎 순서를 다르게 배치해 8개 암종 행을 세로로
비교하기 어려웠다. 고정 순서를 쓰는 대신 트리 선이 서로 교차할 수
있다(거리·병합 구조 자체는 그대로 정확하다).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import dendrogram, linkage, to_tree
from scipy.spatial.distance import pdist

from src.config import REPO_ROOT
from src.data.merge import load_cohort
from src.viz.style import save, use_style

TABLES = REPO_ROOT / "results" / "tables"
TARGETS = {"wgd": "WGD", "cin": "CIN", "loh": "LOH"}
MODEL_LABEL = {"random_forest": "Random Forest", "elastic_net": "Elastic Net"}
MIN_LINEAGE_N = 10
TOP_N_LINEAGE_ROWS = 8


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


def draw_fixed_order_dendrogram(ax, Z: np.ndarray, labels: list[str], fixed_order: list[str],
                                 color: str = "#4c72b0") -> None:
    """`labels` 순서의 잎을 `fixed_order`가 정한 y위치에 강제로 그린다.

    scipy dendrogram()은 잎 순서를 군집 결과에 따라 매번 다르게 정하므로,
    여러 트리(암종별)를 같은 y축 순서로 나란히 비교할 수 없다. 병합 거리는
    Z 그대로 쓰되, 각 리프의 y좌표만 외부에서 고정하고 내부 노드는 자식의
    y좌표 평균으로 재귀 계산해 직접 선을 그린다 — 선이 교차할 수 있지만
    병합 구조(거리)는 정확하다.
    """
    pos = {label: i for i, label in enumerate(fixed_order)}
    tree = to_tree(Z)

    def recurse(node):
        if node.is_leaf():
            return pos[labels[node.id]], 0.0
        y_left, x_left = recurse(node.left)
        y_right, x_right = recurse(node.right)
        x_node = node.dist
        ax.plot([x_left, x_node], [y_left, y_left], color=color, lw=1)
        ax.plot([x_right, x_node], [y_right, y_right], color=color, lw=1)
        ax.plot([x_node, x_node], [y_left, y_right], color=color, lw=1)
        return (y_left + y_right) / 2, x_node

    recurse(tree)
    ax.set_yticks(range(len(fixed_order)))
    ax.set_yticklabels(fixed_order, fontsize=7)
    ax.set_ylim(-0.5, len(fixed_order) - 0.5)
    ax.invert_yaxis()


def gene_by_sample_matrix(genes: list[str], lineage: str, cohort) -> pd.DataFrame:
    """row=gene, col=이 암종 소속 샘플 — Figure 25의 row=gene/col=fold 와 같은 모양,
    fold 대신 암종 내 샘플을 관측 단위로 쓴다."""
    ids = cohort.groups[cohort.groups == lineage].index
    return cohort.X.loc[ids, genes].T


def plot_lineage_feature_dendrogram(model: str, panel_size: int, top_n: int = TOP_N_LINEAGE_ROWS) -> Path:
    """Figure 25c. 열=WGD/CIN/LOH, 행=암종(표본 수 상위 top_n). 각 셀은
    Figure 25와 같은 y=feature, x=Jaccard distance dendrogram."""
    cohort = load_cohort()
    counts = cohort.groups.value_counts()
    lineages = counts[counts >= MIN_LINEAGE_N].head(top_n).index.tolist()

    # 표현형(열)마다 유전자 순서를 한 번만 고정 — 같은 열의 8개 암종 행이
    # 전부 이 순서를 공유해야 세로 비교가 가능하다.
    fixed_genes = {target: sorted(panel_genes(model, target, panel_size)) for target in TARGETS}

    fig, axes = plt.subplots(len(lineages), 3, figsize=(19, 2.8 * len(lineages)), squeeze=False)
    fig.subplots_adjust(left=0.11, top=0.95, bottom=0.03, hspace=0.55, wspace=0.3)

    for row, lineage in enumerate(lineages):
        for col, target in enumerate(TARGETS):
            ax = axes[row][col]
            genes = fixed_genes[target]
            matrix = gene_by_sample_matrix(genes, lineage, cohort)
            distances = pdist(matrix.to_numpy(), metric="jaccard")
            distances = np.nan_to_num(distances, nan=0.0)  # 두 유전자 모두 이 암종에서 mutation 0건이면 0/0
            if len(matrix) > 1:
                Z = linkage(distances, method="average")
                draw_fixed_order_dendrogram(ax, Z, labels=matrix.index.tolist(), fixed_order=genes)
            else:
                ax.set_yticks(range(len(genes)))
                ax.set_yticklabels(genes, fontsize=7)
                ax.invert_yaxis()
            ax.set_xlim(0, 1)
            ax.set_xlabel("Jaccard distance", fontsize=8)
            if row == 0:
                ax.set_title(f"{TARGETS[target]}", fontsize=13)

        # 암종 이름은 y tick label과 겹치지 않도록 subplot 밖(figure 왼쪽 여백)에 별도로 붙인다.
        bbox = axes[row][0].get_position()
        fig.text(0.01, (bbox.y0 + bbox.y1) / 2, f"{lineage}\n(n={int(counts[lineage])})",
                  rotation=90, ha="left", va="center", fontsize=10, fontweight="bold")

    fig.suptitle(f"Figure 25c. 암종별 패널 유전자 co-mutation 패턴 (Figure 25와 같은 축, "
                 f"{MODEL_LABEL.get(model, model)}, {panel_size}-gene 패널, "
                 f"표본 수 상위 {top_n}개 암종, 유전자 순서는 열별로 고정)", y=0.985, fontsize=14)
    return save(fig, f"fig25c_lineage_feature_dendrogram_{model}_panel{panel_size}.png")


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

    use_style()
    path3 = plot_lineage_feature_dendrogram(args.model, args.panel_size)

    print(f"저장: {path1.name}, {path2.name}, {path3.name}, day48*_*.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
