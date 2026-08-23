"""Day 44 — mutation UMAP 좌표 계산 (psh03 탐색 분석 adapt).

원본: docs/research/2026-08-22/depmap_viz/시각화 코드_1.py (팀원 psh03 제공).
빈도 상위 mutation feature로 UMAP(jaccard metric) 좌표를 계산해 WGD/CIN/LOH
상태를 겹쳐 볼 수 있게 한다 — outcome 기반 selection 이 아닌 탐색적 분석이며,
nested-CV 성능 추정치를 대체하지 않는다.

umap-learn 이 필요하다: `uv pip install umap-learn`.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

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


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--min-prevalence", type=float, default=0.01)
    p.add_argument("--umap-features", type=int, default=80,
                    help="UMAP에 쓸 빈도 상위 mutation 개수")
    args = p.parse_args()

    try:
        import umap.umap_ as umap
    except ImportError as exc:
        raise SystemExit("umap-learn이 필요합니다: uv pip install umap-learn") from exc

    cohort = load_cohort()
    prevalence = cohort.X.mean(axis=0)
    keep = prevalence[prevalence >= args.min_prevalence].sort_values(ascending=False)
    top_features = keep.index[:args.umap_features]
    X_umap = cohort.X.loc[:, top_features]
    labels = label_matrix(cohort.y)

    # 하나의 좌표계를 세 표현형이 공유해야 fig23 패널 세 개를 나란히 비교할 수 있다.
    reducer = umap.UMAP(n_neighbors=20, min_dist=0.25, metric="jaccard", random_state=42)
    coords = reducer.fit_transform(X_umap.to_numpy(dtype=bool))

    out = pd.DataFrame({"UMAP1": coords[:, 0], "UMAP2": coords[:, 1]}, index=cohort.X.index)
    for target in TARGETS:
        out[target] = labels[target].values
    out.to_csv(TABLES / "day44_mutation_umap_coords.csv", index=True)

    print(f"UMAP feature: {X_umap.shape[1]}개 (prevalence >= {args.min_prevalence:.1%} 중 상위)")
    print(f"저장: day44_mutation_umap_coords.csv ({out.shape[0]}개 모델)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
