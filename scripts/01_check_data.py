"""Day 1 — 데이터 점검.

필요한 파일이 모두 있는지 확인하고, 있으면 WGD/CIN/LOH 후보 컬럼과
lineage 컬럼을 찾아 출력한다. 아직 없는 파일은 무엇을 받아야 하는지 알려준다.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src.config import data_path, data_root, load_config, missing_data_files

# OmicsGlobalSignatures 에서 찾을 표현형 키워드
LABEL_KEYWORDS = {
    "WGD": ("wgd", "doubling", "genome_doubl"),
    "CIN": ("cin", "aneuploidy", "instability", "arm_level"),
    "LOH": ("loh", "heterozygosity"),
}


def check_presence() -> dict[str, Path]:
    print(f"데이터 루트: {data_root()}")
    missing = missing_data_files()

    files = load_config("data")["files"]
    for key in files:
        mark = "없음" if key in missing else "있음"
        print(f"  [{mark}] {key:20s} {files[key]}")

    if missing:
        print("\n다음 파일을 DepMap 포털에서 받아야 합니다:")
        for key, path in missing.items():
            print(f"  - {path.name}  ->  {path.parent}")
    return missing


def report_label_columns() -> None:
    """OmicsGlobalSignatures 의 컬럼에서 WGD/CIN/LOH 후보를 찾는다."""
    sig = pd.read_csv(data_path("global_signatures"), nrows=5)
    print(f"\nOmicsGlobalSignatures 컬럼 {len(sig.columns)}개")

    for phenotype, keywords in LABEL_KEYWORDS.items():
        hits = [c for c in sig.columns if any(k in c.lower() for k in keywords)]
        print(f"  {phenotype}: {hits or '후보 없음 — 수동 확인 필요'}")

    print("\n찾은 컬럼은 configs/experiment.yaml 의 source_column 에 기록하세요.")


def report_lineage() -> None:
    keys = load_config("data")["keys"]
    model = pd.read_csv(data_path("model"), usecols=[keys["sample_id"], keys["lineage"]])
    counts = model[keys["lineage"]].value_counts()

    print(f"\nModel.csv: 세포주 {len(model)}개, lineage {len(counts)}종")
    print(counts.head(10).to_string())

    small = counts[counts < 20]
    if len(small):
        print(
            f"\n세포주 20개 미만 lineage {len(small)}종 — "
            "Leave-One-Lineage-Out 결과가 불안정할 수 있습니다."
        )


def main() -> int:
    missing = check_presence()

    if "model" not in missing:
        report_lineage()
    if "global_signatures" not in missing:
        report_label_columns()

    if missing:
        print("\n파일이 갖춰지면 다시 실행하세요.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
