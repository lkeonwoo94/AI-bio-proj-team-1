"""Figure 9 — CIN/LoHFraction: 분류(이진화) vs 회귀(연속값) 신호 비교.

§26⑤ 후속, "보완 5번"(CIN/LOH 를 high/low 로 나누며 정보가 손실된다는
지적)에 대한 실험 결과. ROC-AUC 와 Spearman rho 는 척도가 달라 직접
비교할 수 없으므로, AUC 를 2*(AUC-0.5) 로 rho 와 같은 -1~1 스케일에
근사 환산해 나란히 놓는다 — 엄밀한 통계적 등가가 아니라 방향과 크기를
가늠하기 위한 근사치다.
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
TARGET_LABEL = {"cin": "CIN", "loh": "LoHFraction"}


def main() -> int:
    use_style()
    cmp_df = pd.read_csv(TABLES / "day15b_regression_vs_classification.csv")
    cmp_df["clf_auc_as_rho"] = (cmp_df.clf_roc_auc - 0.5) * 2

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))
    families = ["elastic_net", "random_forest"]
    family_label = {"elastic_net": "Elastic Net", "random_forest": "Random Forest"}

    for ax, target in zip(axes, ("cin", "loh")):
        sub = cmp_df[cmp_df.target == target].set_index("model_family").reindex(families)
        x = np.arange(len(families))
        width = 0.32
        ax.bar(x - width / 2, sub.clf_auc_as_rho, width,
              label="분류 ROC-AUC (근사환산: 2×(AUC-0.5))",
              color="#bfbfbf")
        ax.bar(x + width / 2, sub.reg_spearman_rho, width,
              label="회귀 Spearman rho", color=PHENOTYPE_COLORS[target])

        for i, (auc_rho, reg_rho) in enumerate(zip(sub.clf_auc_as_rho, sub.reg_spearman_rho)):
            ax.text(i, max(auc_rho, reg_rho) + 0.02, f"{reg_rho - auc_rho:+.3f}",
                    ha="center", fontsize=8.5, color="#333")

        ax.set_xticks(x)
        ax.set_xticklabels([family_label[f] for f in families])
        ax.set_ylim(0, 0.65)
        ax.set_ylabel("스케일 근사값 (0~1)")
        ax.set_title(f"{TARGET_LABEL[target]}")
        ax.legend(fontsize=7.5, loc="upper left")

    fig.suptitle(
        "Figure 9. 이진 분류 vs 연속값 회귀 — 정보 손실이 있다면 회귀 막대가 더 높아야 한다\n"
        "(막대 위 숫자 = 회귀 - 환산분류, 라벨 위 텍스트는 근사 비교용이지 엄밀한 등가가 아님)",
        y=1.06, fontsize=11,
    )
    fig.tight_layout()
    path = save(fig, "fig9_regression_vs_classification.png")
    print(f"저장: {path.name}")
    print(cmp_df.round(3).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
