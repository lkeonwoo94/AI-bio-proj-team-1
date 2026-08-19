"""Random Forest(최고 성능 모델) confusion matrix — WGD/CIN/LOH.

`day10_model_comparison.csv`(Figure 3)의 RF 행은 요약 지표(sensitivity/
specificity 등)만 담고 있어 confusion matrix 자체는 어디에도 저장돼
있지 않다. `05_run_cv.py`/`06_compare_models.py` 와 완전히 같은 nested
CV 조건(random 5-fold, outer test 의 threshold 는 training fold OOF 로
결정, §13)으로 다시 돌리되, 이번엔 **5개 outer fold 의 test 예측을
모아(pool)** confusion matrix 하나로 합친다 — outer fold 마다 따로
그리면 세포주 수가 fold당 ~326개로 너무 작다.

재현성 확인: 여기서 나오는 sensitivity/specificity 는
`day10_model_comparison.csv` 의 random_forest 행과 거의 같아야 한다
(같은 config·seed·모델).
"""

from __future__ import annotations

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
from src.models.zoo import get_model

TABLES = REPO_ROOT / "results" / "tables"
TARGETS = ("wgd", "cin", "loh")
TARGET_LABEL = {"wgd": "WGD", "cin": "CIN", "loh": "LOH"}
CLASS_LABEL = {
    "wgd": ("WGD-", "WGD+"), "cin": ("CIN-low", "CIN-high"), "loh": ("LOH-low", "LOH-high"),
}


def main() -> int:
    cohort = load_cohort()
    spec = get_model("random_forest")
    print(f"[Random Forest confusion matrix] {cohort.summary()}\n")

    rows = []
    for target in TARGETS:
        y_raw = cohort.y[target]
        y_strat = LabelBinarizer(target).fit_transform(y_raw)
        X_values = cohort.X.to_numpy()

        pooled_true, pooled_pred, pooled_prob = [], [], []
        for fold, (tr, te) in enumerate(outer_splits(y_strat.to_numpy(), cohort.groups, scheme="random")):
            binz = LabelBinarizer(target).fit(y_raw.iloc[tr])
            y_tr = binz.transform(y_raw.iloc[tr]).to_numpy()
            y_te = binz.transform(y_raw.iloc[te]).to_numpy()
            X_tr, X_te = X_values[tr], X_values[te]

            with warnings.catch_warnings():
                warnings.simplefilter("ignore", ConvergenceWarning)
                search = GridSearchCV(spec.build(), spec.param_grid, scoring="roc_auc",
                                      cv=inner_cv(), n_jobs=1, refit=True)
                search.fit(X_tr, y_tr)
                best = search.best_estimator_
                oof = cross_val_predict(best, X_tr, y_tr, cv=inner_cv(),
                                        method="predict_proba", n_jobs=1)[:, 1]
            threshold = choose_threshold(y_tr, oof)

            prob_te = best.predict_proba(X_te)[:, 1]
            pred_te = (prob_te >= threshold).astype(int)
            pooled_true.extend(y_te.tolist())
            pooled_pred.extend(pred_te.tolist())
            pooled_prob.extend(prob_te.tolist())
            print(f"  {TARGET_LABEL[target]} fold {fold}: threshold {threshold:.3f}, "
                  f"n_test {len(te)}")

        pooled_true = np.array(pooled_true)
        pooled_pred = np.array(pooled_pred)
        cm = confusion_matrix(pooled_true, pooled_pred, labels=[0, 1])
        tn, fp, fn, tp = cm.ravel()

        sens = tp / (tp + fn) if (tp + fn) else float("nan")
        spec_ = tn / (tn + fp) if (tn + fp) else float("nan")
        bal_acc = (sens + spec_) / 2

        print(f"\n[{TARGET_LABEL[target]}] confusion matrix (pooled, n={len(pooled_true)})")
        print(f"           예측-  예측+")
        print(f"  실제-    {tn:5d}  {fp:5d}")
        print(f"  실제+    {fn:5d}  {tp:5d}")
        print(f"  sensitivity {sens:.3f} | specificity {spec_:.3f} | balanced_acc {bal_acc:.3f}\n")

        rows.append({"target": target, "tn": tn, "fp": fp, "fn": fn, "tp": tp,
                    "n": len(pooled_true), "sensitivity": sens, "specificity": spec_,
                    "balanced_accuracy": bal_acc})

        pd.DataFrame({"y_true": pooled_true, "y_pred": pooled_pred, "y_prob": pooled_prob}).to_csv(
            TABLES / f"day33_rf_pooled_predictions_{target}.csv", index=False)

    out = pd.DataFrame(rows)
    out.to_csv(TABLES / "day33_rf_confusion_matrix.csv", index=False)
    print("저장: day33_rf_confusion_matrix.csv, day33_rf_pooled_predictions_{target}.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
