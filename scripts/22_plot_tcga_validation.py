"""Figure 11 — DepMap 내부 vs TCGA 외부 검증.

damaging-only 기준으로 맞춘 두 성능을 나란히 놓는다. TP53 damaging
비율의 코호트 간 격차(방법론적 원인)도 함께 보여줘서, 하락폭을 그대로
"세포주→종양 일반화 실패"로 읽지 않도록 한다.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import pandas as pd

from src.config import REPO_ROOT
from src.viz.style import PHENOTYPE_COLORS, save, use_style

TABLES = REPO_ROOT / "results" / "tables"


def tp53_damaging_rates() -> list[float]:
    """두 코호트의 TP53 damaging 보유 비율을 원본에서 직접 계산한다.

    예전에는 [0.578, 0.124] 를 하드코딩해 뒀는데, 그 숫자가 어디서 나왔는지
    그림만 봐서는 알 수 없었다(실제로 "TCGA 근사값을 어떻게 냈나" 라는 질문을
    받았다). 데이터가 있으면 매번 다시 계산하고, 없을 때만 커밋된 값으로
    돌아간다.

    DepMap 은 VEP LofTool 기반 LikelyLoF 판정이고, TCGA 는 MC3 MAF 의 표준
    truncating variant class(src/data/tcga.py 의 LOF_CLASSES)로 근사한 것이다 —
    두 값은 정의가 완전히 같지 않다. 자세한 내용은
    docs/gdc/tcga_data_summary.md §4 참고.
    """
    from src.data.merge import load_cohort

    fallback = [0.578, 0.124]
    try:
        cohort = load_cohort()
        col = next(c for c in cohort.X.columns if c.startswith("TP53 (7157)_damaging"))
        depmap_rate = float(cohort.X[col].mean())
    except Exception as exc:                     # 데이터 미보유 환경
        print(f"  DepMap TP53 비율 계산 실패({exc.__class__.__name__}) — 커밋된 값 사용")
        return fallback

    tcga_path = REPO_ROOT / "data" / "gdc" / "tcga_damaging_matrix.parquet"
    if not tcga_path.exists():
        print("  tcga_damaging_matrix.parquet 없음 — TCGA 는 커밋된 값 사용")
        return [depmap_rate, fallback[1]]

    tcga_rate = float(pd.read_parquet(tcga_path, columns=["TP53"])["TP53"].mean())
    print(f"  TP53 damaging 비율 — DepMap {depmap_rate:.4f} / TCGA {tcga_rate:.4f}")
    return [depmap_rate, tcga_rate]


def main() -> int:
    use_style()
    summary = pd.read_csv(TABLES / "day21_tcga_validation_summary.csv")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))

    ax = axes[0]
    colors = ["#bfbfbf", PHENOTYPE_COLORS["wgd"]]
    bars = ax.bar(summary.stage.str.replace("(", "\n(", regex=False), summary.roc_auc,
                  color=colors, width=0.55)
    for b, v, n in zip(bars, summary.roc_auc, summary.n):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.015, f"{v:.3f}\n(n={n:,})",
                ha="center", fontsize=9)
    ax.axhline(0.5, color="#999", ls=":", lw=0.8, label="무작위 수준")
    ax.set_ylim(0.4, 0.9)
    ax.set_ylabel("ROC-AUC (WGD, damaging-only)")
    ax.set_title("(a) 내부 vs 외부 검증")
    ax.legend(fontsize=8)
    ax.tick_params(axis="x", labelsize=8.5)

    ax = axes[1]
    tp53 = pd.DataFrame({
        "cohort": ["DepMap\n(세포주)", "TCGA\n(환자 종양)"],
        "rate": tp53_damaging_rates(),
    })
    ax.bar(tp53.cohort, tp53.rate, color=["#bfbfbf", PHENOTYPE_COLORS["wgd"]], width=0.55)
    for i, v in enumerate(tp53.rate):
        ax.text(i, v + 0.02, f"{v:.1%}", ha="center", fontsize=9)
    ax.set_ylim(0, 0.7)
    ax.set_ylabel("TP53 damaging(근사) 비율")
    ax.set_title("(b) 격차의 방법론적 원인 — TP53")

    fig.suptitle(
        "Figure 11. TCGA 독립 코호트 검증 (WGD, damaging-only)\n"
        "(b)는 (a)의 하락폭 -0.168 을 '일반화 실패'로 단정하면 안 되는 이유:\n"
        "TP53 missense 2,786건(검증 코호트 10,261명)이 truncating-only 근사에서 전부 누락됨",
        y=1.12, fontsize=11,
    )
    fig.tight_layout()
    path = save(fig, "fig11_tcga_validation.png")
    print(f"저장: {path.name}")
    print(summary.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
