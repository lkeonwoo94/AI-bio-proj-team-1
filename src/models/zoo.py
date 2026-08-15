"""모델 정의와 hyperparameter 탐색 범위 (README §11).

모든 모델은 동일한 Pipeline 구조를 쓴다.

    RareMutationFilter -> [StandardScaler] -> estimator

희귀 변이 필터가 Pipeline 안에 있으므로 inner CV 의 매 fold 마다
training 데이터만으로 다시 적합된다 (README §13).

hyperparameter 는 inner CV 가 고른다. 여기 적힌 것은 후보 범위일 뿐이다.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.config import load_config
from src.features.filter import RareMutationFilter


@dataclass
class ModelSpec:
    name: str
    build: callable
    param_grid: dict = field(default_factory=dict)
    importance: str = "none"   # coef | tree | none
    supports_multitask: bool = False


def _filter_step() -> tuple[str, RareMutationFilter]:
    cfg = load_config("experiment")["features"]
    return ("filter", RareMutationFilter(min_count=cfg["min_mutation_count"],
                                         min_freq=cfg["min_mutation_freq"]))


def _seed() -> int:
    return load_config("experiment")["seed"]


def logistic() -> ModelSpec:
    """가장 단순한 baseline (README §11).

    feature 가 많아 규제 없는 로지스틱은 발산한다. L2 규제를 기본으로 두고
    강도만 inner CV 가 고른다.
    """
    pipe = Pipeline([
        _filter_step(),
        ("scale", StandardScaler(with_mean=True)),
        ("clf", LogisticRegression(penalty="l2", solver="lbfgs", max_iter=2000,
                                   class_weight="balanced", random_state=_seed())),
    ])
    return ModelSpec("logistic", lambda: pipe,
                     {"clf__C": [0.01, 0.1, 1.0]}, importance="coef")


def elastic_net() -> ModelSpec:
    """L1/L2 혼합 규제 — feature selection 과 직접 연결된다 (README §11)."""
    pipe = Pipeline([
        _filter_step(),
        ("scale", StandardScaler(with_mean=True)),
        ("clf", LogisticRegression(penalty="elasticnet", solver="saga", max_iter=3000,
                                   class_weight="balanced", random_state=_seed())),
    ])
    return ModelSpec("elastic_net", lambda: pipe,
                     {"clf__C": [0.05, 0.2, 1.0], "clf__l1_ratio": [0.3, 0.7]},
                     importance="coef")


def random_forest() -> ModelSpec:
    """변이 간 비선형 관계와 interaction 반영 (README §11)."""
    pipe = Pipeline([
        _filter_step(),
        ("clf", RandomForestClassifier(n_estimators=500, class_weight="balanced_subsample",
                                       n_jobs=-1, random_state=_seed())),
    ])
    return ModelSpec("random_forest", lambda: pipe,
                     {"clf__max_depth": [None, 8], "clf__min_samples_leaf": [1, 5]},
                     importance="tree")


def xgboost() -> ModelSpec:
    """복잡한 변이 패턴 학습 (README §11)."""
    from xgboost import XGBClassifier

    pipe = Pipeline([
        _filter_step(),
        ("clf", XGBClassifier(n_estimators=400, learning_rate=0.05, subsample=0.8,
                              colsample_bytree=0.5, eval_metric="logloss",
                              tree_method="hist", n_jobs=-1, random_state=_seed())),
    ])
    return ModelSpec("xgboost", lambda: pipe,
                     {"clf__max_depth": [3, 6], "clf__reg_lambda": [1.0, 10.0]},
                     importance="tree")


def multitask_ann() -> ModelSpec:
    """공유 hidden layer 뒤에 WGD/CIN/LOH 세 출력을 두는 구조 (README §11).

    sklearn MLPClassifier 는 y 가 2차원 이진 행렬이면 multilabel 로 학습하는데,
    이것이 곧 '공유 표현 + 표현형별 출력 head' 구조다. torch 없이 같은 구조를
    얻을 수 있어 별도 프레임워크를 쓰지 않았다.
    """
    pipe = Pipeline([
        _filter_step(),
        ("scale", StandardScaler(with_mean=True)),
        ("clf", MLPClassifier(hidden_layer_sizes=(128,), activation="relu",
                              alpha=1e-3, max_iter=400, early_stopping=True,
                              n_iter_no_change=15, random_state=_seed())),
    ])
    return ModelSpec("multitask_ann", lambda: pipe,
                     {"clf__hidden_layer_sizes": [(128,), (256, 64)],
                      "clf__alpha": [1e-4, 1e-2]},
                     importance="none", supports_multitask=True)


REGISTRY = {
    "logistic": logistic,
    "elastic_net": elastic_net,
    "random_forest": random_forest,
    "xgboost": xgboost,
    "multitask_ann": multitask_ann,
}


def get_model(name: str) -> ModelSpec:
    if name not in REGISTRY:
        raise ValueError(f"알 수 없는 모델: {name!r} (사용 가능: {sorted(REGISTRY)})")
    return REGISTRY[name]()


def extract_importance(fitted_pipeline, kind: str) -> np.ndarray | None:
    """적합된 Pipeline 에서 필터 통과 feature 의 중요도를 뽑는다.

    반환 길이는 filter 통과 feature 수와 같다.
    """
    clf = fitted_pipeline.named_steps["clf"]
    if kind == "coef":
        return np.abs(np.asarray(clf.coef_).ravel())
    if kind == "tree":
        return np.asarray(clf.feature_importances_)
    return None
