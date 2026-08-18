"""CIN/LoHFraction 을 연속값으로 직접 예측하는 회귀 모델 (§26⑤ 후속).

분류 파이프라인(중앙값 이진화)이 버리는 정보를 회귀로 직접 예측해서,
지금까지의 분류 AUC 가 "이진화 때문에 낮아 보이는 것"인지 "연속값으로
봐도 원래 신호가 그 정도인 것"인지 구분하려는 목적이다.

Pipeline 구조는 분류와 동일하게 유지한다.

    RareMutationFilter -> [StandardScaler] -> regressor

같은 `ModelSpec` 을 재사용하되 `importance` 필드는 분류와 동일한 방식으로
읽는다(회귀 계수의 절댓값 / RF 의 feature_importances_).
"""

from __future__ import annotations

from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import ElasticNet
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.config import load_config
from src.features.filter import RareMutationFilter
from src.models.zoo import ModelSpec


def _filter_step() -> tuple[str, RareMutationFilter]:
    cfg = load_config("experiment")["features"]
    return ("filter", RareMutationFilter(min_count=cfg["min_mutation_count"],
                                         min_freq=cfg["min_mutation_freq"]))


def _seed() -> int:
    return load_config("experiment")["seed"]


def elastic_net_reg() -> ModelSpec:
    """분류 쪽 Elastic Net 과 대응되는 회귀 버전."""
    pipe = Pipeline([
        _filter_step(),
        ("scale", StandardScaler(with_mean=True)),
        ("clf", ElasticNet(max_iter=5000, random_state=_seed())),
    ])
    return ModelSpec("elastic_net_reg", lambda: pipe,
                     {"clf__alpha": [0.01, 0.1, 1.0], "clf__l1_ratio": [0.3, 0.7]},
                     importance="coef")


def random_forest_reg() -> ModelSpec:
    """분류 쪽 1위 모델(Random Forest)과 대응되는 회귀 버전."""
    pipe = Pipeline([
        _filter_step(),
        ("clf", RandomForestRegressor(n_estimators=500, n_jobs=-1, random_state=_seed())),
    ])
    return ModelSpec("random_forest_reg", lambda: pipe,
                     {"clf__max_depth": [None, 8], "clf__min_samples_leaf": [1, 5]},
                     importance="tree")


REGRESSION_REGISTRY = {
    "elastic_net_reg": elastic_net_reg,
    "random_forest_reg": random_forest_reg,
}


def get_regression_model(name: str) -> ModelSpec:
    if name not in REGRESSION_REGISTRY:
        raise ValueError(f"알 수 없는 회귀 모델: {name!r} (사용 가능: {sorted(REGRESSION_REGISTRY)})")
    return REGRESSION_REGISTRY[name]()
