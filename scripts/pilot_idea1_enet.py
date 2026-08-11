"""아이디어 1 파일럿 — C-1 최소 데이터(발현)만으로 CRISPR 의존성 예측이 되는가.

Q4-1 답변의 근거 수치를 생성한다. 세포주 단위 5-fold CV, out-of-fold 예측으로
유전자별 Pearson r 을 계산하고 베이스라인 3종과 비교한다.

출력: results/tables/pilot_idea1_gene_scores.csv, pilot_idea1_summary.json
"""
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from sklearn.linear_model import ElasticNetCV, Ridge
from sklearn.model_selection import StratifiedKFold

RAW = Path("/home/kali/adni-shared/raw/DepMap")
OUT = Path("/home/kali/adni-shared/AI-bio-proj-team-1/results/tables")
OUT.mkdir(parents=True, exist_ok=True)

SD_CUT = 0.25       # 선택적 의존 유전자 기준
TOP_FEAT = 500      # fold 내부 상관 기반 사전선별 개수
N_FOLDS = 5
SEED = 0


def load():
    ge = pd.read_csv(RAW / "CRISPRGeneEffect.csv", index_col=0)
    ge.index.name = "ModelID"
    ex = pd.read_csv(RAW / "OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv",
                     index_col=0, low_memory=False)
    ex = ex[ex["IsDefaultEntryForModel"] == "Yes"].set_index("ModelID")
    ex = ex[[c for c in ex.columns if c.endswith(")")]]
    mod = pd.read_csv(RAW / "Model.csv").set_index("ModelID")
    ce = set(pd.read_csv(RAW / "CRISPRInferredCommonEssentials.csv")["Essentials"])
    cells = sorted(set(ge.index) & set(ex.index))
    return ge.loc[cells], ex.loc[cells], mod.loc[cells], ce


def fit_one_gene(y, Xtr_all, Xte_all, tr_idx, te_idx, lin_tr, lin_te, self_col):
    """한 유전자에 대해 fold별 out-of-fold 예측을 만든다."""
    pred = {k: np.full(len(y), np.nan) for k in ("mean", "lineage", "self", "enet")}
    for tr, te in zip(tr_idx, te_idx):
        ytr, yte = y[tr], y[te]
        ok = ~np.isnan(ytr)
        if ok.sum() < 50:
            continue
        mu = ytr[ok].mean()
        pred["mean"][te] = mu

        # 베이스라인: 암종 원핫 ridge
        r = Ridge(alpha=1.0).fit(lin_tr[tr][ok], ytr[ok])
        pred["lineage"][te] = r.predict(lin_te[te])

        # 베이스라인: 자기 자신 발현 1개 특징
        if self_col is not None:
            s_tr = Xtr_all[tr][:, self_col][ok].reshape(-1, 1)
            r2 = Ridge(alpha=1.0).fit(s_tr, ytr[ok])
            pred["self"][te] = r2.predict(Xte_all[te][:, self_col].reshape(-1, 1))

        # Elastic Net: fold 내부에서만 상관 기반 사전선별 (누출 방지)
        Xa, ya = Xtr_all[tr][ok], ytr[ok]
        Xc = Xa - Xa.mean(0)
        yc = ya - ya.mean()
        denom = (np.sqrt((Xc ** 2).sum(0)) * np.sqrt((yc ** 2).sum()))
        denom[denom == 0] = np.inf
        corr = np.abs(Xc.T @ yc / denom)
        keep = np.argsort(-corr)[:TOP_FEAT]
        m = ElasticNetCV(l1_ratio=0.5, n_alphas=20, cv=3, max_iter=3000,
                         random_state=SEED, n_jobs=1)
        m.fit(Xa[:, keep], ya)
        pred["enet"][te] = m.predict(Xte_all[te][:, keep])
    return pred


def pearson(a, b):
    m = ~(np.isnan(a) | np.isnan(b))
    if m.sum() < 30 or np.std(a[m]) == 0 or np.std(b[m]) == 0:
        return np.nan
    return float(np.corrcoef(a[m], b[m])[0, 1])


def main():
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

    res = Parallel(n_jobs=20, verbose=1)(
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
    df.to_csv(OUT / "pilot_idea1_gene_scores.csv", index=False)

    summ = {
        "n_cells": int(len(ge)), "n_features": int(X.shape[1]),
        "n_targets": len(targets), "sd_cut": SD_CUT, "folds": N_FOLDS,
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
    (OUT / "pilot_idea1_summary.json").write_text(json.dumps(summ, indent=2))
    print(json.dumps(summ, indent=2))


if __name__ == "__main__":
    main()
