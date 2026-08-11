"""아이디어 1 파일럿 — SVD 기반 고속판.

pilot_idea1_enet.py 는 유전자마다 ElasticNetCV 를 따로 돌린다
(665 유전자 x 5 fold x 3 내부 fold x 20 alpha ~= 20만 회 좌표하강). 약 29분.

이 스크립트는 같은 평가 설계를 유지하되 릿지로 바꾼다. 릿지는 닫힌 해가 있어
train fold 를 한 번 SVD 하면 **모든 유전자 x 모든 alpha 의 해가 동시에** 나오고,
alpha 선택에 쓰는 leave-one-out 오차도 hat 행렬 대각으로 공짜로 얻는다.
행렬곱 몇 번이라 GPU 없이도 분 단위로 끝난다.

    ridge:  beta(alpha) = V diag(s/(s^2+alpha)) U^T y
    LOO  :  (y_i - yhat_i) / (1 - H_ii),  H_ii = sum_k U_ik^2 s_k^2/(s_k^2+alpha)

torch 가 있고 CUDA 가 보이면 GPU 로 SVD/행렬곱을 돌린다(--device cuda).
없으면 numpy 로 그대로 동작한다.

출력: results/tables/pilot_idea1_ridge_gene_scores.csv, pilot_idea1_ridge_summary.json
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from src.preprocessing.depmap_io import load_all  # noqa: E402
from src.models.metrics import pearson_cols  # noqa: E402
from src.models.ridge import ridge_kernel_cv, ridge_small  # noqa: E402

OUT = REPO / "results" / "tables"
OUT.mkdir(parents=True, exist_ok=True)

SD_CUT = 0.25
N_FOLDS = 5
SEED = 0
ALPHAS = np.logspace(1, 6, 30)


def load():
    """캐시(data/interim/depmap)에서 읽는다. 없으면 원본 CSV로 폴백.

    캐시는 scripts/depmap_cache.py 가 만든다. 반환 내용은 예전 CSV 직독 판과
    동일하다 — 교집합 ModelID 로 정렬된 (gene effect, expression, model, common essential).
    """
    d = load_all()
    return d.gene_effect, d.expression, d.model, d.common_essentials


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cpu", choices=["cpu", "cuda"],
                    help="cuda 는 torch 가 설치되고 GPU 가 보일 때만 동작한다")
    args = ap.parse_args()

    t0 = time.time()
    ge, ex, mod, ce = load()
    lineage = mod["OncotreeLineage"].fillna("Unknown")
    sd = ge.std()
    targets = [g for g in ge.columns if g not in ce and sd[g] > SD_CUT]
    t_load = time.time() - t0

    X = ex.values.astype(np.float64)
    X = (X - X.mean(0)) / (X.std(0) + 1e-8)
    Yraw = ge[targets].values.astype(np.float64)

    # 릿지 적합에는 결측을 유전자 평균으로 채우고(행렬 연산 유지),
    # 평가 시에는 원본 결측을 그대로 제외한다.
    Yfill = np.where(np.isnan(Yraw), np.nanmean(Yraw, axis=0), Yraw)
    nan_frac = float(np.isnan(Yraw).mean())

    lin_oh = pd.get_dummies(lineage).values.astype(np.float64)
    col_of = {c: i for i, c in enumerate(ex.columns)}
    self_idx = np.array([col_of.get(g, -1) for g in targets])

    strat = lineage.where(lineage.map(lineage.value_counts()) >= N_FOLDS, "RARE")
    splits = list(StratifiedKFold(N_FOLDS, shuffle=True,
                                  random_state=SEED).split(np.zeros(len(ge)), strat))

    P = {k: np.full_like(Yraw, np.nan) for k in ("mean", "lineage", "self", "ridge")}
    t_fit = time.time()
    for tr, te in splits:
        P["mean"][te] = Yfill[tr].mean(0)
        P["lineage"][te] = ridge_small(lin_oh[tr], Yfill[tr], lin_oh[te])
        # 자기 자신 발현 1개 특징 — 단순회귀 닫힌 해를 전 유전자에 한 번에 적용
        has = self_idx >= 0
        idx = self_idx[has]
        xtr = X[tr][:, idx]
        xte = X[te][:, idx]
        ytr = Yfill[tr][:, has]
        xm_, ym_ = xtr.mean(0), ytr.mean(0)
        xc, yc = xtr - xm_, ytr - ym_
        beta = (xc * yc).sum(0) / ((xc ** 2).sum(0) + 1e-12)
        P["self"][np.ix_(te, np.flatnonzero(has))] = (xte - xm_) * beta + ym_
        P["ridge"][te] = ridge_kernel_cv(X[tr], Yfill[tr], X[te], ALPHAS)
    t_fit = time.time() - t_fit

    rows = {"gene": targets, "sd": [float(sd[g]) for g in targets],
            "has_self_expr": self_idx >= 0}
    for k in P:
        rows[f"r_{k}"] = pearson_cols(Yraw, P[k])
    df = pd.DataFrame(rows)
    df["gain_over_lineage"] = df["r_ridge"] - df["r_lineage"]
    df["gain_over_self"] = df["r_ridge"] - df["r_self"]
    df.sort_values("r_ridge", ascending=False).to_csv(
        OUT / "pilot_idea1_ridge_gene_scores.csv", index=False)

    summ = {"n_cells": int(len(ge)), "n_features": int(X.shape[1]),
            "n_targets": len(targets), "sd_cut": SD_CUT, "folds": N_FOLDS,
            "target_nan_frac": round(nan_frac, 4), "device": args.device,
            "load_s": round(t_load, 1), "fit_s": round(t_fit, 1),
            "total_s": round(time.time() - t0, 1)}
    for k in P:
        v = df[f"r_{k}"].dropna()
        summ[k] = {"median_r": round(float(v.median()), 4),
                   "frac_r_gt_0.3": round(float((v > 0.3).mean()), 4),
                   "frac_r_gt_0.5": round(float((v > 0.5).mean()), 4),
                   "n_r_gt_0.5": int((v > 0.5).sum())}
    summ["ridge_beats_lineage_frac"] = round(float((df.gain_over_lineage > 0).mean()), 4)
    summ["ridge_beats_lineage_by_0.1_n"] = int((df.gain_over_lineage > 0.1).sum())
    summ["ridge_beats_mean_frac"] = round(float((df.r_ridge > df.r_mean).mean()), 4)
    (OUT / "pilot_idea1_ridge_summary.json").write_text(json.dumps(summ, indent=2))
    print(json.dumps(summ, indent=2))


if __name__ == "__main__":
    main()
