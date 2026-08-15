"""DepMap 원본 로딩.

모든 로더는 세포주당 한 행(ModelID 유일)이 되도록 정규화해서 돌려준다.
원본은 시퀀싱 프로파일 단위(3,044행)이므로 이 정규화를 거치지 않으면
같은 세포주가 여러 번 들어가 CV split 이 오염된다.
"""

from __future__ import annotations

import pandas as pd

from src.config import data_path, load_config

DEFAULT_FLAG = "IsDefaultEntryForModel"
DEFAULT_VALUE = "Yes"


def _keep_default_profile(df: pd.DataFrame, name: str) -> pd.DataFrame:
    """세포주당 대표 프로파일만 남긴다.

    IsDefaultEntryForModel 은 불리언이 아니라 'Yes'/'No' 문자열이다.
    """
    if DEFAULT_FLAG not in df.columns:
        raise KeyError(f"{name}: {DEFAULT_FLAG} 컬럼이 없습니다.")

    out = df[df[DEFAULT_FLAG].astype(str).str.strip() == DEFAULT_VALUE]
    if out.empty:
        raise ValueError(
            f"{name}: {DEFAULT_FLAG}=='{DEFAULT_VALUE}' 인 행이 없습니다. "
            f"관측된 값: {sorted(df[DEFAULT_FLAG].dropna().unique())[:5]}"
        )

    dup = out["ModelID"].duplicated().sum()
    if dup:
        raise ValueError(f"{name}: 대표 프로파일 필터 후에도 ModelID 중복 {dup}건")
    return out.set_index("ModelID")


def load_signatures() -> pd.DataFrame:
    """WGD / CIN / LoHFraction 등 유전체 불안정성 지표. index=ModelID."""
    df = pd.read_csv(data_path("global_signatures"))
    return _keep_default_profile(df, "GlobalSignatures")


def load_model() -> pd.DataFrame:
    """세포주 메타. index=ModelID. lineage 컬럼 포함."""
    keys = load_config("data")["keys"]
    df = pd.read_csv(data_path("model"))
    dup = df[keys["sample_id"]].duplicated().sum()
    if dup:
        raise ValueError(f"Model.csv: ModelID 중복 {dup}건")
    return df.set_index(keys["sample_id"])


def load_mutation(kind: str, binarize: bool = True) -> pd.DataFrame:
    """hotspot 또는 damaging mutation matrix. index=ModelID, 컬럼=유전자.

    원본 값은 변이 개수이지만 본 분석은 존재 여부만 사용하므로 기본 이진화한다.
    """
    if kind not in ("hotspot", "damaging"):
        raise ValueError(f"kind 는 hotspot 또는 damaging: {kind!r}")

    meta = load_config("experiment")["features"]["meta_columns"]
    df = pd.read_csv(data_path(f"mutation_{kind}"))
    df = _keep_default_profile(df, f"Mutation{kind.capitalize()}")

    genes = df.drop(columns=[c for c in meta if c in df.columns], errors="ignore")
    genes = genes.apply(pd.to_numeric, errors="coerce").fillna(0.0)
    return (genes > 0).astype("int8") if binarize else genes
