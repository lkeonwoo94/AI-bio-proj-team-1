"""CIN 회귀 기반 최소 패널 (한계 6번 후속, "남은 과제").

Elastic Net 으로 CIN 을 분류할 때만 이진화 손실이 있었다
(`docs/research/2026-08-19/additional_results.md` §2). 그 손실이 §26③④
의 CIN feature selection·최소 패널 결과에도 반영되는지 직접 확인한다 —
분류 대신 회귀(연속값)로 feature selection 을 다시 하고, 분류 기반
CIN 패널(Day 11/12, `day12_panel_picks_{model}.csv`)과 겹치는 유전자가
얼마나 되는지 비교한다.

LoHFraction 은 다루지 않는다 — 회귀 검증에서 이진화 손실이 거의 없었던
표현형이라(§26⑤ 회귀 검증) 패널을 다시 뽑을 동기가 약하다.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src.config import REPO_ROOT
from src.cv.nested_regression import run_nested_cv_regression
from src.data.merge import load_cohort
from src.models.regression import get_regression_model
from src.panel.curve import jaccard_across_folds, panel_stability
from src.panel.regression_curve import run_panel_curve_regression
from src.selection.aggregate import aggregate_selection

TABLES = REPO_ROOT / "results" / "tables"
TARGET = "cin"
MODELS = ("elastic_net_reg", "random_forest_reg")
CLF_MODEL_OF = {"elastic_net_reg": "elastic_net", "random_forest_reg": "random_forest"}
SIZES = [5, 10, 20, 50]


def main() -> int:
    cohort = load_cohort()
    y = cohort.y[TARGET]
    print(f"[CIN 회귀 기반 패널] {cohort.summary()}\n")

    all_agg, all_metrics, all_picks, all_stab = {}, [], [], []

    for model_name in MODELS:
        spec = get_regression_model(model_name)

        # --- Day 11 analog: fold 반복 selection 집계 ---
        print(f"--- {model_name} / 반복 selection ---")
        result = run_nested_cv_regression(cohort.X, y, spec, TARGET)
        agg = aggregate_selection(result.importances, top_k=50)
        agg.to_csv(TABLES / f"day28_cin_regression_selection_{model_name}.csv", index=False)
        all_agg[model_name] = agg
        top10 = ", ".join(agg.head(10).feature.str.split(" \\(").str[0])
        print(f"  전 fold 반복 상위 10: {top10}\n")

        # --- Day 12 analog: 패널 크기별 성능 곡선 ---
        print(f"--- {model_name} / 패널 곡선 ---")
        metrics, picks = run_panel_curve_regression(
            X=cohort.X, y=y, spec=spec, target=TARGET, sizes=SIZES,
        )
        metrics["model"] = model_name
        picks["model"] = model_name
        all_metrics.append(metrics)
        all_picks.append(picks)

        mean_rho = metrics.groupby("panel_size").spearman_rho.mean()
        full = mean_rho.get("all")
        print(f"  전체 rho {full:.3f} 대비 유지율: " + " | ".join(
            f"{k}개 {mean_rho.get(k, float('nan')) / full:.1%}" for k in SIZES))

        for k in SIZES:
            j = jaccard_across_folds(picks, k)
            all_stab.append({"model": model_name, "panel_size": k, "jaccard": j})
        print()

    metrics = pd.concat(all_metrics, ignore_index=True)
    metrics["panel_size"] = metrics["panel_size"].astype(str)
    picks = pd.concat(all_picks, ignore_index=True)
    stab = pd.DataFrame(all_stab)

    metrics.to_csv(TABLES / "day28_cin_regression_panel_metrics.csv", index=False)
    picks.to_csv(TABLES / "day28_cin_regression_panel_picks.csv", index=False)
    stab.to_csv(TABLES / "day28_cin_regression_panel_stability.csv", index=False)

    print("[회귀 기반 CIN 패널 안정성] fold 간 Jaccard")
    print(stab.pivot(index="model", columns="panel_size", values="jaccard").round(3).to_string())

    # --- 분류 기반 CIN 패널과 10개 패널 겹침 비교 ---
    print("\n[분류 vs 회귀 — 10개 패널 유전자 겹침]")
    for model_name in MODELS:
        clf_model = CLF_MODEL_OF[model_name]
        clf_path = TABLES / f"day12_panel_picks_{clf_model}.csv"
        if not clf_path.exists():
            print(f"  {clf_model}: day12 패널 파일 없음 — 건너뜀")
            continue
        clf_picks = pd.read_csv(clf_path)
        clf_genes = set(
            clf_picks[(clf_picks.target == TARGET) & (clf_picks.panel_size == 10)]
            .feature.str.split(" \\(").str[0]
        )
        reg_picks = picks[(picks.model == model_name) & (picks.panel_size == 10)]
        reg_genes = set(reg_picks.feature.str.split(" \\(").str[0])
        overlap = clf_genes & reg_genes
        union = clf_genes | reg_genes
        jac = len(overlap) / len(union) if union else float("nan")
        print(f"  {clf_model}(분류) vs {model_name}(회귀): "
              f"Jaccard {jac:.3f} | 공통 {sorted(overlap)}")

    print("\n저장: day28_cin_regression_selection_{model}.csv, "
          "day28_cin_regression_panel_{metrics,picks,stability}.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
