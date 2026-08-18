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
from src.data.merge import load_cohort

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


def cohort_matrix_stats() -> pd.DataFrame:
    """학습 직전 X (cohort.X) 통계 — 병합·이진화 완료, fold 필터 이전.

    이 다음 단계(RareMutationFilter)는 fold 마다 다시 계산되므로
    단일 통계로 고정할 수 없다. 즉 여기가 '고정 가능한 마지막 지점'이다.
    """
    cohort = load_cohort()
    X = cohort.X
    vals = X.to_numpy()
    is_hot = X.columns.str.endswith("_hotspot")

    rows = []
    for name, mask in (("전체", slice(None)), ("hotspot", is_hot), ("damaging", ~is_hot)):
        v = vals if isinstance(mask, slice) else vals[:, mask]
        rows.append({
            "구분": name, "n_rows": X.shape[0], "n_cols": v.shape[1],
            "dtype": str(X.dtypes.iloc[0]),
            "min": v.min(), "max": v.max(), "mean": v.mean(), "var": v.var(),
            "positive_rate": v.mean(),
        })
    return pd.DataFrame(rows)


def cohort_matrix_top_columns(top_n: int = 10) -> pd.DataFrame:
    """cohort.X 의 컬럼(유전자)별 통계 상위 top_n — 분산 기준.

    이진 변수의 var = mean*(1-mean) 이므로 분산 상위는 곧 '양성비율이
    0.5 에 가장 가까운' 유전자들이다. 20,132개를 뭉뚱그린 doc_cohort_X_stats
    와 달리 개별 유전자 수준을 보여준다.
    """
    X = load_cohort().X
    var = X.var(axis=0, ddof=0)

    top = pd.DataFrame({
        "column": X.columns,
        "dtype": [str(X[c].dtype) for c in X.columns],
        "min": X.min(axis=0).to_numpy(),
        "max": X.max(axis=0).to_numpy(),
        "mean": X.mean(axis=0).to_numpy(),
        "var": var.to_numpy(),
    })
    return top.sort_values("var", ascending=False).head(top_n).reset_index(drop=True)


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
    print("[Mutation matrix — 병합 전 원본] row/col 과 셀 값 분포")
    print(mat.to_string(index=False))
    mat.to_csv(TABLES / "doc_mutation_matrix_stats.csv", index=False)

    cohort_mat = cohort_matrix_stats()
    print("\n[학습 직전 X — cohort.X, 병합·이진화 완료] row/col 과 셀 값 분포")
    print(cohort_mat.to_string(index=False))
    cohort_mat.to_csv(TABLES / "doc_cohort_X_stats.csv", index=False)

    top_cols = cohort_matrix_top_columns(top_n=10)
    print("\n[학습 직전 X — 컬럼별 분산 상위 10개]")
    print(top_cols.to_string(index=False))
    top_cols.to_csv(TABLES / "doc_cohort_X_top10_columns.csv", index=False)

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
