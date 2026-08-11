"""Q4 D-1 그림 — 발현 기반 예측 vs 베이스라인 3종.

`pilot_idea1_ridge.py` 가 만든 유전자별 점수와 raw 데이터를 읽어
`results/figures/q4_d1_baseline_comparison.png` 를 생성한다.

    python3 scripts/pilot_idea1_ridge.py   # 먼저 실행 (점수 생성)
    python3 scripts/plot_q4_d1.py

파일명 규칙은 results/figures/README.md 참고.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = Path("/home/kali/adni-shared/raw")
TABLES = ROOT / "results" / "tables"
FIGURES = ROOT / "results" / "figures"
OUT = FIGURES / "q4_d1_baseline_comparison.png"

GREY = "#8c8c8c"
BLUE = "#08519c"
ORANGE = "#c6762e"


def use_korean_font():
    """시스템 나눔고딕을 등록한다. 없으면 기본 폰트로 진행(한글 깨짐)."""
    nanum = Path("/usr/share/fonts/truetype/nanum")
    if nanum.exists():
        for p in fm.findSystemFonts(fontpaths=[str(nanum)]):
            fm.fontManager.addfont(p)
        plt.rcParams["font.family"] = "NanumGothic"
    plt.rcParams.update({
        "axes.unicode_minus": False, "figure.dpi": 110,
        "axes.spines.top": False, "axes.spines.right": False,
        "font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8,
        "xtick.labelsize": 7, "ytick.labelsize": 7,
    })


def sample_sizes():
    """아이디어 1·2 의 학습 가능 세포주 수를 raw 에서 직접 센다."""
    ge = pd.read_csv(RAW / "DepMap" / "CRISPRGeneEffect.csv", index_col=0, usecols=[0])
    ex = pd.read_csv(RAW / "DepMap" / "OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv",
                     usecols=["ModelID", "IsDefaultEntryForModel"])
    ex = ex[ex["IsDefaultEntryForModel"] == "Yes"]
    n1 = set(ge.index) & set(ex["ModelID"])

    prism = pd.read_csv(
        RAW / "PRISM_Repurposing_24Q2" /
        "Repurposing_Public_24Q2_Extended_Primary_Data_Matrix.csv",
        index_col=0, nrows=1)
    # 이 행렬은 화합물 x 세포주 방향이라 열이 ModelID 다
    return len(n1), len(n1 & set(prism.columns))


def main():
    use_korean_font()
    gs = pd.read_csv(TABLES / "pilot_idea1_ridge_gene_scores.csv")
    n1, n2 = sample_sizes()

    fig, axes = plt.subplots(1, 3, figsize=(12.5, 3.8))

    # A — 베이스라인별 유전자 r 분포
    ax = axes[0]
    series = [("r_mean", "유전자별 평균", GREY), ("r_self", "자기 발현 1개", "#9ecae1"),
              ("r_lineage", "암종 원핫", "#6baed6"), ("r_ridge", "발현 전체", BLUE)]
    for i, (key, label, color) in enumerate(series):
        v = gs[key].dropna().values
        for body in ax.violinplot([v], positions=[i], widths=0.82,
                                  showextrema=False)["bodies"]:
            body.set_facecolor(color)
            body.set_alpha(0.85)
            body.set_edgecolor("none")
        ax.hlines(np.median(v), i - 0.33, i + 0.33, color="black", lw=1.5, zorder=5)
        ax.text(i, 0.93, f"{np.median(v):.2f}", ha="center", fontsize=6.5, color="#333333")
    ax.set_xticks(range(len(series)))
    ax.set_xticklabels([s[1] for s in series], rotation=16, ha="right")
    ax.axhline(0, color=GREY, lw=0.7, ls=":")
    ax.set_ylim(-0.45, 1.0)
    ax.set_ylabel("유전자별 Pearson r")
    ax.set_title("발현은 암종 위에 증분을 얹는다", loc="left")

    # B — 릿지 vs 암종 베이스라인
    ax = axes[1]
    ax.scatter(gs.r_lineage, gs.r_ridge, s=9, color=BLUE, alpha=0.42, edgecolor="none")
    lim = [-0.35, 0.92]
    ax.plot(lim, lim, color=GREY, lw=0.9, ls="--", zorder=1)
    ax.set_xlim(lim)
    ax.set_ylim(lim)
    offsets = {"PAX8": (-38, 14), "SOX10": (6, 16), "EBF1": (-44, -2), "MYB": (10, -10)}
    for _, row in gs.head(4).iterrows():
        name = row.gene.split(" (")[0]
        ax.annotate(name, (row.r_lineage, row.r_ridge), fontsize=6.5,
                    xytext=offsets.get(name, (6, 6)), textcoords="offset points",
                    arrowprops=dict(arrowstyle="-", lw=0.5, color=GREY))
    ax.set_xlabel("암종 원핫만 (r)")
    ax.set_ylabel("발현 전체 릿지 (r)")
    ax.set_title(f"{len(gs)}개 중 {int((gs.gain_over_lineage > 0).sum())}개가 대각선 위",
                 loc="left")

    # C — 멀티태스크 확장 시 표본 손실
    ax = axes[2]
    values = [n1, n2]
    ax.bar(["아이디어 1\n발현 ∩ CRISPR", "아이디어 2\n+ PRISM 약물"], values,
           color=[BLUE, ORANGE], width=0.5)
    for i, v in enumerate(values):
        ax.text(i, v + 20, f"n = {v:,}", ha="center", fontsize=7.5)
    ax.set_ylabel("학습 가능한 세포주 수")
    ax.set_ylim(0, max(values) * 1.17)
    ax.set_title(f"멀티태스크는 표본 {1 - n2 / n1:.0%}를 잃는다", loc="left")

    fig.tight_layout()
    fig.savefig(OUT, dpi=300, bbox_inches="tight")
    print(f"{OUT}  (n1={n1}, n2={n2}, genes={len(gs)})")


if __name__ == "__main__":
    main()
