#!/usr/bin/env python3
"""DepMap 원본 CSV를 빠른 로컬 캐시로 변환한다.

CSV 파싱이 파일럿 런타임의 대부분을 차지해서(14.5초 중 10초) 만든다.
원본은 raw/DepMap/ 에 그대로 두고 읽기 전용으로만 쓴다.

형식을 두 가지로 나눈다 — 벤치마크 결과에 따른 것이다.

  밀집 실수 행렬(gene effect, expression) → .npy
      컬럼이 18,000개가 넘어 parquet 은 컬럼별 메타데이터 오버헤드가 크다.
      값도 난수에 가까워 압축이 거의 안 먹는다. 실측으로 .npy 가
      parquet 보다 20배 이상 빠르고 파일도 더 작았다.
  혼합 타입 테이블(Model 등) → .parquet
      문자열·범주형이 섞여 있어 스키마가 필요하다. 작아서 속도는 무관.

적용하는 변환은 딱 두 가지 — 안 하면 반드시 사고가 나는 것들이다.
  1) 발현: IsDefaultEntryForModel == "Yes" 필터 (안 하면 중복 세포주 누출)
  2) 인덱스를 ModelID 로 통일
그 외 값은 손대지 않는다. 실수는 float32 로 저장하며 오차를 manifest 에 기록한다.

사용법:
    python3 scripts/depmap_cache.py
    python3 scripts/depmap_cache.py --float64     # 무손실로 저장
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parent.parent
DEFAULT_RAW = (REPO.parent / "raw" / "DepMap").resolve()
DEFAULT_OUT = REPO / "data" / "interim" / "depmap"
RELEASE = "DepMap Public 26Q1"


def md5(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def human(n: float) -> str:
    for unit, div in (("GB", 1e9), ("MB", 1e6), ("KB", 1e3)):
        if n >= div:
            return f"{n / div:.1f} {unit}"
    return f"{n:.0f} B"


def gene_cols(cols) -> list[str]:
    return [c for c in cols if c.endswith(")") and " (" in c]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", type=Path, default=DEFAULT_RAW)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--float64", action="store_true", help="무손실 저장 (기본은 float32)")
    args = ap.parse_args()
    dtype = np.float64 if args.float64 else np.float32
    args.out.mkdir(parents=True, exist_ok=True)
    entries: list[dict] = []

    def timed_csv(fn):
        t = time.perf_counter()
        return fn(), time.perf_counter() - t

    def save_matrix(name: str, src: str, df: pd.DataFrame, t_csv: float, notes: list[str]):
        """밀집 실수 행렬 → values/index/columns 3개 .npy"""
        a64 = df.to_numpy(dtype=np.float64)
        a = a64.astype(dtype)
        err = float(np.nanmax(np.abs(a64 - a.astype(np.float64)))) if dtype is np.float32 else 0.0

        np.save(args.out / f"{name}.npy", a)
        np.save(args.out / f"{name}.index.npy", df.index.to_numpy())
        np.save(args.out / f"{name}.columns.npy", df.columns.to_numpy())

        t = time.perf_counter()
        back = np.load(args.out / f"{name}.npy")
        t_load = time.perf_counter() - t
        assert back.shape == df.shape

        size = sum((args.out / f"{name}{s}.npy").stat().st_size
                   for s in ("", ".index", ".columns"))
        entries.append(dict(
            name=name, format="npy", source=src,
            source_md5=md5(args.raw / src), source_bytes=(args.raw / src).stat().st_size,
            cache_bytes=size, rows=int(df.shape[0]), cols=int(df.shape[1]),
            index_name=df.index.name, dtype=str(np.dtype(dtype)),
            max_abs_error_vs_csv=err,
            csv_load_s=round(t_csv, 2), cache_load_s=round(t_load, 4),
            speedup=round(t_csv / t_load) if t_load else None, transforms=notes,
        ))
        e = entries[-1]
        print(f"  {name:20s} npy      {human(e['source_bytes']):>9} → {human(size):>9}"
              f"   로딩 {t_csv:5.2f}s → {t_load:6.3f}s  ({e['speedup']}배)")

    def save_table(name: str, src: str, df: pd.DataFrame, t_csv: float, notes: list[str]):
        """혼합 타입 테이블 → parquet"""
        dst = args.out / f"{name}.parquet"
        df.to_parquet(dst, compression="zstd", index=True)
        t = time.perf_counter()
        back = pd.read_parquet(dst)
        t_load = time.perf_counter() - t
        assert back.shape == df.shape
        entries.append(dict(
            name=name, format="parquet", source=src,
            source_md5=md5(args.raw / src), source_bytes=(args.raw / src).stat().st_size,
            cache_bytes=dst.stat().st_size, rows=int(df.shape[0]), cols=int(df.shape[1]),
            index_name=df.index.name, dtype="mixed", max_abs_error_vs_csv=0.0,
            csv_load_s=round(t_csv, 2), cache_load_s=round(t_load, 4),
            speedup=round(t_csv / t_load, 1) if t_load else None, transforms=notes,
        ))
        e = entries[-1]
        print(f"  {name:20s} parquet  {human(e['source_bytes']):>9} → {human(e['cache_bytes']):>9}"
              f"   로딩 {t_csv:5.2f}s → {t_load:6.3f}s  ({e['speedup']}배)")

    print(f"원본: {args.raw}\n캐시: {args.out}\n")

    ge, t = timed_csv(lambda: pd.read_csv(args.raw / "CRISPRGeneEffect.csv", index_col=0))
    ge.index.name = "ModelID"
    save_matrix("crispr_gene_effect", "CRISPRGeneEffect.csv", ge, t,
                ["첫 컬럼(무명)을 ModelID 인덱스로 지정"])

    ex, t = timed_csv(lambda: pd.read_csv(
        args.raw / "OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv",
        index_col=0, low_memory=False))
    n0 = len(ex)
    ex = ex[ex["IsDefaultEntryForModel"].astype(str) == "Yes"].set_index("ModelID")
    meta = [c for c in ex.columns if c not in gene_cols(ex.columns)]
    ex = ex[gene_cols(ex.columns)]
    assert ex.index.is_unique, "필터 후에도 ModelID 가 중복된다"
    save_matrix("expression", "OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv", ex, t,
                [f'IsDefaultEntryForModel == "Yes" 필터: {n0} → {len(ex)} 행',
                 "ModelID 를 인덱스로 지정",
                 f"메타데이터 컬럼 {len(meta)}개 제거: {', '.join(meta)}"])

    mod, t = timed_csv(lambda: pd.read_csv(args.raw / "Model.csv", low_memory=False))
    save_table("model", "Model.csv", mod.set_index("ModelID"), t, ["ModelID 를 인덱스로 지정"])

    ce, t = timed_csv(lambda: pd.read_csv(args.raw / "CRISPRInferredCommonEssentials.csv"))
    save_table("common_essentials", "CRISPRInferredCommonEssentials.csv", ce, t, [])

    inter = sorted(set(ge.index) & set(ex.index) & set(mod["ModelID"]))
    tot_src = sum(e["source_bytes"] for e in entries)
    tot_dst = sum(e["cache_bytes"] for e in entries)
    tot_csv = sum(e["csv_load_s"] for e in entries)
    tot_cache = sum(e["cache_load_s"] for e in entries)

    (args.out / "manifest.json").write_text(json.dumps(dict(
        release=RELEASE, created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        raw_dir=str(args.raw), float_dtype=str(np.dtype(dtype)),
        n_intersection=len(inter), files=entries,
        totals=dict(source_bytes=tot_src, cache_bytes=tot_dst,
                    csv_load_s=round(tot_csv, 2), cache_load_s=round(tot_cache, 4)),
    ), ensure_ascii=False, indent=2))

    print(f"\n  합계  {human(tot_src)} → {human(tot_dst)}"
          f"   로딩 {tot_csv:.2f}s → {tot_cache:.3f}s  ({tot_csv / tot_cache:.0f}배)")
    print(f"  교집합 세포주: {len(inter):,}")
    if dtype is np.float32:
        print(f"  float32 최대 절대오차: {max(e['max_abs_error_vs_csv'] for e in entries):.2e}")
    print(f"\n  사용: from src.preprocessing.depmap_io import load_all")


if __name__ == "__main__":
    main()
