"""패널 Jaccard 안정성이 왜 1.0 이 안 되는지 설명하는 보조 분석.

final_conclusion.md의 "Day 11/12 Random Forest 재검증 > 왜 1.0 이 안
되는가" 절의 수치를 재현한다. 08_panel_curve.py, 07_aggregate_selection.py
가 이미 만든 산출물을 다시 읽기만 하며 새로 CV 를 돌리지 않는다.
"""

from __future__ import annotations

import argparse
import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src.config import REPO_ROOT
from src.data.merge import load_cohort

TABLES = REPO_ROOT / "results" / "tables"
TARGETS = ("wgd", "cin", "loh")


def pairwise_overlap(model: str, panel_size: int = 10) -> pd.DataFrame:
    """fold 두 개를 비교했을 때 패널이 평균 몇 개나 겹치는지.

    Jaccard 는 겹치는 비율이라 직관이 잘 안 붙는다. '10개 중 몇 개 겹치는가'
    로 바꾸면 같은 정보를 훨씬 읽기 쉽게 전달한다.
    """
    picks = pd.read_csv(TABLES / f"day12_panel_picks_{model}.csv")
    rows = []
    for target in TARGETS:
        sub = picks[(picks.target == target) & (picks.panel_size == panel_size)]
        sets = [set(g.feature) for _, g in sub.groupby("fold")]
        overlaps = [len(a & b) for a, b in itertools.combinations(sets, 2)]
        rows.append({
            "target": target,
            "panel_size": panel_size,
            "avg_overlap": sum(overlaps) / len(overlaps) if overlaps else float("nan"),
            "n_fold_pairs": len(overlaps),
        })
    return pd.DataFrame(rows)


def importance_tail(model: str, target: str, top_n: int = 10) -> pd.DataFrame:
    """상위 유전자의 importance 가 얼마나 빨리 완만해지는지.

    순위 표준편차(rank_std)가 커지는 지점이 곧 '경계선에서 흔들리기
    시작하는 지점'이다.
    """
    path = TABLES / f"day11_selection_{model}_{target}.csv"
    d = pd.read_csv(path).sort_values("mean_rank").head(top_n)
    return d[["gene", "kind", "selection_freq", "mean_importance", "mean_rank", "rank_std"]]


def fold_overlap_fraction(outer_folds: int = 5) -> float:
    """서로 다른 outer fold 의 training set 이 얼마나 겹치는가.

    k-fold CV 에서 training set 크기는 n*(k-1)/k, 두 training set 의
    교집합은 n - 2*(n/k) 이므로 겹치는 비율은 (k-2)/(k-1) 로 수렴한다.
    mutation 이 희소한 상황에서는 이 나머지 부분(비겹침)이 경계선 유전자의
    순위를 흔드는 실질적 원인이 된다.
    """
    n = len(load_cohort())
    test = n // outer_folds
    train = n - test
    overlap = n - 2 * test
    return overlap / train


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="random_forest")
    p.add_argument("--panel-size", type=int, default=10)
    args = p.parse_args()

    print(f"[{args.model}] {args.panel_size}개 패널 — fold 쌍 평균 겹치는 유전자 수")
    overlap = pairwise_overlap(args.model, args.panel_size)
    print(overlap.to_string(index=False))

    print(f"\n[{args.model}] WGD 상위 {args.panel_size}개 — importance 꼬리")
    print(importance_tail(args.model, "wgd", args.panel_size).to_string(index=False))

    frac = fold_overlap_fraction()
    print(f"\nouter 5-fold 간 training set 중복률: {frac:.0%}")
    print("(mutation 이 희소하므로 나머지 비겹침 구간이 경계선 유전자 순위를 흔든다)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
