"""Day 46 — mutation ↔ 유전체 불안정성 공유 축(CCA) (psh03 탐색 분석 adapt).

원본: docs/research/2026-08-22/depmap_viz/시각화 코드_1.py, 이미지_subplot
코드_2.py (팀원 psh03 제공). SVD로 sparse mutation을 축소한 뒤 WGD/CIN/LOH와
CCA(canonical correlation)를 본다 — 탐색적 분석이며 nested-CV 대체가 아니다.

이진화 라벨(원본 방식: WGD 그대로, CIN/LOH median split)과 연속값 라벨 두
버전을 모두 계산해 Figure 24에서 비교한다.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from sklearn.cross_decomposition import CCA
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import StandardScaler

from src.config import REPO_ROOT
from src.data.merge import load_cohort

TABLES = REPO_ROOT / "results" / "tables"
TARGETS = ("wgd", "cin", "loh")


def label_matrix(y: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=y.index)
    out["wgd"] = y["wgd"].astype(int)
    for target in ("cin", "loh"):
        out[target] = (y[target] >= y[target].median()).astype(int)
    return out


def run_cca(mutation_scaled: np.ndarray, Y_raw: np.ndarray, n_components: int) -> tuple[np.ndarray, np.ndarray, list[float]]:
    Y_scaled = StandardScaler().fit_transform(Y_raw)
    cca = CCA(n_components=n_components, max_iter=2000)
    U, V = cca.fit_transform(mutation_scaled, Y_scaled)
    correlations = [float(np.corrcoef(U[:, i], V[:, i])[0, 1]) for i in range(n_components)]
    return U, V, correlations


def main() -> int:
    cohort = load_cohort()
    labels = label_matrix(cohort.y)

    n_components = min(3, len(TARGETS))
    n_svd = min(20, cohort.X.shape[1] - 1, cohort.X.shape[0] - 1)
    mutation_scores = TruncatedSVD(n_components=n_svd, random_state=42).fit_transform(cohort.X)
    mutation_scaled = StandardScaler().fit_transform(mutation_scores)

    Y_bin = labels[list(TARGETS)].to_numpy()
    U_bin, V_bin, corr_bin = run_cca(mutation_scaled, Y_bin, n_components)

    Y_cont = cohort.y[list(TARGETS)].to_numpy()
    U_cont, V_cont, corr_cont = run_cca(mutation_scaled, Y_cont, 1)

    result = pd.DataFrame({
        "canonical_component": np.arange(1, n_components + 1),
        "correlation_binarized": corr_bin,
    })
    result.loc[0, "correlation_continuous_component1"] = corr_cont[0]
    result.to_csv(TABLES / "day46_cca.csv", index=False)

    coords = pd.DataFrame(index=cohort.X.index)
    for i in range(n_components):
        coords[f"U_bin_{i + 1}"] = U_bin[:, i]
        coords[f"V_bin_{i + 1}"] = V_bin[:, i]
    coords["U_cont_1"] = U_cont[:, 0]
    coords["V_cont_1"] = V_cont[:, 0]
    coords.to_csv(TABLES / "day46_cca_coordinates.csv", index=True)

    print("CCA correlations (이진화):", ", ".join(f"{c:.3f}" for c in corr_bin))
    print(f"CCA correlation (연속값, component 1): {corr_cont[0]:.3f}")
    print("저장: day46_cca.csv, day46_cca_coordinates.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
