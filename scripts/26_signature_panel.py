"""Mutation signature(96-class) 최소 패널 (한계 3번 후속).

`docs/research/2026-08-19/additional_results.md` §4 의 열린 질문 —
"96개 signature feature 로도 반복 selection·최소 패널을 뽑을 수 있는가"
— 에 답한다. 유전자 단위 Day 11/12(`07_aggregate_selection.py`,
`08_panel_curve.py`)와 같은 논리(training fold 안에서만 패널을 고른다,
§13)를 signature 96개에 적용한다.

`scripts/24_signature_representation.py` 와 마찬가지로 signature 행렬은
fold 와 무관하게 고정이라 `RareMutationFilter` 가 필요 없다 — 그래서
`src/panel/curve.py` 를 그대로 재사용하지 않고(그 함수는
`named_steps["filter"]` 를 가정) 격리된 로컬 파이프라인/루프를 쓴다.

패널 크기는 5/10/20/30 — 전체가 96개뿐이라 유전자 패널의 50 은
과반이라 의미가 옅어 30 으로 낮췄다.
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
from src.labels.binarize import LabelBinarizer
from src.panel.curve import jaccard_across_folds, panel_stability
from src.selection.aggregate import aggregate_selection

TABLES = REPO_ROOT / "results" / "tables"
TARGETS = ("wgd", "cin", "loh")
TARGET_LABEL = {"wgd": "WGD", "cin": "CIN", "loh": "LOH"}
SIG_PATH = REPO_ROOT / "data" / "depmap" / "sbs96_signature_matrix.parquet"
SIZES = [5, 10, 20, 30]


def build_pipeline(model_name: str):
    """`24_signature_representation.py` 와 같은 모델 — 여기 로지스틱은
    L1(liblinear) 으로 바꿔 feature selection 이 되도록 한다(24 의
    로지스틱은 순수 L2 라 계수가 0 이 되지 않는다). saga+elasticnet 은
    96개 signature 컬럼이 세포주별로 합이 1(완전 다중공선성)이라 수렴이
    극단적으로 느려 liblinear+L1 로 바꿨다 — 두 방식 다 sparse selection
    을 만든다는 목적은 같다."""
    seed = load_config("experiment")["seed"]
    if model_name == "logistic_l1":
        pipe = Pipeline([
            ("scale", StandardScaler()),
            ("clf", LogisticRegression(penalty="l1", solver="liblinear",
                                       max_iter=2000,
                                       class_weight="balanced", random_state=seed)),
        ])
        grid = {"clf__C": [0.05, 0.5, 1.0]}
        importance = "coef"
    elif model_name == "random_forest":
        pipe = Pipeline([
            ("clf", RandomForestClassifier(n_estimators=500,
                                           class_weight="balanced_subsample",
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


def run_signature_panel(sig: pd.DataFrame, y_raw: pd.Series, groups: pd.Series,
                        model_name: str, target: str, n_jobs: int = 1):
    # n_jobs=1(기본): feature 96개 뿐이라 개별 fit 은 순식간이고, 오히려
    # outer fold 당 5번(all + 4 패널 크기)씩 GridSearchCV 를 새로 열 때마다
    # loky 프로세스 풀을 매번 새로 띄우는 오버헤드가 실제 연산보다 훨씬 크다
    # — 그래서 병렬화를 끄는 쪽이 더 빠르다.
    feature_names = np.asarray(sig.columns)
    X_values = sig.to_numpy()
    y_strat = LabelBinarizer(target).fit_transform(y_raw)

    metric_rows, pick_rows, importance_rows = [], [], []

    for fold, (tr, te) in enumerate(outer_splits(y_strat.to_numpy(), groups, scheme="random")):
        binz = LabelBinarizer(target).fit(y_raw.iloc[tr])
        y_tr = binz.transform(y_raw.iloc[tr]).to_numpy()
        y_te = binz.transform(y_raw.iloc[te]).to_numpy()
        X_tr, X_te = X_values[tr], X_values[te]

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
        row.update({"fold": fold, "panel_size": "all", "target": target, "model": model_name})
        metric_rows.append(row)

        imp = _extract_importance(best, importance_kind)
        importance_rows.append(pd.DataFrame({"fold": fold, "feature": feature_names, "importance": imp}))
        order = np.argsort(imp)[::-1]

        for k in SIZES:
            top_idx = order[:k]
            picked = feature_names[top_idx]
            cols = np.flatnonzero(np.isin(feature_names, picked))
            Xk_tr, Xk_te = X_values[np.ix_(tr, cols)], X_values[np.ix_(te, cols)]

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
            row_k.update({"fold": fold, "panel_size": k, "target": target, "model": model_name})
            metric_rows.append(row_k)
            pick_rows.append(pd.DataFrame({"fold": fold, "panel_size": k, "target": target,
                                           "model": model_name, "feature": picked}))

        got = {r["panel_size"]: r["roc_auc"] for r in metric_rows if r["fold"] == fold}
        print(f"  fold {fold}: " + " | ".join(f"{k}:{v:.3f}" for k, v in got.items()))

    metrics = pd.DataFrame(metric_rows)
    picks = pd.concat(pick_rows, ignore_index=True)
    importances = pd.concat(importance_rows, ignore_index=True)
    return metrics, picks, importances


def main() -> int:
    cohort = load_cohort()
    sig = pd.read_parquet(SIG_PATH).reindex(cohort.X.index)
    print(f"signature feature {sig.shape[1]}개, 세포주 {sig.shape[0]}개, "
          f"패널 크기 {SIZES} + 전체\n")

    all_metrics, all_picks, all_stab, all_sel = [], [], [], {}

    for model_name in ("logistic_l1", "random_forest"):
        for target in TARGETS:
            print(f"--- {model_name} / {TARGET_LABEL[target]} ---")
            metrics, picks, importances = run_signature_panel(
                sig, cohort.y[target], cohort.groups, model_name, target)
            all_metrics.append(metrics)
            all_picks.append(picks)

            # Day 11 analog: 전체(96개) 기준 fold 반복 selection 집계
            agg = aggregate_selection(importances, top_k=20)
            all_sel[f"{model_name}_{target}"] = agg
            agg.to_csv(TABLES / f"day26_signature_selection_{model_name}_{target}.csv", index=False)

            mean = metrics.groupby("panel_size").roc_auc.mean()
            full = mean.get("all")
            print(f"  전체(96) {full:.3f} 대비 유지율: " + " | ".join(
                f"{k}개 {mean.get(k, float('nan')) / full:.1%}" for k in SIZES))

            for k in SIZES:
                j = jaccard_across_folds(picks, k)
                all_stab.append({"model": model_name, "target": target, "panel_size": k, "jaccard": j})
            print()

    metrics = pd.concat(all_metrics, ignore_index=True)
    metrics["panel_size"] = metrics["panel_size"].astype(str)
    picks = pd.concat(all_picks, ignore_index=True)
    stab = pd.DataFrame(all_stab)

    metrics.to_csv(TABLES / "day26_signature_panel_metrics.csv", index=False)
    picks.to_csv(TABLES / "day26_signature_panel_picks.csv", index=False)
    stab.to_csv(TABLES / "day26_signature_panel_stability.csv", index=False)

    print("[패널 크기별 ROC-AUC]")
    pivot = metrics.pivot_table(index=["model", "target"], columns="panel_size",
                                values="roc_auc", aggfunc="mean")
    pivot = pivot.reindex(columns=[str(s) for s in SIZES] + ["all"])
    print(pivot.round(3).to_string())

    print("\n[패널 안정성] fold 간 Jaccard")
    print(stab.pivot_table(index=["model", "target"], columns="panel_size",
                           values="jaccard").round(3).to_string())

    print("\n[전 fold 공통 선택(20개 패널 기준) — 상위 5개 클래스]")
    for key, sub in [(f"{m}_{t}", picks[(picks.model == m) & (picks.target == t) &
                                        (picks.panel_size == 20)])
                     for m in ("logistic_l1", "random_forest") for t in TARGETS]:
        st = panel_stability(sub.assign(panel_size=20), 20)
        common = st[st.freq == 1.0]
        classes = ", ".join(common.feature.head(5))
        print(f"  {key}: 전 fold 공통 {len(common)}개 — {classes}")

    print("\n저장: day26_signature_selection_{model}_{target}.csv, "
          "day26_signature_panel_{metrics,picks,stability}.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
