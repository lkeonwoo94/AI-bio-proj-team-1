"""Figure 7 — 암종 내부 학습 vs 암종 간 전이(LOLO).

세 패널로 나눈다.

  (a) 산점도: 점이 대각선에 붙으면 '전이 실패가 아니다' 라는 뜻
  (b) 라벨 정의 함정: internal 기준에서 보이던 CIN 이득이 external 에서 사라짐
  (c) WGD 암종별 비교 — 이진 label 이라 두 방식이 완전히 동일한 조건
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.config import REPO_ROOT
from src.viz.style import PHENOTYPE_COLORS, save, use_style

TABLES = REPO_ROOT / "results" / "tables"
TARGETS = ("wgd", "cin", "loh")
TARGET_LABEL = {"wgd": "WGD", "cin": "CIN", "loh": "LOH"}
MODEL = "random_forest"


def load(kind: str) -> pd.DataFrame:
    path = TABLES / f"day13b_within_vs_lolo_{MODEL}_{kind}.csv"
    if not path.exists():
        raise SystemExit(f"{path.name} 없음 — 11_lineage_specific.py 를 먼저 실행하세요.")
    return pd.read_csv(path)


def panel_scatter(ax, ext: pd.DataFrame) -> None:
    lo, hi = 0.35, 0.85
    ax.plot([lo, hi], [lo, hi], color="k", ls="--", lw=1, zorder=1)
    ax.fill_between([lo, hi], [lo, hi], hi, color="#4f81bd", alpha=0.05, zorder=0)
    ax.fill_between([lo, hi], lo, [lo, hi], color="#c0504d", alpha=0.05, zorder=0)

    for target in TARGETS:
        sub = ext[ext.target == target]
        ax.errorbar(sub.roc_auc_lolo, sub.roc_auc, yerr=sub.roc_auc_std,
                    fmt="o", ms=6, capsize=2, elinewidth=0.8, alpha=0.85,
                    color=PHENOTYPE_COLORS[target], label=TARGET_LABEL[target], zorder=3)

    # 양극단 사례만 이름을 단다 — 전부 달면 읽을 수 없다.
    for _, r in ext.iterrows():
        if abs(r["차이"]) > 0.08 or r.roc_auc_lolo > 0.75 or r.roc_auc_lolo < 0.45:
            ax.annotate(r.lineage, (r.roc_auc_lolo, r.roc_auc), fontsize=6.5,
                        xytext=(4, 4), textcoords="offset points", color="#444")

    ax.axhline(0.5, color="#999", ls=":", lw=0.8)
    ax.axvline(0.5, color="#999", ls=":", lw=0.8)
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_xlabel("LOLO — 다른 암종으로 학습 (ROC-AUC)")
    ax.set_ylabel("내부 학습 — 이 암종만으로 (ROC-AUC)")
    ax.set_title("(a) 점이 대각선 근처 = 전이 실패가 아님")
    ax.text(0.37, 0.815, "내부 학습이 유리", fontsize=7.5, color="#4f81bd")
    ax.text(0.545, 0.372, "전이가 유리", fontsize=7.5, color="#c0504d")
    ax.legend(fontsize=8, loc="lower right", title="오차막대: fold 표준편차",
              title_fontsize=7)
    ax.set_aspect("equal")


def panel_artifact(ax, internal: pd.DataFrame, ext: pd.DataFrame) -> None:
    x = np.arange(len(TARGETS))
    width = 0.36
    for i, (df, name, color) in enumerate(
        ((internal, "암종 내부 기준", "#bfbfbf"), (ext, "암종 외부 기준 (비교 가능)", "#4f81bd"))
    ):
        means = [df[df.target == t]["차이"].mean() for t in TARGETS]
        errs = [df[df.target == t]["차이"].sem() for t in TARGETS]
        bars = ax.bar(x + (i - 0.5) * width, means, width, yerr=errs, capsize=3,
                      label=name, color=color)
        for b, m in zip(bars, means):
            ax.text(b.get_x() + b.get_width() / 2, m + (0.006 if m >= 0 else -0.014),
                    f"{m:+.3f}", ha="center", fontsize=7.5)

    ax.axhline(0, color="k", lw=1)
    ax.set_xticks(x)
    ax.set_xticklabels([TARGET_LABEL[t] for t in TARGETS])
    ax.set_ylabel("내부 학습 - LOLO (ROC-AUC)")
    ax.set_title("(b) CIN 의 이득은 라벨 재정의가 만든 착시")
    ax.legend(fontsize=8)
    ax.set_ylim(-0.09, 0.12)


def panel_wgd(ax, ext: pd.DataFrame) -> None:
    sub = ext[ext.target == "wgd"].sort_values("roc_auc_lolo")
    y = np.arange(len(sub))

    for yi, (_, r) in zip(y, sub.iterrows()):
        better = r.roc_auc > r.roc_auc_lolo
        ax.plot([r.roc_auc_lolo, r.roc_auc], [yi, yi],
                color="#4f81bd" if better else "#c0504d", lw=1.5, alpha=0.6, zorder=1)
    ax.scatter(sub.roc_auc_lolo, y, s=42, color="#c0504d", label="LOLO (전이)", zorder=2)
    ax.scatter(sub.roc_auc, y, s=42, color="#4f81bd", label="내부 학습", zorder=2)

    ax.axvline(0.5, color="k", ls=":", lw=1, label="무작위 수준")
    ax.set_yticks(y)
    ax.set_yticklabels([f"{r.lineage} (n={int(r.n)})" for _, r in sub.iterrows()], fontsize=8)
    ax.set_xlabel("ROC-AUC")
    ax.set_title("(c) WGD — 이진 label 이라 조건이 완전히 동일")
    ax.legend(fontsize=8, loc="lower right")
    ax.set_xlim(0.35, 0.85)


def main() -> int:
    use_style()
    internal, ext = load("internal"), load("external")

    fig, axes = plt.subplots(1, 3, figsize=(17, 5.2),
                             gridspec_kw={"width_ratios": [1.05, 0.85, 1.1]})
    panel_scatter(axes[0], ext)
    panel_artifact(axes[1], internal, ext)
    panel_wgd(axes[2], ext)

    fig.suptitle(
        "Figure 7. 암종 내부 학습 vs 암종 간 전이 — Random Forest, 세포주 60개 이상 9종",
        y=1.02, fontsize=12,
    )
    fig.tight_layout()
    path = save(fig, "fig7_lineage_specific.png")

    print(f"저장: {path.name}")
    print("\n[평균 차이] 내부 학습 - LOLO")
    for t in TARGETS:
        print(f"  {TARGET_LABEL[t]}: internal {internal[internal.target == t]['차이'].mean():+.3f} "
              f"| external {ext[ext.target == t]['차이'].mean():+.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
