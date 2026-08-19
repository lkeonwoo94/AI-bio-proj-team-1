"""Figure 13 — Mutation signature(96-class) 최소 패널 곡선.

`scripts/26_signature_panel.py` 결과를 Day 12(Figure 5)와 같은 형식으로
그린다.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import pandas as pd

from src.config import REPO_ROOT
from src.viz.style import PHENOTYPE_COLORS, save, use_style

TABLES = REPO_ROOT / "results" / "tables"
TARGETS = ("wgd", "cin", "loh")
TARGET_LABEL = {"wgd": "WGD", "cin": "CIN", "loh": "LOH"}
MODEL_LABEL = {"logistic_l1": "Logistic(L1)", "random_forest": "Random Forest"}
SIZES = [5, 10, 20, 30]


def main() -> int:
    use_style()
    metrics = pd.read_csv(TABLES / "day26_signature_panel_metrics.csv")
    order = [str(s) for s in SIZES] + ["all"]

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    for ax, model in zip(axes, ("logistic_l1", "random_forest")):
        for target in TARGETS:
            sub = metrics[(metrics.model == model) & (metrics.target == target)]
            g = sub.groupby(sub.panel_size.astype(str)).roc_auc
            mean = g.mean().reindex(order)
            std = g.std().reindex(order)
            ax.errorbar(range(len(order)), mean, yerr=std, marker="o", capsize=3,
                        label=TARGET_LABEL[target], color=PHENOTYPE_COLORS[target])
            full = mean.get("all")
            if pd.notna(full):
                ax.axhline(full, color=PHENOTYPE_COLORS[target], ls=":", lw=0.8, alpha=0.5)

        ax.set_xticks(range(len(order)))
        ax.set_xticklabels([f"{o}개" if o != "all" else "전체(96)" for o in order])
        ax.set_xlabel("패널 크기")
        ax.set_ylabel("ROC-AUC")
        ax.set_title(MODEL_LABEL[model])
        ax.legend(fontsize=9)

    fig.suptitle(
        "Figure 13. Mutation signature 최소 패널 — 20~30개로 전체(96개) 성능의 95~99% 유지\n"
        "(점선은 전체 96-class 성능, 유전자 단위 Day 12(Figure 5)와 같은 형식)",
        y=1.06, fontsize=11,
    )
    fig.tight_layout()
    path = save(fig, "fig13_signature_panel_curve.png")
    print(f"저장: {path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
