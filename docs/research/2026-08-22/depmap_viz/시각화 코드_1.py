"""원 mutation 기반 탐색 시각화: UMAP, 변이-표현형 검정, dendrogram, CCA.

실행 예시 (작업 폴더 D:\범부처 에서):
    python vis.py --target wgd --model random_forest --n-features 80

원본 DepMap mutation을 병합한 cohort_X 캐시(값은 원본 mutation matrix와 동일)를
사용한다. UMAP/CCA/유전자 검정에 outcome/model 기반 feature selection을 쓰지
않는다. mutation 빈도만으로 필터링하므로 이들은 전체 코호트의 *탐색적* 분석이며,
nested-CV 성능 추정치를 대체하지 않는다. CIN/LOH의 high/low는 전체 코호트 중앙값
기준이며, 그림과 연관성 검정용으로만 사용한다.
"""

from __future__ import annotations

import argparse
import sys
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT / "AI-bio-proj-team-1"
sys.path.insert(0, str(REPO))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import pdist
from scipy.stats import chi2_contingency, fisher_exact
from sklearn.cross_decomposition import CCA
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import StandardScaler

from src.config import REPO_ROOT
from src.viz.style import use_style

TABLES = REPO_ROOT / "results" / "tables"
OUTPUT_DIR = ROOT / "vis"
TARGETS = ("wgd", "cin", "loh")

# 같은 종류의 그림은 target이 달라도 동일한 눈금·크기·범례 형식을 사용한다.
UMAP_FIGSIZE = (10, 8)
ASSOCIATION_FIGSIZE = (10, 6)
ASSOCIATION_X_LIMIT = (0, 40)  # 현재 WGD/CIN/LOH의 최대 -log10(FDR)를 모두 포함
CCA_FIGSIZE = (12, 5)
LEGEND_FONTSIZE = 10
OUTPUT_DPI = 300  # 발표·문서용 PNG 해상도 고정


def padded_limits(values: np.ndarray, fraction: float = 0.05) -> tuple[float, float]:
    """여러 패널에서 공유할 수 있도록 데이터 범위에 여백을 더한 축 한계를 만든다."""
    low, high = float(np.nanmin(values)), float(np.nanmax(values))
    padding = max((high - low) * fraction, 0.1)
    return low - padding, high + padding


def save_figure(fig: plt.Figure, name: str) -> Path:
    """이번 탐색 분석 산출물만 workspace/vis 폴더에 저장한다."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / name
    fig.savefig(path, dpi=OUTPUT_DPI, bbox_inches="tight")
    plt.close(fig)
    return path


def bh_fdr(p_values: pd.Series) -> pd.Series:
    """Benjamini-Hochberg FDR q-value (외부 statsmodels 의존성 없음)."""
    p = p_values.to_numpy(dtype=float)
    order = np.argsort(p)
    ranked = p[order] * len(p) / np.arange(1, len(p) + 1)
    ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    q = np.empty_like(ranked)
    q[order] = np.minimum(ranked, 1.0)
    return pd.Series(q, index=p_values.index)


def label_matrix(y: pd.DataFrame) -> pd.DataFrame:
    """WGD는 원래 binary, CIN/LOH는 전체 코호트 중앙값으로 탐색용 이진화."""
    out = pd.DataFrame(index=y.index)
    out["wgd"] = y["wgd"].astype(int)
    for target in ("cin", "loh"):
        out[target] = (y[target] >= y[target].median()).astype(int)
    return out


def load_data(min_prevalence: float, umap_features: int):
    """원 mutation cohort를 outcome과 무관한 mutation 빈도로만 필터링한다.

    UMAP은 너무 많은 sparse binary feature에서 hairball이 되기 쉬워, 필터를
    통과한 mutation 중 코호트 빈도가 높은 ``umap_features``개로만 그린다.
    반면 association test와 CCA는 필터 통과 feature 전체를 사용한다.
    """
    x_path = ROOT / "data" / "interim" / "cohort_X.parquet"
    y_path = ROOT / "data" / "interim" / "cohort_y.parquet"
    g_path = ROOT / "data" / "interim" / "cohort_groups.parquet"
    X = pd.read_parquet(x_path).astype(np.float32)
    y = pd.read_parquet(y_path)
    lineage = pd.read_parquet(g_path)["lineage"].fillna("Unknown")
    if not (X.index.equals(y.index) and X.index.equals(lineage.index)):
        raise ValueError("cohort_X/y/groups의 ModelID index가 일치하지 않습니다.")
    prevalence = X.mean(axis=0)
    keep = prevalence[prevalence >= min_prevalence].sort_values(ascending=False)
    if keep.empty:
        raise ValueError(f"최소 변이 빈도 {min_prevalence:.3%}를 통과한 feature가 없습니다.")
    X_filtered = X.loc[:, keep.index]
    X_umap = X_filtered.iloc[:, :min(umap_features, X_filtered.shape[1])]
    feature_summary = pd.DataFrame({"feature": prevalence.index, "mutation_prevalence": prevalence.values})
    feature_summary["passed_frequency_filter"] = feature_summary.mutation_prevalence >= min_prevalence
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    feature_summary.sort_values("mutation_prevalence", ascending=False).to_csv(
        OUTPUT_DIR / "mutation_frequency_filter.csv", index=False
    )
    return X_filtered, X_umap, y, lineage


def plot_umap_by_lineage(X: pd.DataFrame, lineage: pd.Series, target: str) -> pd.DataFrame:
    """보조 그림: mutation UMAP을 lineage 색으로 표시한다."""
    try:
        import umap.umap_ as umap
    except ImportError as exc:
        raise ImportError(
            "UMAP을 위해 umap-learn이 필요합니다. `pip install umap-learn` 후 다시 실행하세요."
        ) from exc

    reducer = umap.UMAP(n_neighbors=20, min_dist=0.25, metric="jaccard", random_state=42)
    coords = reducer.fit_transform(X.to_numpy(dtype=bool))
    # 좌표와 lineage 모두 ModelID를 인덱스로 사용해야 boolean mask가 정확히 정렬된다.
    out = pd.DataFrame(
        {"UMAP1": coords[:, 0], "UMAP2": coords[:, 1], "lineage": lineage.values},
        index=X.index,
    )
    counts = lineage.value_counts()
    shown = counts.head(12).index
    plot_group = lineage.where(lineage.isin(shown), "Other lineage")

    fig, ax = plt.subplots(figsize=(11, 8))
    palette = dict(zip(list(shown) + ["Other lineage"], sns.color_palette("tab20", len(shown)).as_hex() + ["#bdbdbd"]))
    for group in list(shown) + ["Other lineage"]:
        idx = plot_group.eq(group)
        ax.scatter(out.loc[idx, "UMAP1"], out.loc[idx, "UMAP2"], s=13, alpha=0.72,
                   color=palette[group], label=f"{group} (n={idx.sum()})", linewidths=0)
    ax.set(title=f"Mutation UMAP by lineage ({target.upper()}, {X.shape[1]} most frequent mutations)",
           xlabel="UMAP 1", ylabel="UMAP 2")
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8, title="Top 12 lineages")
    save_figure(fig, f"umap_lineage_{target}.png")
    out.to_csv(OUTPUT_DIR / f"umap_coordinates_{target}.csv", index=True)
    return out


def plot_umap_by_target(X: pd.DataFrame, labels: pd.DataFrame, target: str) -> pd.DataFrame:
    """주 그림: mutation UMAP을 WGD/CIN/LOH 상태 색으로 표시한다."""
    try:
        import umap.umap_ as umap
    except ImportError as exc:
        raise ImportError(
            "UMAP을 위해 umap-learn이 필요합니다. `pip install umap-learn` 후 다시 실행하세요."
        ) from exc

    reducer = umap.UMAP(n_neighbors=20, min_dist=0.25, metric="jaccard", random_state=42)
    coords = reducer.fit_transform(X.to_numpy(dtype=bool))
    status = labels[target].map({0: f"{target.upper()}-", 1: f"{target.upper()}+"})
    out = pd.DataFrame(
        {"UMAP1": coords[:, 0], "UMAP2": coords[:, 1], target: labels[target].values,
         "status": status.values},
        index=X.index,
    )

    fig, ax = plt.subplots(figsize=UMAP_FIGSIZE)
    palette = {f"{target.upper()}-": "#4f81bd", f"{target.upper()}+": "#e76f51"}
    for group, color in palette.items():
        idx = out["status"].eq(group)
        ax.scatter(out.loc[idx, "UMAP1"], out.loc[idx, "UMAP2"], s=13, alpha=0.72,
                   color=color, label=f"{group} (n={idx.sum()})", linewidths=0)
    ax.set(title=f"Mutation UMAP by {target.upper()} status ({X.shape[1]} most frequent mutations)",
           xlabel="UMAP 1", ylabel="UMAP 2")
    # 동일 mutation 입력과 seed를 쓰는 WGD/CIN/LOH 그림의 좌표축을 통일한다.
    ax.set_xlim(*padded_limits(coords[:, 0]))
    ax.set_ylim(*padded_limits(coords[:, 1]))
    ax.legend(title=target.upper(), fontsize=LEGEND_FONTSIZE, title_fontsize=LEGEND_FONTSIZE)
    save_figure(fig, f"umap_{target}_status.png")
    out.to_csv(OUTPUT_DIR / f"umap_coordinates_{target}.csv", index=True)
    return out


def association_tests(X: pd.DataFrame, labels: pd.DataFrame, target: str) -> pd.DataFrame:
    """feature × binary phenotype의 Fisher/chi-square, OR와 95% CI, BH-FDR."""
    rows = []
    outcome = labels[target].to_numpy()
    for feature in X.columns:
        mutation = X[feature].to_numpy().astype(int)
        a = int(((mutation == 1) & (outcome == 1)).sum())
        b = int(((mutation == 1) & (outcome == 0)).sum())
        c = int(((mutation == 0) & (outcome == 1)).sum())
        d = int(((mutation == 0) & (outcome == 0)).sum())
        table = np.array([[a, b], [c, d]])
        expected = chi2_contingency(table, correction=False).expected_freq
        if (expected < 5).any():
            odds_ratio, p_value = fisher_exact(table)
            test = "Fisher exact"
        else:
            _, p_value, _, _ = chi2_contingency(table, correction=False)
            odds_ratio = (a * d) / (b * c) if b and c else np.inf
            test = "Chi-square"
        # 0 cell에서 OR/CI가 무한대가 되지 않도록 Haldane-Anscombe 보정.
        aa, bb, cc, dd = np.array([a, b, c, d], dtype=float) + 0.5
        log_or = np.log((aa * dd) / (bb * cc))
        se = np.sqrt(1 / aa + 1 / bb + 1 / cc + 1 / dd)
        rows.append({"feature": feature, "mutated_and_positive": a, "mutated_and_negative": b,
                     "unmutated_and_positive": c, "unmutated_and_negative": d, "test": test,
                     "odds_ratio": odds_ratio, "odds_ratio_ci_low": np.exp(log_or - 1.96 * se),
                     "odds_ratio_ci_high": np.exp(log_or + 1.96 * se), "p_value": p_value})
    result = pd.DataFrame(rows).sort_values("p_value").reset_index(drop=True)
    result["fdr_q_value"] = bh_fdr(result["p_value"])
    result.to_csv(OUTPUT_DIR / f"association_{target}.csv", index=False)

    top = result.head(min(30,len(result))).copy()
    top["minus_log10_fdr"] = -np.log10(top.fdr_q_value.clip(lower=1e-300))
   #fig, ax = plt.subplots(figsize=ASSOCIATION_FIGSIZE)
    fig, ax = plt.subplots(figsize=(ASSOCIATION_FIGSIZE[0], max(ASSOCIATION_FIGSIZE[1], 0.3 * len(top))))
    sns.barplot(data=top, y="feature", x="minus_log10_fdr", hue="test", dodge=False, ax=ax, palette="Set2")
    ax.axvline(-np.log10(0.05), color="#555", linestyle="--", linewidth=1, label="FDR = 0.05")
    ax.set(title=f"Mutation association with {target.upper()} (top {len(top)})",
           # 일부 Windows matplotlib 폰트에는 유니코드 minus(−) 글리프가 없다.
           xlabel="-log10(BH-FDR q value)", ylabel="Mutation feature")
    # 세 target의 효과 강도를 같은 눈금에서 비교한다.
    ax.set_xlim(*ASSOCIATION_X_LIMIT)
    ax.set_ylim(len(top) - 0.5, -0.5)
    ax.legend(fontsize=LEGEND_FONTSIZE, title_fontsize=LEGEND_FONTSIZE)
    save_figure(fig, f"association_{target}.png")
    return result


def plot_selection_dendrogram(model: str, target: str, panel_size: int) -> None:
    picks = pd.read_csv(TABLES / f"day12_panel_picks_{model}.csv")
    picks = picks[(picks.target == target) & (picks.panel_size == panel_size)]
    if picks.empty:
        raise ValueError(f"{target}, panel size {panel_size}의 fold별 panel pick이 없습니다.")
    matrix = pd.crosstab(picks.feature, picks.fold).reindex(columns=sorted(picks.fold.unique()), fill_value=0)
    # identical feature vectors가 있어도 계층 군집화를 안정적으로 수행할 수 있다.
    distances = pdist(matrix.to_numpy(), metric="jaccard")
    fig, ax = plt.subplots(figsize=(12, max(5, 0.35 * len(matrix))))
    if len(matrix) > 1:
        dendrogram(linkage(distances, method="average"), labels=matrix.index.tolist(), orientation="right", ax=ax)
    else:
        ax.text(0.5, 0.5, matrix.index[0], ha="center", va="center")
    ax.set(title=f"Fold selection-pattern dendrogram ({target.upper()}, {panel_size}-gene panel)",
           xlabel="Jaccard distance between fold-selection vectors")
    # Jaccard distance의 이론 범위는 0~1이므로 target별 그림에서도 고정한다.
    ax.set_xlim(0, 1)
    save_figure(fig, f"selection_dendrogram_{model}_{target}_panel{panel_size}.png")
    matrix.to_csv(OUTPUT_DIR / f"selection_matrix_{model}_{target}_panel{panel_size}.csv")


def run_cca(X: pd.DataFrame, labels: pd.DataFrame, n_components: int = 2) -> pd.DataFrame:
    """SVD로 sparse mutation을 축소한 뒤 CCA. WGD/CIN/LOH high-low label을 사용."""
    n_components = min(n_components, 3, X.shape[1])
    n_svd = min(20, X.shape[1] - 1, X.shape[0] - 1)
    mutation_scores = TruncatedSVD(n_components=n_svd, random_state=42).fit_transform(X)
    Y = StandardScaler().fit_transform(labels[list(TARGETS)])
    cca = CCA(n_components=n_components, max_iter=2000)
    U, V = cca.fit_transform(StandardScaler().fit_transform(mutation_scores), Y)
    correlations = [np.corrcoef(U[:, i], V[:, i])[0, 1] for i in range(n_components)]
    result = pd.DataFrame({"canonical_component": np.arange(1, n_components + 1), "correlation": correlations})
    result.to_csv(OUTPUT_DIR / "cca.csv", index=False)
    fig, axes = plt.subplots(1, n_components, figsize=CCA_FIGSIZE, squeeze=False)
    x_limits = padded_limits(U[:, :n_components])
    y_limits = padded_limits(V[:, :n_components])
    for i, ax in enumerate(axes.flat):
        ax.scatter(U[:, i], V[:, i], s=12, alpha=0.55, color="#4f81bd", linewidths=0)
        ax.set(title=f"CCA component {i + 1}: r={correlations[i]:.3f}",
               xlabel="Mutation canonical score", ylabel="Instability canonical score",
               xlim=x_limits, ylim=y_limits)
    save_figure(fig, "cca.png")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="random_forest")
    parser.add_argument("--target", choices=TARGETS, default="wgd")
    parser.add_argument("--min-prevalence", type=float, default=0.01,
                        help="원 mutation feature 유지 최소 비율 (기본 1%%)")
    parser.add_argument("--umap-features", type=int, default=80,
                        help="UMAP에 쓸 빈도 상위 mutation 개수 (기본 80)")
    parser.add_argument("--panel-size", type=int, default=10)
    parser.add_argument("--skip-umap", action="store_true", help="umap-learn 미설치 시 나머지 분석만 실행")
    args = parser.parse_args()

    use_style()
    X, X_umap, y, lineage = load_data(args.min_prevalence, args.umap_features)
    labels = label_matrix(y)
    if not args.skip_umap:
        # 이전 보조 그림: lineage에 따른 mutation 군집을 볼 때 사용한다.
        # plot_umap_by_lineage(X_umap, lineage, args.target)
        # 주 그림: mutation 공간에서 target high/low 또는 +/-의 분포를 확인한다.
        plot_umap_by_target(X_umap, labels, args.target)
    association = association_tests(X, labels, args.target)
    plot_selection_dendrogram(args.model, args.target, args.panel_size)
    cca = run_cca(X, labels)
    print(f"Frequency-filtered mutation features: {X.shape[1]} (prevalence >= {args.min_prevalence:.1%})")
    print(f"UMAP mutation features: {X_umap.shape[1]} (most frequent among filtered features)")
    print(f"Output folder: {OUTPUT_DIR}")
    print(f"Association table: {OUTPUT_DIR / f'association_{args.target}.csv'}")
    print(f"FDR < 0.05: {(association.fdr_q_value < 0.05).sum()} features")
    print("CCA correlations:", ", ".join(f"{x:.3f}" for x in cca.correlation))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
