"""Figure 17 — 유전자+Mutation signature 결합 패널.

`scripts/32_combined_gene_signature_panel.py` 결과를 그린다.
  (a) 결합 vs 유전자만 vs signature만 (전체 feature 기준 ROC-AUC)
  (b) 10개 패널 안에서 유전자/signature 가 각각 몇 개씩 뽑히는지(모델별)
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
MODELS = ("logistic_l1", "random_forest")
MODEL_LABEL = {"logistic_l1": "Logistic(L1)", "random_forest": "Random Forest"}


def main() -> int:
    use_style()
    summary = pd.read_csv(TABLES / "day32_combined_vs_single_summary.csv")
    comp = pd.read_csv(TABLES / "day32_combined_panel_composition.csv")

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))

    ax = axes[0]
    x = np.arange(len(MODELS) * len(TARGETS))
    width = 0.26
    labels = [f"{MODEL_LABEL[m]}\n{TARGET_LABEL[t]}" for m in MODELS for t in TARGETS]
    combos = [(m, t) for m in MODELS for t in TARGETS]
    combined_v = [summary[(summary.model == m) & (summary.target == t)]["결합"].iloc[0] for m, t in combos]
    gene_v = [summary[(summary.model == m) & (summary.target == t)]["유전자만"].iloc[0] for m, t in combos]
    sig_v = [summary[(summary.model == m) & (summary.target == t)]["signature만"].iloc[0] for m, t in combos]

    ax.bar(x - width, gene_v, width, label="유전자만", color="#bfbfbf")
    ax.bar(x, sig_v, width, label="Signature만", color="#8faadc")
    ax.bar(x + width, combined_v, width, label="결합", color="#c0504d")
    for i, gv in enumerate(gene_v):
        ax.text(i - width, gv + 0.008, f"{gv:.3f}", ha="center", fontsize=8)
    for i, sv in enumerate(sig_v):
        ax.text(i, sv + 0.008, f"{sv:.3f}", ha="center", fontsize=8)
    for i, cv in enumerate(combined_v):
        ax.text(i + width, cv + 0.008, f"{cv:.3f}", ha="center", fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8.5)
    ax.set_ylabel("ROC-AUC (전체 feature)")
    ax.set_ylim(0.6, 0.85)
    ax.set_title("(a) 결합이 항상 단일 축보다 높다 (6/6 조합)")
    ax.legend(fontsize=8.5)

    ax2 = axes[1]
    comp10 = comp[comp.panel_size == 10].groupby("model")[["n_genes", "n_sig"]].mean()
    comp10 = comp10.reindex(MODELS)
    xm = np.arange(len(MODELS))
    ax2.bar(xm, comp10.n_genes, 0.5, label="유전자", color="#bfbfbf")
    ax2.bar(xm, comp10.n_sig, 0.5, bottom=comp10.n_genes, label="Signature class", color="#8faadc")
    for i, (g, s) in enumerate(zip(comp10.n_genes, comp10.n_sig)):
        ax2.text(i, g / 2, f"유전자\n{g:.1f}", ha="center", va="center", fontsize=8.5)
        ax2.text(i, g + s / 2, f"signature\n{s:.1f}", ha="center", va="center", fontsize=8.5, color="white")
    ax2.set_xticks(list(xm))
    ax2.set_xticklabels([MODEL_LABEL[m] for m in MODELS])
    ax2.set_ylabel("10개 패널 평균 구성")
    ax2.set_title("(b) 모델에 따라 구성이 다르다 (3표현형 평균)")

    fig.suptitle(
        "Figure 17. 유전자+Signature 결합 패널 — 성능은 항상 개선, 구성은 모델마다 다르다\n"
        "(RF 는 signature 쪽으로 쏠림 — RF impurity importance 의 연속형 feature 편향 가능성, 본문 참고)",
        y=1.08, fontsize=11,
    )
    fig.tight_layout()
    path = save(fig, "fig17_combined_panel.png")
    print(f"저장: {path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
