"""Day 2-3 — QC 와 분석 테이블 구축.

ModelID 중복·결측·교집합을 확인하고, 최종 분석 코호트를 만들어 캐시한다.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src.config import REPO_ROOT
from src.data.io import load_model, load_mutation, load_signatures
from src.data.merge import label_prevalence, load_cohort

TABLES = REPO_ROOT / "results" / "tables"


def qc_sources() -> pd.DataFrame:
    """각 원본의 행 수와 ModelID 상태를 표로 만든다."""
    sources = {
        "hotspot": load_mutation("hotspot"),
        "damaging": load_mutation("damaging"),
        "signatures": load_signatures(),
        "model": load_model(),
    }
    rows = []
    for name, df in sources.items():
        rows.append(
            {
                "source": name,
                "n_rows": len(df),
                "n_modelid": df.index.nunique(),
                "n_columns": df.shape[1],
                "modelid_duplicated": int(df.index.duplicated().sum()),
            }
        )
    qc = pd.DataFrame(rows)

    ids = {k: set(v.index) for k, v in sources.items()}
    print("\n[교집합]")
    print(f"  hotspot ∩ damaging          : {len(ids['hotspot'] & ids['damaging']):,}")
    print(f"  mutation ∩ signatures       : "
          f"{len(ids['hotspot'] & ids['damaging'] & ids['signatures']):,}")
    print(f"  전체 4개 교집합             : {len(set.intersection(*ids.values())):,}")
    return qc


def main() -> int:
    print("[원본 QC]")
    qc = qc_sources()
    print(qc.to_string(index=False))

    print("\n[코호트 구축]")
    cohort = load_cohort(rebuild=True, verbose=True)
    print(f"  {cohort.summary()}")

    print("\n[라벨 분포]")
    prev = label_prevalence(cohort.y)
    print(prev.to_string(index=False))

    print("\n[lineage 상위 10종]")
    lin = cohort.groups.value_counts()
    print(lin.head(10).to_string())
    small = lin[lin < 20]
    print(f"\n  세포주 20개 미만 lineage: {len(small)}종 ({small.sum()}개 세포주)")

    TABLES.mkdir(parents=True, exist_ok=True)
    qc.to_csv(TABLES / "qc_sources.csv", index=False)
    prev.to_csv(TABLES / "qc_label_prevalence.csv", index=False)
    lin.rename("n_cell_lines").to_csv(TABLES / "qc_lineage_counts.csv")
    print(f"\n저장: {TABLES}/qc_*.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
