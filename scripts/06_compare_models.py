"""Day 10 — 전체 모델 성능 비교.

results/tables/cv_random_*.csv 를 모아 Figure 3 과 비교표를 만든다.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.config import REPO_ROOT
from src.evaluation.metrics import METRIC_COLUMNS
from src.viz.style import PHENOTYPE_COLORS, save, use_style

TABLES = REPO_ROOT / "results" / "tables"
MODEL_ORDER = ["logistic", "elastic_net", "random_forest", "xgboost", "multitask_ann"]
MODEL_LABEL = {
    "logistic": "Logistic", "elastic_net": "Elastic Net",
    "random_forest": "Random Forest", "xgboost": "XGBoost",
    "multitask_ann": "Multi-task ANN",
}
TARGET_LABEL = {"wgd": "WGD", "cin": "CIN", "loh": "LOH"}


def load_cv(scheme: str = "random") -> pd.DataFrame:
    files = sorted(TABLES.glob(f"cv_{scheme}_*.csv"))
    if not files:
        raise SystemExit(f"{scheme} 결과가 없습니다. 먼저 05_run_cv.py 를 실행하세요.")
    return pd.concat([pd.read_csv(f) for f in files], ignore_index=True)


def plot_comparison(df: pd.DataFrame) -> Path:
    use_style()
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.2), sharey=False)

    for ax, metric, title in ((axes[0], "roc_auc", "ROC-AUC"), (axes[1], "pr_auc", "PR-AUC")):
        models = [m for m in MODEL_ORDER if m in set(df.model)]
        width = 0.26
        x = np.arange(len(models))

        for i, target in enumerate(("wgd", "cin", "loh")):
            sub = df[df.target == target]
            means = [sub[sub.model == m][metric].mean() for m in models]
            errs = [sub[sub.model == m][metric].std() for m in models]
            ax.bar(x + (i - 1) * width, means, width, yerr=errs, capsize=3,
                   label=TARGET_LABEL[target], color=PHENOTYPE_COLORS[target])

        ax.axhline(0.5, color="k", ls=":", lw=1, label="무작위 수준" if metric == "roc_auc" else None)
        ax.set_xticks(x)
        ax.set_xticklabels([MODEL_LABEL[m] for m in models], rotation=15, ha="right")
        ax.set_title(title)
        ax.set_ylim(0.4, 1.0)
        ax.legend(fontsize=8, ncol=2)

    fig.suptitle("Figure 3. 모델별 예측 성능 (random 5x5 nested CV, 오차막대는 fold 표준편차)",
                 y=1.02, fontsize=12)
    fig.tight_layout()
    return save(fig, "fig3_model_comparison.png")


def main() -> int:
    df = load_cv("random")

    print("[모델 x 표현형 ROC-AUC]")
    pivot = df.pivot_table(index="model", columns="target", values="roc_auc", aggfunc="mean")
    pivot = pivot.reindex([m for m in MODEL_ORDER if m in pivot.index])
    print(pivot.round(3).to_string())

    print("\n[전체 지표 평균]")
    summary = (
        df.groupby(["target", "model"])[METRIC_COLUMNS].mean()
        .round(3).reset_index()
        .sort_values(["target", "roc_auc"], ascending=[True, False])
    )
    print(summary.to_string(index=False))

    print("\n[표현형별 최고 모델]")
    for target in ("wgd", "cin", "loh"):
        sub = summary[summary.target == target]
        best = sub.iloc[0]
        print(f"  {TARGET_LABEL[target]}: {MODEL_LABEL[best.model]} "
              f"ROC-AUC {best.roc_auc:.3f} | PR-AUC {best.pr_auc:.3f} | "
              f"BA {best.balanced_accuracy:.3f} | Brier {best.brier:.3f}")

    summary.to_csv(TABLES / "day10_model_comparison.csv", index=False)
    path = plot_comparison(df)
    print(f"\n저장: {path.name}, day10_model_comparison.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
