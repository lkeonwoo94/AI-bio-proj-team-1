"""Figure — RF N개 패널 confusion matrix (2026-08-21).

`scripts/34_plot_rf_confusion_matrix.py` 와 같은 형식이지만
`scripts/40_rf_panel_confusion_matrix.py` 결과(N개 패널로 inference)를
그린다. fig 번호는 패널 크기에 따라 10→19, 20→20 으로 고정한다(그 외
크기는 fig 번호 없이 파일명에 패널 크기만 붙는다).
"""

from __future__ import annotations

import argparse
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
FIG_NUMBER = {10: "19", 20: "20"}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--panel-size", type=int, default=10)
    args = p.parse_args()
    panel_size = args.panel_size

    use_style()
    cm_df = pd.read_csv(TABLES / f"day40_rf_panel{panel_size}_confusion_matrix.csv").set_index("target")

    fig, axes = plt.subplots(1, 3, figsize=(13, 4.4))
    for ax, target in zip(axes, TARGETS):
        row = cm_df.loc[target]
        cm = np.array([[row.tn, row.fp], [row.fn, row.tp]])
        cm_pct = cm / cm.sum() * 100

        ax.imshow(cm_pct, cmap="Oranges", vmin=0, vmax=cm_pct.max() * 1.15)
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
        f"RF 최소 {panel_size}개 유전자 패널 — inference confusion matrix (5 outer fold pooled, n=1,631)\n"
        "(패널은 각 fold의 training 데이터에서 독립적으로 뽑음 — 표현형별로 정확히 같은 유전자는 아님, §13)",
        y=1.08, fontsize=11,
    )
    fig.tight_layout()
    fig_num = FIG_NUMBER.get(panel_size)
    name = f"fig{fig_num}_rf_panel{panel_size}_confusion_matrix.png" if fig_num \
        else f"rf_panel{panel_size}_confusion_matrix.png"
    path = save(fig, name)
    print(f"저장: {path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
