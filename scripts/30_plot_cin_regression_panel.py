"""Figure 14 — CIN 회귀 기반 최소 패널 (한계 6번 후속).

`scripts/28_cin_regression_panel.py` 결과를 그린다. 두 패널:
  (a) 패널 크기별 회귀 성능(Spearman rho) — 유전자 단위 Figure 5 와 같은 형식
  (b) 분류 패널(Day 11/12) vs 회귀 패널의 10개 유전자 Jaccard 겹침
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import pandas as pd

from src.config import REPO_ROOT
from src.viz.style import save, use_style

TABLES = REPO_ROOT / "results" / "tables"
MODELS = ("elastic_net_reg", "random_forest_reg")
MODEL_LABEL = {"elastic_net_reg": "Elastic Net (회귀)", "random_forest_reg": "Random Forest (회귀)"}
CLF_MODEL_OF = {"elastic_net_reg": "elastic_net", "random_forest_reg": "random_forest"}
CLF_LABEL = {"elastic_net_reg": "Elastic Net", "random_forest_reg": "Random Forest"}
SIZES = [5, 10, 20, 50]
COLORS = {"elastic_net_reg": "#4f81bd", "random_forest_reg": "#c0504d"}


def compute_overlap() -> pd.DataFrame:
    picks = pd.read_csv(TABLES / "day28_cin_regression_panel_picks.csv")
    rows = []
    for model_name in MODELS:
        clf_model = CLF_MODEL_OF[model_name]
        clf_path = TABLES / f"day12_panel_picks_{clf_model}.csv"
        clf_picks = pd.read_csv(clf_path)
        clf_genes = set(
            clf_picks[(clf_picks.target == "cin") & (clf_picks.panel_size == 10)]
            .feature.str.split(" \\(").str[0]
        )
        reg_genes = set(
            picks[(picks.model == model_name) & (picks.panel_size == 10)]
            .feature.str.split(" \\(").str[0]
        )
        overlap = clf_genes & reg_genes
        union = clf_genes | reg_genes
        rows.append({
            "model": model_name, "jaccard": len(overlap) / len(union) if union else float("nan"),
            "n_common": len(overlap), "n_clf_only": len(clf_genes - reg_genes),
            "n_reg_only": len(reg_genes - clf_genes),
        })
    return pd.DataFrame(rows)


def main() -> int:
    use_style()
    metrics = pd.read_csv(TABLES / "day28_cin_regression_panel_metrics.csv")
    overlap = compute_overlap()

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    ax = axes[0]
    order = [str(s) for s in SIZES] + ["all"]
    for model_name in MODELS:
        sub = metrics[metrics.model == model_name]
        g = sub.groupby(sub.panel_size.astype(str)).spearman_rho
        mean = g.mean().reindex(order)
        std = g.std().reindex(order)
        ax.errorbar(range(len(order)), mean, yerr=std, marker="o", capsize=3,
                    label=MODEL_LABEL[model_name], color=COLORS[model_name])
        full = mean.get("all")
        if pd.notna(full):
            ax.axhline(full, color=COLORS[model_name], ls=":", lw=0.8, alpha=0.5)
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels([f"{o}개" if o != "all" else "전체" for o in order])
    ax.set_xlabel("패널 크기")
    ax.set_ylabel("Spearman rho")
    ax.set_title("(a) CIN 회귀 기반 패널 크기별 성능")
    ax.legend(fontsize=9)

    ax2 = axes[1]
    x = range(len(MODELS))
    bars = ax2.bar(x, overlap.jaccard, color=[COLORS[m] for m in MODELS], alpha=0.85)
    for i, row in overlap.iterrows():
        ax2.text(i, row.jaccard + 0.02, f"공통 {row.n_common}개\n(clf만 {row.n_clf_only},"
                 f" reg만 {row.n_reg_only})", ha="center", fontsize=8)
    ax2.set_xticks(list(x))
    ax2.set_xticklabels([CLF_LABEL[m] for m in MODELS])
    ax2.set_ylabel("Jaccard (분류 vs 회귀, 10개 패널)")
    ax2.set_ylim(0, 0.7)
    ax2.set_title("(b) 분류 패널과 회귀 패널의 유전자 겹침")

    fig.suptitle(
        "Figure 14. CIN 회귀 기반 최소 패널 — 분류·회귀 방법을 넘어 핵심 유전자가 겹친다\n"
        "(TP53/BRAF/ID3/CREBBP/PIK3CA/RB1/TERT 등, 한계 6번 후속)",
        y=1.06, fontsize=11,
    )
    fig.tight_layout()
    path = save(fig, "fig14_cin_regression_panel.png")
    print(f"저장: {path.name}")
    print(overlap.round(3).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
