"""Mutation signature(trinucleotide context) feature 생성 (Future Work 2).

원시 MAF(`OmicsSomaticMutations.csv`)의 SNV 하나하나에서 앞뒤 염기를
읽어 COSMIC SBS 표준 96-class(치환 6종 × context 16종)로 분류하고,
세포주별로 그 분포(비율)를 feature 로 만든다.

이 계산은 fold 와 무관하다 — 참조 게놈 서열은 표현형과 무관한 고정된
사실이라, 전체 데이터에서 한 번 계산해도 §13 누출 위험이 없다
(gene-set 매핑을 fold 밖에서 계산해도 되는 것과 같은 이유,
`pathway_aggregate.py` 참고).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src.config import REPO_ROOT, data_path

REFERENCE_2BIT = REPO_ROOT / "data" / "reference" / "hg38.2bit"

# COSMIC SBS 표준 6종 치환(피리미딘 기준 strand 로 통일)
SUBSTITUTIONS = ["C>A", "C>G", "C>T", "T>A", "T>C", "T>G"]
BASES = ["A", "C", "G", "T"]
COMPLEMENT = {"A": "T", "T": "A", "C": "G", "G": "C"}

# 96 개 표준 컬럼 이름: 예 "A[C>A]A"
SBS_96_COLUMNS = [
    f"{five}[{sub}]{three}"
    for sub in SUBSTITUTIONS
    for five in BASES
    for three in BASES
]


def _reverse_complement(seq: str) -> str:
    return "".join(COMPLEMENT[b] for b in reversed(seq))


def load_snv_records() -> pd.DataFrame:
    """원시 MAF 에서 default 프로파일의 SNV 만 읽는다."""
    usecols = ["ModelID", "IsDefaultEntryForModel", "Chrom", "Pos", "Ref", "Alt", "VariantType"]
    df = pd.read_csv(data_path("global_signatures").parent / "OmicsSomaticMutations.csv",
                     usecols=usecols, low_memory=False)
    df = df[(df.IsDefaultEntryForModel == "Yes") & (df.VariantType == "SNV")]
    df = df[df.Ref.isin(BASES) & df.Alt.isin(BASES)]  # 순수 단일염기치환만
    return df.drop(columns=["IsDefaultEntryForModel", "VariantType"])


def classify_sbs96(records: pd.DataFrame, batch_size: int = 200_000) -> pd.DataFrame:
    """각 SNV 에 96-class SBS 라벨을 붙인다.

    py2bit 로 변이 위치의 5'-Ref-3' 3-mer 를 읽고, Ref 가 퓨린(A/G)이면
    역상보를 취해 피리미딘(C/T) 기준으로 통일한다 — COSMIC 표준과 동일.
    """
    import py2bit

    tb = py2bit.open(str(REFERENCE_2BIT))
    n = len(records)
    sbs = np.empty(n, dtype=object)

    chrom = records.Chrom.to_numpy()
    pos = records.Pos.to_numpy()  # 1-based (MAF 관례)
    ref = records.Ref.to_numpy()
    alt = records.Alt.to_numpy()

    for start in range(0, n, batch_size):
        end = min(start + batch_size, n)
        for i in range(start, end):
            try:
                # py2bit 는 0-based half-open. 1-based Pos 의 3-mer 는 [Pos-2, Pos+1).
                tri = tb.sequence(chrom[i], int(pos[i]) - 2, int(pos[i]) + 1)
            except RuntimeError:
                sbs[i] = None
                continue
            if len(tri) != 3 or tri[1] != ref[i]:
                sbs[i] = None  # 참조와 안 맞으면(좌표 문제 등) 버린다
                continue

            five, center, three = tri[0], tri[1], tri[2]
            a = alt[i]
            if center in ("A", "G"):
                five, center, three = _reverse_complement(three), COMPLEMENT[center], _reverse_complement(five)
                a = COMPLEMENT[a]
            sbs[i] = f"{five}[{center}>{a}]{three}"

    tb.close()
    records = records.copy()
    records["sbs96"] = sbs
    return records.dropna(subset=["sbs96"])


def build_signature_matrix(cell_line_ids: list[str] | None = None) -> pd.DataFrame:
    """ModelID x 96 SBS class 비율 행렬을 만든다.

    반환값은 세포주별로 합이 1 인 비율(proportion) — mutation burden
    자체는 이미 다른 feature(예: cohort.X 의 유전자 개수)로 어느 정도
    반영되므로, 여기서는 "어떤 종류의 변이가 상대적으로 많은가"라는
    signature 고유의 정보만 남긴다.
    """
    records = load_snv_records()
    if cell_line_ids is not None:
        records = records[records.ModelID.isin(cell_line_ids)]

    classified = classify_sbs96(records)
    counts = pd.crosstab(classified.ModelID, classified.sbs96)
    counts = counts.reindex(columns=SBS_96_COLUMNS, fill_value=0)

    if cell_line_ids is not None:
        counts = counts.reindex(cell_line_ids, fill_value=0)

    proportions = counts.div(counts.sum(axis=1).replace(0, np.nan), axis=0).fillna(0)
    return proportions
