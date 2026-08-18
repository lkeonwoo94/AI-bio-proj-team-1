"""Figure 8 — 암종별 LOLO 성능 편차 원인 가설 다섯 가지 (모두 기각).

§26⑤ 후속. 09(기저율·표본크기)와 15(TP53 변이율·burden·극단성)가 각각
계산한 값을 한 그림으로 모아, "무엇을 시도했고 왜 다 기각됐는지"를
한눈에 보여준다.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from src.config import REPO_ROOT
from src.viz.style import PHENOTYPE_COLORS, save, use_style

TABLES = REPO_ROOT / "results" / "tables"
COLOR = PHENOTYPE_COLORS["wgd"]

# 라벨을 붙일 대표 사례 (본문에서 실제로 인용한 반례들)
ANNOTATE = {"Eye", "Fibroblast", "Thyroid", "Lung"}


def build_data() -> pd.DataFrame:
    lolo = pd.read_csv(TABLES / "cv_lolo_elastic_net_wgd.csv")[
        ["held_out_lineage", "roc_auc", "n_test", "positive_rate"]
    ].rename(columns={"held_out_lineage": "lineage", "n_test": "n"})
    lolo["base_rate_dev"] = (lolo.positive_rate - 0.652).abs()

    extra = pd.read_csv(TABLES / "day15_lineage_hypothesis_features.csv")[
        ["lineage", "tp53_rate", "mean_burden", "tp53_extremity"]
    ]
    return lolo.merge(extra, on="lineage")


def panel(ax, df: pd.DataFrame, x_col: str, xlabel: str) -> None:
    r = spearmanr(df[x_col], df.roc_auc)
    ax.scatter(df[x_col], df.roc_auc, s=36, color=COLOR, alpha=0.8, zorder=3)
    ax.axhline(0.5, color="#999", ls=":", lw=0.8, zorder=1)

    for _, row in df.iterrows():
        if row.lineage in ANNOTATE:
            ax.annotate(row.lineage, (row[x_col], row.roc_auc), fontsize=7,
                        xytext=(4, 3), textcoords="offset points", color="#444")

    verdict = "기각" if r.pvalue >= 0.05 else "유의"
    ax.set_title(f"{xlabel}\nrho={r.statistic:+.3f}, p={r.pvalue:.3f} ({verdict})",
                fontsize=9.5)
    ax.set_ylabel("LOLO ROC-AUC")
    ax.set_ylim(0.28, 0.92)


def main() -> int:
    use_style()
    df = build_data()

    fig, axes = plt.subplots(2, 3, figsize=(14, 8.5))
    specs = [
        ("base_rate_dev", "① WGD+ 기저율 편차 |p-0.652|"),
        ("n", "② 세포주 수"),
        ("tp53_rate", "③ TP53 변이율"),
        ("mean_burden", "④ 세포주당 평균 mutation burden"),
        ("tp53_extremity", "⑤ TP53 변이율의 극단성\n(0 또는 1에 가까울수록 작음)"),
    ]
    for ax, (col, label) in zip(axes.flat, specs):
        panel(ax, df, col, label)
    axes.flat[-1].set_visible(False)

    fig.suptitle(
        "Figure 8. 암종별 LOLO 성능 편차 — 원인 가설 다섯 가지 (전부 기각, n=24 lineage)",
        y=1.01, fontsize=12,
    )
    fig.tight_layout()
    path = save(fig, "fig8_lineage_hypotheses.png")

    print(f"저장: {path.name}")
    for col, label in specs:
        r = spearmanr(df[col], df.roc_auc)
        print(f"  {label.splitlines()[0]:38s} rho={r.statistic:+.3f} p={r.pvalue:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
