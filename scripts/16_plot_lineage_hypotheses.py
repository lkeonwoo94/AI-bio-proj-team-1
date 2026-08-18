"""Figure 8 — 암종별 LOLO 성능 편차 원인 가설 다섯 가지 (모두 기각).

§26⑤ 후속. 09(기저율·표본크기)와 15(TP53 변이율·burden·극단성)가 각각
계산한 값을 한 그림으로 모아, "무엇을 시도했고 왜 다 기각됐는지"를
한눈에 보여준다.

점 하나 = lineage(암종) 하나(24개). mutation 종류가 아니라 그 암종
전체를 요약한 값(예: 그 암종 안에서 TP53 변이율)과, 그 암종을 LOLO 로
평가했을 때의 ROC-AUC 를 짝지은 것이다.
"""

from __future__ import annotations

import argparse
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
TARGET_LABEL = {"wgd": "WGD", "cin": "CIN", "loh": "LOH"}
MODEL_LABEL = {
    "logistic": "Logistic", "elastic_net": "Elastic Net",
    "random_forest": "Random Forest", "xgboost": "XGBoost", "catboost": "CatBoost",
}


def build_data(model: str, target: str) -> pd.DataFrame:
    lolo = pd.read_csv(TABLES / f"cv_lolo_{model}_{target}.csv")[
        ["held_out_lineage", "roc_auc", "n_test", "positive_rate"]
    ].rename(columns={"held_out_lineage": "lineage", "n_test": "n"})

    # '전체 기저율'을 표현형마다 다시 하드코딩하지 않기 위해, 같은 LOLO 결과
    # 안에서 세포주 수로 가중평균한 값을 쓴다. WGD 로 검산하면 0.655 로
    # 원래 쓰던 상수 0.652(전체 코호트 비율, 20개 미만 lineage 포함)와
    # 거의 같다 — LOLO 는 그 8종을 빼므로 완전히 같지는 않다.
    global_rate = (lolo.positive_rate * lolo.n).sum() / lolo.n.sum()
    lolo["base_rate_dev"] = (lolo.positive_rate - global_rate).abs()

    extra = pd.read_csv(TABLES / f"day15_lineage_hypothesis_features_{model}_{target}.csv")[
        ["lineage", "tp53_rate", "mean_burden", "tp53_extremity"]
    ]
    return lolo.merge(extra, on="lineage"), global_rate


def panel(ax, df: pd.DataFrame, x_col: str, title: str, xlabel: str,
         target: str, target_label: str, n_label: int = 5) -> None:
    """점 = lineage 1개. AUC 상/하위 n_label 개씩 이름을 붙인다.

    패널마다 x 값이 다르므로, 어떤 lineage 가 극단인지도 패널마다 다를 수
    있다 — 고정된 몇 개만 라벨을 다는 대신 이 패널 기준 상/하위를 뽑는다.
    """
    r = spearmanr(df[x_col], df.roc_auc)
    ax.scatter(df[x_col], df.roc_auc, s=40, color=PHENOTYPE_COLORS[target], alpha=0.8,
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
    ax.set_ylabel(f"LOLO ROC-AUC ({target_label})")
    ax.set_ylim(0.28, 0.92)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="elastic_net")
    p.add_argument("--target", default="wgd", help="wgd | cin | loh")
    args = p.parse_args()
    target_label = TARGET_LABEL[args.target]

    use_style()
    df, global_rate = build_data(args.model, args.target)

    fig, axes = plt.subplots(2, 3, figsize=(14, 9))
    specs = [
        ("base_rate_dev", f"① {target_label}+ 기저율 편차",
         f"|해당 lineage {target_label}+ 비율 - 전체 {global_rate:.3f}|"),
        ("n", "② 세포주 수", "그 lineage 의 세포주 개수 (n)"),
        ("tp53_rate", "③ TP53 변이율", "그 lineage 안에서 TP53 hotspot/damaging 보유 비율"),
        ("mean_burden", "④ 평균 mutation burden",
         "세포주 1개당 평균 mutation feature 개수 (필터 통과 2,062개 기준)"),
        ("tp53_extremity", "⑤ TP53 변이율의 극단성",
         "min(TP53 변이율, 1-TP53 변이율) — 0 에 가까울수록 그 lineage 안에서 변별력 없음"),
    ]
    for ax, (col, title, xlabel) in zip(axes.flat, specs):
        panel(ax, df, col, title, xlabel, args.target, target_label)
    axes.flat[-1].axis("off")  # set_visible(False) 는 이후 text() 까지 숨겨버려서 axis(off) 로 대체
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
        f"Figure 8. 암종별 LOLO 성능 편차 — 원인 가설 다섯 가지 "
        f"({target_label}, {MODEL_LABEL.get(args.model, args.model)}, n=24 lineage)",
        y=1.01, fontsize=12,
    )
    fig.tight_layout()
    path = save(fig, f"fig8_lineage_hypotheses_{args.model}_{args.target}.png")

    print(f"저장: {path.name}")
    for col, title, _ in specs:
        r = spearmanr(df[col], df.roc_auc)
        print(f"  {title:12s} rho={r.statistic:+.3f} p={r.pvalue:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
