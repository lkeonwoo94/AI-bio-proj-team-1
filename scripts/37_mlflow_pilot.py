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
import ast
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import mlflow
import mlflow.sklearn

from src.cv.nested import run_nested_cv
from src.data.merge import load_cohort
from src.labels.binarize import LabelBinarizer
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

                # --- Model Registry 용 모델 로깅 ---
                # nested CV 는 fold 마다 다른 fitted 모델을 만들어서 "그 CV 실험을
                # 대표하는 단일 모델"이 원래 없다. 여기서는 outer fold 중 ROC-AUC
                # 가 가장 높았던 fold 의 하이퍼파라미터를 그대로 가져와, **전체
                # 코호트**로 다시 학습한 모델 하나를 "참고용 최종 모델"로 저장한다
                # — 이 모델은 outer test 로 평가된 적이 없으므로 위의 CV 지표를
                # 이 모델 자체의 성능으로 오독하면 안 된다(§13 원칙과 별개로,
                # Model Registry 데모 목적의 부가 산출물일 뿐).
                best_row = result.metrics.loc[result.metrics.roc_auc.idxmax()]
                best_params = ast.literal_eval(best_row.best_params)  # 이미 "clf__..." 형식
                # 주의: spec.build() 는 ModelSpec 생성 시 클로저에 캡쳐된 "같은"
                # Pipeline 객체를 매번 반환한다(src/models/zoo.py, `lambda: pipe`).
                # CatBoost 는 sklearn 의 clone() 프로토콜을 완전히 따르지 않아,
                # nested CV 동안 그 공유 객체 자체가 이미 fit 된 채로 남는다 —
                # 그 상태에서 set_params() 를 부르면 "You can't change params of
                # fitted model" 에러가 난다. get_model() 을 다시 불러 완전히 새
                # Pipeline 인스턴스를 받는다.
                final_pipe = get_model(args.model).build()
                final_pipe.set_params(**best_params)
                y_full = LabelBinarizer(target).fit_transform(cohort.y[target])
                final_pipe.fit(cohort.X, y_full)

                mlflow.sklearn.log_model(
                    final_pipe, name="model", serialization_format="cloudpickle",
                    registered_model_name=f"{spec.name}_{target}",
                )
                mlflow.log_param("final_model_source_fold", int(best_row.fold))

                print(f"  parent run 요약: mean ROC-AUC {summary.roc_auc:.3f} "
                      f"(run_id={parent_run.info.run_id})\n")

    print("완료. 확인: .venv/bin/mlflow ui --backend-store-uri sqlite:///mlflow.db")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
