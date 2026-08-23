"""Day 45 — mutation UMAP 시각화 (psh03 탐색 분석 adapt).

Figure 23. WGD/CIN/LOH 상태별 mutation UMAP 분포 (한 좌표계 공유).
Figure 23b. 같은 좌표를 암종(lineage)별로 색칠한 버전 — 표현형 클러스터가
실제로는 암종 클러스터를 반영하는 건 아닌지 눈으로 확인하는 용도.
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
TARGETS = {"wgd": "WGD", "cin": "CIN", "loh": "LOH"}
STATUS_COLORS = {"-": "#4f81bd", "+": "#e76f51"}
TOP_N_LINEAGES = 12


def padded_limits(values: np.ndarray, fraction: float = 0.05) -> tuple[float, float]:
    low, high = float(np.nanmin(values)), float(np.nanmax(values))
    pad = max((high - low) * fraction, 0.1)
    return low - pad, high + pad


def plot_lineage(coords: pd.DataFrame, x_lim: tuple[float, float], y_lim: tuple[float, float]) -> Path:
    """Figure 23b. 암종(lineage) 색칠 — 상위 12종 + 나머지는 'Other'로 묶는다."""
    counts = coords.lineage.value_counts()
    shown = counts.head(TOP_N_LINEAGES).index
    plot_group = coords.lineage.where(coords.lineage.isin(shown), "Other lineage")
    groups = list(shown) + ["Other lineage"]
    palette = dict(zip(groups, sns.color_palette("tab20", len(shown)).as_hex() + ["#bdbdbd"]))

    fig, ax = plt.subplots(figsize=(11, 8))
    for group in groups:
        idx = plot_group.eq(group).to_numpy()
        ax.scatter(coords.UMAP1[idx], coords.UMAP2[idx], s=13, alpha=0.72,
                   color=palette[group], label=f"{group} (n={idx.sum()})", linewidths=0)
    ax.set_title("암종(lineage)별 mutation 패턴 분포", fontsize=13)
    ax.set_xlabel("UMAP 1")
    ax.set_ylabel("UMAP 2")
    ax.set_xlim(*x_lim)
    ax.set_ylim(*y_lim)
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8, title=f"상위 {TOP_N_LINEAGES}개 암종")
    fig.suptitle("Figure 23b. Mutation UMAP — 암종별 분포 (Figure 23과 같은 좌표계)", y=1.0, fontsize=13)
    return save(fig, "fig23b_mutation_umap_lineage.png")


def main() -> int:
    path = TABLES / "day44_mutation_umap_coords.csv"
    if not path.exists():
        raise SystemExit(f"{path.name} 없음 — 먼저 44_mutation_umap.py 를 실행하세요.")
    coords = pd.read_csv(path, index_col=0)

    use_style()
    x_lim = padded_limits(coords.UMAP1.to_numpy())
    y_lim = padded_limits(coords.UMAP2.to_numpy())

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    for ax, target in zip(axes, TARGETS):
        label = TARGETS[target]
        status = coords[target].map({0: f"{label}-", 1: f"{label}+"})
        for suffix, color in STATUS_COLORS.items():
            idx = status.eq(f"{label}{suffix}").to_numpy()
            ax.scatter(coords.UMAP1[idx], coords.UMAP2[idx], s=12, alpha=0.7,
                       color=color, label=f"{label}{suffix} (n={idx.sum()})", linewidths=0)
        ax.set_title(f"{label} 상태별 mutation 패턴 분포", fontsize=13)
        ax.set_xlabel("UMAP 1")
        ax.set_ylabel("UMAP 2")
        ax.set_xlim(*x_lim)
        ax.set_ylim(*y_lim)
        ax.legend(fontsize=9)

    fig.suptitle("Figure 23. Mutation UMAP — WGD·CIN·LOH 상태별 분포", y=1.02, fontsize=14)
    fig.tight_layout()
    out1 = save(fig, "fig23_mutation_umap.png")

    out2 = plot_lineage(coords, x_lim, y_lim)

    print(f"저장: {out1.name}, {out2.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
