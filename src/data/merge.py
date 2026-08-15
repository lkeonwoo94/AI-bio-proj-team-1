"""ModelID 기준 병합과 분석 코호트 구성 (README §9.1).

여기서 만드는 것은 "누가 분석에 들어가는가"와 "원시 feature/label 이 무엇인가"
까지다. 이진화·필터링처럼 fold 에 의존하는 처리는 절대 하지 않는다.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.config import load_config
from src.data.io import load_model, load_mutation, load_signatures

CACHE_DIR_KEY = "data/interim"


@dataclass
class Cohort:
    """분석에 들어가는 전체 데이터.

    X: mutation feature (0/1), index=ModelID
    y: 원시 label. wgd 는 0/1, cin/loh 는 연속형 (이진화는 fold 안에서)
    groups: lineage. GroupKFold 와 Leave-One-Lineage-Out 에 사용
    """

    X: pd.DataFrame
    y: pd.DataFrame
    groups: pd.Series

    def __post_init__(self) -> None:
        if not (self.X.index.equals(self.y.index) and self.X.index.equals(self.groups.index)):
            raise ValueError("X / y / groups 의 index(ModelID) 가 일치하지 않습니다.")

    def __len__(self) -> int:
        return len(self.X)

    def summary(self) -> str:
        n_hot = sum(c.endswith("_hotspot") for c in self.X.columns)
        n_dam = len(self.X.columns) - n_hot
        return (
            f"세포주 {len(self):,} | feature {self.X.shape[1]:,} "
            f"(hotspot {n_hot:,} / damaging {n_dam:,}) | lineage {self.groups.nunique()}종"
        )


def build_cohort(verbose: bool = False) -> Cohort:
    """네 파일을 ModelID 로 결합해 분석 코호트를 만든다."""
    cfg = load_config("experiment")
    keys = load_config("data")["keys"]
    label_cols = {name: spec["source_column"] for name, spec in cfg["labels"].items()}
    suffix = cfg["features"]["suffix"]

    hotspot = load_mutation("hotspot")
    damaging = load_mutation("damaging")
    sig = load_signatures()
    model = load_model()

    # 세 표현형이 모두 있는 세포주만 사용한다 (동일한 337행에서 함께 결측).
    labels = sig[list(label_cols.values())].dropna()
    labels.columns = list(label_cols.keys())

    common = (
        hotspot.index.intersection(damaging.index)
        .intersection(labels.index)
        .intersection(model.index)
        .sort_values()
    )
    if verbose:
        print(f"  hotspot {len(hotspot):,} / damaging {len(damaging):,} / "
              f"label {len(labels):,} / model {len(model):,} -> 교집합 {len(common):,}")

    if cfg["features"]["merge_rule"] == "keep_separate":
        X = pd.concat(
            [
                hotspot.loc[common].add_suffix(suffix["hotspot"]),
                damaging.loc[common].add_suffix(suffix["damaging"]),
            ],
            axis=1,
        )
    else:  # union_or — 같은 유전자를 하나로 합친다
        h, d = hotspot.loc[common], damaging.loc[common]
        genes = h.columns.union(d.columns)
        X = (
            h.reindex(columns=genes, fill_value=0) | d.reindex(columns=genes, fill_value=0)
        ).astype("int8")

    groups = model.loc[common, keys["lineage"]]
    # lineage 결측은 GroupKFold 에서 하나의 그룹으로 뭉쳐 버리므로 별도 표시한다.
    groups = groups.fillna("Unknown")

    return Cohort(X=X, y=labels.loc[common], groups=groups)


def _cache_dir():
    from src.config import REPO_ROOT

    path = REPO_ROOT / CACHE_DIR_KEY
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_cohort(rebuild: bool = False, verbose: bool = False) -> Cohort:
    """캐시된 코호트를 읽고, 없으면 만들어 저장한다.

    damaging matrix 가 228MB 라 매번 CSV 를 파싱하면 느리다.
    캐시는 data/interim/ 에 두며 git 추적 대상이 아니다.
    """
    cache = _cache_dir()
    files = {n: cache / f"cohort_{n}.parquet" for n in ("X", "y", "groups")}

    if not rebuild and all(f.exists() for f in files.values()):
        X = pd.read_parquet(files["X"])
        y = pd.read_parquet(files["y"])
        groups = pd.read_parquet(files["groups"])["lineage"]
        if verbose:
            print(f"  캐시 사용: {cache}")
        return Cohort(X=X, y=y, groups=groups)

    cohort = build_cohort(verbose=verbose)
    cohort.X.to_parquet(files["X"])
    cohort.y.to_parquet(files["y"])
    cohort.groups.rename("lineage").to_frame().to_parquet(files["groups"])
    if verbose:
        print(f"  캐시 저장: {cache}")
    return cohort


def label_prevalence(y: pd.DataFrame) -> pd.DataFrame:
    """라벨 요약. 연속형은 분포, binary 는 양성 비율."""
    rows = []
    cfg = load_config("experiment")["labels"]
    for name in y.columns:
        s = y[name]
        if cfg[name]["type"] == "binary":
            rows.append({"label": name, "type": "binary", "positive_rate": s.mean(),
                         "n_pos": int(s.sum()), "n_neg": int((1 - s).sum()),
                         "median": np.nan})
        else:
            rows.append({"label": name, "type": "continuous", "positive_rate": np.nan,
                         "n_pos": np.nan, "n_neg": np.nan, "median": s.median()})
    return pd.DataFrame(rows)
