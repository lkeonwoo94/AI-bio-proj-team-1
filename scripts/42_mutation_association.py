"""Day 42 — mutation × 표현형 연관성 검정 (psh03 탐색 분석 adapt).

원본: docs/research/2026-08-22/depmap_viz/시각화 코드_1.py (팀원 psh03 제공,
D:\\범부처 환경에서 별도 cohort 캐시로 실행). 이 저장소의 `load_cohort()` /
`use_style()` / `save()` 규약에 맞춰 다시 작성했다.

outcome/model 기반 feature selection 없이 mutation *빈도*만으로 필터링한
전체 코호트 탐색적 분석이다 — nested-CV 성능 추정치(day10_model_comparison.csv
등)를 대체하지 않는다. CIN/LOH 는 전체 코호트 중앙값 기준 high/low 로 이진화해
검정에만 쓴다(§13 원칙과 무관 — 이 스크립트는 outer/inner CV 를 쓰지 않는다).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, fisher_exact

from src.config import REPO_ROOT
from src.data.merge import load_cohort

TABLES = REPO_ROOT / "results" / "tables"
TARGETS = ("wgd", "cin", "loh")


def bh_fdr(p_values: pd.Series) -> pd.Series:
    """Benjamini-Hochberg FDR q-value (외부 statsmodels 의존성 없음)."""
    p = p_values.to_numpy(dtype=float)
    order = np.argsort(p)
    ranked = p[order] * len(p) / np.arange(1, len(p) + 1)
    ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    q = np.empty_like(ranked)
    q[order] = np.minimum(ranked, 1.0)
    return pd.Series(q, index=p_values.index)


def label_matrix(y: pd.DataFrame) -> pd.DataFrame:
    """WGD는 원래 binary, CIN/LOH는 전체 코호트 중앙값으로 탐색용 이진화."""
    out = pd.DataFrame(index=y.index)
    out["wgd"] = y["wgd"].astype(int)
    for target in ("cin", "loh"):
        out[target] = (y[target] >= y[target].median()).astype(int)
    return out


def filter_by_frequency(X: pd.DataFrame, min_prevalence: float) -> pd.DataFrame:
    prevalence = X.mean(axis=0)
    keep = prevalence[prevalence >= min_prevalence].sort_values(ascending=False)
    if keep.empty:
        raise ValueError(f"최소 변이 빈도 {min_prevalence:.3%}를 통과한 feature가 없습니다.")
    return X.loc[:, keep.index]


def association_tests(X: pd.DataFrame, labels: pd.DataFrame, target: str) -> pd.DataFrame:
    """feature × binary phenotype의 Fisher/chi-square, OR와 95% CI, BH-FDR."""
    rows = []
    outcome = labels[target].to_numpy()
    for feature in X.columns:
        mutation = X[feature].to_numpy().astype(int)
        a = int(((mutation == 1) & (outcome == 1)).sum())
        b = int(((mutation == 1) & (outcome == 0)).sum())
        c = int(((mutation == 0) & (outcome == 1)).sum())
        d = int(((mutation == 0) & (outcome == 0)).sum())
        table = np.array([[a, b], [c, d]])
        expected = chi2_contingency(table, correction=False).expected_freq
        if (expected < 5).any():
            odds_ratio, p_value = fisher_exact(table)
            test = "Fisher exact"
        else:
            _, p_value, _, _ = chi2_contingency(table, correction=False)
            odds_ratio = (a * d) / (b * c) if b and c else np.inf
            test = "Chi-square"
        # 0 cell에서 OR/CI가 무한대가 되지 않도록 Haldane-Anscombe 보정.
        aa, bb, cc, dd = np.array([a, b, c, d], dtype=float) + 0.5
        log_or = np.log((aa * dd) / (bb * cc))
        se = np.sqrt(1 / aa + 1 / bb + 1 / cc + 1 / dd)
        rows.append({"feature": feature, "mutated_and_positive": a, "mutated_and_negative": b,
                     "unmutated_and_positive": c, "unmutated_and_negative": d, "test": test,
                     "odds_ratio": odds_ratio, "odds_ratio_ci_low": np.exp(log_or - 1.96 * se),
                     "odds_ratio_ci_high": np.exp(log_or + 1.96 * se), "p_value": p_value})
    result = pd.DataFrame(rows).sort_values("p_value").reset_index(drop=True)
    result["fdr_q_value"] = bh_fdr(result["p_value"])
    return result


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--min-prevalence", type=float, default=0.01,
                    help="원 mutation feature 유지 최소 비율 (기본 1%%)")
    args = p.parse_args()

    cohort = load_cohort()
    X = filter_by_frequency(cohort.X, args.min_prevalence)
    labels = label_matrix(cohort.y)
    print(f"빈도 필터 통과 feature: {X.shape[1]}개 (prevalence >= {args.min_prevalence:.1%})")

    for target in TARGETS:
        result = association_tests(X, labels, target)
        result.to_csv(TABLES / f"day42_association_{target}.csv", index=False)
        n_sig = int((result.fdr_q_value < 0.05).sum())
        print(f"[{target.upper()}] FDR < 0.05: {n_sig}개 / {len(result)}개 "
              f"(상위: {result.iloc[0].feature}, q={result.iloc[0].fdr_q_value:.2e})")

    print("\n저장: day42_association_{wgd,cin,loh}.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
