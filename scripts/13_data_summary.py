"""입력 데이터 통계 요약 (docs/depmap/input_data_summary.md 재현용).

병합 전 원본 파일 단위로 row/col 과 dtype/min/max/mean/var 를 낸다.
병합 후 코호트 통계는 02_qc_merge.py, 04_eda.py 가 이미 담당하므로
이 스크립트는 '파일 하나하나가 어떻게 생겼는가' 에 집중한다.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src.config import REPO_ROOT, data_path

TABLES = REPO_ROOT / "results" / "tables"
META = ["Unnamed: 0", "SequencingID", "ModelID", "ModelConditionID",
        "IsDefaultEntryForModel", "IsDefaultEntryForMC"]


def mutation_matrix_stats() -> pd.DataFrame:
    rows = []
    for kind in ("hotspot", "damaging"):
        path = data_path(f"mutation_{kind}")
        raw = pd.read_csv(path)
        n_raw = len(raw)
        default = raw[raw.IsDefaultEntryForModel == "Yes"]

        genes = default.drop(columns=[c for c in META if c in default.columns])
        genes = genes.apply(pd.to_numeric, errors="coerce").fillna(0)
        vals = genes.to_numpy()

        rows.append({
            "file": kind, "n_rows_raw": n_raw, "n_rows_default": len(default),
            "n_cols_feature": genes.shape[1], "dtype": "int (변이 개수)",
            "min": vals.min(), "max": vals.max(), "mean": vals.mean(), "var": vals.var(),
            "binarized_positive_rate": (vals > 0).mean(),
        })
    return pd.DataFrame(rows)


def global_signatures_stats() -> pd.DataFrame:
    sig = pd.read_csv(data_path("global_signatures"))
    default = sig[sig.IsDefaultEntryForModel == "Yes"]

    cols = ["WGD", "CIN", "LoHFraction", "Ploidy", "Aneuploidy", "MSIScore"]
    rows = []
    for c in cols:
        s = default[c]
        rows.append({
            "column": c, "dtype": str(s.dtype), "n": int(s.notna().sum()),
            "n_missing": int(s.isna().sum()),
            "min": s.min(), "max": s.max(), "mean": s.mean(), "var": s.var(),
        })
    return pd.DataFrame(rows)


def model_stats() -> pd.DataFrame:
    mdl = pd.read_csv(data_path("model"))
    num_cols = mdl.select_dtypes(include="number").columns.tolist()
    desc = mdl[num_cols].describe().T[["min", "max", "mean", "std"]]
    desc.insert(0, "column", desc.index)
    return desc.reset_index(drop=True)


def main() -> int:
    TABLES.mkdir(parents=True, exist_ok=True)

    mat = mutation_matrix_stats()
    print("[Mutation matrix] row/col 과 셀 값 분포")
    print(mat.to_string(index=False))
    mat.to_csv(TABLES / "doc_mutation_matrix_stats.csv", index=False)

    sig = global_signatures_stats()
    print("\n[OmicsGlobalSignatures.csv]")
    print(sig.round(4).to_string(index=False))
    sig.to_csv(TABLES / "doc_globalsignatures_stats.csv", index=False)

    mdl = model_stats()
    print("\n[Model.csv] 수치형 컬럼")
    print(mdl.round(3).to_string(index=False))
    mdl.to_csv(TABLES / "doc_model_numeric_stats.csv", index=False)

    print(f"\n저장: {TABLES}/doc_*.csv")
    print("문서: docs/depmap/input_data_summary.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
