"""Day 12 — 5/10/20/50/전체 패널 성능 비교 (README §17-18).

Figure 5 (패널 크기-성능 곡선) 를 만든다. 이 그림이 최소 패널 결과의
가장 중요한 시각화다 (README §21).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import pandas as pd

from src.config import REPO_ROOT, load_config
from src.data.merge import load_cohort
from src.models.zoo import get_model
from src.panel.curve import jaccard_across_folds, panel_stability, run_panel_curve
from src.viz.style import PHENOTYPE_COLORS, save, use_style

TABLES = REPO_ROOT / "results" / "tables"
TARGETS = ("wgd", "cin", "loh")
TARGET_LABEL = {"wgd": "WGD", "cin": "CIN", "loh": "LOH"}


def plot_curve(metrics: pd.DataFrame, sizes: list[int]) -> Path:
    use_style()
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.4))
    order = [str(s) for s in sizes] + ["all"]

    for ax, metric, title in ((axes[0], "roc_auc", "ROC-AUC"), (axes[1], "pr_auc", "PR-AUC")):
        for target in TARGETS:
            sub = metrics[metrics.target == target]
            if sub.empty:
                continue
            g = sub.groupby("panel_size")[metric]
            mean = g.mean().reindex(order)
            std = g.std().reindex(order)
            ax.errorbar(range(len(order)), mean, yerr=std, marker="o", capsize=3,
                        label=TARGET_LABEL[target], color=PHENOTYPE_COLORS[target])

            # 전체 대비 성능 유지율을 마지막 점 옆에 표시
            full = mean.get("all")
            if pd.notna(full):
                ax.axhline(full, color=PHENOTYPE_COLORS[target], ls=":", lw=0.8, alpha=0.5)

        ax.set_xticks(range(len(order)))
        ax.set_xticklabels([f"{o}개" if o != "all" else "전체" for o in order])
        ax.set_xlabel("패널 크기")
        ax.set_title(title)
        ax.legend(fontsize=9)

    fig.suptitle("Figure 5. 패널 크기별 예측 성능 (점선은 전체 feature 성능)",
                 y=1.02, fontsize=12)
    fig.tight_layout()
    return save(fig, "fig5_panel_curve.png")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="elastic_net")
    p.add_argument("--n-jobs", type=int, default=-1)
    args = p.parse_args()

    cfg = load_config("experiment")["panel"]
    sizes = cfg["sizes"]
    spec = get_model(args.model)
    cohort = load_cohort()

    print(f"[{spec.name}] 패널 크기 {sizes} + 전체 | {cohort.summary()}\n")

    all_metrics, all_picks = [], []
    for target in TARGETS:
        print(f"--- {TARGET_LABEL[target]} ---")
        metrics, picks = run_panel_curve(
            X=cohort.X, y_raw=cohort.y[target], groups=cohort.groups,
            spec=spec, target=target, sizes=sizes, n_jobs=args.n_jobs,
        )
        all_metrics.append(metrics)
        all_picks.append(picks)

        mean = metrics.groupby("panel_size").roc_auc.mean()
        full = mean.get("all")
        print(f"  전체 {full:.3f} 대비 유지율: " + " | ".join(
            f"{k}개 {mean.get(k, float('nan')) / full:.1%}" for k in sizes))
        print()

    metrics = pd.concat(all_metrics, ignore_index=True)
    metrics["panel_size"] = metrics["panel_size"].astype(str)
    picks = pd.concat(all_picks, ignore_index=True)

    print("[패널 크기별 ROC-AUC]")
    pivot = metrics.pivot_table(index="target", columns="panel_size",
                                values="roc_auc", aggfunc="mean")
    pivot = pivot.reindex(columns=[str(s) for s in sizes] + ["all"])
    print(pivot.round(3).to_string())

    print("\n[패널 안정성] fold 간 Jaccard 유사도 (1 에 가까울수록 안정)")
    rows = []
    for target in TARGETS:
        sub = picks[picks.target == target]
        for k in sizes:
            j = jaccard_across_folds(sub, k)
            rows.append({"target": target, "panel_size": k, "jaccard": j})
    stab = pd.DataFrame(rows)
    print(stab.pivot(index="target", columns="panel_size", values="jaccard").round(3).to_string())

    print("\n[전 fold 공통 선택 유전자 — 20개 패널 기준]")
    for target in TARGETS:
        st = panel_stability(picks[picks.target == target], 20)
        common = st[st.freq == 1.0]
        genes = ", ".join(f.split(" (")[0] for f in common.feature.head(12))
        print(f"  {TARGET_LABEL[target]}: {len(common)}개 — {genes}")

    metrics.to_csv(TABLES / "day12_panel_metrics.csv", index=False)
    picks.to_csv(TABLES / "day12_panel_picks.csv", index=False)
    stab.to_csv(TABLES / "day12_panel_stability.csv", index=False)
    path = plot_curve(metrics, sizes)
    print(f"\n저장: {path.name}, day12_*.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
