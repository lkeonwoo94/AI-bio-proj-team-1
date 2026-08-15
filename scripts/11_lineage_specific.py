"""암종 내부 학습·평가 (Day 13 후속).

Day 13 의 Leave-One-Lineage-Out 은 '다른 암종으로 배워서 이 암종을 맞히는가'
를 물었다. 여기서는 '이 암종 안에서만 배우면 맞힐 수 있는가' 를 묻는다.

두 결과를 비교하면 암종별 성능 편차가
  (a) 암종 간 전이(transfer)의 실패인지
  (b) 그 암종 자체에 예측 가능한 신호가 없어서인지
를 구분할 수 있다.

주의: CIN/LOH 의 high/low 기준은 각 training fold 안에서 계산되므로
암종 내부 분석에서는 '그 암종 안에서의 상대적 high/low' 가 된다.
LOLO 결과와 직접 비교할 때 WGD(이진 label)만 완전히 동일한 기준이다.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from src.config import REPO_ROOT
from src.cv.nested import run_nested_cv
from src.data.merge import load_cohort
from src.labels.binarize import LabelBinarizer
from src.models.zoo import get_model
from src.selection.aggregate import aggregate_selection

TABLES = REPO_ROOT / "results" / "tables"
TARGETS = ("wgd", "cin", "loh")


def eligible(cohort, min_n: int, min_minority: int) -> list[str]:
    """암종 내부 학습이 가능한 lineage.

    표본 수와 함께 WGD 소수 클래스 크기도 본다. WGD+ 가 95% 인 암종은
    음성이 몇 개 없어 내부 CV 자체가 성립하지 않는다.
    """
    out = []
    counts = cohort.groups.value_counts()
    for lineage, n in counts.items():
        if n < min_n:
            continue
        y = cohort.y.loc[cohort.groups == lineage, "wgd"]
        minority = int(min(y.sum(), len(y) - y.sum()))
        if minority < min_minority:
            print(f"  {lineage}: n={n} 이지만 WGD 소수 클래스 {minority}개 — 제외")
            continue
        out.append(lineage)
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="random_forest")
    p.add_argument("--min-n", type=int, default=60)
    p.add_argument("--min-minority", type=int, default=12)
    p.add_argument("--outer-folds", type=int, default=5)
    p.add_argument("--inner-folds", type=int, default=3)
    p.add_argument("--n-jobs", type=int, default=-1)
    p.add_argument(
        "--label-threshold", default="internal", choices=("internal", "external"),
        help=("internal: 암종 내부 fold 에서 CIN/LOH threshold 계산 "
              "(그 암종 안에서의 상대적 high/low). "
              "external: 다른 암종들로 threshold 를 계산해 LOLO 와 같은 정의를 사용. "
              "해당 암종 데이터를 보지 않으므로 누출이 아니다."),
    )
    args = p.parse_args()

    spec = get_model(args.model)
    cohort = load_cohort()

    print(f"[{spec.name}] 암종 내부 nested CV "
          f"(outer {args.outer_folds} / inner {args.inner_folds})\n")
    lineages = eligible(cohort, args.min_n, args.min_minority)
    print(f"\n대상 {len(lineages)}종: {', '.join(lineages)}\n")

    rows, sel_rows = [], []
    for lineage in lineages:
        mask = (cohort.groups == lineage).to_numpy()
        Xl, yl, gl = cohort.X[mask], cohort.y[mask], cohort.groups[mask]
        print(f"--- {lineage} (n={int(mask.sum())}) ---")

        for target in TARGETS:
            external = args.label_threshold == "external"
            if external:
                # 해당 암종을 제외한 나머지로 threshold 를 정한다.
                # 이 암종의 값은 전혀 보지 않으므로 누출이 아니며,
                # LOLO 와 동일한 label 정의가 된다.
                outside = cohort.y.loc[~mask, target]
                y_series = LabelBinarizer(target).fit(outside).transform(yl[target])
            else:
                y_series = yl[target]
            yb = y_series.astype(int) if external else LabelBinarizer(target).fit_transform(y_series)
            minority = int(min(yb.sum(), len(yb) - yb.sum()))
            if minority < args.min_minority:
                print(f"  {target}: 소수 클래스 {minority}개 — 건너뜀")
                continue

            res = run_nested_cv(
                Xl, y_series, gl, spec, target, scheme="random",
                n_jobs=args.n_jobs, verbose=False,
                outer_folds=args.outer_folds, inner_folds=args.inner_folds,
                pre_binarized=external,
            )
            if res.metrics.empty:
                continue

            m = res.metrics
            rows.append({
                "lineage": lineage, "target": target, "n": int(mask.sum()),
                "roc_auc": m.roc_auc.mean(), "roc_auc_std": m.roc_auc.std(),
                "pr_auc": m.pr_auc.mean(),
                "balanced_accuracy": m.balanced_accuracy.mean(),
                "positive_rate": float(yb.mean()), "n_minority": minority,
            })
            print(f"  {target}: ROC-AUC {m.roc_auc.mean():.3f} "
                  f"(±{m.roc_auc.std():.3f}) | 양성 {yb.mean():.1%}")

            if not res.importances.empty:
                agg = aggregate_selection(res.importances, top_k=20).head(20)
                agg.insert(0, "lineage", lineage)
                agg.insert(1, "target", target)
                sel_rows.append(agg)
        print()

    if not rows:
        raise SystemExit("실행된 조합이 없습니다.")

    within = pd.DataFrame(rows)
    suffix = f"{spec.name}_{args.label_threshold}"
    within.to_csv(TABLES / f"day13b_within_lineage_{suffix}.csv", index=False)

    # --- LOLO(암종 간 전이) 결과와 비교 ---
    lolo_frames = []
    for target in TARGETS:
        f = TABLES / f"cv_lolo_elastic_net_{target}.csv"
        if f.exists():
            d = pd.read_csv(f)[["held_out_lineage", "roc_auc"]]
            d["target"] = target
            lolo_frames.append(d.rename(columns={"held_out_lineage": "lineage",
                                                 "roc_auc": "roc_auc_lolo"}))
    print("=" * 64)
    if lolo_frames:
        lolo = pd.concat(lolo_frames, ignore_index=True)
        cmp_ = within.merge(lolo, on=["lineage", "target"], how="left")
        cmp_["차이"] = cmp_.roc_auc - cmp_.roc_auc_lolo
        cmp_.to_csv(TABLES / f"day13b_within_vs_lolo_{suffix}.csv", index=False)

        print("[암종 내부 학습 vs 암종 간 전이(LOLO)] ROC-AUC\n")
        for target in TARGETS:
            sub = cmp_[cmp_.target == target].sort_values("차이", ascending=False)
            if sub.empty:
                continue
            print(f"  {target.upper()}")
            for _, r in sub.iterrows():
                print(f"    {r.lineage:26s} 내부 {r.roc_auc:.3f} | "
                      f"LOLO {r.roc_auc_lolo:.3f} | {r['차이']:+.3f}")
            print(f"    {'평균':26s} 내부 {sub.roc_auc.mean():.3f} | "
                  f"LOLO {sub.roc_auc_lolo.mean():.3f} | "
                  f"{sub['차이'].mean():+.3f}\n")

    if sel_rows:
        sel = pd.concat(sel_rows, ignore_index=True)
        sel.to_csv(TABLES / f"day13b_lineage_panels_{suffix}.csv", index=False)
        print(f"암종별 상위 유전자 저장: day13b_lineage_panels_{suffix}.csv")

    print(f"\n저장: day13b_*_{suffix}.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
