"""암종별 LOLO 성능 편차의 원인 후보 가설 검정 (§26⑤ 후속).

이미 기각된 두 가설(기저율 편차, 표본 크기)에 이어 세 가지를 추가로
검정한다. 전부 새로운 데이터 없이 cohort.X 와 기존 LOLO 결과만으로
계산 가능하다.

  1. TP53 변이율 — 가장 중요한 단일 유전자이므로, 그 lineage 안에서
     변이율이 극단적이면(0% 또는 100%) 그 유전자가 변별력을 잃는다는 가설
  2. mutation burden — 세포주당 평균 mutation 개수가 적으면 정보 자체가
     부족하다는 가설
  3. TP53 변이율의 극단성 — 1번을 0/1로부터의 거리로 재정의한 버전
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from src.config import REPO_ROOT
from src.data.merge import load_cohort

TABLES = REPO_ROOT / "results" / "tables"
TP53_COLS = ["TP53 (7157)_hotspot", "TP53 (7157)_damaging"]


def build_lineage_features(target: str = "wgd", model: str = "elastic_net") -> pd.DataFrame:
    cohort = load_cohort()
    lolo = pd.read_csv(TABLES / f"cv_lolo_{model}_{target}.csv")

    rows = []
    for lineage in lolo.held_out_lineage:
        mask = cohort.groups == lineage
        Xl = cohort.X[mask]
        tp53_rate = Xl[TP53_COLS].max(axis=1).mean()
        rows.append({
            "lineage": lineage,
            "n": int(mask.sum()),
            "tp53_rate": tp53_rate,
            "tp53_extremity": min(tp53_rate, 1 - tp53_rate),
            "mean_burden": Xl.sum(axis=1).mean(),
        })
    feat = pd.DataFrame(rows)
    return feat.merge(lolo[["held_out_lineage", "roc_auc"]],
                      left_on="lineage", right_on="held_out_lineage")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="elastic_net")
    args = p.parse_args()

    feat = build_lineage_features("wgd", args.model)

    tests = {
        "TP53 변이율": feat.tp53_rate,
        "mutation burden": feat.mean_burden,
        "TP53 변이율의 극단성(0/1에 가까움)": feat.tp53_extremity,
    }

    print(f"[{args.model} / WGD LOLO, {len(feat)}개 lineage]\n")
    for name, series in tests.items():
        r = spearmanr(series, feat.roc_auc)
        verdict = "유의함" if r.pvalue < 0.05 else "기각 (유의하지 않음)"
        print(f"  {name:32s} rho={r.statistic:+.3f}  p={r.pvalue:.3f}  -> {verdict}")

    print(f"\n검정력 참고: lineage {len(feat)}개로는 |rho|>0.4 정도는 되어야")
    print("  p<0.05 를 얻을 수 있다 — 통계적 검정력 자체가 낮다.")

    out = TABLES / f"day15_lineage_hypothesis_features_{args.model}.csv"
    feat.to_csv(out, index=False)
    print(f"\n저장: {out.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
