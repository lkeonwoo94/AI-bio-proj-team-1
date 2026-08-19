"""Figure 12 — 유전자 단위 vs Mutation signature(96-class) 표현 비교.

Future Work 2 결과. 96개 SBS feature 가 유전자 단위(필터 후 ~2,062개)와
같은 random 5-fold 조건에서 어떻게 다른지 6개 조합 전부 보여준다.
Figure 10(pathway, 전부 음성)과 나란히 놓고 보면 대비가 뚜렷하다.
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
TARGET_LABEL = {"wgd": "WGD", "cin": "CIN", "loh": "LOH"}
MODEL_LABEL = {"logistic": "Logistic", "random_forest": "Random Forest"}


def main() -> int:
    use_style()
    df = pd.read_csv(TABLES / "day24_signature_vs_gene.csv")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
    models = ["logistic", "random_forest"]

    for ax, model in zip(axes, models):
        sub = df[df.model == model].set_index("target").reindex(["wgd", "cin", "loh"])
        x = np.arange(3)
        width = 0.32

        ax.bar(x - width / 2, sub.gene_level_auc, width,
              label="유전자 단위 (~2,062개, 필터 후)", color="#bfbfbf")
        colors = [PHENOTYPE_COLORS[t] for t in ("wgd", "cin", "loh")]
        ax.bar(x + width / 2, sub.signature_auc, width,
              label="Mutation signature (96개)", color=colors, alpha=0.85)

        for i, (gene_auc, sig_auc) in enumerate(zip(sub.gene_level_auc, sub.signature_auc)):
            ax.text(i, max(gene_auc, sig_auc) + 0.015, f"{sig_auc - gene_auc:+.3f}",
                    ha="center", fontsize=8.5, color="#333")

        ax.axhline(0.5, color="#999", ls=":", lw=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels([TARGET_LABEL[t] for t in ("wgd", "cin", "loh")])
        ax.set_ylim(0.4, 0.85)
        ax.set_ylabel("ROC-AUC")
        ax.set_title(MODEL_LABEL[model])
        ax.legend(fontsize=7.5, loc="upper right")

    fig.suptitle(
        "Figure 12. 유전자 단위 vs Mutation Signature(96-class) — 5/6 조합에서 개선\n"
        "(막대 위 숫자 = signature - 유전자단위. Figure 10(pathway, 전부 음성)과 대비)",
        y=1.05, fontsize=11,
    )
    fig.tight_layout()
    path = save(fig, "fig12_signature_vs_gene.png")
    print(f"저장: {path.name}")
    print(df.round(3).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
