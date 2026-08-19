"""Figure 15 — Mutation signature 성능의 seed 재현성 (한계 2번 후속).

`scripts/27_signature_seed_robustness.py` 결과를 그린다. 3개 outer
fold seed 에 걸친 ROC-AUC 산포와, 원래(기본 seed) 값을 함께 표시한다.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.config import REPO_ROOT
from src.viz.style import PHENOTYPE_COLORS, save, use_style

TABLES = REPO_ROOT / "results" / "tables"
TARGETS = ("wgd", "cin", "loh")
TARGET_LABEL = {"wgd": "WGD", "cin": "CIN", "loh": "LOH"}
MODEL_LABEL = {"logistic": "Logistic", "random_forest": "Random Forest"}


def main() -> int:
    use_style()
    result = pd.read_csv(TABLES / "day27_signature_seed_robustness.csv")
    summary = pd.read_csv(TABLES / "day27_signature_seed_robustness_summary.csv")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
    for ax, model in zip(axes, ("logistic", "random_forest")):
        for i, target in enumerate(TARGETS):
            sub = result[(result.model == model) & (result.target == target)]
            jitter = np.random.default_rng(0).uniform(-0.06, 0.06, size=len(sub))
            ax.scatter(np.full(len(sub), i) + jitter, sub.roc_auc,
                      color=PHENOTYPE_COLORS[target], s=45, zorder=3, label="_nolegend_")

            row = summary[(summary.model == model) & (summary.target == target)].iloc[0]
            ax.hlines(row.default_seed_auc, i - 0.22, i + 0.22,
                      color=PHENOTYPE_COLORS[target], lw=2.2, zorder=4)
            ax.vlines(i, row["min"], row["max"], color=PHENOTYPE_COLORS[target], lw=1, alpha=0.4, zorder=2)

        ax.set_xticks(range(len(TARGETS)))
        ax.set_xticklabels([TARGET_LABEL[t] for t in TARGETS])
        ax.set_ylabel("ROC-AUC")
        ax.set_title(MODEL_LABEL[model])

    handles = [
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#888", markersize=7,
                  label="개별 seed(0,1,2)"),
        plt.Line2D([0], [0], color="#888", lw=2.2, label="기본 seed(원래 값)"),
    ]
    fig.legend(handles=handles, loc="upper center", ncol=2, fontsize=9, bbox_to_anchor=(0.5, 1.02))

    fig.suptitle(
        "Figure 15. Mutation signature 성능의 seed 재현성 — 변동폭 0.001~0.005 로 매우 안정적\n"
        "(세로선은 3-seed 범위, 굵은 가로선은 기존 결과에 쓴 기본 seed 값)",
        y=1.14, fontsize=11,
    )
    fig.tight_layout()
    path = save(fig, "fig15_signature_seed_robustness.png")
    print(f"저장: {path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
