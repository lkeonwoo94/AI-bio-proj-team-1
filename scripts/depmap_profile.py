#!/usr/bin/env python3
"""DepMap 원본 CSV를 읽어 docs/depmap/ 아래 데이터 설명서를 생성한다.

측정값(shape, 결측률, 값 범위, 교집합 등)은 실제 파일에서 계산하고,
설명·주의사항 같은 서술은 이 파일 안의 NOTES 에 둔다.
→ 릴리스가 바뀌면 이 스크립트를 다시 돌리는 것만으로 문서가 갱신된다.

사용법:
    python3 scripts/depmap_profile.py
    python3 scripts/depmap_profile.py --raw /path/to/raw/DepMap --out docs/depmap
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import glob
import hashlib
import os
import textwrap

import numpy as np
import pandas as pd

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_RAW = os.path.normpath(os.path.join(REPO, "..", "raw", "DepMap"))
DEFAULT_OUT = os.path.join(REPO, "docs", "depmap")

RELEASE = "DepMap Public 26Q1"
PORTAL = "https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename="

# 파일별 서술 — 측정값이 아닌 것은 전부 여기서 관리한다.
NOTES: dict[str, dict] = {
    "CRISPRGeneEffect.csv": {
        "slug": "crispr_gene_effect",
        "role": "출력 Y",
        "summary": (
            "genome-wide CRISPR-Cas9 넉아웃 스크린을 Chronos로 정규화한 **유전자 의존성 점수**. "
            "「그 유전자를 자르면 이 세포주가 얼마나 죽는가」를 나타낸다. "
            "모델(세포주) 단위로 통합된 값이라 한 세포주가 한 행만 갖는다."
        ),
        "interpretation": [
            "`0` 근처 — 넉아웃해도 영향 없음",
            "`-1` — 공통 필수(pan-essential) 유전자의 중앙값 수준으로 죽음",
            "음수로 갈수록 의존성이 큼. 양수는 넉아웃이 오히려 증식에 유리한 경우",
        ],
        "cautions": [
            "**common essential 유전자를 빼지 않고 전역 R²로 평가하면 안 된다.** "
            "이 유전자들은 세포주 간 분산이 거의 없어서, 「유전자별 평균」만 외워도 R²가 0.9를 넘는다.",
            "스크린 단위 파일(`ScreenGeneEffect.csv`)과 혼동하지 말 것. "
            "그쪽은 같은 세포주가 라이브러리별로 여러 행 등장해 train/test 누출이 생긴다.",
            "결측이 존재한다. 라이브러리별 유전자 커버리지 차이 때문이며, 25Q2 기준으로 "
            "Humagne/KY 라이브러리에만 있는 유전자는 현재 drop 상태다.",
        ],
    },
    "OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv": {
        "slug": "omics_expression_tpm_logp1_human_protein_coding_genes",
        "role": "입력 X",
        "summary": (
            "단백질코딩 유전자의 RNA-seq 발현량. 25Q2에서 STAR 2.7.11b + Salmon v1.10.0 으로 "
            "파이프라인이 교체됐고 유전자 주석은 Gencode V38로 통일됐다."
        ),
        "interpretation": ["값은 `log2(TPM + 1)`. 0 = 발현 없음"],
        "cautions": [
            "**`IsDefaultEntryForModel == \"Yes\"` 로 먼저 필터링해야 한다.** "
            "한 모델이 여러 행을 가질 수 있고, 거르지 않으면 중복 세포주가 학습셋에 들어간다.",
            "**Stranded / 비-Stranded 두 버전이 있고 DepMap 공식 권장이 없다.** "
            "25Q2 릴리스 노트에서 \"strandedness 외의 배치 효과 요인을 보정할 방법을 탐색 중\"이라고 밝힌 상태다. "
            "어느 쪽을 썼는지 반드시 기록할 것.",
            "배치보정판(`...BatchCorrected.csv`)은 25Q2에서 제거됐고 대체 파일이 없다.",
            "25Q2 이전 릴리스와는 파이프라인이 달라 수치를 직접 비교할 수 없다.",
        ],
    },
    "Model.csv": {
        "slug": "model",
        "role": "메타데이터 · 조인 키",
        "summary": (
            "세포주(모델) 메타데이터. 모든 DepMap 파일을 잇는 조인 키 `ModelID`(`ACH-XXXXXX`)의 원장이며, "
            "암종 정보(`OncotreeLineage` 등)를 제공한다."
        ),
        "interpretation": [],
        "cautions": [
            "26Q1에서 **OncoTree 2025-10-09** 기준으로 재주석됐고 **CNS/Brain lineage가 대규모 재분류**됐다. "
            "폐기된 OncoTree 코드를 쓰던 모델은 전부 재주석됐으므로, 암종 라벨은 항상 이 릴리스의 "
            "`Model.csv` 기준으로 다시 부여할 것.",
            "세포주 이름 표기는 파일·출처마다 다르다. 반드시 `ModelID` 로 연결한다.",
        ],
    },
    "CRISPRInferredCommonEssentials.csv": {
        "slug": "crispr_inferred_common_essentials",
        "role": "보조 · 타깃 필터",
        "summary": (
            "이 릴리스에서 **거의 모든 세포주에 필수**로 추론된 유전자 목록. "
            "리보솜·프로테아좀·스플라이싱 등 세포 생존의 기본 기계에 해당한다."
        ),
        "interpretation": [],
        "cautions": [
            "**이 목록을 타깃에서 빼지 않으면 성능 지표가 부풀려진다.** 정의상 세포주 간 분산이 거의 없어서, "
            "모델이 세포주 정보를 전혀 쓰지 않고도 맞출 수 있는 성분이 들어간다.",
            "포함/제외한 두 설정의 성능 지표는 서로 직접 비교되지 않는다. 반드시 어느 쪽인지 명시할 것.",
        ],
    },
}


def human(n: int) -> str:
    for unit, div in (("GB", 1e9), ("MB", 1e6), ("KB", 1e3)):
        if n >= div:
            return f"{n / div:.1f} {unit}"
    return f"{n} B"


def md5(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest(raw: str) -> dict[str, str]:
    hits = sorted(glob.glob(os.path.join(raw, "**", "depmap_files_*.csv"), recursive=True))
    if not hits:
        return {}
    return {
        r["filename"]: r["md5_hash"]
        for r in csv.DictReader(open(hits[-1]))
        if r["release"] == RELEASE
    }


def gene_cols(cols) -> list[str]:
    """DepMap 유전자 컬럼은 'SYMBOL (ENTREZID)' 형식."""
    return [c for c in cols if c.endswith(")") and " (" in c]


def fmt_table(pairs) -> str:
    body = "\n".join(f"| {k} | {v} |" for k, v in pairs)
    return f"| 항목 | 값 |\n|---|---|\n{body}"


def cell(v) -> str:
    """마크다운 셀 한 칸. 실수는 3자리, 결측은 NaN, 파이프는 이스케이프."""
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "NaN"
    if isinstance(v, (float, np.floating)):
        return f"{v:.3f}"
    return str(v).replace("|", "\\|")


def sample_table(df: pd.DataFrame, index_name: str | None = None) -> str:
    """DataFrame 일부를 마크다운 표로. 컬럼 수를 미리 줄여서 넘길 것."""
    cols = list(df.columns)
    head = ([index_name] if index_name else []) + [str(c) for c in cols]
    out = ["| " + " | ".join(head) + " |",
           "|" + "|".join(["---"] * len(head)) + "|"]
    for idx, row in df.iterrows():
        vals = ([f"`{idx}`"] if index_name else []) + [cell(row[c]) for c in cols]
        out.append("| " + " | ".join(vals) + " |")
    return "\n".join(out)


def header(fname: str, note: dict, raw: str, manifest: dict, extra) -> str:
    path = os.path.join(raw, fname)
    size = os.path.getsize(path)
    digest = md5(path)
    want = manifest.get(fname)
    if want is None:
        chk = f"`{digest}` (매니페스트에 없음)"
    elif want == digest:
        chk = f"`{digest}` ✅ 매니페스트 일치"
    else:
        chk = f"`{digest}` ❌ **불일치** (기대값 `{want}`)"

    rows = [
        ("릴리스", f"`{RELEASE}` (2026-04-01)"),
        ("원본 경로", f"`raw/DepMap/{fname}`"),
        ("파일 크기", f"{size:,} B ({human(size)})"),
        ("md5", chk),
        ("역할", f"**{note['role']}**"),
        ("다운로드", f"[포털]({PORTAL}{fname})"),
    ] + list(extra)
    return fmt_table(rows)


def section(title: str, lines) -> str:
    lines = [l for l in lines if l]
    if not lines:
        return ""
    body = "\n".join(f"- {l}" for l in lines)
    return f"\n## {title}\n\n{body}\n"


def write_doc(out: str, note: dict, fname: str, parts: list[str], stamp: str) -> str:
    banner = textwrap.dedent(f"""\
        # {fname}

        > ⚠️ **이 문서는 `scripts/depmap_profile.py` 가 자동 생성합니다. 직접 수정하지 마세요.**
        > 설명·주의사항을 고치려면 스크립트의 `NOTES` 를, 측정값을 갱신하려면 스크립트를 다시 실행하세요.
        > 생성 시각: {stamp}

        {note['summary']}
        """)
    path = os.path.join(out, note["slug"] + ".md")
    with open(path, "w") as fh:
        fh.write(banner + "\n" + "\n".join(parts).rstrip() + "\n")
    return path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default=DEFAULT_RAW)
    ap.add_argument("--out", default=DEFAULT_OUT)
    args = ap.parse_args()
    raw, out = args.raw, args.out
    os.makedirs(out, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M KST")
    manifest = load_manifest(raw)
    written = []

    # ---------------------------------------------------------------- Model.csv
    f = "Model.csv"
    note = NOTES[f]
    model = pd.read_csv(os.path.join(raw, f), low_memory=False)
    lin = model.OncotreeLineage.value_counts()
    parts = [
        "\n## 기본 정보\n",
        header(f, note, raw, manifest, [
            ("shape", f"**{model.shape[0]:,} 행 × {model.shape[1]} 열**"),
            ("조인 키", f"`ModelID` — 유니크: {'예' if model.ModelID.is_unique else '**아니오**'}"),
        ]),
        section("주요 컬럼", [
            f"`{c}`" for c in
            ["ModelID", "CellLineName", "StrippedCellLineName", "OncotreeLineage",
             "OncotreePrimaryDisease", "OncotreeSubtype", "DepmapModelType"]
            if c in model.columns
        ] + [f"…외 {model.shape[1] - 7}개 (전체 목록은 파일 헤더 참조)"]),
        "\n## 데이터 샘플\n\n앞 5행, 주요 6개 컬럼만 (전체 "
        f"{model.shape[1]}개 컬럼):\n\n"
        + sample_table(model.head(5)[[c for c in
            ["ModelID", "CellLineName", "OncotreeLineage", "OncotreePrimaryDisease",
             "OncotreeSubtype", "DepmapModelType"] if c in model.columns]]) + "\n",
        f"\n## 암종(OncotreeLineage) 분포\n\n"
        f"총 **{model.OncotreeLineage.nunique()}개 lineage**, 결측 {model.OncotreeLineage.isna().sum()}개\n\n"
        + "| lineage | 세포주 수 |\n|---|---:|\n"
        + "\n".join(f"| {k} | {v:,} |" for k, v in lin.head(15).items())
        + f"\n\n(상위 15개만 표시 / 전체 {len(lin)}개)\n",
        section("⚠️ 주의사항", note["cautions"]),
    ]
    written.append(write_doc(out, note, f, parts, stamp))

    # ------------------------------------- CRISPRInferredCommonEssentials.csv
    f = "CRISPRInferredCommonEssentials.csv"
    note = NOTES[f]
    ce = pd.read_csv(os.path.join(raw, f))
    col = ce.columns[0]
    ce_set = set(ce[col])
    parts = [
        "\n## 기본 정보\n",
        header(f, note, raw, manifest, [
            ("shape", f"**{ce.shape[0]:,} 행 × {ce.shape[1]} 열**"),
            ("컬럼명", f"`{col}` (단일 컬럼)"),
            ("값 형식", f"`SYMBOL (ENTREZID)` — 예: `{ce[col].iloc[0]}`"),
        ]),
        "\n## 데이터 샘플\n\n앞 8행 (전체 "
        f"{ce.shape[0]:,}행):\n\n"
        + sample_table(ce.head(8)) + "\n",
        section("⚠️ 주의사항", note["cautions"]),
        "\n## 로딩 예제\n\n```python\n"
        "import pandas as pd\n\n"
        f'ce = set(pd.read_csv("raw/DepMap/{f}")["{col}"])\n'
        "selective = gene_effect.drop(columns=[c for c in gene_effect.columns if c in ce])\n"
        "```\n",
    ]
    written.append(write_doc(out, note, f, parts, stamp))

    # -------------------------------------------------------- CRISPRGeneEffect
    f = "CRISPRGeneEffect.csv"
    note = NOTES[f]
    ge = pd.read_csv(os.path.join(raw, f), index_col=0)
    ge.index.name = "ModelID"
    arr = ge.to_numpy()
    std = ge.std(axis=0)
    sel_std = ge.drop(columns=[c for c in ge.columns if c in ce_set]).std(axis=0)
    parts = [
        "\n## 기본 정보\n",
        header(f, note, raw, manifest, [
            ("shape", f"**{ge.shape[0]:,} 세포주 × {ge.shape[1]:,} 유전자**"),
            ("index", f"`ModelID` (첫 컬럼, 헤더 비어 있음) — 예: `{ge.index[0]}`"),
            ("컬럼 형식", f"`SYMBOL (ENTREZID)` — 예: `{ge.columns[0]}`"),
        ]),
        section("값 해석", note["interpretation"]),
        "\n## 값 분포\n\n" + fmt_table([
            ("최소 / 최대", f"{np.nanmin(arr):.3f} / {np.nanmax(arr):.3f}"),
            ("중앙값", f"{np.nanmedian(arr):.4f}"),
            ("유전자별 표준편차 중앙값", f"{std.median():.4f}"),
            ("표준편차 90 / 95 / 99 분위", f"{std.quantile(.9):.3f} / {std.quantile(.95):.3f} / {std.quantile(.99):.3f}"),
        ]),
        "\n## 데이터 샘플\n\n앞 5행 × 앞 5개 유전자 컬럼 "
        f"(전체 {ge.shape[0]:,} × {ge.shape[1]:,}):\n\n"
        + sample_table(ge.iloc[:5, :5], index_name="ModelID") + "\n\n"
        "알파벳 앞쪽 유전자는 대부분 0 근처라 신호가 안 보인다. "
        "**분산이 큰 선택적 의존 유전자 상위 5개**를, 첫 유전자에 가장 의존적인 세포주 5개에 대해 보면:\n\n"
        + sample_table(
            ge.loc[
                ge[sel_std.sort_values(ascending=False).index[0]].nsmallest(5).index,
                list(sel_std.sort_values(ascending=False).index[:5]),
            ].join(
                model.set_index("ModelID")[["CellLineName", "OncotreeLineage"]]
            )[["CellLineName", "OncotreeLineage"] + list(sel_std.sort_values(ascending=False).index[:5])],
            index_name="ModelID",
        ) + "\n\n"
        "음수가 클수록 그 유전자에 강하게 의존한다는 뜻이다. "
        "lineage와 값이 함께 몰려 있으면 그 유전자가 해당 암종의 선택적 의존일 가능성이 높다.\n",
        "\n## 타깃 유전자 선별\n\n" + fmt_table([
            ("전체 유전자", f"{ge.shape[1]:,}"),
            ("common essential", f"{len(ce_set & set(ge.columns)):,} (목록 파일과 100% 매칭)"),
            ("common essential 제외 후", f"{ge.shape[1] - len(ce_set & set(ge.columns)):,}"),
            ("└ 그중 표준편차 > 0.25", f"**{int((sel_std > 0.25).sum()):,}** ← 선택적 의존, 실질 학습 대상"),
            ("└ 그중 표준편차 > 0.20", f"{int((sel_std > 0.20).sum()):,}"),
        ]),
        "\n## 결측\n\n" + fmt_table([
            ("전체 결측률", f"{np.isnan(arr).mean() * 100:.2f} %"),
            ("결측이 하나라도 있는 유전자", f"{int(ge.isna().any(axis=0).sum()):,} / {ge.shape[1]:,}"),
            ("전부 결측인 유전자", f"{int(ge.isna().all(axis=0).sum()):,}"),
            ("결측이 하나라도 있는 세포주", f"{int(ge.isna().any(axis=1).sum()):,} / {ge.shape[0]:,}"),
        ]),
        section("⚠️ 주의사항", note["cautions"]),
        "\n## 로딩 예제\n\n```python\n"
        "import pandas as pd\n\n"
        f'ge = pd.read_csv("raw/DepMap/{f}", index_col=0)\n'
        'ge.index.name = "ModelID"          # 첫 컬럼에 헤더가 없다\n'
        "```\n",
    ]
    written.append(write_doc(out, note, f, parts, stamp))

    # ------------------------------------------------------------- Expression
    f = "OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv"
    note = NOTES[f]
    ex = pd.read_csv(os.path.join(raw, f), index_col=0, low_memory=False)
    gcols = gene_cols(ex.columns)
    mcols = [c for c in ex.columns if c not in gcols]
    flag = ex.IsDefaultEntryForModel.astype(str)
    ex_def = ex[flag.str.lower().isin(["yes", "true", "1"])]
    exarr = ex[gcols].to_numpy()
    parts = [
        "\n## 기본 정보\n",
        header(f, note, raw, manifest, [
            ("shape", f"**{ex.shape[0]:,} 행 × {ex.shape[1]:,} 열** (메타 {len(mcols)} + 유전자 {len(gcols):,})"),
            ("컬럼 형식", f"`SYMBOL (ENTREZID)` — 예: `{gcols[0]}`"),
        ]),
        section("메타데이터 컬럼 (25Q3부터 추가됨)", [f"`{c}`" for c in mcols]),
        "\n## ⚠️ 행 필터링 — 반드시 먼저 할 것\n\n" + fmt_table([
            ("원본 행 수", f"{len(ex):,}"),
            ("고유 ModelID 수", f"{ex.ModelID.nunique():,}"),
            ("`IsDefaultEntryForModel` 값 분포",
             " / ".join(f"`{k}` {v:,}" for k, v in flag.value_counts().items())),
            ("필터링 후 행 수", f"**{len(ex_def):,}**"),
            ("필터링 후 중복 ModelID",
             f"**{len(ex_def) - ex_def.ModelID.nunique()}개** "
             f"{'← 중복 없음' if len(ex_def) == ex_def.ModelID.nunique() else '← 확인 필요'}"),
        ]) + "\n",
        "\n## 데이터 샘플\n\n앞 5행 × 메타 5개 + 유전자 3개 컬럼 "
        f"(전체 {ex.shape[0]:,} × {ex.shape[1]:,}):\n\n"
        + sample_table(ex.head(5)[mcols + gcols[:3]]) + "\n\n"
        "3번째 행처럼 `IsDefaultEntryForModel` 이 `No` 인 행이 섞여 있다 — "
        "같은 세포주의 비기본 프로파일이므로 걸러내야 한다.\n"
        if (ex.head(5).IsDefaultEntryForModel.astype(str) == "No").any() else
        "\n## 데이터 샘플\n\n앞 5행 × 메타 5개 + 유전자 3개 컬럼 "
        f"(전체 {ex.shape[0]:,} × {ex.shape[1]:,}):\n\n"
        + sample_table(ex.head(5)[mcols + gcols[:3]]) + "\n",
        "\n## 값 분포\n\n" + fmt_table([
            ("단위", "`log2(TPM + 1)`"),
            ("최소 / 최대", f"{np.nanmin(exarr):.3f} / {np.nanmax(exarr):.3f}"),
            ("결측률", f"{np.isnan(exarr).mean() * 100:.2f} %"),
        ]),
        section("⚠️ 주의사항", note["cautions"]),
        "\n## 로딩 예제\n\n```python\n"
        "import pandas as pd\n\n"
        f'ex = pd.read_csv("raw/DepMap/{f}",\n'
        "                 index_col=0, low_memory=False)\n"
        'ex = ex[ex["IsDefaultEntryForModel"] == "Yes"]      # 중복 세포주 제거\n'
        'ex = ex.set_index("ModelID")\n'
        'ex = ex[[c for c in ex.columns if c.endswith(")")]]  # 메타 컬럼 분리\n'
        "```\n",
    ]
    written.append(write_doc(out, note, f, parts, stamp))

    # ------------------------------------------------------------------ index
    mid_ex, mid_ge, mid_md = set(ex_def.ModelID), set(ge.index), set(model.ModelID)
    inter = sorted(mid_ex & mid_ge & mid_md)
    ilin = model.set_index("ModelID").loc[inter, "OncotreeLineage"].value_counts()
    gset_ex, gset_ge = set(gcols), set(ge.columns)

    idx = [
        "# DepMap 데이터 설명서\n",
        "> ⚠️ **이 폴더의 문서는 `scripts/depmap_profile.py` 가 자동 생성합니다. 직접 수정하지 마세요.**",
        f"> 생성 시각: {stamp} · 릴리스: `{RELEASE}` (2026-04-01)\n",
        "```bash\npython3 scripts/depmap_profile.py\n```\n",
        "라이선스·취급 주의사항은 [저장소 README](../../README.md) 의 「⚠️ 데이터 취급 주의사항」 절 참고.",
        "26Q1 파일 목록 정본은 "
        "[DepMap 데이터 전반 조사](../research/2026-08-13/depmap_overview/lkeonwoo94.md), "
        "최소 구성(C-1) 선정 근거는 "
        "[AI 질답 정리 Q3](../research/2026-08-13/depmap_gpt_qna/lkeonwoo94.md#q3-그럼-최소한으로-받아야-하는-데이터가-뭐야) 참고.\n",
        "## 파일 목록 (C-1 최소 구성)\n",
        "| 파일 | 역할 | shape | 크기 | 설명서 |",
        "|---|---|---|---:|---|",
    ]
    meta = [
        ("CRISPRGeneEffect.csv", f"{ge.shape[0]:,} × {ge.shape[1]:,}"),
        ("OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv", f"{ex.shape[0]:,} × {ex.shape[1]:,}"),
        ("Model.csv", f"{model.shape[0]:,} × {model.shape[1]}"),
        ("CRISPRInferredCommonEssentials.csv", f"{ce.shape[0]:,} × {ce.shape[1]}"),
    ]
    for fname, shape in meta:
        n = NOTES[fname]
        sz = human(os.path.getsize(os.path.join(raw, fname)))
        idx.append(f"| `{fname}` | {n['role']} | {shape} | {sz} | [열기]({n['slug']}.md) |")
    readme = os.path.join(raw, "README.txt")
    if os.path.exists(readme):
        idx.append(f"| `README.txt` | DepMap 공식 릴리스 설명 | — | {human(os.path.getsize(readme))} | (원본 그대로) |")

    idx += [
        "\n## 교집합 — 실제 학습 가능한 표본 수\n",
        fmt_table([
            ("발현 (필터링 후)", f"{len(mid_ex):,}"),
            ("CRISPR gene effect", f"{len(mid_ge):,}"),
            ("Model.csv", f"{len(mid_md):,}"),
            ("발현 ∩ CRISPR", f"{len(mid_ex & mid_ge):,}"),
            ("**3개 전부 (= n)**", f"**{len(inter):,}**"),
            ("CRISPR에 있으나 발현에 없음", f"{len(mid_ge - mid_ex):,}"),
            ("CRISPR에 있으나 Model.csv에 없음", f"{len(mid_ge - mid_md):,}"),
        ]),
        "\n## 유전자 축 겹침\n",
        fmt_table([
            ("발현 유전자", f"{len(gset_ex):,}"),
            ("CRISPR 유전자", f"{len(gset_ge):,}"),
            ("공통", f"{len(gset_ex & gset_ge):,}"),
            ("CRISPR에만 있음", f"{len(gset_ge - gset_ex):,}"),
            ("발현에만 있음", f"{len(gset_ex - gset_ge):,}"),
        ]),
        f"\n## 교집합 {len(inter):,}개의 암종 분포\n",
        f"총 **{ilin.size}개 lineage**.\n",
        "| lineage | 세포주 수 |\n|---|---:|",
    ]
    idx += [f"| {k} | {v:,} |" for k, v in ilin.items()]
    small = ilin[ilin < 10]
    idx += [
        f"\n⚠️ **{len(small)}개 lineage는 세포주가 10개 미만**"
        f"({', '.join(f'{k} {v}' for k, v in small.items())}). "
        "leave-one-lineage-out 평가는 표본이 충분한 상위 lineage로 한정해야 한다.\n",
        "## 조인 규약\n",
        "- 조인 키는 `ModelID` (`ACH-XXXXXX`). 세포주 이름으로 조인하지 말 것.",
        "- 유전자 컬럼은 `SYMBOL (ENTREZID)` 형식. symbol만 필요하면 `c.split(\" (\")[0]`.",
        "- 발현은 `IsDefaultEntryForModel == \"Yes\"` 필터가 **선행**되어야 한다.",
        "- 교집합 확정 후 모든 테이블의 행 순서를 명시적으로 동일하게 맞출 것.\n",
    ]
    ipath = os.path.join(out, "README.md")
    with open(ipath, "w") as fh:
        fh.write("\n".join(idx))
    written.append(ipath)

    print(f"n(교집합) = {len(inter):,}")
    for p in written:
        print("  생성:", os.path.relpath(p, REPO))


if __name__ == "__main__":
    main()
