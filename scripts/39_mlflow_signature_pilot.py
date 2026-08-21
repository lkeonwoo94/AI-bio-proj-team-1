"""MLflow 추적 파일럿 — signature(96-class) 표현 (후속 실험 편입).

`scripts/37_mlflow_pilot.py` 는 유전자 단위(day10)만 담았다. 이 스크립트는
같은 패턴을 mutation signature 표현(08-19 Future Work, additional_results.md
§4)에도 적용해, MLflow 로 "표현 방식"까지 비교할 수 있게 한다 —
`representation` 태그가 `gene` 대신 `signature` 로 붙는다.

기존 `scripts/24_signature_representation.py` 의 `run_signature_cv()`
를 그대로 재사용한다(파이프라인 로직은 안 건드림, importlib 로 로드 —
`scripts/27_signature_seed_robustness.py` 와 같은 패턴).
"""

from __future__ import annotations

import argparse
import ast
import importlib.util
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import mlflow
import mlflow.sklearn
import pandas as pd

from src.config import REPO_ROOT
from src.data.merge import load_cohort
from src.labels.binarize import LabelBinarizer
from src.tracking.mlflow_utils import experiment_name, init_tracking, log_artifact_df

METRIC_COLUMNS = ["roc_auc", "pr_auc", "balanced_accuracy", "sensitivity", "specificity", "f1", "brier"]
TARGET_LABEL = {"wgd": "WGD", "cin": "CIN", "loh": "LOH"}
MODEL_LABEL = {"logistic": "Logistic", "random_forest": "Random Forest"}
SIG_PATH = REPO_ROOT / "data" / "depmap" / "sbs96_signature_matrix.parquet"


def _load_script24():
    spec = importlib.util.spec_from_file_location(
        "signature_representation", Path(__file__).parent / "24_signature_representation.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--targets", nargs="+", default=["wgd"], choices=["wgd", "cin", "loh"])
    p.add_argument("--model", default="random_forest", choices=["logistic", "random_forest"])
    args = p.parse_args()

    mod = _load_script24()
    init_tracking()
    cohort = load_cohort()
    sig = pd.read_parquet(SIG_PATH).reindex(cohort.X.index)
    model_label = MODEL_LABEL[args.model]
    print(f"[MLflow 파일럿 — signature] {args.model} / {args.targets} | "
          f"signature {sig.shape[1]}개, 세포주 {sig.shape[0]}개\n")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        for target in args.targets:
            mlflow.set_experiment(experiment_name(target, "signature"))
            print(f"--- {TARGET_LABEL[target]} ---")

            with mlflow.start_run(run_name=f"{args.model}_{target}_signature") as parent_run:
                mlflow.log_param("model", args.model)
                mlflow.log_param("target", target)
                mlflow.log_param("scheme", "random")
                mlflow.log_param("n_features", sig.shape[1])
                mlflow.set_tags({
                    "representation": "signature",
                    "target_label": TARGET_LABEL[target],
                    "model_label": model_label,
                    "mlflow.note.content": (
                        f"{model_label} / {TARGET_LABEL[target]} — mutation signature"
                        "(96-class), random 5-fold. additional_results.md §4 재현."
                    ),
                })

                df = mod.run_signature_cv(sig, cohort.y[target], cohort.groups, args.model, target)

                for _, row in df.iterrows():
                    with mlflow.start_run(run_name=f"{args.model}_{target}_signature_fold{int(row.fold)}",
                                          nested=True):
                        mlflow.log_param("fold", int(row.fold))
                        mlflow.set_tags({"representation": "signature", "target_label": TARGET_LABEL[target]})
                        if "best_params" in row.index:
                            mlflow.log_param("best_params", str(row["best_params"]))
                        for col in METRIC_COLUMNS:
                            if col in row.index:
                                mlflow.log_metric(col, float(row[col]))
                    print(f"  fold {int(row.fold)}: ROC-AUC {row.roc_auc:.3f} (MLflow child run 기록 완료)")

                summary = df[METRIC_COLUMNS].mean(numeric_only=True)
                for metric, value in summary.items():
                    mlflow.log_metric(f"mean_{metric}", float(value))

                log_artifact_df(df, f"signature_cv_{args.model}_{target}.csv", tmp_dir)

                # --- 참고용 최종 모델 (전체 코호트 재학습) ---
                best_row = df.loc[df.roc_auc.idxmax()]
                pipe, _grid = mod.build_pipeline(args.model)
                if "best_params" in best_row.index:
                    pipe.set_params(**ast.literal_eval(best_row.best_params))
                y_full = LabelBinarizer(target).fit_transform(cohort.y[target])
                pipe.fit(sig, y_full)
                mlflow.sklearn.log_model(
                    pipe, name="model", serialization_format="cloudpickle",
                    registered_model_name=f"{args.model}_{target}_signature",
                )
                mlflow.log_param("final_model_source_fold", int(best_row.fold))

                print(f"  parent run 요약: mean ROC-AUC {summary.roc_auc:.3f} "
                      f"(run_id={parent_run.info.run_id})\n")

    print("완료.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
