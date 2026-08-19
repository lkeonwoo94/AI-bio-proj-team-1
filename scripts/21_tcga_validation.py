"""TCGA 독립 코호트 검증 (한계 6번 후속, final_conclusion.md "Future Work 3").

DepMap 세포주로 학습한 WGD 예측이 실제 환자 종양(TCGA)에도 통하는지
확인한다. 세 단계로 진행한다.

  1. damaging-only 기준선: DepMap 내부에서 hotspot 을 뺀 damaging 만으로
     nested CV 성능을 잰다 — TCGA 와 같은 feature 종류로 맞춘 비교 기준.
  2. 외부 검증: DepMap 전체(1,631개)로 최종 모델을 학습해 TCGA(10,261개)
     에 그대로 적용한다. 이게 진짜 "독립 코호트 검증"이다.
  3. 두 성능을 나란히 놓고 해석한다.

hotspot 채널은 TCGA 쪽에 대응 데이터가 없어(큐레이션 hotspot DB 필요)
포함하지 않는다 — 즉 1번이 "같은 조건에서의 DepMap 성능"이다.
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, cross_val_predict

from src.config import REPO_ROOT
from src.cv.nested import run_nested_cv
from src.data.merge import load_cohort
from src.data.tcga import load_tcga_cohort
from src.evaluation.metrics import choose_threshold, evaluate
from src.features.filter import RareMutationFilter
from src.models.zoo import ModelSpec

TABLES = REPO_ROOT / "results" / "tables"


def damaging_only_spec() -> ModelSpec:
    """Random Forest, damaging feature 만(§26② 최고 모델과 동일 계열)."""
    from sklearn.pipeline import Pipeline

    def build():
        return Pipeline([
            ("filter", RareMutationFilter(min_count=10)),
            ("clf", RandomForestClassifier(n_estimators=500,
                                           class_weight="balanced_subsample",
                                           n_jobs=-1, random_state=42)),
        ])
    return ModelSpec("random_forest", build,
                     {"clf__max_depth": [None, 8], "clf__min_samples_leaf": [1, 5]},
                     importance="tree")


def internal_baseline(cohort) -> float:
    """1단계: DepMap 내부, damaging feature 만으로 random 5-fold 성능."""
    damaging_cols = [c for c in cohort.X.columns if c.endswith("_damaging")]
    X_dmg = cohort.X[damaging_cols]

    spec = damaging_only_spec()
    result = run_nested_cv(X_dmg, cohort.y["wgd"], cohort.groups, spec, "wgd",
                           scheme="random", n_jobs=-1)
    result.metrics.to_csv(TABLES / "cv_random_random_forest_damaging_only_wgd.csv", index=False)
    return result.metrics.roc_auc.mean()


def external_validation(cohort, X_tcga: pd.DataFrame, y_tcga: pd.Series) -> dict:
    """2단계: DepMap 전체로 최종 모델을 학습해 TCGA 에 그대로 적용."""
    damaging_cols = [c for c in cohort.X.columns if c.endswith("_damaging")]
    X_dmg = cohort.X[damaging_cols].copy()
    X_dmg.columns = [c.split(" (")[0] for c in X_dmg.columns]  # TCGA 와 이름 맞추기
    # 같은 유전자가 여러 damaging 컬럼에 흩어질 일은 없지만(§9.1 병합이
    # ModelID 단위 유일성 보장) 혹시 몰라 합쳐준다.
    X_dmg = X_dmg.T.groupby(level=0).max().T

    common_genes = sorted(set(X_dmg.columns) & set(X_tcga.columns))
    print(f"공통 유전자: {len(common_genes)}개 (DepMap {X_dmg.shape[1]}, TCGA {X_tcga.shape[1]})")

    X_dmg = X_dmg[common_genes]
    X_tcga = X_tcga[common_genes]

    # DepMap 전체로 최종 모델을 학습한다 — 더는 outer test 가 없다,
    # TCGA 자체가 outer test 이기 때문이다.
    pipe = damaging_only_spec().build()
    grid = {"clf__max_depth": [None, 8], "clf__min_samples_leaf": [1, 5]}

    from src.cv.splitters import inner_cv
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ConvergenceWarning)
        search = GridSearchCV(pipe, grid, scoring="roc_auc", cv=inner_cv(),
                              n_jobs=-1, refit=True)
        search.fit(X_dmg.to_numpy(), cohort.y["wgd"].to_numpy())
    best = search.best_estimator_
    print(f"DepMap 전체 학습 완료. best_params={search.best_params_}, "
          f"필터 통과 feature {best.named_steps['filter'].n_features_out_}")

    # threshold 도 DepMap 안에서만 정한다 — TCGA 라벨은 전혀 보지 않는다.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ConvergenceWarning)
        oof = cross_val_predict(search.best_estimator_, X_dmg.to_numpy(),
                                cohort.y["wgd"].to_numpy(), cv=inner_cv(),
                                method="predict_proba", n_jobs=-1)[:, 1]
    threshold = choose_threshold(cohort.y["wgd"].to_numpy(), oof)

    prob_tcga = best.predict_proba(X_tcga.to_numpy())[:, 1]
    row = evaluate(y_tcga.to_numpy(), prob_tcga, threshold=threshold)
    row["n_common_genes"] = len(common_genes)
    row["best_params"] = str(search.best_params_)
    return row


def main() -> int:
    cohort = load_cohort()
    print(f"[DepMap] {cohort.summary()}")

    X_tcga, y_tcga = load_tcga_cohort()
    print(f"[TCGA] 샘플 {len(X_tcga):,} | 유전자 {X_tcga.shape[1]:,} | "
          f"WGD+ {y_tcga.mean():.1%}\n")

    print("=== 1단계: DepMap 내부 damaging-only 기준선 (random 5-fold) ===")
    baseline_auc = internal_baseline(cohort)
    print(f"기준선 ROC-AUC: {baseline_auc:.3f}\n")

    print("=== 2단계: DepMap 전체 학습 -> TCGA 외부 검증 ===")
    ext_row = external_validation(cohort, X_tcga, y_tcga)
    print(f"\nTCGA 외부 검증 ROC-AUC: {ext_row['roc_auc']:.3f} | "
          f"PR-AUC {ext_row['pr_auc']:.3f} | BA {ext_row['balanced_accuracy']:.3f} | "
          f"n_test {ext_row['n_test']}")

    summary = pd.DataFrame([
        {"stage": "DepMap 내부(damaging-only, random 5-fold)", "roc_auc": baseline_auc,
        "n": len(cohort)},
        {"stage": "TCGA 외부 검증", "roc_auc": ext_row["roc_auc"], "n": ext_row["n_test"]},
    ])
    summary.to_csv(TABLES / "day21_tcga_validation_summary.csv", index=False)
    pd.DataFrame([ext_row]).to_csv(TABLES / "day21_tcga_validation_detail.csv", index=False)

    print("\n=== 3단계: 해석 ===")
    diff = ext_row["roc_auc"] - baseline_auc
    print(f"차이(TCGA - DepMap 내부): {diff:+.3f}")
    print("큰 폭으로 떨어지면 세포주(in vitro) 학습이 실제 종양(in vivo)")
    print("으로는 잘 전이되지 않는다는 뜻 — lineage-dependent 결론(§26⑤)")
    print("과 같은 방향이면 일관된 해석이 된다.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
