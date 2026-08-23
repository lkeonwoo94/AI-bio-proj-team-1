"""Day 47 — CCA 시각화 (psh03 탐색 분석 adapt).

Figure 24. canonical component 별 산점도(이진화 라벨) + 이진화 vs 연속값
라벨 비교(component 1) — 후자는 암종(lineage)별로 색칠해 공유 축이 암종
차이를 반영하는 건 아닌지 확인한다.
Figure 24c. Figure 24와 같은 component별 3패널 구성, 색만 암종 기준
(Figure 23/23b 관계와 동일하게 대응).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src.config import REPO_ROOT
from src.viz.style import save, use_style

TABLES = REPO_ROOT / "results" / "tables"
TOP_N_LINEAGES = 12


def lineage_palette(lineage: pd.Series) -> tuple[pd.Series, dict[str, str]]:
    counts = lineage.value_counts()
    shown = counts.head(TOP_N_LINEAGES).index
    grouped = lineage.where(lineage.isin(shown), "Other lineage")
    groups = list(shown) + ["Other lineage"]
    palette = dict(zip(groups, sns.color_palette("tab20", len(shown)).as_hex() + ["#bdbdbd"]))
    return grouped, palette


def padded_limits(values: np.ndarray, fraction: float = 0.05) -> tuple[float, float]:
    low, high = float(np.nanmin(values)), float(np.nanmax(values))
    pad = max((high - low) * fraction, 0.1)
    return low - pad, high + pad


def main() -> int:
    cca_path = TABLES / "day46_cca.csv"
    coord_path = TABLES / "day46_cca_coordinates.csv"
    if not (cca_path.exists() and coord_path.exists()):
        raise SystemExit(f"{cca_path.name}/{coord_path.name} 없음 — 먼저 46_mutation_cca.py 를 실행하세요.")
    cca = pd.read_csv(cca_path)
    coords = pd.read_csv(coord_path, index_col=0)

    use_style()
    n_components = len(cca)

    # Figure 24a. component 별 canonical score 산점도 (이진화 라벨)
    U_cols = [f"U_bin_{i + 1}" for i in range(n_components)]
    V_cols = [f"V_bin_{i + 1}" for i in range(n_components)]
    x_limits = padded_limits(coords[U_cols].to_numpy())
    y_limits = padded_limits(coords[V_cols].to_numpy())
    fig, axes = plt.subplots(1, n_components, figsize=(12, 5), squeeze=False)
    for i, ax in enumerate(axes.flat):
        ax.scatter(coords[f"U_bin_{i + 1}"], coords[f"V_bin_{i + 1}"], s=12, alpha=0.55,
                   color="#4f81bd", linewidths=0)
        r = cca.loc[i, "correlation_binarized"]
        ax.set(title=f"CCA component {i + 1}: r={r:.3f}",
               xlabel="Mutation canonical score", ylabel="Instability canonical score",
               xlim=x_limits, ylim=y_limits)
    fig.suptitle("Figure 24. WGD·CIN·LOH 공유 축 (CCA, 이진화 라벨)", y=1.03, fontsize=13)
    fig.text(0.5, -0.04,
             "* component 2에서 mutation canonical score > 10인 8개는 특정 암종이 아니라 hypermutator "
             "(전체 mutation 500~1600개, 코호트 중앙값 26개) 이상치 — 표현형 신호가 아닌 mutation burden 축임.",
             ha="center", fontsize=8, color="#555")
    fig.tight_layout()
    path1 = save(fig, "fig24_mutation_cca.png")

    # Figure 24b. 이진화 vs 연속값 라벨 비교 (component 1) — 암종별 색칠
    grouped, palette = lineage_palette(coords.lineage)
    fig, axes = plt.subplots(1, 2, figsize=(15, 5.5))
    for group, color in palette.items():
        idx = grouped.eq(group).to_numpy()
        axes[0].scatter(coords.U_bin_1[idx], coords.V_bin_1[idx], s=14, alpha=0.6,
                         color=color, label=f"{group} (n={idx.sum()})", linewidths=0)
        axes[1].scatter(coords.U_cont_1[idx], coords.V_cont_1[idx], s=14, alpha=0.6,
                         color=color, label=f"{group} (n={idx.sum()})", linewidths=0)
    axes[0].set_title(f"이진화 라벨 사용\nr = {cca.loc[0, 'correlation_binarized']:.3f}", fontsize=12)
    axes[1].set_title(f"연속값 라벨 사용\nr = {cca.loc[0, 'correlation_continuous_component1']:.3f}", fontsize=12)
    for ax in axes:
        ax.set_xlabel("mutation 패턴 점수 (canonical)")
        ax.set_ylabel("유전체 불안정성 점수 (canonical)")
    axes[1].legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=7.5,
                   title=f"상위 {TOP_N_LINEAGES}개 암종", title_fontsize=8)
    fig.suptitle("Figure 24b. WGD·CIN·LOH 공유 축 검증 (이진화 vs 연속값, 암종별 색칠)",
                 y=1.03, fontsize=13)
    fig.tight_layout()
    path2 = save(fig, "fig24b_mutation_cca_comparison.png")

    # Figure 24c. Figure 24와 같은 component별 3패널, 색은 암종(lineage) 기준.
    fig, axes = plt.subplots(1, n_components, figsize=(15, 5), squeeze=False)
    for i, ax in enumerate(axes.flat):
        for group, color in palette.items():
            idx = grouped.eq(group).to_numpy()
            ax.scatter(coords[f"U_bin_{i + 1}"][idx], coords[f"V_bin_{i + 1}"][idx], s=12, alpha=0.6,
                       color=color, label=f"{group} (n={idx.sum()})", linewidths=0)
        r = cca.loc[i, "correlation_binarized"]
        ax.set(title=f"CCA component {i + 1}: r={r:.3f}",
               xlabel="Mutation canonical score", ylabel="Instability canonical score",
               xlim=x_limits, ylim=y_limits)
    axes.flat[-1].legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=7,
                          title=f"상위 {TOP_N_LINEAGES}개 암종", title_fontsize=8)
    fig.suptitle("Figure 24c. WGD·CIN·LOH 공유 축 (CCA, 암종별 색칠 — Figure 24 대응)",
                 y=1.03, fontsize=13)
    fig.tight_layout()
    path3 = save(fig, "fig24c_mutation_cca_lineage.png")

    print(f"저장: {path1.name}, {path2.name}, {path3.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
