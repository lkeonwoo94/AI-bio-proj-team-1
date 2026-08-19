"""Future Work 2 — mutation signature(SBS 96-class) feature 행렬 생성.

원시 MAF 를 파싱해 세포주별 96-class 치환 비율 행렬을 만들고 저장한다.
이 스크립트는 데이터 준비 단계이고, 실제 모델 비교는
`24_signature_representation.py` 에서 한다(pathway 실험과 같은 구조,
`scripts/19_pathway_representation.py` 참고).
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import REPO_ROOT
from src.data.merge import load_cohort
from src.features.mutation_signature import build_signature_matrix


def main() -> int:
    cohort = load_cohort()
    print(f"대상 세포주: {len(cohort)}개")

    t0 = time.time()
    sig = build_signature_matrix(cell_line_ids=list(cohort.X.index))
    print(f"signature 행렬 생성 완료: {sig.shape}, {time.time()-t0:.1f}초")

    zero_rows = (sig.sum(axis=1) == 0).sum()
    print(f"SNV 가 0건이라 전부 0인 세포주: {zero_rows}개")

    out = REPO_ROOT / "data" / "depmap" / "sbs96_signature_matrix.parquet"
    out.parent.mkdir(parents=True, exist_ok=True)
    sig.to_parquet(out)
    print(f"저장: {out}")

    print("\n[96-class 평균 비율 상위 10개]")
    print(sig.mean().sort_values(ascending=False).head(10).round(4).to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
