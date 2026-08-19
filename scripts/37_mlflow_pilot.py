"""MLflow 추적 파일럿 (`feature/mlflow-tracking-pilot` 브랜치).

Random Forest 로 기존 nested CV(`run_nested_cv`, §13 원칙 동일)를
그대로 돌리되, 결과를 CSV 파일명 컨벤션 대신 MLflow run 으로 기록한다.
기존 `scripts/06_compare_models.py` 등은 전혀 건드리지 않았다 — 이
스크립트는 같은 계산을 MLflow 로 "다시" 기록해보는 병행 실험이다.

기본값은 WGD 하나만 돈다(빠른 평가용). 다른 표현형도 보려면
`--targets wgd cin loh` 로 넘긴다.

확인:
    .venv/bin/python scripts/37_mlflow_pilot.py
    .venv/bin/mlflow ui --backend-store-uri sqlite:///mlflow.db
    (브라우저에서 http://127.0.0.1:5000 접속)
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import mlflow

from src.cv.nested import run_nested_cv
from src.data.merge import load_cohort
from src.models.zoo import get_model
from src.tracking.mlflow_utils import experiment_name, init_tracking, log_artifact_df, log_fold_metrics

METRIC_COLUMNS = ["roc_auc", "pr_auc", "balanced_accuracy", "sensitivity", "specificity", "f1", "brier"]
TARGET_LABEL = {"wgd": "WGD", "cin": "CIN", "loh": "LOH"}
MODEL_LABEL = {
    "logistic": "Logistic", "elastic_net": "Elastic Net", "random_forest": "Random Forest",
    "xgboost": "XGBoost", "catboost": "CatBoost", "multitask_ann": "Multi-task ANN",
}
MODEL_FAMILY = {
    "logistic": "linear", "elastic_net": "linear", "random_forest": "tree",
    "xgboost": "tree", "catboost": "tree", "multitask_ann": "neural",
}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--targets", nargs="+", default=["wgd"], choices=["wgd", "cin", "loh"])
    p.add_argument("--model", default="random_forest")
    args = p.parse_args()

    init_tracking()
    cohort = load_cohort()
    spec = get_model(args.model)
    print(f"[MLflow 파일럿] {spec.name} / {args.targets} | {cohort.summary()}\n")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        for target in args.targets:
            mlflow.set_experiment(experiment_name(target, "gene"))
            print(f"--- {TARGET_LABEL[target]} ---")

            model_label = MODEL_LABEL.get(spec.name, spec.name)
            with mlflow.start_run(run_name=f"{spec.name}_{target}") as parent_run:
                mlflow.log_param("model", spec.name)
                mlflow.log_param("target", target)
                mlflow.log_param("scheme", "random")
                mlflow.log_param("n_cell_lines", len(cohort))
                mlflow.set_tags({
                    "representation": "gene",
                    "target_label": TARGET_LABEL[target],
                    "model_label": model_label,
                    "model_family": MODEL_FAMILY.get(spec.name, "unknown"),
                    "mlflow.note.content": (
                        f"{model_label} / {TARGET_LABEL[target]} — 유전자 단위"
                        "(필터 후 ~2,062개), random 5-fold nested CV. "
                        "day10_model_comparison.csv 재현."
                    ),
                })

                result = run_nested_cv(cohort.X, cohort.y[target], cohort.groups, spec, target)

                for _, row in result.metrics.iterrows():
                    with mlflow.start_run(run_name=f"{spec.name}_{target}_fold{int(row.fold)}", nested=True):
                        mlflow.log_param("fold", int(row.fold))
                        mlflow.set_tags({
                            "representation": "gene",
                            "target_label": TARGET_LABEL[target],
                            "model_label": model_label,
                        })
                        log_fold_metrics(row, METRIC_COLUMNS)
                    print(f"  fold {int(row.fold)}: ROC-AUC {row.roc_auc:.3f} "
                          f"(MLflow child run 기록 완료)")

                # parent run 에는 fold 평균을 요약 지표로 남긴다.
                summary = result.metrics[METRIC_COLUMNS].mean(numeric_only=True)
                for metric, value in summary.items():
                    mlflow.log_metric(f"mean_{metric}", float(value))

                # feature importance 는 CSV artifact 로 — 기존 day07 산출물과 같은 내용.
                log_artifact_df(result.importances, f"importances_{target}.csv", tmp_dir)

                print(f"  parent run 요약: mean ROC-AUC {summary.roc_auc:.3f} "
                      f"(run_id={parent_run.info.run_id})\n")

    print("완료. 확인: .venv/bin/mlflow ui --backend-store-uri sqlite:///mlflow.db")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
