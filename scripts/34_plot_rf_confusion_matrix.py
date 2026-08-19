"""Figure 16 — Random Forest confusion matrix (WGD/CIN/LOH).

`scripts/33_rf_confusion_matrix.py` 결과(5개 outer fold 를 합친 pooled
confusion matrix)를 세 표현형 나란히 그린다.
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
TARGETS = ("wgd", "cin", "loh")
TARGET_LABEL = {"wgd": "WGD", "cin": "CIN", "loh": "LOH"}
CLASS_LABEL = {
    "wgd": ("WGD-", "WGD+"), "cin": ("CIN-low", "CIN-high"), "loh": ("LOH-low", "LOH-high"),
}


def main() -> int:
    use_style()
    cm_df = pd.read_csv(TABLES / "day33_rf_confusion_matrix.csv").set_index("target")

    fig, axes = plt.subplots(1, 3, figsize=(13, 4.4))
    for ax, target in zip(axes, TARGETS):
        row = cm_df.loc[target]
        cm = np.array([[row.tn, row.fp], [row.fn, row.tp]])
        cm_pct = cm / cm.sum() * 100

        im = ax.imshow(cm_pct, cmap="Blues", vmin=0, vmax=cm_pct.max() * 1.15)
        labels = CLASS_LABEL[target]
        for i in range(2):
            for j in range(2):
                color = "white" if cm_pct[i, j] > cm_pct.max() * 0.6 else "black"
                ax.text(j, i, f"{int(cm[i, j])}\n({cm_pct[i, j]:.1f}%)",
                       ha="center", va="center", fontsize=11, color=color)

        ax.set_xticks([0, 1]); ax.set_xticklabels([f"예측\n{labels[0]}", f"예측\n{labels[1]}"])
        ax.set_yticks([0, 1]); ax.set_yticklabels([f"실제 {labels[0]}", f"실제 {labels[1]}"])
        ax.set_title(f"{TARGET_LABEL[target]}\nsens {row.sensitivity:.3f} | "
                     f"spec {row.specificity:.3f} | bal.acc {row.balanced_accuracy:.3f}")
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.grid(False)

    fig.suptitle(
        "Figure 16. Random Forest confusion matrix — 5개 outer fold pooled (n=1,631)\n"
        "(threshold 는 각 fold training 데이터의 out-of-fold 예측으로 결정, §13)",
        y=1.06, fontsize=11,
    )
    fig.tight_layout()
    path = save(fig, "fig16_rf_confusion_matrix.png")
    print(f"저장: {path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
