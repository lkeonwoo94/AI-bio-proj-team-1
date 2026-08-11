"""Q5 E-3 그림 — 성능 천장의 세 가지 증거.

`q5_ceiling.py` 가 만든 표 3개를 읽어
`results/figures/q5_e3_ceiling.png` 를 생성한다.

    python3 scripts/q5_ceiling.py    # 먼저 실행 (표 생성)
    python3 scripts/plot_q5_e3.py

수치는 전부 CSV 에서 읽는다(results/figures/README.md 규칙 2).
한글 폰트 등록은 plot_q4_d1.py 의 함수를 재사용한다(규칙 4).
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot_q4_d1 import use_korean_font  # noqa: E402  (matplotlib.use("Agg") 포함)

ROOT = Path(__file__).resolve().parent.parent
TABLES = ROOT / "results" / "tables"
OUT = ROOT / "results" / "figures" / "q5_e3_ceiling.png"

GREY = "#8c8c8c"
BLUE = "#08519c"
ORANGE = "#c6762e"
RED = "#a63603"


def main():
    use_korean_font()
    abl = pd.read_csv(TABLES / "q5_ceiling_ablation.csv")
    curve = pd.read_csv(TABLES / "q5_ceiling_learning_curve.csv")
    sweep = pd.read_csv(TABLES / "q5_ceiling_sd_sweep.csv")

    base = float(abl.median_r.iloc[0])
    fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.0))

    # A — 개선안 ablation. 베이스라인을 넘는 막대가 하나도 없다.
    ax = axes[0]
    y = np.arange(len(abl))[::-1]
    colors = [BLUE] + [GREY] * (len(abl) - 1)
    ax.barh(y, abl.median_r, color=colors, height=0.62)
    ax.axvline(base, color=RED, lw=1.1, ls="--", zorder=5)
    ax.text(base + 0.004, y[0] + 0.55, f"베이스라인 {base:.3f}",
            fontsize=6.5, color=RED, va="bottom")
    for yi, v in zip(y, abl.median_r):
        ax.text(v - 0.008, yi, f"{v:.3f}", ha="right", va="center",
                fontsize=6.5, color="white")
    ax.set_yticks(y)
    ax.set_yticklabels([s.split(". ", 1)[-1] for s in abl.setting], fontsize=6.5)
    ax.set_xlim(0.30, 0.43)
    ax.set_xlabel("유전자별 중앙 Pearson r")
    n_win = int((abl.delta_vs_baseline.iloc[1:] > 0).sum())
    ax.set_title(f"① 베이스라인을 넘은 개선안 {n_win} / {len(abl) - 1}개", loc="left")

    # B — 학습곡선. 중앙 r 은 완만히 오르고 max r 은 일찍 포화된다.
    ax = axes[1]
    ax.plot(curve.train_n, curve.median_r, "o-", color=BLUE, lw=1.6, ms=4.5,
            label="중앙 r")
    ax.plot(curve.train_n, curve.max_r, "s--", color=ORANGE, lw=1.4, ms=4,
            label="max r (가장 잘 맞는 유전자)")
    ax.axhline(0.8, color=RED, lw=1.0, ls=":")
    ax.text(curve.train_n.min(), 0.808, "목표 0.8", fontsize=6.5, color=RED)
    ax.set_xscale("log", base=2)
    ax.set_xticks(curve.train_n)
    ax.set_xticklabels([f"{n:,}" for n in curve.train_n], rotation=35, fontsize=6.5)
    ax.set_ylim(0.15, 0.92)
    ax.set_xlabel("학습에 쓴 세포주 수 (log2 축)")
    ax.set_ylabel("Pearson r")
    ax.legend(fontsize=6.5, loc="center right", frameon=False)
    tail = curve.tail(3)
    slope = float(np.polyfit(np.log2(tail.train_n), tail.median_r, 1)[0])
    ax.set_title(f"② n 2배당 +{slope:.3f} — max r 은 이미 포화", loc="left")

    # C — SD 컷 스윕. 올라가지만 그건 대상을 버려서 얻은 값이다.
    ax = axes[2]
    ax.plot(sweep.sd_cut, sweep.median_r, "o-", color=BLUE, lw=1.6, ms=5)
    for _, row in sweep.iterrows():
        ax.annotate(f"{int(row.n_genes)}개", (row.sd_cut, row.median_r),
                    textcoords="offset points", xytext=(0, 8),
                    ha="center", fontsize=6.5, color=GREY)
    ax.axhline(0.8, color=RED, lw=1.0, ls=":")
    ax.text(sweep.sd_cut.min(), 0.808, "목표 0.8", fontsize=6.5, color=RED)
    ax.set_ylim(0.35, 0.92)
    ax.set_xlabel("타깃 선정 기준 (gene effect 표준편차 컷)")
    ax.set_ylabel("유전자별 중앙 Pearson r")
    ax.set_title(f"③ 타깃을 좁혀도 {sweep.median_r.max():.2f} 에서 멈춘다", loc="left")

    fig.tight_layout()
    fig.savefig(OUT, dpi=300, bbox_inches="tight")
    print(f"{OUT}  (베이스라인 {base:.4f}, 전 설정 max r {abl.max_r.max():.3f})")


if __name__ == "__main__":
    main()
