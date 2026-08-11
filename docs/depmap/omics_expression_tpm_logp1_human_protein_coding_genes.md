# OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv

> ⚠️ **이 문서는 `scripts/depmap_profile.py` 가 자동 생성합니다. 직접 수정하지 마세요.**
> 설명·주의사항을 고치려면 스크립트의 `NOTES` 를, 측정값을 갱신하려면 스크립트를 다시 실행하세요.
> 생성 시각: 2026-08-11 17:23 KST

단백질코딩 유전자의 RNA-seq 발현량. 25Q2에서 STAR 2.7.11b + Salmon v1.10.0 으로 파이프라인이 교체됐고 유전자 주석은 Gencode V38로 통일됐다.


## 기본 정보

| 항목 | 값 |
|---|---|
| 릴리스 | `DepMap Public 26Q1` (2026-04-01) |
| 원본 경로 | `raw/DepMap/OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv` |
| 파일 크기 | 305,007,605 B (305.0 MB) |
| md5 | `559245dfb8dc496a8e30bba4c97d9b25` ✅ 매니페스트 일치 |
| 역할 | **입력 X** |
| 다운로드 | [포털](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv) |
| shape | **1,775 행 × 19,220 열** (메타 5 + 유전자 19,215) |
| 컬럼 형식 | `SYMBOL (ENTREZID)` — 예: `TSPAN6 (7105)` |

## 메타데이터 컬럼 (25Q3부터 추가됨)

- `SequencingID`
- `ModelConditionID`
- `ModelID`
- `IsDefaultEntryForMC`
- `IsDefaultEntryForModel`


## ⚠️ 행 필터링 — 반드시 먼저 할 것

| 항목 | 값 |
|---|---|
| 원본 행 수 | 1,775 |
| 고유 ModelID 수 | 1,719 |
| `IsDefaultEntryForModel` 값 분포 | `Yes` 1,719 / `No` 56 |
| 필터링 후 행 수 | **1,719** |
| 필터링 후 중복 ModelID | **0개** ← 중복 없음 |


## 데이터 샘플

앞 5행 × 메타 5개 + 유전자 3개 컬럼 (전체 1,775 × 19,220):

| SequencingID | ModelConditionID | ModelID | IsDefaultEntryForMC | IsDefaultEntryForModel | TSPAN6 (7105) | TNMD (64102) | DPM1 (8813) |
|---|---|---|---|---|---|---|---|
| CDS-010xbm | MC-001113-k2lR | ACH-001113 | Yes | Yes | 4.957 | 0.000 | 7.578 |
| CDS-02TzJp | MC-001289-BpdI | ACH-001289 | Yes | Yes | 4.955 | 0.617 | 7.334 |
| CDS-0693hw | MC-001339-5nRN | ACH-001339 | Yes | Yes | 3.422 | 0.000 | 7.546 |
| CDS-07Plat | MC-001619-IR6I | ACH-001619 | No | No | 5.197 | 0.000 | 6.362 |
| CDS-08FOcu | MC-001979-E3qW | ACH-001979 | Yes | Yes | 4.652 | 0.000 | 5.946 |

3번째 행처럼 `IsDefaultEntryForModel` 이 `No` 인 행이 섞여 있다 — 같은 세포주의 비기본 프로파일이므로 걸러내야 한다.


## 값 분포

| 항목 | 값 |
|---|---|
| 단위 | `log2(TPM + 1)` |
| 최소 / 최대 | 0.000 / 17.361 |
| 결측률 | 0.00 % |

## ⚠️ 주의사항

- **`IsDefaultEntryForModel == "Yes"` 로 먼저 필터링해야 한다.** 한 모델이 여러 행을 가질 수 있고, 거르지 않으면 중복 세포주가 학습셋에 들어간다.
- **Stranded / 비-Stranded 두 버전이 있고 DepMap 공식 권장이 없다.** 25Q2 릴리스 노트에서 "strandedness 외의 배치 효과 요인을 보정할 방법을 탐색 중"이라고 밝힌 상태다. 어느 쪽을 썼는지 반드시 기록할 것.
- 배치보정판(`...BatchCorrected.csv`)은 25Q2에서 제거됐고 대체 파일이 없다.
- 25Q2 이전 릴리스와는 파이프라인이 달라 수치를 직접 비교할 수 없다.


## 로딩 예제

```python
import pandas as pd

ex = pd.read_csv("raw/DepMap/OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv",
                 index_col=0, low_memory=False)
ex = ex[ex["IsDefaultEntryForModel"] == "Yes"]      # 중복 세포주 제거
ex = ex.set_index("ModelID")
ex = ex[[c for c in ex.columns if c.endswith(")")]]  # 메타 컬럼 분리
```
