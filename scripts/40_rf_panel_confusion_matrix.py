"""RF 최소 N개 유전자 패널 — inference confusion matrix (2026-08-21).

`scripts/33_rf_confusion_matrix.py` 는 필터 통과 전체 feature(~1,200\~1,700개)
로 학습한 RF의 confusion matrix였다. 이 스크립트는 그 대신 **Day 12 방식으로
뽑은 N개 유전자 패널**(기본 10, `--panel-size` 로 변경)로 학습·추론했을 때의
confusion matrix를 본다 — "최소 패널로 실제 추론하면 오분류 패턴이 어떻게
달라지는가"에 대한 답이다.

패널은 08-16 §26④와 동일한 방법으로 뽑는다 — **각 outer fold의 training
데이터 안에서** 전체 feature로 학습한 RF importance 상위 N개를 그 fold의
패널로 쓰고, 그 N개 열만으로 다시 학습해 그 fold의 test를 예측한다
(`src/panel/curve.py:run_panel_curve` 와 같은 로직, §13 원칙 동일 — outer
test 는 패널 선택에도 학습에도 관여하지 않는다). 5개 fold의 test 예측을
모두 pool해서 confusion matrix 하나로 합친다.

주의: 이 패널은 폴드마다 정확히 같은 N개가 아니다(08-16 §26④, "Day 11/12
RF 재검증" — 10개 패널의 fold 간 Jaccard는 WGD 0.607/CIN 0.520/LOH 0.544).
"N개짜리 고정 유전자 목록"이 아니라 "매 fold 그 fold의 training 데이터로
뽑은 N개 패널"의 추론 성능이라는 점에 유의한다.
"""

from __future__ import annotations

import argparse
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import GridSearchCV, cross_val_predict

from src.config import REPO_ROOT
from src.cv.splitters import inner_cv, outer_splits
from src.data.merge import load_cohort
from src.evaluation.metrics import choose_threshold
from src.labels.binarize import LabelBinarizer
from src.models.zoo import extract_importance, get_model

TABLES = REPO_ROOT / "results" / "tables"
TARGETS = ("wgd", "cin", "loh")
TARGET_LABEL = {"wgd": "WGD", "cin": "CIN", "loh": "LOH"}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--panel-size", type=int, default=10)
    args = p.parse_args()
    panel_size = args.panel_size

    cohort = load_cohort()
    spec = get_model("random_forest")
    print(f"[RF {panel_size}개 패널 confusion matrix] {cohort.summary()}\n")

    rows, all_picks = [], []
    for target in TARGETS:
        y_raw = cohort.y[target]
        y_strat = LabelBinarizer(target).fit_transform(y_raw)
        X_values = cohort.X.to_numpy()
        feature_names = np.asarray(cohort.X.columns)

        pooled_true, pooled_pred = [], []
        for fold, (tr, te) in enumerate(outer_splits(y_strat.to_numpy(), cohort.groups, scheme="random")):
            binz = LabelBinarizer(target).fit(y_raw.iloc[tr])
            y_tr = binz.transform(y_raw.iloc[tr]).to_numpy()
            y_te = binz.transform(y_raw.iloc[te]).to_numpy()
            X_tr, X_te = X_values[tr], X_values[te]

            # --- 1) 전체 feature로 학습해 그 fold의 importance 상위 N개를 뽑는다 ---
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", ConvergenceWarning)
                search = GridSearchCV(spec.build(), spec.param_grid, scoring="roc_auc",
                                      cv=inner_cv(), n_jobs=-1, refit=True)
                search.fit(X_tr, y_tr)
            best = search.best_estimator_
            kept_mask = best.named_steps["filter"].get_support()
            kept_names = feature_names[kept_mask]
            imp = extract_importance(best, spec.importance)
            order = np.argsort(imp)[::-1]
            panel = kept_names[order[:panel_size]]
            all_picks.append(pd.DataFrame({"fold": fold, "target": target, "feature": panel}))

            # --- 2) 그 N개 열만으로 다시 학습 ---
            cols = np.flatnonzero(np.isin(feature_names, panel))
            Xk_tr, Xk_te = X_values[np.ix_(tr, cols)], X_values[np.ix_(te, cols)]

            with warnings.catch_warnings():
                warnings.simplefilter("ignore", ConvergenceWarning)
                search_k = GridSearchCV(get_model("random_forest").build(), spec.param_grid,
                                        scoring="roc_auc", cv=inner_cv(), n_jobs=-1, refit=True)
                search_k.fit(Xk_tr, y_tr)
                best_k = search_k.best_estimator_
                oof_k = cross_val_predict(best_k, Xk_tr, y_tr, cv=inner_cv(),
                                          method="predict_proba", n_jobs=-1)[:, 1]
            threshold = choose_threshold(y_tr, oof_k)

            prob_te = best_k.predict_proba(Xk_te)[:, 1]
            pred_te = (prob_te >= threshold).astype(int)
            pooled_true.extend(y_te.tolist())
            pooled_pred.extend(pred_te.tolist())
            print(f"  {TARGET_LABEL[target]} fold {fold}: 패널={list(panel)}, threshold={threshold:.3f}")

        pooled_true = np.array(pooled_true)
        pooled_pred = np.array(pooled_pred)
        cm = confusion_matrix(pooled_true, pooled_pred, labels=[0, 1])
        tn, fp, fn, tp = cm.ravel()
        sens = tp / (tp + fn) if (tp + fn) else float("nan")
        spec_ = tn / (tn + fp) if (tn + fp) else float("nan")
        bal_acc = (sens + spec_) / 2

        print(f"\n[{TARGET_LABEL[target]}] {panel_size}개 패널 confusion matrix (pooled, n={len(pooled_true)})")
        print(f"  실제-  {tn:5d}  {fp:5d}")
        print(f"  실제+  {fn:5d}  {tp:5d}")
        print(f"  sensitivity {sens:.3f} | specificity {spec_:.3f} | balanced_acc {bal_acc:.3f}\n")

        rows.append({"target": target, "tn": tn, "fp": fp, "fn": fn, "tp": tp,
                    "n": len(pooled_true), "sensitivity": sens, "specificity": spec_,
                    "balanced_accuracy": bal_acc})

    out = pd.DataFrame(rows)
    out.to_csv(TABLES / f"day40_rf_panel{panel_size}_confusion_matrix.csv", index=False)
    picks = pd.concat(all_picks, ignore_index=True)
    picks.to_csv(TABLES / f"day40_rf_panel{panel_size}_picks.csv", index=False)

    print("전체 feature RF(day33) 대비 비교:")
    full = pd.read_csv(TABLES / "day33_rf_confusion_matrix.csv").set_index("target")
    cmp = out.set_index("target")[["sensitivity", "specificity", "balanced_accuracy"]]
    cmp.columns = pd.MultiIndex.from_product([[f"{panel_size}개 패널"], cmp.columns])
    full_cmp = full[["sensitivity", "specificity", "balanced_accuracy"]]
    full_cmp.columns = pd.MultiIndex.from_product([["전체 feature"], full_cmp.columns])
    print(pd.concat([full_cmp, cmp], axis=1).round(3).to_string())

    print(f"\n저장: day40_rf_panel{panel_size}_confusion_matrix.csv, day40_rf_panel{panel_size}_picks.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
