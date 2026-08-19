"""Future Work 2 — Mutation signature(96-class) 표현 vs 유전자 단위 성능 비교.

`scripts/19_pathway_representation.py` 와 같은 설계다. 96개 SBS
signature feature 를 gene-level filter 대신 넣은 파이프라인으로 같은
random 5-fold 조건에서 성능을 비교한다.

signature 행렬은 fold 와 무관하게 미리 계산돼 있으므로(§13 무관,
`mutation_signature.py` docstring 참고) Pipeline 안에 변환 단계를 둘
필요 없이 고정 feature 로 바로 쓴다 — RareMutationFilter/
PathwayAggregator 자리에 아무것도 없이 StandardScaler 부터 시작.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

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
from src.labels.binarize import LabelBinarizer

TABLES = REPO_ROOT / "results" / "tables"
TARGETS = ("wgd", "cin", "loh")
SIG_PATH = REPO_ROOT / "data" / "depmap" / "sbs96_signature_matrix.parquet"


def build_pipeline(model_name: str):
    seed = load_config("experiment")["seed"]
    if model_name == "logistic":
        pipe = Pipeline([
            ("scale", StandardScaler()),
            ("clf", LogisticRegression(max_iter=2000, class_weight="balanced",
                                       random_state=seed)),
        ])
        grid = {"clf__C": [0.01, 0.1, 1.0]}
    elif model_name == "random_forest":
        pipe = Pipeline([
            ("clf", RandomForestClassifier(n_estimators=500,
                                           class_weight="balanced_subsample",
                                           n_jobs=-1, random_state=seed)),
        ])
        grid = {"clf__max_depth": [None, 8], "clf__min_samples_leaf": [1, 5]}
    else:
        raise ValueError(model_name)
    return pipe, grid


def run_signature_cv(X: pd.DataFrame, y_raw: pd.Series, groups: pd.Series,
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
                    "representation": "signature", "n_features": X.shape[1],
                    "best_params": str(search.best_params_)})
        rows.append(row)
        print(f"  fold {fold}: ROC-AUC {row['roc_auc']:.3f} | {search.best_params_}")

    return pd.DataFrame(rows)


def main() -> int:
    cohort = load_cohort()
    sig = pd.read_parquet(SIG_PATH).reindex(cohort.X.index)
    print(f"signature feature: {sig.shape[1]}개, 세포주 {sig.shape[0]}개\n")

    all_rows = []
    for model_name in ("logistic", "random_forest"):
        for target in TARGETS:
            print(f"--- {model_name} / {target.upper()} (signature 표현) ---")
            df = run_signature_cv(sig, cohort.y[target], cohort.groups, model_name, target)
            df.to_csv(TABLES / f"cv_signature_{model_name}_{target}.csv", index=False)
            all_rows.append(df)
            print(f"  평균 ROC-AUC {df.roc_auc.mean():.3f}\n")

    sig_summary = pd.concat(all_rows, ignore_index=True)
    sig_summary.to_csv(TABLES / "day24_signature_summary.csv", index=False)

    gene_level = pd.read_csv(TABLES / "day10_model_comparison.csv")
    print("[유전자 단위 vs Signature 단위] ROC-AUC (random 5-fold)")
    rows = []
    for model_name in ("logistic", "random_forest"):
        for target in TARGETS:
            sg = sig_summary[(sig_summary.model == model_name) &
                             (sig_summary.target == target)].roc_auc.mean()
            gl = gene_level[(gene_level.model == model_name) &
                            (gene_level.target == target)].roc_auc
            gl_val = gl.iloc[0] if not gl.empty else float("nan")
            rows.append({"target": target, "model": model_name,
                        "gene_level_auc": gl_val, "signature_auc": sg,
                        "차이": sg - gl_val})
    cmp_df = pd.DataFrame(rows)
    print(cmp_df.round(3).to_string(index=False))
    cmp_df.to_csv(TABLES / "day24_signature_vs_gene.csv", index=False)

    print("\n해석: signature 가 유전자 단위보다 높으면 mutation 발생 패턴")
    print("      자체에 유전자 정체성으로는 안 잡히는 신호가 있다는 뜻.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
