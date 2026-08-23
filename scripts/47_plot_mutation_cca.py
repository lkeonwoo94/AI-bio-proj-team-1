"""Day 47 — CCA 시각화 (psh03 탐색 분석 adapt).

Figure 24. canonical component 별 산점도(이진화 라벨) + 이진화 vs 연속값
라벨 비교(component 1).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.config import REPO_ROOT
from src.viz.style import save, use_style

TABLES = REPO_ROOT / "results" / "tables"


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
    fig.tight_layout()
    path1 = save(fig, "fig24_mutation_cca.png")

    # Figure 24b. 이진화 vs 연속값 라벨 비교 (component 1)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.5))
    axes[0].scatter(coords.U_bin_1, coords.V_bin_1, s=14, alpha=0.5, color="#4f81bd")
    axes[0].set_title(f"이진화 라벨 사용\nr = {cca.loc[0, 'correlation_binarized']:.3f}", fontsize=12)
    axes[1].scatter(coords.U_cont_1, coords.V_cont_1, s=14, alpha=0.5, color="#c0504d")
    axes[1].set_title(f"연속값 라벨 사용\nr = {cca.loc[0, 'correlation_continuous_component1']:.3f}", fontsize=12)
    for ax in axes:
        ax.set_xlabel("mutation 패턴 점수 (canonical)")
        ax.set_ylabel("유전체 불안정성 점수 (canonical)")
    fig.suptitle("Figure 24b. WGD·CIN·LOH 공유 축 검증 (이진화 vs 연속값 비교)", y=1.03, fontsize=13)
    fig.tight_layout()
    path2 = save(fig, "fig24b_mutation_cca_comparison.png")

    print(f"저장: {path1.name}, {path2.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
