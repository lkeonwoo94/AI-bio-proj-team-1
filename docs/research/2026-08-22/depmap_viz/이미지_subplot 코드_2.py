#앞서 만든 이미지 subplot해서 wgd,cin,loh 한 그림에 넣는 코드
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

targets = {"wgd": "WGD", "cin": "CIN", "loh": "LoH"}
colors = {"wgd": "#c0504d", "cin": "#4f81bd", "loh": "#9bbb59"}

# 세 target의 결과를 미리 읽어서 x축 최댓값을 통일
tops = {}
max_val = 0
for target in targets:
    result = pd.read_csv(f"vis/association_{target}.csv")
    top30 = result.head(30).sort_values("fdr_q_value", ascending=False)
    top30["minus_log10_fdr"] = -np.log10(top30["fdr_q_value"].clip(lower=1e-300))
    tops[target] = top30
    max_val = max(max_val, top30["minus_log10_fdr"].max())

x_limit = (0, max_val * 1.05)  # 여유 5%

fig, axes = plt.subplots(1, 3, figsize=(18, 9))

for ax, (target, label) in zip(axes, targets.items()):
    top30 = tops[target]
    ax.barh(top30["feature"], top30["minus_log10_fdr"], color=colors[target])
    ax.axvline(-np.log10(0.05), color="#555", linestyle="--", linewidth=1, label="FDR = 0.05")
    ax.set_title(f"{label} 연관 유전자 (상위 30개)", fontsize=13)
    ax.set_xlabel("-log10(FDR 보정 p-value)")
    ax.set_xlim(*x_limit)
    ax.tick_params(axis="y", labelsize=8)
    if ax is axes[0]:
        ax.set_ylabel("변이 feature")
    ax.legend(fontsize=8)

fig.suptitle(" 유전자-표현형 통계적 연관성 (Chi-square/Fisher 검정, FDR 보정)", fontsize=15, y=1.02)
plt.tight_layout()
plt.savefig("vis/association_combined_kr.png", dpi=200, bbox_inches="tight")


import pandas as pd
import numpy as np
from pathlib import Path

# vis.py가 읽던 것과 같은 캐시 파일 위치 — 본인 환경에 맞게 확인
DATA_DIR = Path(r"D:\범부처\data\interim")

X_raw = pd.read_parquet(DATA_DIR / "cohort_X.parquet").astype(np.float32)
y = pd.read_parquet(DATA_DIR / "cohort_y.parquet")

# vis.py의 load_data()와 동일: mutation 빈도 1% 미만 feature 제거
min_prevalence = 0.01
prevalence = X_raw.mean(axis=0)
keep = prevalence[prevalence >= min_prevalence].index
X = X_raw.loc[:, keep]

# vis.py의 label_matrix()와 동일: wgd는 원래 이진값, cin/loh는 전체 중앙값 기준 이진화
labels = pd.DataFrame(index=y.index)
labels["wgd"] = y["wgd"].astype(int)
for target in ("cin", "loh"):
    labels[target] = (y[target] >= y[target].median()).astype(int)

print(f"X: {X.shape}, y: {y.shape}, labels: {labels.shape}")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.cross_decomposition import CCA
from sklearn.preprocessing import StandardScaler

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

n_svd = min(20, X.shape[1] - 1, X.shape[0] - 1)
mutation_scores = TruncatedSVD(n_components=n_svd, random_state=42).fit_transform(X)
mutation_scaled = StandardScaler().fit_transform(mutation_scores)

def run_and_get(Y_raw):
    Y_scaled = StandardScaler().fit_transform(Y_raw)
    cca = CCA(n_components=1, max_iter=2000)
    U, V = cca.fit_transform(mutation_scaled, Y_scaled)
    r = np.corrcoef(U[:, 0], V[:, 0])[0, 1]
    return U[:, 0], V[:, 0], r

# 이진화 버전 (vis.py 원래 방식: wgd 그대로, cin/loh는 median split)
Y_bin = labels[["wgd", "cin", "loh"]].to_numpy()
U_bin, V_bin, r_bin = run_and_get(Y_bin)

# 연속값 버전 (이진화 없이)
Y_cont = y[["wgd", "cin", "loh"]].to_numpy()
U_cont, V_cont, r_cont = run_and_get(Y_cont)

fig, axes = plt.subplots(1, 2, figsize=(12, 5.5))

axes[0].scatter(U_bin, V_bin, s=14, alpha=0.5, color="#4f81bd")
axes[0].set_title(f"이진화 라벨 사용\nr = {r_bin:.3f}", fontsize=12)

axes[1].scatter(U_cont, V_cont, s=14, alpha=0.5, color="#c0504d")
axes[1].set_title(f"연속값 라벨 사용\nr = {r_cont:.3f}", fontsize=12)

for ax in axes:
    ax.set_xlabel("mutation 패턴 점수 (canonical)")
    ax.set_ylabel("유전체 불안정성 점수 (canonical)")

fig.suptitle("그림 X. WGD·CIN·LOH 공유 축 검증 (CCA, 이진화 vs 연속값 비교)", fontsize=14, y=1.03)
plt.tight_layout()
plt.savefig("vis/cca_comparison_kr.png", dpi=200, bbox_inches="tight")


import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import re

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

targets = {"wgd": "WGD", "cin": "CIN", "loh": "LoH"}
columns = ["유전자", "OR", "95% CI", "p-value", "FDR q"]

def shorten_feature(name: str) -> str:
    name = re.sub(r"\s*\(\d+\)", "", name)
    return name.replace("_damaging", " (dmg)").replace("_hotspot", " (hs)")

def format_row(row):
    or_val = row["odds_ratio"]
    or_str = f"{or_val:.2f}" if np.isfinite(or_val) else "∞"
    ci_str = f"({row['odds_ratio_ci_low']:.1f}~{row['odds_ratio_ci_high']:.1f})"
    p_str = "< .001" if row["p_value"] < 0.001 else f"{row['p_value']:.3f}"
    q_str = "< .001" if row["fdr_q_value"] < 0.001 else f"{row['fdr_q_value']:.3f}"
    return [shorten_feature(row["feature"]), or_str, ci_str, p_str, q_str]

fig, axes = plt.subplots(1, 3, figsize=(20, 5.5))

for ax, (target, label) in zip(axes, targets.items()):
    result = pd.read_csv(f"vis/association_{target}.csv")
    top10 = result.head(10)
    rows = [format_row(r) for _, r in top10.iterrows()]

    ax.axis("off")
    table = ax.table(cellText=rows, colLabels=columns, loc="center", cellLoc="center",
                      colWidths=[0.30, 0.14, 0.24, 0.16, 0.16])
    table.auto_set_font_size(False)
    table.set_fontsize(9.5)
    table.scale(1, 1.6)

    for j in range(len(columns)):
        table[0, j].set_facecolor("#4f81bd")
        table[0, j].set_text_props(color="white", weight="bold")
    for i in range(1, len(rows) + 1):
        table[i, 0].set_text_props(ha="left")

    ax.set_title(f"{label} 연관 유전자 상위 10개", fontsize=13, pad=15)

fig.suptitle(" WGD·CIN·LOH 연관 유전자 상세 수치 (Odds Ratio, 95% CI)", fontsize=15, y=1.02)
plt.tight_layout()
plt.savefig("vis/association_tables_combined.png", dpi=200, bbox_inches="tight")


import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import umap.umap_ as umap

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

targets = {"wgd": "WGD", "cin": "CIN", "loh": "LoH"}
colors = {"-": "#4f81bd", "+": "#e76f51"}

umap_features = 80
X_umap = X.loc[:, X.mean(axis=0).sort_values(ascending=False).index[:umap_features]]

# mutation 데이터(X_umap)로 UMAP을 딱 한 번만 계산 -> 세 그림이 같은 좌표를 공유
reducer = umap.UMAP(n_neighbors=20, min_dist=0.25, metric="jaccard", random_state=42)
coords = reducer.fit_transform(X_umap.to_numpy(dtype=bool))

def padded_limits(values, fraction=0.05):
    low, high = float(np.nanmin(values)), float(np.nanmax(values))
    pad = max((high - low) * fraction, 0.1)
    return low - pad, high + pad

x_lim = padded_limits(coords[:, 0])
y_lim = padded_limits(coords[:, 1])

fig, axes = plt.subplots(1, 3, figsize=(18, 6))

for ax, (target, label) in zip(axes, targets.items()):
    status = labels[target].map({0: f"{label}-", 1: f"{label}+"})
    for suffix, color in colors.items():
        group = f"{label}{suffix}"
        idx = status.eq(group).to_numpy()
        ax.scatter(coords[idx, 0], coords[idx, 1], s=12, alpha=0.7,
                   color=color, label=f"{group} (n={idx.sum()})", linewidths=0)
    ax.set_title(f"{label} 상태별 mutation 패턴 분포", fontsize=13)
    ax.set_xlabel("UMAP 1")
    ax.set_ylabel("UMAP 2")
    ax.set_xlim(*x_lim)
    ax.set_ylim(*y_lim)
    ax.legend(fontsize=9)

fig.suptitle(" Mutation UMAP — WGD·CIN·LOH 상태별 분포", fontsize=15, y=1.02)
plt.tight_layout()
plt.savefig("vis/umap_status_combined.png", dpi=200, bbox_inches="tight")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
from pathlib import Path

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

OUTPUT_DIR = Path(r"D:\범부처\vis")
targets = {"wgd": "WGD", "cin": "CIN", "loh": "LoH"}

fig, axes = plt.subplots(1, 3, figsize=(20, 8))

for ax, (target, label) in zip(axes, targets.items()):
    img = Image.open(OUTPUT_DIR / f"selection_dendrogram_random_forest_{target}_panel10.png")
    ax.imshow(img)
    ax.axis("off")
    ax.set_title(f"{label} — 10-gene 패널 fold 선택 패턴", fontsize=13)

fig.suptitle("Fold별 feature selection 안정성 (Random Forest, 10-gene 패널)", fontsize=15, y=1.0)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "selection_dendrogram_combined.png", dpi=200, bbox_inches="tight")

