"""DepMap 캐시 로더.

`scripts/depmap_cache.py` 가 만든 캐시를 읽는다. 캐시가 없으면 원본 CSV로
그대로 폴백하므로, 호출부는 캐시 유무를 신경 쓰지 않아도 된다.

    from src.preprocessing.depmap_io import load_all
    d = load_all()
    d.expression        # (1140, 19215)  DataFrame, ModelID 인덱스
    d.gene_effect       # (1140, 18531)
    d.model             # (1140, 48)
    d.common_essentials # set

행은 세 데이터의 교집합 ModelID로 맞춰지고 순서도 동일하다.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
CACHE = REPO / "data" / "interim" / "depmap"
RAW = (REPO.parent / "raw" / "DepMap").resolve()


@dataclass
class DepMap:
    expression: pd.DataFrame
    gene_effect: pd.DataFrame
    model: pd.DataFrame
    common_essentials: set

    @property
    def cells(self) -> pd.Index:
        return self.expression.index

    @property
    def lineage(self) -> pd.Series:
        return self.model["OncotreeLineage"].fillna("Unknown")

    def selective_targets(self, sd_cut: float = 0.25) -> list[str]:
        """common essential 을 뺀 뒤 세포주 간 분산이 큰 유전자."""
        sd = self.gene_effect.std()
        return [g for g in self.gene_effect.columns
                if g not in self.common_essentials and sd[g] > sd_cut]


def _load_matrix(name: str, mmap: bool = False) -> pd.DataFrame:
    values = np.load(CACHE / f"{name}.npy", mmap_mode="r" if mmap else None)
    index = np.load(CACHE / f"{name}.index.npy", allow_pickle=True)
    columns = np.load(CACHE / f"{name}.columns.npy", allow_pickle=True)
    return pd.DataFrame(values, index=pd.Index(index, name="ModelID"),
                        columns=columns, copy=False)


def _gene_cols(cols) -> list[str]:
    return [c for c in cols if c.endswith(")") and " (" in c]


def _from_raw() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, set]:
    ge = pd.read_csv(RAW / "CRISPRGeneEffect.csv", index_col=0)
    ge.index.name = "ModelID"
    ex = pd.read_csv(RAW / "OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv",
                     index_col=0, low_memory=False)
    ex = ex[ex["IsDefaultEntryForModel"].astype(str) == "Yes"].set_index("ModelID")
    ex = ex[_gene_cols(ex.columns)]
    mod = pd.read_csv(RAW / "Model.csv", low_memory=False).set_index("ModelID")
    ce = set(pd.read_csv(RAW / "CRISPRInferredCommonEssentials.csv")["Essentials"])
    return ex, ge, mod, ce


def cache_exists() -> bool:
    return (CACHE / "manifest.json").exists()


def load_all(align: bool = True, mmap: bool = False) -> DepMap:
    """캐시(없으면 원본 CSV)에서 읽어 교집합 ModelID로 정렬해 돌려준다.

    align=False 면 각 테이블을 원래 행 구성 그대로 돌려준다.
    mmap=True 면 대용량 행렬을 메모리 매핑으로 연다(읽기 전용, 초기 로딩 즉시).
    """
    if cache_exists():
        ex = _load_matrix("expression", mmap)
        ge = _load_matrix("crispr_gene_effect", mmap)
        mod = pd.read_parquet(CACHE / "model.parquet")
        ce = set(pd.read_parquet(CACHE / "common_essentials.parquet")["Essentials"])
    else:
        ex, ge, mod, ce = _from_raw()

    if not align:
        return DepMap(ex, ge, mod, ce)

    cells = sorted(set(ex.index) & set(ge.index) & set(mod.index))
    return DepMap(ex.loc[cells], ge.loc[cells], mod.loc[cells], ce)
