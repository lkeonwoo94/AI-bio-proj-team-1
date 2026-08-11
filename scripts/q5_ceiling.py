"""Q5 — 「릿지 중앙 r 0.404 를 0.8~0.9 로 올릴 수 있는가」에 대한 실측.

Q4 D-1 이 「되는가」를 물었다면 여기서는 **「어디까지 되는가」**를 묻는다.
세 가지를 잰다.

1. **개선안 ablation** — 알고리즘·특징 처리를 바꾸면 중앙 r 이 오르는가
2. **학습곡선** — 세포주(n) 를 늘리면 오르는가
3. **SD 컷 스윕** — 타깃을 좁히면 오르는가 (오르지만 「성능 향상」이 아니라 「대상 축소」)

평가 설계는 `pilot_idea1_ridge.py` 와 동일하게 유지한다 — 세포주 단위 5-fold
층화 CV(암종으로 층화), out-of-fold 예측으로 유전자별 Pearson r 을 세포주 축을
따라 계산. 바꾸는 것은 입력·타깃 처리뿐이다.

    python3 scripts/q5_ceiling.py          # 약 4분 (24코어 + OpenBLAS 기준)
    python3 scripts/plot_q5_e3.py          # 그림

출력: results/tables/q5_ceiling_{ablation,learning_curve,sd_sweep}.csv
      results/tables/q5_ceiling_summary.json

⚠️ BLAS 구현에 따라 시간이 5배 이상 차이난다. Q4 D-4 의 경고 참고.
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from src.models.metrics import pearson_cols  # noqa: E402
from src.models.ridge import ridge_kernel_cv, ridge_lowrank_cv  # noqa: E402
from src.preprocessing.depmap_io import load_all  # noqa: E402

OUT = REPO / "results" / "tables"
OUT.mkdir(parents=True, exist_ok=True)

# pilot_idea1_ridge.py 와 같은 값을 쓴다. 여기서 바꾸면 D-1 수치와 비교가 깨진다.
SD_CUT = 0.25
N_FOLDS = 5
SEED = 0
ALPHAS = np.logspace(1, 6, 30)

SD_GRID = [0.25, 0.30, 0.35, 0.40, 0.50, 0.60]
CURVE_FRACS = [0.15, 0.25, 0.40, 0.55, 0.70, 0.85, 1.00]


def summarize(r: pd.Series) -> dict:
    """유전자별 r 분포를 한 줄로 요약한다."""
    return {
        "n_genes": int(len(r)),
        "median_r": round(float(r.median()), 4),
        "mean_r": round(float(r.mean()), 4),
        "frac_gt_0.3": round(float((r > 0.3).mean()), 4),
        "frac_gt_0.5": round(float((r > 0.5).mean()), 4),
        "n_gt_0.8": int((r > 0.8).sum()),
        "max_r": round(float(r.max()), 4),
    }


def zscore(A: np.ndarray, fit_rows: np.ndarray) -> np.ndarray:
    """fit_rows 의 평균·표준편차로 전체를 표준화한다(fold 내부 전처리)."""
    m, s = A[fit_rows].mean(0), A[fit_rows].std(0)
    return (A - m) / (s + 1e-8)


def main():
    t_start = time.time()

    d = load_all()
    ge, ex, mod, ce = d.gene_effect, d.expression, d.model, d.common_essentials
    lineage = mod["OncotreeLineage"].fillna("Unknown")
    sd = ge.std()
    targets = [g for g in ge.columns if g not in ce and sd[g] > SD_CUT]

    Xraw = ex.values.astype(np.float64)
    Xz = (Xraw - Xraw.mean(0)) / (Xraw.std(0) + 1e-8)   # D-1 과 동일한 전역 표준화
    Yraw = ge[targets].values.astype(np.float64)
    Yfill = np.where(np.isnan(Yraw), np.nanmean(Yraw, axis=0), Yraw)
    lin_oh = pd.get_dummies(lineage).values.astype(np.float64)

    strat = lineage.where(lineage.map(lineage.value_counts()) >= N_FOLDS, "RARE")
    splits = list(StratifiedKFold(N_FOLDS, shuffle=True, random_state=SEED)
                  .split(np.zeros(len(ge)), strat))

    print(f"세포주 n = {len(ge)}, 특징 p = {Xraw.shape[1]}, "
          f"타깃 = {len(targets)}개 (SD > {SD_CUT}, common essential 제외)\n")

    def evaluate(predict) -> pd.Series:
        """predict(tr, te) -> (n_te, n_targets) 를 5-fold 로 돌려 유전자별 r 을 낸다."""
        P = np.full_like(Yraw, np.nan)
        for tr, te in splits:
            P[te] = predict(tr, te)
        return pd.Series(pearson_cols(Yraw, P), index=targets).dropna()

    # ── 1. 개선안 ablation ────────────────────────────────────────────────
    # 「무엇을 바꾸면 오르는가」. 베이스라인을 이기는 것이 있는지 본다.
    def feat_topvar(k):
        def predict(tr, te):
            keep = np.argsort(Xraw[tr].var(0))[-k:]
            A = zscore(Xraw[:, keep], tr)
            return ridge_kernel_cv(A[tr], Yfill[tr], A[te], ALPHAS)
        return predict

    def with_lineage(tr, te):
        # 원핫에 가중치 5 — 표준화된 발현 특징 19,215개에 묻히지 않게 한다
        A = np.hstack([Xz, lin_oh * 5.0])
        return ridge_kernel_cv(A[tr], Yfill[tr], A[te], ALPHAS)

    ablation = [
        ("0. 베이스라인 (발현 19,215, 전역 표준화)",
         lambda tr, te: ridge_kernel_cv(Xz[tr], Yfill[tr], Xz[te], ALPHAS)),
        ("0b. 대조: fold 내부 표준화",
         lambda tr, te: (lambda A: ridge_kernel_cv(A[tr], Yfill[tr], A[te], ALPHAS))(
             zscore(Xraw, tr))),
        ("1. + 암종 원핫 명시적 추가", with_lineage),
        ("2a. 발현 분산 상위 2,000개만", feat_topvar(2000)),
        ("2b. 발현 분산 상위 5,000개만", feat_topvar(5000)),
        ("3a. 저랭크 멀티태스크 rank=50",
         lambda tr, te: ridge_lowrank_cv(Xz[tr], Yfill[tr], Xz[te], ALPHAS, 50)),
        ("3b. 저랭크 멀티태스크 rank=150",
         lambda tr, te: ridge_lowrank_cv(Xz[tr], Yfill[tr], Xz[te], ALPHAS, 150)),
        ("3c. 저랭크 멀티태스크 rank=300",
         lambda tr, te: ridge_lowrank_cv(Xz[tr], Yfill[tr], Xz[te], ALPHAS, 300)),
    ]

    print("── 1. 개선안 ablation " + "─" * 42)
    print(f"{'설정':<38} {'중앙 r':>8} {'>0.5':>7} {'>0.8':>5} {'max r':>7}")
    rows, r_base = [], None
    for name, predict in ablation:
        t0 = time.time()
        r = evaluate(predict)
        if r_base is None:
            r_base = r
        rows.append({"setting": name, **summarize(r),
                     "sec": round(time.time() - t0, 1)})
        print(f"{name:<38} {r.median():>8.4f} {(r > 0.5).mean() * 100:>6.1f}% "
              f"{(r > 0.8).sum():>5} {r.max():>7.3f}")
    abl = pd.DataFrame(rows)
    abl["delta_vs_baseline"] = (abl.median_r - abl.median_r.iloc[0]).round(4)
    abl.to_csv(OUT / "q5_ceiling_ablation.csv", index=False)

    # ── 2. 학습곡선 ──────────────────────────────────────────────────────
    # 「세포주를 더 구하면 오르는가」. train fold 크기만 줄이고 test 는 그대로 둔다.
    print("\n── 2. 학습곡선 " + "─" * 49)
    print(f"{'train n':>8} {'중앙 r':>8} {'>0.3':>7} {'>0.5':>7} {'max r':>7}")
    rng = np.random.default_rng(SEED)
    rows = []
    for frac in CURVE_FRACS:
        sizes = []

        def predict(tr, te, frac=frac, sizes=sizes):
            k = max(30, int(len(tr) * frac))
            sizes.append(k)
            sub = rng.choice(tr, size=k, replace=False)
            return ridge_kernel_cv(Xz[sub], Yfill[sub], Xz[te], ALPHAS)

        r = evaluate(predict)
        rows.append({"train_n": int(np.mean(sizes)), "frac": frac, **summarize(r)})
        print(f"{rows[-1]['train_n']:>8} {r.median():>8.4f} "
              f"{(r > 0.3).mean() * 100:>6.1f}% {(r > 0.5).mean() * 100:>6.1f}% "
              f"{r.max():>7.3f}")
    curve = pd.DataFrame(rows)
    curve.to_csv(OUT / "q5_ceiling_learning_curve.csv", index=False)

    # n 을 2배로 늘렸을 때의 중앙 r 증분 — 마지막 세 점의 log2 기울기
    tail = curve.tail(3)
    slope = float(np.polyfit(np.log2(tail.train_n), tail.median_r, 1)[0])
    n_now = int(curve.train_n.iloc[-1])
    doublings = (0.8 - float(curve.median_r.iloc[-1])) / slope
    n_needed = int(n_now * 2 ** doublings)

    # ── 3. SD 컷 스윕 ────────────────────────────────────────────────────
    # 「타깃을 좁히면 오르는가」. 베이스라인 예측을 재사용하므로 추가 적합이 없다.
    print("\n── 3. SD 컷 스윕 (베이스라인 예측 재사용) " + "─" * 22)
    print(f"{'SD 컷':>7} {'유전자수':>9} {'중앙 r':>8} {'>0.5':>7}")
    sd_t = pd.Series({g: float(sd[g]) for g in targets})
    rows = []
    for cut in SD_GRID:
        r = r_base[sd_t.reindex(r_base.index) > cut]
        if len(r) < 5:
            continue
        rows.append({"sd_cut": cut, **summarize(r)})
        print(f"{cut:>7.2f} {len(r):>9} {r.median():>8.4f} "
              f"{(r > 0.5).mean() * 100:>6.1f}%")
    sweep = pd.DataFrame(rows)
    sweep.to_csv(OUT / "q5_ceiling_sd_sweep.csv", index=False)

    # ── 요약 ─────────────────────────────────────────────────────────────
    summ = {
        "n_cells": int(len(ge)),
        "n_features": int(Xraw.shape[1]),
        "n_targets": len(targets),
        "sd_cut": SD_CUT,
        "folds": N_FOLDS,
        "baseline_median_r": float(abl.median_r.iloc[0]),
        "best_median_r": float(abl.median_r.max()),
        "best_setting": abl.loc[abl.median_r.idxmax(), "setting"],
        "any_setting_beats_baseline": bool(abl.delta_vs_baseline.iloc[1:].max() > 0),
        # 어떤 설정에서도 넘지 못한 상한 — 천장의 증거
        "max_r_over_all_settings": float(abl.max_r.max()),
        "curve_slope_per_doubling": round(slope, 4),
        "curve_n_for_median_r_0.8": n_needed,
        "total_s": round(time.time() - t_start, 1),
    }
    (OUT / "q5_ceiling_summary.json").write_text(
        json.dumps(summ, indent=2, ensure_ascii=False))

    print("\n" + "─" * 68)
    print(f"베이스라인을 이긴 설정: "
          f"{'없음' if not summ['any_setting_beats_baseline'] else summ['best_setting']}")
    print(f"모든 설정을 통틀어 max r = {summ['max_r_over_all_settings']:.3f} "
          f"— 모델을 바꿔도 이 위로 못 간다")
    print(f"학습곡선 기울기: train n 2배당 중앙 r +{slope:.4f}")
    print(f"→ 중앙 r 0.8 까지 외삽하면 세포주 약 {n_needed:,}개 필요 "
          f"(천장을 무시한 낙관적 외삽)")
    print(f"\n{summ['total_s']}초")


if __name__ == "__main__":
    main()
