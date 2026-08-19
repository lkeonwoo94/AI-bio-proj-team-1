"""TCGA 독립 코호트 로더 (한계 6번 후속, final_conclusion.md "Future Work 3").

DepMap 에서 학습한 모델이 실제 환자 종양(TCGA)에도 통하는지 검증하기
위한 최소 로더. WGD 라벨만 다룬다 — CIN/LoHFraction 에 대응하는 지표는
받아둔 파일(ABSOLUTE purity/ploidy table)에 없다(§"Future Work" 참고).

두 파일을 쓴다.
  - TCGA_mastercalls.abs_tables_JSedit.fixed.txt : ABSOLUTE 결과.
    'sample' 컬럼이 MAF 의 Tumor_Sample_Barcode 와 형식이 완전히 같아
    별도 barcode 절단 없이 그대로 join 된다.
  - mc3.v0.2.8.PUBLIC.maf.gz : 전체 TCGA somatic mutation MAF.

DepMap 의 'damaging(LikelyLoF)' 과 개념을 맞추기 위해 표준 truncating
variant class 집합(frameshift/nonsense/splice site/start loss/stop loss)
만 damaging 으로 센다. DepMap 은 VEP LofTool 기반 판정이라 완전히
동일하지는 않다 — 근사치라는 점을 §"Future Work" 한계에 명시한다.
hotspot 에 대응하는 채널은 만들지 않는다(큐레이션 DB 필요, README §7
논의와 동일한 이유로 재현 범위 밖).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src.config import REPO_ROOT

GDC_DIR = REPO_ROOT / "data" / "gdc"
ABSOLUTE_FILE = GDC_DIR / "TCGA_mastercalls.abs_tables_JSedit.fixed.txt"
MAF_FILE = GDC_DIR / "mc3.v0.2.8.PUBLIC.maf.gz"

# DepMap 의 LikelyLoF(=damaging) 에 대응하는 표준 truncating variant class.
# In_Frame_Del/Ins 는 reading frame 을 보존하므로 제외한다(표준 LoF 정의와 동일).
LOF_CLASSES = {
    "Frame_Shift_Del", "Frame_Shift_Ins", "Nonsense_Mutation",
    "Splice_Site", "Translation_Start_Site", "Nonstop_Mutation",
}


def _short_barcode(full: pd.Series) -> pd.Series:
    """barcode 를 앞 15자(참가자+샘플타입)로 절단한다.

    ABSOLUTE 와 MC3 는 서로 다른 시퀀싱 플레이트/센터에서 만들어져
    barcode 뒤쪽(plate, center 코드)이 서로 다르다 — 전체 barcode 로
    join 하면 10,642개 중 12개만 매칭된다. TCGA 데이터 종류 간 병합의
    표준 관례대로 앞 15자(예: TCGA-3A-A9IR-01A)만 잘라서 맞추면
    91%(9,651개)가 매칭된다.
    """
    return full.str.slice(0, 15)


def load_wgd_labels() -> pd.DataFrame:
    """ABSOLUTE 결과에서 WGD 라벨을 만든다.

    'Genome doublings' 컬럼이 이미 whole genome doubling 횟수다(0/1/2).
    DepMap 의 WGD 와 같은 정의로 맞추기 위해 >=1 을 WGD+ 로 이진화한다.
    """
    df = pd.read_csv(ABSOLUTE_FILE, sep="\t")
    df = df.rename(columns={"sample": "barcode", "Genome doublings": "genome_doublings"})
    df = df.dropna(subset=["genome_doublings"])
    df["barcode"] = _short_barcode(df["barcode"])

    dup = df.barcode.duplicated().sum()
    if dup:
        # 같은 샘플이 여러 번 나오면 첫 항목만 사용 — DepMap 의
        # IsDefaultEntryForModel 필터와 같은 역할.
        df = df.drop_duplicates(subset="barcode", keep="first")

    df["wgd"] = (df.genome_doublings >= 1).astype(int)
    return df.set_index("barcode")[["wgd", "purity", "ploidy", "call status"]]


def build_damaging_matrix(barcodes: set[str], min_count: int = 0) -> pd.DataFrame:
    """MC3 MAF 에서 barcode x 유전자 damaging(LikelyLoF 근사) 이진 행렬을 만든다.

    barcodes 로 미리 필터링해 불필요한 샘플의 레코드를 걷어내고 메모리를
    아낀다 — TCGA 전체가 아니라 WGD 라벨이 있는 샘플만 필요하기 때문이다.
    """
    usecols = ["Hugo_Symbol", "Variant_Classification", "Tumor_Sample_Barcode"]
    chunks = []
    for chunk in pd.read_csv(MAF_FILE, sep="\t", usecols=usecols, chunksize=500_000,
                             low_memory=False):
        chunk = chunk.assign(Tumor_Sample_Barcode=_short_barcode(chunk.Tumor_Sample_Barcode))
        chunk = chunk[chunk.Tumor_Sample_Barcode.isin(barcodes) &
                      chunk.Variant_Classification.isin(LOF_CLASSES)]
        if not chunk.empty:
            chunks.append(chunk)

    if not chunks:
        raise ValueError("MAF 에서 barcode 와 매칭되는 damaging 변이를 찾지 못했습니다.")

    hits = pd.concat(chunks, ignore_index=True)
    hits = hits.drop_duplicates(subset=["Tumor_Sample_Barcode", "Hugo_Symbol"])

    mat = pd.crosstab(hits.Tumor_Sample_Barcode, hits.Hugo_Symbol)
    mat = (mat > 0).astype("int8")

    # WGD 라벨은 있지만 mutation 이 하나도 안 걸린 샘플(전부 0)도 행으로
    # 살려야 한다 — 없으면 그 샘플은 "정보 없음"이 아니라 "정상"이 된다.
    mat = mat.reindex(sorted(barcodes), fill_value=0)
    return mat


def load_tcga_cohort() -> tuple[pd.DataFrame, pd.Series]:
    """WGD 라벨과 damaging 행렬을 barcode 기준으로 합쳐 반환한다."""
    labels = load_wgd_labels()
    X = build_damaging_matrix(set(labels.index))
    common = labels.index.intersection(X.index)
    return X.loc[common], labels.loc[common, "wgd"]
