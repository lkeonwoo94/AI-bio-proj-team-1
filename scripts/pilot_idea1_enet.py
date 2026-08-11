"""아이디어 1 파일럿 — C-1 최소 데이터(발현)만으로 CRISPR 의존성 예측이 되는가.

Q4-1 답변의 근거 수치를 생성한다. 세포주 단위 5-fold CV, out-of-fold 예측으로
유전자별 Pearson r 을 계산하고 베이스라인 3종과 비교한다.

출력: results/tables/pilot_idea1_enet_gene_scores.csv, pilot_idea1_enet_summary.json
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from sklearn.model_selection import StratifiedKFold

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from src.models.elastic_net import enet_preselect_cv  # noqa: E402
from src.models.metrics import pearson_cols  # noqa: E402
from src.models.ridge import ridge_small  # noqa: E402
from src.preprocessing.depmap_io import load_all  # noqa: E402

OUT = REPO / "results" / "tables"
OUT.mkdir(parents=True, exist_ok=True)

SD_CUT = 0.25       # 선택적 의존 유전자 기준
N_FOLDS = 5
SEED = 0

# 좌표하강 설정. 아래 값은 2026-08-11 실측으로 정한 것이다.
# sklearn 기본값(top_feat 500 / n_alphas 20 / tol 1e-4 / max_iter 3000)으로 돌리면
# 2,969초가 걸리는데, 아래 설정은 263초로 11.3배 빠르면서 품질은 거의 같다
# (중앙값 r 0.365 → 0.354, 유전자별 상관 0.986). 근거는 Q4 D-4 참고.
CFG = {"top_feat": 200, "n_alphas": 10, "tol": 1e-3, "max_iter": 1000}


def load():
    """캐시(data/interim/depmap)에서 읽는다. 없으면 원본 CSV로 폴백.

    캐시는 scripts/depmap_cache.py 가 만든다. 반환 내용은 예전 CSV 직독 판과
    동일하다 — 교집합 ModelID 로 정렬된 (gene effect, expression, model, common essential).
    """
    d = load_all()
    return d.gene_effect, d.expression, d.model, d.common_essentials


def fit_one_gene(y, Xtr_all, Xte_all, tr_idx, te_idx, lin_tr, lin_te, self_col):
    """한 유전자에 대해 fold별 out-of-fold 예측을 만든다.

    베이스라인 3종과 Elastic Net 을 같은 분할 위에서 계산한다. 결측 타깃은
    fold 안에서 마스킹하고, 유효 표본이 50 미만이면 그 fold 는 건너뛴다.
    """
    pred = {k: np.full(len(y), np.nan) for k in ("mean", "lineage", "self", "enet")}
    for tr, te in zip(tr_idx, te_idx):
        ytr = y[tr]
        ok = ~np.isnan(ytr)
        if ok.sum() < 50:
            continue
        ytr_ok = ytr[ok]

        pred["mean"][te] = ytr_ok.mean()

        # 베이스라인: 암종 원핫
        pred["lineage"][te] = ridge_small(
            lin_tr[tr][ok], ytr_ok[:, None], lin_te[te]).ravel()

        # 베이스라인: 자기 자신 발현 1개 특징
        if self_col is not None:
            pred["self"][te] = ridge_small(
                Xtr_all[tr][ok][:, [self_col]], ytr_ok[:, None],
                Xte_all[te][:, [self_col]]).ravel()

        # Elastic Net — 사전선별은 train fold 안에서만 (누출 방지)
        pred["enet"][te], _ = enet_preselect_cv(
            Xtr_all[tr][ok], ytr_ok, Xte_all[te], seed=SEED, **CFG)
    return pred


def pearson(a, b):
    """단일 유전자용 래퍼. 판정 규칙은 pearson_cols 와 동일하다."""
    return float(pearson_cols(a[:, None], b[:, None])[0])


def main():
    ap = argparse.ArgumentParser(description="아이디어 1 파일럿 — Elastic Net")
    ap.add_argument("--top-feat", type=int, default=CFG["top_feat"])
    ap.add_argument("--n-alphas", type=int, default=CFG["n_alphas"])
    ap.add_argument("--tol", type=float, default=CFG["tol"])
    ap.add_argument("--max-iter", type=int, default=CFG["max_iter"])
    ap.add_argument("--tag", default="", help="출력 파일명 접미사 (예: --tag _fast)")
    ap.add_argument("--n-jobs", type=int, default=20)
    a = ap.parse_args()
    CFG.update(top_feat=a.top_feat, n_alphas=a.n_alphas, tol=a.tol, max_iter=a.max_iter)
    tag = a.tag

    t0 = time.time()
    ge, ex, mod, ce = load()
    lineage = mod["OncotreeLineage"].fillna("Unknown")
    sd = ge.std()
    targets = [g for g in ge.columns if g not in ce and sd[g] > SD_CUT]

    Xdf = ex.astype(np.float32)
    X = Xdf.values
    X = (X - X.mean(0)) / (X.std(0) + 1e-8)
    lin_oh = pd.get_dummies(lineage).values.astype(np.float32)

    # 세포주 단위 분할 (암종으로 층화)
    strat = lineage.where(lineage.map(lineage.value_counts()) >= N_FOLDS, "RARE")
    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
    splits = list(skf.split(np.zeros(len(ge)), strat))
    tr_idx = [s[0] for s in splits]
    te_idx = [s[1] for s in splits]

    col_of = {c: i for i, c in enumerate(Xdf.columns)}
    Y = ge[targets].values.astype(np.float32)

    res = Parallel(n_jobs=a.n_jobs, verbose=1)(
        delayed(fit_one_gene)(Y[:, j], X, X, tr_idx, te_idx, lin_oh, lin_oh,
                              col_of.get(targets[j]))
        for j in range(len(targets))
    )

    rows = []
    for j, g in enumerate(targets):
        y = Y[:, j]
        rows.append({
            "gene": g, "sd": float(sd[g]),
            "has_self_expr": targets[j] in col_of,
            **{f"r_{k}": pearson(y, res[j][k]) for k in ("mean", "lineage", "self", "enet")},
        })
    df = pd.DataFrame(rows)
    df["gain_over_lineage"] = df["r_enet"] - df["r_lineage"]
    df.to_csv(OUT / f"pilot_idea1_enet{tag}_gene_scores.csv", index=False)

    summ = {
        "n_cells": int(len(ge)), "n_features": int(X.shape[1]),
        "n_targets": len(targets), "sd_cut": SD_CUT, "folds": N_FOLDS, **CFG,
        "runtime_s": round(time.time() - t0, 1),
    }
    for k in ("mean", "lineage", "self", "enet"):
        v = df[f"r_{k}"].dropna()
        summ[k] = {
            "median_r": round(float(v.median()), 4),
            "frac_r_gt_0.3": round(float((v > 0.3).mean()), 4),
            "frac_r_gt_0.5": round(float((v > 0.5).mean()), 4),
            "n_r_gt_0.5": int((v > 0.5).sum()),
        }
    summ["enet_beats_lineage_frac"] = round(float((df.gain_over_lineage > 0).mean()), 4)
    summ["enet_beats_lineage_by_0.1_n"] = int((df.gain_over_lineage > 0.1).sum())
    (OUT / f"pilot_idea1_enet{tag}_summary.json").write_text(json.dumps(summ, indent=2))
    print(json.dumps(summ, indent=2))


if __name__ == "__main__":
    main()
