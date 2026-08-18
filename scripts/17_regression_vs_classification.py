"""Day 15b — CIN/LoHFraction 을 회귀로 직접 예측 (§26⑤ 후속, "보완 5번").

지금까지 CIN/LoHFraction 은 중앙값으로 잘라 이진 분류로만 예측했다.
"중앙값 부근의 세포주는 실제 값이 비슷해도 다른 그룹으로 분류될 수
있다"는 우려(README §10 의 이진화 비용)를 직접 검증하기 위해, 같은
mutation feature 로 연속값을 회귀 예측하고 분류 ROC-AUC 와 비교한다.

두 지표는 척도가 다르므로 직접 등치하지 않는다. 대신 Spearman rho(순위
상관)를 ROC-AUC 에 대응하는 값으로 놓고 방향을 비교한다 — 둘 다 "값
자체" 가 아니라 "상대적 순서를 얼마나 잘 맞히는가" 를 재는 지표라는
점에서 가장 가까운 대응이다.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src.config import REPO_ROOT
from src.cv.nested_regression import run_nested_cv_regression
from src.data.merge import load_cohort
from src.evaluation.metrics_regression import REGRESSION_METRIC_COLUMNS
from src.models.regression import get_regression_model

TABLES = REPO_ROOT / "results" / "tables"
TARGETS = ("cin", "loh")   # WGD 는 원래 binary 라 회귀 대상이 아니다
TARGET_LABEL = {"cin": "CIN", "loh": "LoHFraction"}


def classification_auc(targets: tuple, clf_models: list) -> pd.DataFrame:
    """비교 기준이 되는 기존 분류 ROC-AUC (random 5x5, day10 산출물)."""
    df = pd.read_csv(TABLES / "day10_model_comparison.csv")
    rows = []
    for target in targets:
        for clf_model in clf_models:
            sub = df[(df.target == target) & (df.model == clf_model)]
            if not sub.empty:
                rows.append({"target": target, "clf_model": clf_model,
                            "roc_auc": sub.roc_auc.iloc[0]})
    return pd.DataFrame(rows)


def main() -> int:
    cohort = load_cohort()
    print(f"[회귀 vs 분류 비교] {cohort.summary()}\n")

    # 분류 쪽과 짝을 맞춘 모델 (같은 계열끼리 비교)
    reg_models = ["elastic_net_reg", "random_forest_reg"]
    clf_pair = {"elastic_net_reg": "elastic_net", "random_forest_reg": "random_forest"}

    all_metrics = []
    for reg_name in reg_models:
        spec = get_regression_model(reg_name)
        for target in TARGETS:
            print(f"--- {reg_name} / {TARGET_LABEL[target]} ---")
            result = run_nested_cv_regression(cohort.X, cohort.y[target], spec, target)
            result.metrics.to_csv(TABLES / f"cv_regression_{reg_name}_{target}.csv", index=False)
            all_metrics.append(result.metrics)

            m = result.metrics[REGRESSION_METRIC_COLUMNS].mean()
            print(f"  평균 R2 {m.r2:.3f} | Spearman rho {m.spearman_rho:.3f} | "
                  f"RMSE {m.rmse:.3f}\n")

    combined = pd.concat(all_metrics, ignore_index=True)
    combined.to_csv(TABLES / "day15b_regression_summary.csv", index=False)

    print("[요약] 회귀 성능")
    summary = combined.groupby(["target", "model"])[REGRESSION_METRIC_COLUMNS].mean().round(3)
    print(summary.to_string())

    print("\n[분류 ROC-AUC 대비 회귀 Spearman rho]")
    clf_auc = classification_auc(TARGETS, list(clf_pair.values()))
    print(clf_auc.round(3).to_string(index=False))

    cmp_rows = []
    for reg_name, clf_name in clf_pair.items():
        for target in TARGETS:
            reg_rho = combined[(combined.model == reg_name) & (combined.target == target)].spearman_rho.mean()
            clf_row = clf_auc[(clf_auc.target == target) & (clf_auc.clf_model == clf_name)]
            clf_val = clf_row.roc_auc.iloc[0] if not clf_row.empty else float("nan")
            cmp_rows.append({
                "target": target, "model_family": clf_name,
                "clf_roc_auc": clf_val, "reg_spearman_rho": reg_rho,
                "차이": reg_rho - (clf_val - 0.5) * 2,  # AUC 를 rho 스케일(-1~1)로 근사 환산
            })
    cmp_df = pd.DataFrame(cmp_rows)
    print("\n[비교] AUC 를 2*(AUC-0.5) 로 rho 스케일에 근사 환산한 값과 비교")
    print(cmp_df.round(3).to_string(index=False))
    cmp_df.to_csv(TABLES / "day15b_regression_vs_classification.csv", index=False)

    print("\n해석: 회귀 rho 가 환산값보다 뚜렷이 높으면 이진화가 정보를")
    print("      버렸다는 뜻이고, 비슷하거나 낮으면 이진화 손실보다는")
    print("      원래 신호 자체가 그 정도라는 뜻이다.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
