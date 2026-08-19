"""Figure 18 — 유전자 단위 vs Signature(96-class) 의 sensitivity/specificity 트레이드오프.

`model.md` "참고 — Mutation signature" 절에서 발견한 것: WGD 는 표현
방식(유전자/signature)에 따라 sensitivity 우세와 specificity 우세가
뒤집힌다. 표로는 잘 안 보이는 이 이동을 화살표로 시각화한다.
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
MODELS = ("logistic", "random_forest")
MODEL_LABEL = {"logistic": "Logistic", "random_forest": "Random Forest"}


def main() -> int:
    use_style()
    gene = pd.read_csv(TABLES / "day10_model_comparison.csv")
    sig = (pd.read_csv(TABLES / "day24_signature_summary.csv")
          .groupby(["target", "model"])[["sensitivity", "specificity"]].mean().reset_index())

    fig, axes = plt.subplots(1, 2, figsize=(11, 5.2))
    for ax, model in zip(axes, MODELS):
        ax.plot([0.45, 0.85], [0.45, 0.85], color="#bbb", ls=":", lw=1, zorder=1)
        ax.text(0.83, 0.845, "sens = spec", fontsize=8, color="#999", ha="right")

        for target in TARGETS:
            g = gene[(gene.target == target) & (gene.model == model)].iloc[0]
            s = sig[(sig.target == target) & (sig.model == model)].iloc[0]
            color = PHENOTYPE_COLORS[target]

            ax.annotate("", xy=(s.sensitivity, s.specificity), xytext=(g.sensitivity, g.specificity),
                       arrowprops=dict(arrowstyle="-|>", color=color, lw=1.8, alpha=0.8), zorder=2)
            ax.scatter(g.sensitivity, g.specificity, marker="o", s=110, color=color,
                      edgecolor="white", linewidth=1, zorder=3, label=f"{TARGET_LABEL[target]} (유전자)")
            ax.scatter(s.sensitivity, s.specificity, marker="^", s=110,
                      facecolor="white", edgecolor=color, linewidth=2, zorder=3,
                      label=f"{TARGET_LABEL[target]} (signature)")
            ax.text(g.sensitivity, g.specificity - 0.02, TARGET_LABEL[target],
                   fontsize=8.5, color=color, ha="center", va="top")

        ax.set_xlim(0.45, 0.85)
        ax.set_ylim(0.45, 0.85)
        ax.set_xlabel("Sensitivity")
        ax.set_ylabel("Specificity")
        ax.set_title(MODEL_LABEL[model])
        ax.set_aspect("equal")

    handles = [
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#888", markersize=9, label="유전자 단위"),
        plt.Line2D([0], [0], marker="^", color="w", markerfacecolor="white", markeredgecolor="#888",
                  markeredgewidth=1.5, markersize=9, label="Signature(96개)"),
    ]
    fig.legend(handles=handles, loc="upper center", ncol=2, fontsize=9.5, bbox_to_anchor=(0.5, 1.02))

    fig.suptitle(
        "Figure 18. 표현 방식을 바꾸면 sensitivity↔specificity 균형이 달라진다\n"
        "(화살표: 유전자 단위 → signature. WGD/Random Forest 는 폭이 가장 크다 — sens 0.752→0.636, spec 0.677→0.764)",
        y=1.14, fontsize=11,
    )
    fig.tight_layout()
    path = save(fig, "fig18_sens_spec_tradeoff.png")
    print(f"저장: {path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
