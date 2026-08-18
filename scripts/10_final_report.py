"""Day 14 — 결과 통합 (README §20, §26).

Day 10~13 산출물을 모아 최종 결론에서 답해야 하는 다섯 질문(§26)에
현재 데이터가 무엇을 말하는지 정리한다.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src.config import REPO_ROOT

TABLES = REPO_ROOT / "results" / "tables"
TARGET_LABEL = {"wgd": "WGD", "cin": "CIN", "loh": "LOH"}


def _read(name: str) -> pd.DataFrame | None:
    path = TABLES / name
    return pd.read_csv(path) if path.exists() else None


def q1_predictable() -> None:
    print("① DNA mutation 만으로 WGD/CIN/LOH 를 예측할 수 있었는가?")
    df = _read("day10_model_comparison.csv")
    if df is None:
        print("   (06_compare_models.py 필요)\n")
        return
    best = df.sort_values("roc_auc", ascending=False).groupby("target").head(1)
    for _, r in best.iterrows():
        verdict = "가능" if r.roc_auc >= 0.7 else "제한적"
        print(f"   {TARGET_LABEL[r.target]}: ROC-AUC {r.roc_auc:.3f} ({r.model}) -> {verdict}")
    print()


def q2_best_model() -> None:
    print("② 어떤 모델이 가장 안정적이었는가?")
    df = _read("day10_model_comparison.csv")
    if df is None:
        print("   (06_compare_models.py 필요)\n")
        return
    rank = df.groupby("model").roc_auc.mean().sort_values(ascending=False)
    for model, score in rank.items():
        print(f"   {model:16s} 평균 ROC-AUC {score:.3f}")
    print()


def q3_important_mutations() -> None:
    print("③ 어떤 mutation 이 반복적으로 선택되었는가?")
    cross = _read("day11_cross_phenotype_elastic_net.csv")
    if cross is None:
        print("   (07_aggregate_selection.py 필요)\n")
        return
    top = cross.head(8)
    for _, r in top.iterrows():
        gene = r.feature.split(" (")[0]
        kind = "hotspot" if r.feature.endswith("_hotspot") else "damaging"
        print(f"   {gene:10s} ({kind:8s}) 평균 선택빈도 {r.mean_freq:.2f} "
              f"| {int(r.n_phenotypes)}개 표현형 공통")
    print()


def q4_minimal_panel() -> None:
    print("④ 몇 개까지 줄여도 성능이 유지되었는가?")
    df = _read("day12_panel_metrics_elastic_net.csv")
    if df is None:
        print("   (08_panel_curve.py 필요)\n")
        return
    df["panel_size"] = df.panel_size.astype(str)
    pivot = df.pivot_table(index="target", columns="panel_size", values="roc_auc", aggfunc="mean")
    for target in pivot.index:
        full = pivot.loc[target, "all"]
        parts = []
        for k in ("5", "10", "20", "50"):
            if k in pivot.columns:
                parts.append(f"{k}개 {pivot.loc[target, k] / full:.0%}")
        print(f"   {TARGET_LABEL[target]}: 전체 {full:.3f} 대비 — " + " | ".join(parts))

    stab = _read("day12_panel_stability_elastic_net.csv")
    if stab is not None:
        print("\n   패널 안정성 (fold 간 Jaccard):")
        piv = stab.pivot(index="target", columns="panel_size", values="jaccard")
        print("   " + piv.round(2).to_string().replace("\n", "\n   "))
    print()


def q5_lineage() -> None:
    print("⑤ 다른 cancer lineage 에서도 유지되었는가?")
    cmp_ = _read("day13_lineage_comparison.csv")
    if cmp_ is None:
        print("   (09_lineage_validation.py 필요)\n")
        return
    cmp_ = cmp_.set_index(cmp_.columns[0])
    for target, r in cmp_.iterrows():
        delta = r.get("차이", r.get("group", 0) - r.get("random", 0))
        verdict = "유지" if delta > -0.05 else "감소 — 암종 의존 가능성"
        print(f"   {TARGET_LABEL.get(target, target)}: random {r['random']:.3f} -> "
              f"group {r['group']:.3f} ({delta:+.3f}) {verdict}")

    lolo = _read("day13_lolo_by_lineage.csv")
    if lolo is not None:
        worst = lolo.groupby("held_out_lineage").roc_auc.mean().nsmallest(3)
        print("\n   LOLO 최저 암종: " + ", ".join(f"{k} {v:.3f}" for k, v in worst.items()))
    print()


def main() -> int:
    print("=" * 70)
    print("README §26 — 최종 결론에서 답해야 하는 다섯 질문")
    print("=" * 70 + "\n")
    q1_predictable()
    q2_best_model()
    q3_important_mutations()
    q4_minimal_panel()
    q5_lineage()
    print("=" * 70)
    print("주의: 이 패널은 임상 확정 바이오마커가 아니라 DepMap 내부 검증으로")
    print("      도출된 연구용 후보다 (README §27).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
