"""Nested CV 실행기 (README §12, §13).

한 outer fold 안에서 벌어지는 일의 순서:

    1. training fold 로만 LabelBinarizer 적합 -> CIN/LOH threshold 결정
    2. 같은 threshold 를 test fold 에 적용
    3. Pipeline(희귀변이 필터 -> 스케일 -> 모델)을 inner CV 로 튜닝
    4. best 설정으로 training fold 전체 재학습
    5. training fold 의 out-of-fold 예측으로 분류 threshold 결정
    6. test fold 예측 -> 성능 기록
    7. training fold 기준 feature 중요도 기록 (§16)

outer test 데이터는 1~6 어디에도 관여하지 않는다.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from sklearn.model_selection import GridSearchCV, cross_val_predict

from src.cv.splitters import inner_cv, outer_splits
from src.evaluation.metrics import choose_threshold, evaluate
from src.labels.binarize import LabelBinarizer
from src.models.zoo import ModelSpec, extract_importance


@dataclass
class NestedResult:
    """outer fold 별 성능과 feature 중요도, 그리고 test fold 예측."""

    metrics: pd.DataFrame        # fold 당 한 행
    importances: pd.DataFrame    # fold × feature (필터 통과분만)
    # outer test fold 예측을 전부 이어붙인 것 (fold, y_true, y_prob, y_pred, threshold).
    # confusion matrix 처럼 fold 를 합쳐야 하는 그림을 위해 남긴다 — 이게 없으면
    # 같은 nested CV 를 한 번 더 돌려야 한다.
    predictions: pd.DataFrame = field(default_factory=pd.DataFrame)

    @property
    def summary(self) -> pd.Series:
        num = self.metrics.select_dtypes("number")
        return num.mean(numeric_only=True)


def run_nested_cv(
    X: pd.DataFrame,
    y_raw: pd.Series,
    groups: pd.Series,
    spec: ModelSpec,
    target: str,
    scheme: str = "random",
    scoring: str = "roc_auc",
    n_jobs: int = -1,
    verbose: bool = True,
    outer_folds: int | None = None,
    inner_folds: int | None = None,
    pre_binarized: bool = False,
) -> NestedResult:
    """하나의 (모델, 표현형, split 방식) 조합에 대한 nested CV.

    outer_folds / inner_folds 를 주면 config 기본값을 덮어쓴다.
    암종 내부 분석처럼 표본이 작을 때 fold 를 줄이기 위한 것이다.

    pre_binarized=True 면 y_raw 가 이미 0/1 이라고 보고 fold 안에서
    threshold 를 다시 잡지 않는다. 암종 외부에서 정한 기준을 그대로
    적용하려는 경우에 쓴다. 이때 y_raw 는 해당 암종 데이터를 보지 않고
    만들어진 것이어야 한다.
    """
    X_values = X.to_numpy()
    feature_names = np.asarray(X.columns)

    # outer split 을 나누려면 stratify 용 이진 label 이 필요하다.
    # 여기서 쓰는 전체 기준 이진화는 '누가 어느 fold 에 가는가' 를 정할 뿐이며,
    # 학습에 쓰이는 label 은 각 fold 안에서 다시 만든다.
    y_strat = y_raw.astype(int) if pre_binarized else LabelBinarizer(target).fit_transform(y_raw)

    metric_rows, importance_rows, prediction_rows = [], [], []

    for fold, (tr, te) in enumerate(
        outer_splits(y_strat.to_numpy(), groups, scheme=scheme, n_splits=outer_folds)
    ):
        # --- 1~2. label threshold 는 training fold 에서만 ---
        if pre_binarized:
            y_tr = y_raw.iloc[tr].astype(int).to_numpy()
            y_te = y_raw.iloc[te].astype(int).to_numpy()
        else:
            binz = LabelBinarizer(target).fit(y_raw.iloc[tr])
            y_tr = binz.transform(y_raw.iloc[tr]).to_numpy()
            y_te = binz.transform(y_raw.iloc[te]).to_numpy()

        if len(np.unique(y_tr)) < 2:
            if verbose:
                print(f"  fold {fold}: training label 이 한 클래스뿐 — 건너뜀")
            continue

        X_tr, X_te = X_values[tr], X_values[te]

        # --- 3. inner CV 로 hyperparameter 선택 ---
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ConvergenceWarning)
            search = GridSearchCV(
                spec.build(), spec.param_grid, scoring=scoring,
                cv=inner_cv(n_splits=inner_folds), n_jobs=n_jobs, refit=True,
                error_score="raise",
            )
            search.fit(X_tr, y_tr)
            best = search.best_estimator_

            # --- 5. 분류 threshold 도 training fold 안에서 ---
            oof = cross_val_predict(
                search.best_estimator_, X_tr, y_tr, cv=inner_cv(n_splits=inner_folds),
                method="predict_proba", n_jobs=n_jobs,
            )[:, 1]
        threshold = choose_threshold(y_tr, oof)

        # --- 6. test fold 평가 ---
        prob_te = best.predict_proba(X_te)[:, 1]
        row = evaluate(y_te, prob_te, threshold=threshold)
        row.update({
            "fold": fold, "model": spec.name, "target": target, "scheme": scheme,
            "best_params": str(search.best_params_),
            "n_train": len(tr),
            "n_features_kept": int(best.named_steps["filter"].n_features_out_),
        })
        if scheme == "lolo":
            row["held_out_lineage"] = groups.iloc[te].iloc[0]
        metric_rows.append(row)
        prediction_rows.append(pd.DataFrame({
            "fold": fold, "y_true": y_te, "y_prob": prob_te,
            "y_pred": (prob_te >= threshold).astype(int), "threshold": threshold,
        }))

        # --- 7. feature 중요도 (필터 통과 feature 에만 해당) ---
        imp = extract_importance(best, spec.importance)
        if imp is not None:
            kept = feature_names[best.named_steps["filter"].get_support()]
            importance_rows.append(
                pd.DataFrame({"fold": fold, "feature": kept, "importance": imp})
            )

        if verbose:
            auc = row["roc_auc"]
            print(f"  fold {fold}: ROC-AUC {auc:.3f} | PR-AUC {row['pr_auc']:.3f} | "
                  f"feature {row['n_features_kept']:,} | {search.best_params_}")

    metrics = pd.DataFrame(metric_rows)
    importances = (
        pd.concat(importance_rows, ignore_index=True)
        if importance_rows else pd.DataFrame(columns=["fold", "feature", "importance"])
    )
    predictions = (
        pd.concat(prediction_rows, ignore_index=True)
        if prediction_rows
        else pd.DataFrame(columns=["fold", "y_true", "y_prob", "y_pred", "threshold"])
    )
    return NestedResult(metrics=metrics, importances=importances, predictions=predictions)
