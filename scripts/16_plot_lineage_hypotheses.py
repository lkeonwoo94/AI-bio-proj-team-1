"""Figure 8 — 암종별 LOLO 성능 편차 원인 가설 다섯 가지 (모두 기각).

§26⑤ 후속. 09(기저율·표본크기)와 15(TP53 변이율·burden·극단성)가 각각
계산한 값을 한 그림으로 모아, "무엇을 시도했고 왜 다 기각됐는지"를
한눈에 보여준다.

점 하나 = lineage(암종) 하나(24개). mutation 종류가 아니라 그 암종
전체를 요약한 값(예: 그 암종 안에서 TP53 변이율)과, 그 암종을 LOLO 로
평가했을 때의 ROC-AUC 를 짝지은 것이다.
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


def build_data() -> pd.DataFrame:
    lolo = pd.read_csv(TABLES / "cv_lolo_elastic_net_wgd.csv")[
        ["held_out_lineage", "roc_auc", "n_test", "positive_rate"]
    ].rename(columns={"held_out_lineage": "lineage", "n_test": "n"})
    lolo["base_rate_dev"] = (lolo.positive_rate - 0.652).abs()

    extra = pd.read_csv(TABLES / "day15_lineage_hypothesis_features.csv")[
        ["lineage", "tp53_rate", "mean_burden", "tp53_extremity"]
    ]
    return lolo.merge(extra, on="lineage")


def panel(ax, df: pd.DataFrame, x_col: str, title: str, xlabel: str, n_label: int = 5) -> None:
    """점 = lineage 1개. AUC 상/하위 n_label 개씩 이름을 붙인다.

    패널마다 x 값이 다르므로, 어떤 lineage 가 극단인지도 패널마다 다를 수
    있다 — 고정된 몇 개만 라벨을 다는 대신 이 패널 기준 상/하위를 뽑는다.
    """
    r = spearmanr(df[x_col], df.roc_auc)
    ax.scatter(df[x_col], df.roc_auc, s=40, color=COLOR, alpha=0.8,
              edgecolor="white", linewidth=0.5, zorder=3)
    ax.axhline(0.5, color="#999", ls=":", lw=0.8, zorder=1)

    ranked = df.sort_values("roc_auc")
    to_label = pd.concat([ranked.head(n_label), ranked.tail(n_label)]).drop_duplicates("lineage")
    for _, row in to_label.iterrows():
        ax.annotate(row.lineage, (row[x_col], row.roc_auc), fontsize=6.5,
                    xytext=(4, 3), textcoords="offset points", color="#444")

    verdict = "기각" if r.pvalue >= 0.05 else "유의"
    ax.set_title(f"{title}\nrho={r.statistic:+.3f}, p={r.pvalue:.3f} ({verdict})",
                fontsize=9.5)
    ax.set_xlabel(xlabel, fontsize=8.5)
    ax.set_ylabel("LOLO ROC-AUC (WGD)")
    ax.set_ylim(0.28, 0.92)


def main() -> int:
    use_style()
    df = build_data()

    fig, axes = plt.subplots(2, 3, figsize=(14, 9))
    specs = [
        ("base_rate_dev", "① WGD+ 기저율 편차", "|해당 lineage WGD+ 비율 - 전체 0.652|"),
        ("n", "② 세포주 수", "그 lineage 의 세포주 개수 (n)"),
        ("tp53_rate", "③ TP53 변이율", "그 lineage 안에서 TP53 hotspot/damaging 보유 비율"),
        ("mean_burden", "④ 평균 mutation burden",
         "세포주 1개당 평균 mutation feature 개수 (필터 통과 2,062개 기준)"),
        ("tp53_extremity", "⑤ TP53 변이율의 극단성",
         "min(TP53 변이율, 1-TP53 변이율) — 0 에 가까울수록 그 lineage 안에서 변별력 없음"),
    ]
    for ax, (col, title, xlabel) in zip(axes.flat, specs):
        panel(ax, df, col, title, xlabel)
    axes.flat[-1].set_visible(False)
    axes.flat[-1].text(
        0.02, 0.5,
        "점 1개 = lineage(암종) 1개, 총 24개.\n"
        "라벨은 그 패널에서 LOLO AUC 상위/하위\n"
        "5개씩만 표시했다 (24개 전부 달면 겹쳐서\n"
        "안 보인다). x 는 그 lineage 전체를 요약한\n"
        "값이지 개별 mutation 이 아니다.",
        fontsize=9, color="#555", va="center", transform=axes.flat[-1].transAxes,
    )

    fig.suptitle(
        "Figure 8. 암종별 LOLO 성능 편차 — 원인 가설 다섯 가지 (전부 기각, n=24 lineage)",
        y=1.01, fontsize=12,
    )
    fig.tight_layout()
    path = save(fig, "fig8_lineage_hypotheses.png")

    print(f"저장: {path.name}")
    for col, title, _ in specs:
        r = spearmanr(df[col], df.roc_auc)
        print(f"  {title:12s} rho={r.statistic:+.3f} p={r.pvalue:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
