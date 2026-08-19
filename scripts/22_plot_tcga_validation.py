"""Figure 11 — DepMap 내부 vs TCGA 외부 검증.

damaging-only 기준으로 맞춘 두 성능을 나란히 놓는다. TP53 damaging
비율의 코호트 간 격차(방법론적 원인)도 함께 보여줘서, 하락폭을 그대로
"세포주→종양 일반화 실패"로 읽지 않도록 한다.
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


def main() -> int:
    use_style()
    summary = pd.read_csv(TABLES / "day21_tcga_validation_summary.csv")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))

    ax = axes[0]
    colors = ["#bfbfbf", PHENOTYPE_COLORS["wgd"]]
    bars = ax.bar(summary.stage.str.replace("(", "\n(", regex=False), summary.roc_auc,
                  color=colors, width=0.55)
    for b, v, n in zip(bars, summary.roc_auc, summary.n):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.015, f"{v:.3f}\n(n={n:,})",
                ha="center", fontsize=9)
    ax.axhline(0.5, color="#999", ls=":", lw=0.8, label="무작위 수준")
    ax.set_ylim(0.4, 0.9)
    ax.set_ylabel("ROC-AUC (WGD, damaging-only)")
    ax.set_title("(a) 내부 vs 외부 검증")
    ax.legend(fontsize=8)
    ax.tick_params(axis="x", labelsize=8.5)

    ax = axes[1]
    tp53 = pd.DataFrame({
        "cohort": ["DepMap\n(세포주)", "TCGA\n(환자 종양)"],
        "rate": [0.578, 0.124],
    })
    ax.bar(tp53.cohort, tp53.rate, color=["#bfbfbf", PHENOTYPE_COLORS["wgd"]], width=0.55)
    for i, v in enumerate(tp53.rate):
        ax.text(i, v + 0.02, f"{v:.1%}", ha="center", fontsize=9)
    ax.set_ylim(0, 0.7)
    ax.set_ylabel("TP53 damaging(근사) 비율")
    ax.set_title("(b) 격차의 방법론적 원인 — TP53")

    fig.suptitle(
        "Figure 11. TCGA 독립 코호트 검증 (WGD, damaging-only)\n"
        "(b)는 (a)의 하락폭 -0.168 을 '일반화 실패'로 단정하면 안 되는 이유:\n"
        "TP53 missense 2,927건 중 대부분이 truncating-only 기준에서 누락됨",
        y=1.12, fontsize=11,
    )
    fig.tight_layout()
    path = save(fig, "fig11_tcga_validation.png")
    print(f"저장: {path.name}")
    print(summary.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
