"""Pathway 단위 mutation burden 재집계 (Future Work 1, final_conclusion.md).

20,132개 유전자 컬럼을 MSigDB Hallmark/KEGG 의 생물학적 경로로 묶어,
"이 세포주가 이 경로 유전자 중 몇 개(비율)에 damaging/hotspot mutation
을 가졌는가" 를 새 feature 로 만든다.

sparsity 를 정면으로 줄이는 접근이다 — hotspot 554개 중 필터를 통과하는
건 36개뿐이지만(§Day4 EDA), pathway 단위로 묶으면 유전자 하나의 관측
빈도가 아니라 경로 전체의 누적 빈도를 보게 되어 신호가 살아난다.

gene-set 목록은 표현형과 무관한 정적 메타데이터(MSigDB/KEGG 공개 자료)
이므로, 이 transformer 를 Pipeline 안에 넣어도 §13 누출 위험이 없다 —
`RareMutationFilter` 처럼 fold 마다 다시 계산해야 하는 통계량이 아니라
fold 이전에 한 번 정해지는 고정 매핑이기 때문이다.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

from src.config import REPO_ROOT

GENESETS_PATH = REPO_ROOT / "configs" / "genesets" / "pathway_genesets.json"


def load_genesets() -> dict[str, list[str]]:
    with GENESETS_PATH.open(encoding="utf-8") as f:
        return json.load(f)


class PathwayAggregator(BaseEstimator, TransformerMixin):
    """유전자×세포주 이진 행렬을 pathway×세포주 비율 행렬로 접는다.

    각 pathway feature 값 = (그 세포주가 mutation 을 가진, 그 pathway
    소속 유전자 수) / (그 pathway 소속 유전자 중 데이터에 존재하는 수).
    hotspot/damaging 은 분리 유지한다(README §9.2 의 keep_separate 원칙과
    동일한 이유 — 기능획득/기능손실 신호가 다르다).

    fold 와 무관하게 컬럼 매핑이 고정되므로 `fit` 은 입력 feature 이름과
    pathway 매핑의 교집합만 계산하고, 실제 학습 데이터의 분포는 보지
    않는다 — 통계량 추정이 아니라 정적 매핑 적용이다.
    """

    def __init__(self, genesets: dict[str, list[str]] | None = None):
        self.genesets = genesets

    def fit(self, X, y=None):
        genesets = self.genesets or load_genesets()
        columns = X.columns if isinstance(X, pd.DataFrame) else self._feature_names_in_
        self.feature_names_in_ = np.asarray(columns)

        gene_of = np.array([c.split(" (")[0] for c in self.feature_names_in_])
        kind_of = np.array(["hotspot" if c.endswith("_hotspot") else "damaging"
                            for c in self.feature_names_in_])

        self.pathway_masks_ = {}
        self.pathway_names_ = []
        for pw_name, genes in genesets.items():
            gene_set = set(genes)
            for kind in ("hotspot", "damaging"):
                mask = (kind_of == kind) & np.isin(gene_of, list(gene_set))
                n_present = int(mask.sum())
                if n_present == 0:
                    continue
                out_name = f"{pw_name}_{kind}"
                self.pathway_masks_[out_name] = mask
                self.pathway_names_.append(out_name)

        return self

    def transform(self, X):
        values = X.to_numpy() if isinstance(X, pd.DataFrame) else np.asarray(X)
        out = np.zeros((values.shape[0], len(self.pathway_names_)), dtype=float)
        for i, name in enumerate(self.pathway_names_):
            mask = self.pathway_masks_[name]
            # 비율 = 그 세포주가 mutation 가진 pathway 내 유전자 수 / pathway 내 유전자 총수
            out[:, i] = (values[:, mask] > 0).sum(axis=1) / mask.sum()
        return out

    def get_feature_names_out(self, input_features=None):
        return np.asarray(self.pathway_names_)
