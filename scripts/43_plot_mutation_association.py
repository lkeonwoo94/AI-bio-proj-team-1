"""Day 43 — mutation 연관성 검정 결과 시각화 (psh03 탐색 분석 adapt).

원본: docs/research/2026-08-22/depmap_viz/이미지_subplot 코드_2.py 의
association 관련 부분(팀원 psh03 제공). Figure 21 (WGD/CIN/LOH 상위 30개
연관 유전자 막대그래프), Figure 22 (상위 10개 상세 수치 표)를 만든다.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.config import REPO_ROOT
from src.viz.style import PHENOTYPE_COLORS, save, use_style

TABLES = REPO_ROOT / "results" / "tables"
TARGETS = {"wgd": "WGD", "cin": "CIN", "loh": "LOH"}


def shorten_feature(name: str) -> str:
    name = re.sub(r"\s*\(\d+\)", "", name)
    return name.replace("_damaging", " (dmg)").replace("_hotspot", " (hs)")


def load_results() -> dict[str, pd.DataFrame]:
    out = {}
    for target in TARGETS:
        path = TABLES / f"day42_association_{target}.csv"
        if not path.exists():
            raise SystemExit(f"{path.name} 없음 — 먼저 42_mutation_association.py 를 실행하세요.")
        out[target] = pd.read_csv(path)
    return out


def plot_bar(results: dict[str, pd.DataFrame]) -> Path:
    """Figure 21. 표현형별 상위 30개 연관 유전자 (-log10 FDR)."""
    use_style()
    tops = {}
    max_val = 0.0
    for target, result in results.items():
        top30 = result.head(30).copy().sort_values("fdr_q_value", ascending=False)
        top30["minus_log10_fdr"] = -np.log10(top30.fdr_q_value.clip(lower=1e-300))
        top30["short_feature"] = top30.feature.map(shorten_feature)
        tops[target] = top30
        max_val = max(max_val, top30.minus_log10_fdr.max())
    x_limit = (0, max_val * 1.05)

    fig, axes = plt.subplots(1, 3, figsize=(18, 9))
    for ax, target in zip(axes, TARGETS):
        top30 = tops[target]
        ax.barh(top30.short_feature, top30.minus_log10_fdr, color=PHENOTYPE_COLORS[target])
        ax.axvline(-np.log10(0.05), color="#555", ls="--", lw=1, label="FDR = 0.05")
        ax.set_title(f"{TARGETS[target]} 연관 유전자 (상위 30개)", fontsize=13)
        ax.set_xlabel("-log10(BH-FDR q value)")
        ax.set_xlim(*x_limit)
        ax.tick_params(axis="y", labelsize=8)
        if ax is axes[0]:
            ax.set_ylabel("변이 feature")
        ax.legend(fontsize=8)

    fig.suptitle("Figure 21. 유전자-표현형 통계적 연관성 (Chi-square/Fisher 검정, BH-FDR 보정)",
                 y=1.02, fontsize=14)
    fig.tight_layout()
    return save(fig, "fig21_mutation_association.png")


def format_row(row: pd.Series) -> list[str]:
    or_val = row.odds_ratio
    or_str = f"{or_val:.2f}" if np.isfinite(or_val) else "inf"
    ci_str = f"({row.odds_ratio_ci_low:.1f}~{row.odds_ratio_ci_high:.1f})"
    p_str = "< .001" if row.p_value < 0.001 else f"{row.p_value:.3f}"
    q_str = "< .001" if row.fdr_q_value < 0.001 else f"{row.fdr_q_value:.3f}"
    return [shorten_feature(row.feature), or_str, ci_str, p_str, q_str]


def plot_tables(results: dict[str, pd.DataFrame]) -> Path:
    """Figure 22. 표현형별 상위 10개 연관 유전자 상세 수치(OR, 95% CI)."""
    use_style()
    columns = ["유전자", "OR", "95% CI", "p-value", "FDR q"]
    fig, axes = plt.subplots(1, 3, figsize=(20, 5.5))

    for ax, target in zip(axes, TARGETS):
        top10 = results[target].head(10)
        rows = [format_row(r) for _, r in top10.iterrows()]
        ax.axis("off")
        table = ax.table(cellText=rows, colLabels=columns, loc="center", cellLoc="center",
                          colWidths=[0.30, 0.14, 0.24, 0.16, 0.16])
        table.auto_set_font_size(False)
        table.set_fontsize(9.5)
        table.scale(1, 1.6)
        for j in range(len(columns)):
            table[0, j].set_facecolor(PHENOTYPE_COLORS[target])
            table[0, j].set_text_props(color="white", weight="bold")
        for i in range(1, len(rows) + 1):
            table[i, 0].set_text_props(ha="left")
        ax.set_title(f"{TARGETS[target]} 연관 유전자 상위 10개", fontsize=13, pad=15)

    fig.suptitle("Figure 22. WGD·CIN·LOH 연관 유전자 상세 수치 (Odds Ratio, 95% CI)",
                 y=1.02, fontsize=14)
    fig.tight_layout()
    return save(fig, "fig22_mutation_association_tables.png")


def main() -> int:
    results = load_results()
    path1 = plot_bar(results)
    path2 = plot_tables(results)
    print(f"저장: {path1.name}, {path2.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
