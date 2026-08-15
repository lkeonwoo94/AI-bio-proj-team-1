"""Day 4 — 표현형 분포와 mutation 빈도 QC, CV 구조 확정.

Figure 2 (WGD/CIN/LOH 분포) 를 생성한다.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.config import REPO_ROOT, load_config
from src.cv.splitters import eligible_lineages
from src.data.merge import load_cohort
from src.labels.binarize import LabelBinarizer
from src.viz.style import PHENOTYPE_COLORS, save, use_style

TABLES = REPO_ROOT / "results" / "tables"


def mutation_frequency(X: pd.DataFrame) -> pd.DataFrame:
    counts = (X > 0).sum(axis=0)
    kind = np.where(X.columns.str.endswith("_hotspot"), "hotspot", "damaging")
    return pd.DataFrame({"feature": X.columns, "kind": kind, "n_cell_lines": counts.to_numpy()})


def plot_distributions(y: pd.DataFrame, freq: pd.DataFrame) -> Path:
    use_style()
    fig, axes = plt.subplots(1, 4, figsize=(17, 3.8))

    # WGD — binary
    counts = y["wgd"].value_counts().sort_index()
    # 유니코드 마이너스(U+2212)는 나눔 폰트에 없어 네모로 깨진다. ASCII 사용.
    axes[0].bar(["WGD-", "WGD+"], counts.to_numpy(), color=["#bfbfbf", PHENOTYPE_COLORS["wgd"]])
    for i, v in enumerate(counts):
        axes[0].text(i, v, f"{v}\n({v / len(y):.1%})", ha="center", va="bottom", fontsize=9)
    axes[0].set_title("WGD (binary)")
    axes[0].set_ylim(0, counts.max() * 1.25)

    # CIN / LOH — continuous with median threshold
    for ax, name, label in ((axes[1], "cin", "CIN"), (axes[2], "loh", "LoHFraction")):
        ax.hist(y[name], bins=40, color=PHENOTYPE_COLORS[name], edgecolor="white")
        med = y[name].median()
        ax.axvline(med, color="k", ls="--", lw=1.5, label=f"전체 중앙값 {med:.3f}")
        ax.set_title(f"{label} (continuous)")
        ax.legend(fontsize=8)

    # mutation 빈도 — 로그 스케일
    for kind, color in (("hotspot", "#c0504d"), ("damaging", "#4f81bd")):
        sub = freq[freq.kind == kind].n_cell_lines
        axes[3].hist(np.log10(sub + 1), bins=40, alpha=0.6, label=f"{kind} (n={len(sub):,})",
                     color=color)
    axes[3].axvline(np.log10(11), color="k", ls=":", lw=1.5, label="필터 기준 10")
    axes[3].set_title("변이 관측 세포주 수")
    axes[3].set_xlabel("log10(세포주 수 + 1)")
    axes[3].legend(fontsize=8)

    fig.suptitle("Figure 2. WGD / CIN / LOH 분포와 mutation 빈도", y=1.04, fontsize=12)
    fig.tight_layout()

    return save(fig, "fig2_phenotype_distribution.png")


def main() -> int:
    cohort = load_cohort(verbose=True)
    print(f"  {cohort.summary()}\n")

    print("[표현형 분포]")
    # 참고용 전체 중앙값. 실제 학습에서는 fold 안에서 다시 계산한다.
    rows = []
    for name in cohort.y.columns:
        binz = LabelBinarizer(name)
        yb = binz.fit_transform(cohort.y[name])
        rows.append({
            "label": name,
            "threshold_전체기준": binz.threshold_,
            "n_high": int(yb.sum()),
            "n_low": int((1 - yb).sum()),
            "positive_rate": yb.mean(),
        })
    dist = pd.DataFrame(rows)
    print(dist.to_string(index=False))

    print("\n[표현형 간 상관] — 세 표현형이 얼마나 겹치는지 (README §4 RQ4 배경)")
    corr = cohort.y.corr(method="spearman")
    print(corr.round(3).to_string())

    print("\n[mutation 빈도]")
    freq = mutation_frequency(cohort.X)
    cfg = load_config("experiment")["features"]
    thr = cfg["min_mutation_count"]
    summary = (
        freq.assign(kept=freq.n_cell_lines >= thr)
        .groupby("kind")
        .agg(n_features=("feature", "size"), n_kept=("kept", "sum"),
             median_count=("n_cell_lines", "median"))
    )
    summary["kept_pct"] = (summary.n_kept / summary.n_features * 100).round(1)
    print(summary.to_string())
    print(f"\n  필터(>={thr} 세포주) 적용 시 {int(summary.n_kept.sum()):,} / "
          f"{len(freq):,} feature 잔존")

    print("\n[CV 구조]")
    cv = load_config("experiment")["cv"]
    print(f"  outer {cv['outer_folds']}-fold / inner {cv['inner_folds']}-fold")
    lolo = eligible_lineages(cohort.groups, min_size=20)
    print(f"  Leave-One-Lineage-Out 대상: {len(lolo)}종 "
          f"(20개 미만 {cohort.groups.nunique() - len(lolo)}종 제외)")

    TABLES.mkdir(parents=True, exist_ok=True)
    dist.to_csv(TABLES / "eda_label_distribution.csv", index=False)
    corr.to_csv(TABLES / "eda_label_correlation.csv")
    freq.to_csv(TABLES / "eda_mutation_frequency.csv", index=False)
    path = plot_distributions(cohort.y, freq)
    print(f"\n저장: {path.name}, eda_*.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
