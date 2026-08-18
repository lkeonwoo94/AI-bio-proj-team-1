"""Day 13 — lineage 기반 검증 (README §15).

random CV 에서는 성능이 높지만 lineage CV 에서 크게 떨어진다면,
모델이 WGD/CIN/LOH 가 아니라 '암종'을 학습했을 가능성이 있다.

Figure 6 (random vs lineage CV 비교) 를 만든다.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.config import REPO_ROOT
from src.cv.nested import run_nested_cv
from src.cv.splitters import eligible_lineages
from src.data.merge import load_cohort
from src.models.zoo import get_model
from src.viz.style import PHENOTYPE_COLORS, save, use_style

TABLES = REPO_ROOT / "results" / "tables"
TARGETS = ("wgd", "cin", "loh")
TARGET_LABEL = {"wgd": "WGD", "cin": "CIN", "loh": "LOH"}


def plot_lineage_comparison(df: pd.DataFrame, lolo: pd.DataFrame, model: str) -> Path:
    use_style()
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.6),
                             gridspec_kw={"width_ratios": [1, 1.6]})

    # 왼쪽: random vs group CV
    schemes = ["random", "group"]
    width = 0.26
    x = np.arange(len(schemes))
    for i, target in enumerate(TARGETS):
        means = [df[(df.target == target) & (df.scheme == s)].roc_auc.mean() for s in schemes]
        errs = [df[(df.target == target) & (df.scheme == s)].roc_auc.std() for s in schemes]
        axes[0].bar(x + (i - 1) * width, means, width, yerr=errs, capsize=3,
                    label=TARGET_LABEL[target], color=PHENOTYPE_COLORS[target])
    axes[0].axhline(0.5, color="k", ls=":", lw=1)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(["Random CV", "Lineage GroupKFold"])
    axes[0].set_ylabel("ROC-AUC")
    axes[0].set_ylim(0.4, 0.9)
    axes[0].set_title("split 방식별 성능")
    axes[0].legend(fontsize=8)

    # 오른쪽: lineage 별 LOLO 성능
    if not lolo.empty:
        order = (lolo[lolo.target == "wgd"]
                 .sort_values("roc_auc", ascending=False).held_out_lineage.tolist())
        for target in TARGETS:
            sub = lolo[lolo.target == target].set_index("held_out_lineage").reindex(order)
            axes[1].plot(range(len(order)), sub.roc_auc, marker="o", ms=4,
                         label=TARGET_LABEL[target], color=PHENOTYPE_COLORS[target])
        axes[1].axhline(0.5, color="k", ls=":", lw=1, label="무작위 수준")
        axes[1].set_xticks(range(len(order)))
        axes[1].set_xticklabels(order, rotation=60, ha="right", fontsize=7)
        axes[1].set_title("Leave-One-Lineage-Out — 제외한 암종별 성능")
        axes[1].legend(fontsize=8)

    fig.suptitle("Figure 6. Lineage 기반 검증", y=1.03, fontsize=12)
    fig.tight_layout()
    return save(fig, f"fig6_lineage_validation_{model}.png")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="elastic_net")
    p.add_argument("--n-jobs", type=int, default=-1)
    p.add_argument("--min-lineage-size", type=int, default=20)
    args = p.parse_args()

    spec = get_model(args.model)
    cohort = load_cohort()
    print(f"[{spec.name}] {cohort.summary()}\n")

    # --- lineage GroupKFold ---
    group_rows = []
    for target in TARGETS:
        print(f"--- {TARGET_LABEL[target]} / lineage GroupKFold ---")
        res = run_nested_cv(cohort.X, cohort.y[target], cohort.groups, spec, target,
                            scheme="group", n_jobs=args.n_jobs)
        res.metrics.to_csv(TABLES / f"cv_group_{spec.name}_{target}.csv", index=False)
        group_rows.append(res.metrics)
        print(f"  평균 ROC-AUC {res.metrics.roc_auc.mean():.3f}\n")

    # --- Leave-One-Lineage-Out (작은 lineage 제외) ---
    keep = eligible_lineages(cohort.groups, min_size=args.min_lineage_size)
    mask = cohort.groups.isin(keep)
    print(f"[LOLO] {len(keep)}종 대상 (세포주 {int(mask.sum()):,}개, "
          f"{args.min_lineage_size}개 미만 lineage 제외)\n")

    lolo_rows = []
    for target in TARGETS:
        print(f"--- {TARGET_LABEL[target]} / Leave-One-Lineage-Out ---")
        res = run_nested_cv(cohort.X[mask], cohort.y[target][mask], cohort.groups[mask],
                            spec, target, scheme="lolo", n_jobs=args.n_jobs, verbose=False)
        res.metrics.to_csv(TABLES / f"cv_lolo_{spec.name}_{target}.csv", index=False)
        lolo_rows.append(res.metrics)
        m = res.metrics
        print(f"  평균 ROC-AUC {m.roc_auc.mean():.3f} "
              f"(최저 {m.roc_auc.min():.3f} / 최고 {m.roc_auc.max():.3f})")
        worst = m.nsmallest(3, "roc_auc")[["held_out_lineage", "roc_auc", "n_test"]]
        print("  성능이 낮은 암종:")
        print(worst.to_string(index=False))
        print()

    group = pd.concat(group_rows, ignore_index=True)
    lolo = pd.concat(lolo_rows, ignore_index=True)

    # random CV 결과와 비교
    random_files = list(TABLES.glob(f"cv_random_{spec.name}_*.csv"))
    random = pd.concat([pd.read_csv(f) for f in random_files], ignore_index=True)
    combined = pd.concat([random, group], ignore_index=True)

    print("[Random CV vs Lineage GroupKFold] ROC-AUC")
    cmp = combined.pivot_table(index="target", columns="scheme", values="roc_auc", aggfunc="mean")
    cmp["차이"] = cmp["group"] - cmp["random"]
    print(cmp.round(3).to_string())

    print("\n해석: 차이가 크게 음수면 해당 표현형의 mutation 신호는")
    print("      암종 의존적일 가능성이 있다 (README §25).")

    cmp.to_csv(TABLES / f"day13_lineage_comparison_{spec.name}.csv")
    lolo.to_csv(TABLES / f"day13_lolo_by_lineage_{spec.name}.csv", index=False)
    path = plot_lineage_comparison(combined, lolo, spec.name)
    print(f"\n저장: {path.name}, day13_*.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
