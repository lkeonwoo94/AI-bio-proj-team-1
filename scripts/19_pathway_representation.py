"""Future Work 1 — Pathway 단위 mutation burden vs 유전자 단위 성능 비교.

20,132개 유전자 컬럼을 11개 pathway(hotspot/damaging 분리 시 최대 22개)
로 접었을 때, 유전자 단위(RareMutationFilter, 필터 후 ~2,000개)와 같은
random 5-fold 조건에서 성능이 어떻게 달라지는지 비교한다.

`src/cv/nested.py` 를 그대로 재사용하지 않는다 — 그 함수는
`RareMutationFilter` 전용 API(get_support, n_features_out_)를 가정하고
feature 중요도를 유전자 이름으로 기록하는데, pathway 표현은 출력 feature
자체가 원본 유전자와 다른 이름 공간이라 그 가정이 깨진다. 안전하게 이
비교만을 위한 가벼운 루프를 새로 짠다 — 재사용 대신 격리를 택했다.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.config import REPO_ROOT, load_config
from src.cv.splitters import inner_cv, outer_splits
from src.data.merge import load_cohort
from src.evaluation.metrics import choose_threshold, evaluate
from src.features.pathway_aggregate import PathwayAggregator, load_genesets
from src.labels.binarize import LabelBinarizer

TABLES = REPO_ROOT / "results" / "tables"
TARGETS = ("wgd", "cin", "loh")


def build_pipeline(model_name: str) -> tuple[Pipeline, dict]:
    seed = load_config("experiment")["seed"]
    if model_name == "logistic":
        pipe = Pipeline([
            ("pathway", PathwayAggregator()),
            ("scale", StandardScaler()),
            ("clf", LogisticRegression(max_iter=2000, class_weight="balanced",
                                       random_state=seed)),
        ])
        grid = {"clf__C": [0.01, 0.1, 1.0]}
    elif model_name == "random_forest":
        pipe = Pipeline([
            ("pathway", PathwayAggregator()),
            ("clf", RandomForestClassifier(n_estimators=500,
                                           class_weight="balanced_subsample",
                                           n_jobs=-1, random_state=seed)),
        ])
        grid = {"clf__max_depth": [None, 8], "clf__min_samples_leaf": [1, 5]}
    else:
        raise ValueError(model_name)
    return pipe, grid


def run_pathway_cv(X: pd.DataFrame, y_raw: pd.Series, groups: pd.Series,
                   model_name: str, target: str, n_jobs: int = -1) -> pd.DataFrame:
    y_strat = LabelBinarizer(target).fit_transform(y_raw)
    rows = []

    for fold, (tr, te) in enumerate(outer_splits(y_strat.to_numpy(), groups, scheme="random")):
        binz = LabelBinarizer(target).fit(y_raw.iloc[tr])
        y_tr = binz.transform(y_raw.iloc[tr]).to_numpy()
        y_te = binz.transform(y_raw.iloc[te]).to_numpy()

        X_tr, X_te = X.iloc[tr], X.iloc[te]
        pipe, grid = build_pipeline(model_name)

        search = GridSearchCV(pipe, grid, scoring="roc_auc", cv=inner_cv(),
                              n_jobs=n_jobs, refit=True)
        search.fit(X_tr, y_tr)
        best = search.best_estimator_

        oof = cross_val_predict(best, X_tr, y_tr, cv=inner_cv(),
                                method="predict_proba", n_jobs=n_jobs)[:, 1]
        threshold = choose_threshold(y_tr, oof)

        prob_te = best.predict_proba(X_te)[:, 1]
        row = evaluate(y_te, prob_te, threshold=threshold)
        row.update({"fold": fold, "model": model_name, "target": target,
                    "representation": "pathway",
                    "n_features": len(best.named_steps["pathway"].pathway_names_),
                    "best_params": str(search.best_params_)})
        rows.append(row)
        print(f"  fold {fold}: ROC-AUC {row['roc_auc']:.3f} | feature {row['n_features']} "
              f"| {search.best_params_}")

    return pd.DataFrame(rows)


def main() -> int:
    cohort = load_cohort()
    genesets = load_genesets()
    print(f"Pathway 표현: {len(genesets)}개 gene set (hotspot/damaging 분리 시 최대 "
          f"{len(genesets) * 2}개 feature)\n")

    all_rows = []
    for model_name in ("logistic", "random_forest"):
        for target in TARGETS:
            print(f"--- {model_name} / {target.upper()} (pathway 표현) ---")
            df = run_pathway_cv(cohort.X, cohort.y[target], cohort.groups, model_name, target)
            df.to_csv(TABLES / f"cv_pathway_{model_name}_{target}.csv", index=False)
            all_rows.append(df)
            print(f"  평균 ROC-AUC {df.roc_auc.mean():.3f}\n")

    pathway_summary = pd.concat(all_rows, ignore_index=True)
    pathway_summary.to_csv(TABLES / "day19_pathway_summary.csv", index=False)

    # 유전자 단위(기존 day10 결과)와 나란히 비교
    gene_level = pd.read_csv(TABLES / "day10_model_comparison.csv")
    print("[유전자 단위 vs Pathway 단위] ROC-AUC (random 5-fold)")
    rows = []
    for model_name, gene_model in (("logistic", "logistic"), ("random_forest", "random_forest")):
        for target in TARGETS:
            pw = pathway_summary[(pathway_summary.model == model_name) &
                                 (pathway_summary.target == target)].roc_auc.mean()
            gl = gene_level[(gene_level.model == gene_model) &
                            (gene_level.target == target)].roc_auc
            gl_val = gl.iloc[0] if not gl.empty else float("nan")
            rows.append({"target": target, "model": model_name,
                        "gene_level_auc": gl_val, "pathway_auc": pw,
                        "차이": pw - gl_val})
    cmp_df = pd.DataFrame(rows)
    print(cmp_df.round(3).to_string(index=False))
    cmp_df.to_csv(TABLES / "day19_pathway_vs_gene.csv", index=False)

    print("\n해석: pathway 가 유전자 단위보다 높으면 sparsity 완화가 이득,")
    print("      낮거나 비슷하면 pathway 집계가 오히려 세부 신호를 뭉갠 것.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
