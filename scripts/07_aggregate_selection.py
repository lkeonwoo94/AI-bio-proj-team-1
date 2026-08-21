"""Day 11 — fold 반복 feature selection 집계 (README §16).

Figure 4 (유전자별 fold 선택 빈도) 를 만든다.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import pandas as pd

from src.config import REPO_ROOT
from src.selection.aggregate import aggregate_selection, cross_phenotype_table
from src.viz.style import PHENOTYPE_COLORS, save, use_style

TABLES = REPO_ROOT / "results" / "tables"
TARGETS = ("wgd", "cin", "loh")
TARGET_LABEL = {"wgd": "WGD", "cin": "CIN", "loh": "LOH"}
MODEL_LABEL = {
    "logistic": "Logistic", "elastic_net": "Elastic Net",
    "random_forest": "Random Forest", "xgboost": "XGBoost", "catboost": "CatBoost",
    "multitask_ann": "Multi-task ANN",
}


def short(feature: str, width: int = 22) -> str:
    """'TP53 (7157)_damaging' -> 'TP53 (damaging)'"""
    gene = feature.split(" (")[0]
    kind = "hs" if feature.endswith("_hotspot") else "dmg"
    label = f"{gene} ({kind})"
    return label[:width]


def plot_stability(aggs: dict[str, pd.DataFrame], model: str, top_n: int = 15) -> Path:
    use_style()
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    for ax, target in zip(axes, TARGETS):
        agg = aggs[target]
        if agg.empty:
            ax.set_visible(False)
            continue
        top = agg.head(top_n).iloc[::-1]
        ax.barh([short(f) for f in top.feature], top.selection_freq,
                color=PHENOTYPE_COLORS[target])
        ax.set_xlim(0, 1.05)
        ax.set_xlabel("fold 선택 빈도")
        ax.set_title(f"{TARGET_LABEL[target]} 상위 {top_n}개")
        ax.tick_params(axis="y", labelsize=8)

    fig.suptitle(f"Figure 4. 반복 feature selection 안정성 "
                 f"({MODEL_LABEL.get(model, model)}, outer 5-fold)",
                 y=1.02, fontsize=12)
    fig.tight_layout()
    return save(fig, f"fig4_selection_stability_{model}.png")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="elastic_net", help="중요도를 집계할 모델")
    p.add_argument("--top-k", type=int, default=50, help="fold 안에서 '선택됨' 으로 볼 상위 개수")
    p.add_argument("--top-n", type=int, default=15, help="Figure 4에 표시할 유전자 개수")
    args = p.parse_args()

    aggs = {}
    for target in TARGETS:
        path = TABLES / f"selection_random_{args.model}_{target}.csv"
        if not path.exists():
            print(f"  {path.name} 없음 — 건너뜀")
            aggs[target] = pd.DataFrame()
            continue

        agg = aggregate_selection(pd.read_csv(path), top_k=args.top_k)
        aggs[target] = agg
        agg.to_csv(TABLES / f"day11_selection_{args.model}_{target}.csv", index=False)

        stable = agg[agg.selection_freq == 1.0]
        print(f"\n[{TARGET_LABEL[target]}] 전 fold 선택 {len(stable)}개 "
              f"(hotspot {(stable.kind == 'hotspot').sum()} / "
              f"damaging {(stable.kind == 'damaging').sum()})")
        print(agg.head(10)[["gene", "kind", "selection_freq", "mean_rank", "rank_std"]]
              .to_string(index=False))

    valid = {k: v for k, v in aggs.items() if not v.empty}
    if not valid:
        raise SystemExit("집계할 selection 결과가 없습니다.")

    print("\n[표현형 공통 후보] — README §16 표 형태")
    cross = cross_phenotype_table(valid, size=20)
    if not cross.empty:
        cols = ["feature"] + [c for c in cross.columns if c.endswith("_freq")] + ["n_phenotypes"]
        print(cross[cols].round(2).to_string(index=False))
        cross.to_csv(TABLES / f"day11_cross_phenotype_{args.model}.csv", index=False)

    path = plot_stability(aggs, args.model, top_n=args.top_n)
    print(f"\n저장: {path.name}, day11_*.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
