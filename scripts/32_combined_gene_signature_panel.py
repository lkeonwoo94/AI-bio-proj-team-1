"""유전자 + Mutation signature 결합 패널 (biomarker_panel.md 후속).

지금까지 유전자 단위(§26③④)와 signature 96-class(additional_results.md
§4 후속)는 **따로** 패널을 뽑았다. 이 스크립트는 둘을 **한 feature
공간에 합쳐** 같은 fold 안에서 함께 feature selection 을 시켜본다 —
"패널에 signature feature 를 섞으면 더 나아지는가"(08-16 Future Work 2
"한계" 항목, 08-19 남은 과제)에 대한 답이다.

설계:
  - 유전자 쪽은 `RareMutationFilter` 를 training fold 에서만 적합한다
    (§13 원칙 동일) — 다만 Pipeline 이 아니라 fold 루프 안에서 직접
    fit/transform 한다(신호 컬럼 이름을 signature 와 나란히 두기 위해).
  - signature 96개는 fold 와 무관한 고정 feature 라 그대로 hstack 한다
    (`scripts/26_signature_panel.py` 와 같은 근거).
  - 합친 feature 공간(유전자 필터 통과분 + signature 96개)에서 다시
    L1 로지스틱/RF 로 feature selection 을 하고, top-k 안에 유전자와
    signature class 가 각각 몇 개씩 뽑히는지를 기록한다.
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.config import REPO_ROOT, load_config
from src.cv.splitters import inner_cv, outer_splits
from src.data.merge import load_cohort
from src.evaluation.metrics import choose_threshold, evaluate
from src.features.filter import RareMutationFilter
from src.labels.binarize import LabelBinarizer
from src.selection.aggregate import aggregate_selection

TABLES = REPO_ROOT / "results" / "tables"
TARGETS = ("wgd", "cin", "loh")
TARGET_LABEL = {"wgd": "WGD", "cin": "CIN", "loh": "LOH"}
SIG_PATH = REPO_ROOT / "data" / "depmap" / "sbs96_signature_matrix.parquet"
SIZES = [10, 20, 30]

# 기존 baseline (재비교용, 각 스크립트에서 이미 계산된 값)
GENE_ONLY_AUC = {  # day10_model_comparison.csv, 필터 후 유전자 단위
    ("logistic_l1", "wgd"): 0.723, ("logistic_l1", "cin"): 0.672, ("logistic_l1", "loh"): 0.683,
    ("random_forest", "wgd"): 0.765, ("random_forest", "cin"): 0.734, ("random_forest", "loh"): 0.730,
}
SIG_ONLY_AUC = {  # day24_signature_summary.csv
    ("logistic_l1", "wgd"): 0.713, ("logistic_l1", "cin"): 0.711, ("logistic_l1", "loh"): 0.693,
    ("random_forest", "wgd"): 0.770, ("random_forest", "cin"): 0.762, ("random_forest", "loh"): 0.743,
}


def build_pipeline(model_name: str):
    seed = load_config("experiment")["seed"]
    if model_name == "logistic_l1":
        pipe = Pipeline([
            ("scale", StandardScaler()),
            ("clf", LogisticRegression(penalty="l1", solver="liblinear", max_iter=2000,
                                       class_weight="balanced", random_state=seed)),
        ])
        grid = {"clf__C": [0.05, 0.5, 1.0]}
        importance = "coef"
    elif model_name == "random_forest":
        pipe = Pipeline([
            ("clf", RandomForestClassifier(n_estimators=500, class_weight="balanced_subsample",
                                           n_jobs=1, random_state=seed)),
        ])
        grid = {"clf__max_depth": [None, 8], "clf__min_samples_leaf": [1, 5]}
        importance = "tree"
    else:
        raise ValueError(model_name)
    return pipe, grid, importance


def _extract_importance(fitted_pipe, kind: str) -> np.ndarray:
    clf = fitted_pipe.named_steps["clf"]
    if kind == "coef":
        return np.abs(np.asarray(clf.coef_).ravel())
    return np.asarray(clf.feature_importances_)


def run_combined_panel(gene_X: pd.DataFrame, sig: pd.DataFrame, y_raw: pd.Series,
                       groups: pd.Series, model_name: str, target: str, n_jobs: int = 1):
    gene_names_all = np.asarray(gene_X.columns)
    sig_names = np.asarray([f"SIG:{c}" for c in sig.columns])
    gene_values = gene_X.to_numpy()
    sig_values = sig.to_numpy()
    y_strat = LabelBinarizer(target).fit_transform(y_raw)
    cfg = load_config("experiment")["features"]

    metric_rows, comp_rows, importance_rows = [], [], []

    for fold, (tr, te) in enumerate(outer_splits(y_strat.to_numpy(), groups, scheme="random")):
        binz = LabelBinarizer(target).fit(y_raw.iloc[tr])
        y_tr = binz.transform(y_raw.iloc[tr]).to_numpy()
        y_te = binz.transform(y_raw.iloc[te]).to_numpy()

        # 유전자 쪽만 training fold 기준으로 희귀 변이 제거 (§13)
        gene_filter = RareMutationFilter(min_count=cfg["min_mutation_count"],
                                         min_freq=cfg["min_mutation_freq"])
        gene_filter.fit(gene_values[tr])
        gene_tr = gene_filter.transform(gene_values[tr])
        gene_te = gene_filter.transform(gene_values[te])
        kept_gene_names = gene_names_all[gene_filter.get_support()]

        X_tr = np.hstack([gene_tr, sig_values[tr]])
        X_te = np.hstack([gene_te, sig_values[te]])
        feature_names = np.concatenate([kept_gene_names, sig_names])

        pipe, grid, importance_kind = build_pipeline(model_name)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ConvergenceWarning)
            search = GridSearchCV(pipe, grid, scoring="roc_auc", cv=inner_cv(),
                                  n_jobs=n_jobs, refit=True)
            search.fit(X_tr, y_tr)
        best = search.best_estimator_

        oof = cross_val_predict(best, X_tr, y_tr, cv=inner_cv(),
                                method="predict_proba", n_jobs=n_jobs)[:, 1]
        thr = choose_threshold(y_tr, oof)
        row = evaluate(y_te, best.predict_proba(X_te)[:, 1], threshold=thr)
        row.update({"fold": fold, "panel_size": "all", "target": target, "model": model_name,
                    "n_genes": len(kept_gene_names), "n_sig": len(sig_names)})
        metric_rows.append(row)

        imp = _extract_importance(best, importance_kind)
        importance_rows.append(pd.DataFrame({"fold": fold, "feature": feature_names, "importance": imp}))
        order = np.argsort(imp)[::-1]

        for k in SIZES:
            top_idx = order[:k]
            picked = feature_names[top_idx]
            n_sig_picked = int(sum(f.startswith("SIG:") for f in picked))
            n_gene_picked = k - n_sig_picked
            comp_rows.append({"fold": fold, "panel_size": k, "target": target, "model": model_name,
                             "n_genes": n_gene_picked, "n_sig": n_sig_picked,
                             "genes": ", ".join(g.split(" (")[0] for g in picked if not g.startswith("SIG:")),
                             "sig_classes": ", ".join(g[4:] for g in picked if g.startswith("SIG:"))})

            cols = np.flatnonzero(np.isin(feature_names, picked))
            Xk_tr, Xk_te = X_tr[:, cols], X_te[:, cols]

            pipe_k, grid_k, _ = build_pipeline(model_name)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", ConvergenceWarning)
                search_k = GridSearchCV(pipe_k, grid_k, scoring="roc_auc", cv=inner_cv(),
                                        n_jobs=n_jobs, refit=True)
                search_k.fit(Xk_tr, y_tr)
            best_k = search_k.best_estimator_
            oof_k = cross_val_predict(best_k, Xk_tr, y_tr, cv=inner_cv(),
                                      method="predict_proba", n_jobs=n_jobs)[:, 1]
            thr_k = choose_threshold(y_tr, oof_k)
            row_k = evaluate(y_te, best_k.predict_proba(Xk_te)[:, 1], threshold=thr_k)
            row_k.update({"fold": fold, "panel_size": k, "target": target, "model": model_name,
                         "n_genes": n_gene_picked, "n_sig": n_sig_picked})
            metric_rows.append(row_k)

        got = {r["panel_size"]: r["roc_auc"] for r in metric_rows if r["fold"] == fold}
        print(f"  fold {fold}: " + " | ".join(f"{k}:{v:.3f}" for k, v in got.items()) +
              f" | 유전자 {len(kept_gene_names)}개 필터 통과")

    metrics = pd.DataFrame(metric_rows)
    comp = pd.DataFrame(comp_rows)
    importances = pd.concat(importance_rows, ignore_index=True)
    return metrics, comp, importances


def main() -> int:
    cohort = load_cohort()
    sig = pd.read_parquet(SIG_PATH).reindex(cohort.X.index)
    print(f"[유전자+signature 결합 패널] 유전자 {cohort.X.shape[1]}개(필터 전), "
          f"signature {sig.shape[1]}개, 세포주 {cohort.X.shape[0]}개\n")

    all_metrics, all_comp = [], []

    for model_name in ("logistic_l1", "random_forest"):
        for target in TARGETS:
            print(f"--- {model_name} / {TARGET_LABEL[target]} ---")
            metrics, comp, importances = run_combined_panel(
                cohort.X, sig, cohort.y[target], cohort.groups, model_name, target)
            all_metrics.append(metrics)
            all_comp.append(comp)

            agg = aggregate_selection(importances, top_k=30)
            agg.to_csv(TABLES / f"day32_combined_selection_{model_name}_{target}.csv", index=False)

            mean = metrics.groupby("panel_size").roc_auc.mean()
            full_combined = mean.get("all")
            gene_only = GENE_ONLY_AUC[(model_name, target)]
            sig_only = SIG_ONLY_AUC[(model_name, target)]
            print(f"  전체 결합 {full_combined:.3f} | 유전자만 {gene_only:.3f} "
                  f"({full_combined - gene_only:+.3f}) | signature만 {sig_only:.3f} "
                  f"({full_combined - sig_only:+.3f})")
            for k in SIZES:
                comp_k = comp[comp.panel_size == k]
                print(f"  {k}개 패널 평균 구성: 유전자 {comp_k.n_genes.mean():.1f}개, "
                      f"signature {comp_k.n_sig.mean():.1f}개")
            print()

    metrics = pd.concat(all_metrics, ignore_index=True)
    metrics["panel_size"] = metrics["panel_size"].astype(str)
    comp = pd.concat(all_comp, ignore_index=True)

    metrics.to_csv(TABLES / "day32_combined_panel_metrics.csv", index=False)
    comp.to_csv(TABLES / "day32_combined_panel_composition.csv", index=False)

    print("[전체 결합 vs 단일 축] ROC-AUC")
    rows = []
    for model_name in ("logistic_l1", "random_forest"):
        for target in TARGETS:
            full = metrics[(metrics.model == model_name) & (metrics.target == target) &
                          (metrics.panel_size == "all")].roc_auc.mean()
            rows.append({"model": model_name, "target": target, "결합": full,
                        "유전자만": GENE_ONLY_AUC[(model_name, target)],
                        "signature만": SIG_ONLY_AUC[(model_name, target)]})
    summary = pd.DataFrame(rows)
    summary["결합-유전자"] = summary["결합"] - summary["유전자만"]
    summary["결합-signature"] = summary["결합"] - summary["signature만"]
    summary.to_csv(TABLES / "day32_combined_vs_single_summary.csv", index=False)
    print(summary.round(3).to_string(index=False))

    print("\n[패널 크기별 구성] 평균 유전자/signature 개수")
    print(comp.groupby(["model", "target", "panel_size"])[["n_genes", "n_sig"]].mean().round(1).to_string())

    print("\n저장: day32_combined_selection_{model}_{target}.csv, "
          "day32_combined_panel_{metrics,composition}.csv, day32_combined_vs_single_summary.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
