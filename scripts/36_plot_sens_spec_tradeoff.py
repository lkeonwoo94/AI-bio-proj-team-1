"""Figure 18 — 유전자 단위 -> Signature -> 유전자+Signature 결합의
sensitivity/specificity 트레이드오프 이동.

`model.md` "참고 — Mutation signature" 절에서 발견한 것: 표현 방식을
바꾸면(유전자 -> signature -> 결합) sensitivity 우세와 specificity
우세가 뒤집히는 경우가 있다. 세 단계 모두를 화살표로 이어 이동
경로를 보여준다. 결합 단계는 `scripts/32_combined_gene_signature_panel.py`
의 "전체 feature" 행(panel_size="all")을 쓴다 — 패널을 줄이지 않은
상태라야 §1/signature 절의 "전체 feature" 성능과 같은 기준으로
비교된다.
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
COMBINED_MODEL_OF = {"logistic": "logistic_l1", "random_forest": "random_forest"}


def main() -> int:
    use_style()
    gene = pd.read_csv(TABLES / "day10_model_comparison.csv")
    sig = (pd.read_csv(TABLES / "day24_signature_summary.csv")
          .groupby(["target", "model"])[["sensitivity", "specificity"]].mean().reset_index())
    comb_raw = pd.read_csv(TABLES / "day32_combined_panel_metrics.csv")
    comb = (comb_raw[comb_raw.panel_size == "all"]
           .groupby(["target", "model"])[["sensitivity", "specificity"]].mean().reset_index())

    fig, axes = plt.subplots(1, 2, figsize=(11, 5.6))
    for ax, model in zip(axes, MODELS):
        ax.plot([0.45, 0.85], [0.45, 0.85], color="#bbb", ls=":", lw=1, zorder=1)
        ax.text(0.83, 0.845, "sens = spec", fontsize=8, color="#999", ha="right")

        for target in TARGETS:
            g = gene[(gene.target == target) & (gene.model == model)].iloc[0]
            s = sig[(sig.target == target) & (sig.model == model)].iloc[0]
            c = comb[(comb.target == target) & (comb.model == COMBINED_MODEL_OF[model])].iloc[0]
            color = PHENOTYPE_COLORS[target]
            points = [(g.sensitivity, g.specificity), (s.sensitivity, s.specificity),
                     (c.sensitivity, c.specificity)]

            for (x0, y0), (x1, y1) in zip(points[:-1], points[1:]):
                ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                           arrowprops=dict(arrowstyle="-|>", color=color, lw=1.6, alpha=0.75), zorder=2)

            ax.scatter(*points[0], marker="o", s=110, color=color, edgecolor="white",
                      linewidth=1, zorder=3, label=f"{TARGET_LABEL[target]} 유전자")
            ax.scatter(*points[1], marker="^", s=110, facecolor="white", edgecolor=color,
                      linewidth=2, zorder=3, label=f"{TARGET_LABEL[target]} signature")
            ax.scatter(*points[2], marker="s", s=100, color=color, edgecolor="white",
                      linewidth=1, alpha=0.55, zorder=3, label=f"{TARGET_LABEL[target]} 결합")
            ax.text(points[0][0], points[0][1] - 0.022, TARGET_LABEL[target],
                   fontsize=8.5, color=color, ha="center", va="top")

        ax.set_xlim(0.45, 0.85)
        ax.set_ylim(0.45, 0.85)
        ax.set_xlabel("Sensitivity")
        ax.set_ylabel("Specificity")
        ax.set_title(MODEL_LABEL[model])
        ax.set_aspect("equal")

    handles = [
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#888", markersize=9, label="① 유전자 단위"),
        plt.Line2D([0], [0], marker="^", color="w", markerfacecolor="white", markeredgecolor="#888",
                  markeredgewidth=1.5, markersize=9, label="② Signature(96개)"),
        plt.Line2D([0], [0], marker="s", color="w", markerfacecolor="#888", markersize=9,
                  alpha=0.55, label="③ 유전자+Signature 결합"),
    ]
    fig.legend(handles=handles, loc="upper center", ncol=3, fontsize=9, bbox_to_anchor=(0.5, 1.03))

    fig.suptitle(
        "Figure 18. 유전자 → signature → 결합, 세 표현 방식의 sensitivity/specificity 이동\n"
        "(대각선을 넘으면 sens/spec 우세가 뒤집힘 — CIN 은 두 모델 모두 세 단계 내내 sens 우세를 유지)",
        y=1.16, fontsize=11,
    )
    fig.tight_layout()
    path = save(fig, "fig18_sens_spec_tradeoff.png")
    print(f"저장: {path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
