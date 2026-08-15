"""Day 5-9 — nested CV 실행.

사용 예:
    python scripts/05_run_cv.py --model logistic
    python scripts/05_run_cv.py --model elastic_net --target wgd
    python scripts/05_run_cv.py --model xgboost --scheme group
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src.config import REPO_ROOT, load_config
from src.cv.nested import run_nested_cv
from src.data.merge import load_cohort
from src.evaluation.metrics import METRIC_COLUMNS
from src.models.zoo import get_model

TABLES = REPO_ROOT / "results" / "tables"
TARGETS = ("wgd", "cin", "loh")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model", required=True, help="logistic | elastic_net | random_forest | xgboost | multitask_ann")
    p.add_argument("--target", default="all", help="wgd | cin | loh | all")
    p.add_argument("--scheme", default="random", help="random | group | lolo")
    p.add_argument("--n-jobs", type=int, default=-1)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    targets = TARGETS if args.target == "all" else (args.target,)
    spec = get_model(args.model)
    cohort = load_cohort()
    TABLES.mkdir(parents=True, exist_ok=True)

    print(f"[{spec.name}] scheme={args.scheme} | {cohort.summary()}")
    cfg = load_config("experiment")["cv"]
    print(f"outer {cfg['outer_folds']}-fold / inner {cfg['inner_folds']}-fold\n")

    all_metrics = []
    for target in targets:
        print(f"--- {target.upper()} ---")
        t0 = time.time()
        result = run_nested_cv(
            X=cohort.X, y_raw=cohort.y[target], groups=cohort.groups,
            spec=spec, target=target, scheme=args.scheme, n_jobs=args.n_jobs,
        )
        elapsed = time.time() - t0

        if result.metrics.empty:
            print("  유효한 fold 없음\n")
            continue

        mean = result.metrics[METRIC_COLUMNS].mean()
        std = result.metrics[METRIC_COLUMNS].std()
        print(f"  평균 ROC-AUC {mean.roc_auc:.3f} (±{std.roc_auc:.3f}) | "
              f"PR-AUC {mean.pr_auc:.3f} | BA {mean.balanced_accuracy:.3f} | "
              f"{elapsed:.0f}초\n")

        stem = f"{args.scheme}_{spec.name}_{target}"
        result.metrics.to_csv(TABLES / f"cv_{stem}.csv", index=False)
        if not result.importances.empty:
            result.importances.to_csv(TABLES / f"selection_{stem}.csv", index=False)
        all_metrics.append(result.metrics)

    if all_metrics:
        combined = pd.concat(all_metrics, ignore_index=True)
        summary = combined.groupby("target")[METRIC_COLUMNS].mean().round(3)
        print("[요약]")
        print(summary.to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
