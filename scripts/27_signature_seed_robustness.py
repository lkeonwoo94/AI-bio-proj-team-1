"""Mutation signature 결과의 seed 재현성 확인 (한계 2번 후속).

`24_signature_representation.py` 의 "6개 조합 중 5개 개선"이 outer fold
구성(=seed)을 바꿔도 유지되는지 본다. 기본 seed(`configs/experiment.yaml`)
외에 2개를 더 써서 signature ROC-AUC 자체의 fold-seed 간 변동폭을 본다.

주의: 유전자 단위(gene-level) 쪽 baseline 은 이 실험에서 다시 돌리지
않는다 — `RareMutationFilter` 까지 포함한 전체 nested CV 를 seed 마다
다시 도는 것은 비용이 커서 범위 밖으로 뒀다. 따라서 여기서 보는 것은
"signature 성능 자체가 seed 에 얼마나 민감한가"이며, "signature > 유전자
단위"라는 방향성 자체의 seed 민감도까지 보장하지는 않는다 — 이 경계는
결과 절에 그대로 남긴다.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src.config import REPO_ROOT
from src.data.merge import load_cohort

TABLES = REPO_ROOT / "results" / "tables"
TARGETS = ("wgd", "cin", "loh")
SIG_PATH = REPO_ROOT / "data" / "depmap" / "sbs96_signature_matrix.parquet"
SEEDS = [0, 1, 2]  # 기본 seed(configs/experiment.yaml) 와 다른 값들


def _load_script24():
    spec = importlib.util.spec_from_file_location(
        "signature_representation", Path(__file__).parent / "24_signature_representation.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    mod = _load_script24()
    cohort = load_cohort()
    sig = pd.read_parquet(SIG_PATH).reindex(cohort.X.index)
    print(f"signature feature {sig.shape[1]}개, seed {SEEDS}\n")

    rows = []
    for model_name in ("logistic", "random_forest"):
        for target in TARGETS:
            for seed in SEEDS:
                print(f"--- {model_name} / {target.upper()} / seed={seed} ---")
                df = mod.run_signature_cv(sig, cohort.y[target], cohort.groups,
                                          model_name, target, seed=seed)
                mean_auc = df.roc_auc.mean()
                rows.append({"model": model_name, "target": target, "seed": seed,
                            "roc_auc": mean_auc})
                print(f"  평균 ROC-AUC {mean_auc:.3f}\n")

    result = pd.DataFrame(rows)
    result.to_csv(TABLES / "day27_signature_seed_robustness.csv", index=False)

    print("[seed 간 변동] 조합별 mean/std/range")
    summary = result.groupby(["model", "target"]).roc_auc.agg(["mean", "std", "min", "max"])
    summary["range"] = summary["max"] - summary["min"]
    print(summary.round(4).to_string())

    default = pd.read_csv(TABLES / "day24_signature_summary.csv") \
        .groupby(["model", "target"]).roc_auc.mean().rename("default_seed_auc")
    merged = summary.join(default)
    merged.to_csv(TABLES / "day27_signature_seed_robustness_summary.csv")
    print("\n[기본 seed 대비] default_seed_auc 가 3-seed 평균/범위 안에 드는지 확인")
    print(merged.round(4).to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
