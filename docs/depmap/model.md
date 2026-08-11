# Model.csv

> ⚠️ **이 문서는 `scripts/depmap_profile.py` 가 자동 생성합니다. 직접 수정하지 마세요.**
> 설명·주의사항을 고치려면 스크립트의 `NOTES` 를, 측정값을 갱신하려면 스크립트를 다시 실행하세요.
> 생성 시각: 2026-08-11 17:23 KST

세포주(모델) 메타데이터. 모든 DepMap 파일을 잇는 조인 키 `ModelID`(`ACH-XXXXXX`)의 원장이며, 암종 정보(`OncotreeLineage` 등)를 제공한다.


## 기본 정보

| 항목 | 값 |
|---|---|
| 릴리스 | `DepMap Public 26Q1` (2026-04-01) |
| 원본 경로 | `raw/DepMap/Model.csv` |
| 파일 크기 | 697,455 B (697.5 KB) |
| md5 | `a15d75dffcc5219111ca39598948df9a` ✅ 매니페스트 일치 |
| 역할 | **메타데이터 · 조인 키** |
| 다운로드 | [포털](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=Model.csv) |
| shape | **2,154 행 × 49 열** |
| 조인 키 | `ModelID` — 유니크: 예 |

## 주요 컬럼

- `ModelID`
- `CellLineName`
- `StrippedCellLineName`
- `OncotreeLineage`
- `OncotreePrimaryDisease`
- `OncotreeSubtype`
- `DepmapModelType`
- …외 42개 (전체 목록은 파일 헤더 참조)


## 데이터 샘플

앞 5행, 주요 6개 컬럼만 (전체 49개 컬럼):

| ModelID | CellLineName | OncotreeLineage | OncotreePrimaryDisease | OncotreeSubtype | DepmapModelType |
|---|---|---|---|---|---|
| ACH-000001 | NIH:OVCAR-3 | Ovary/Fallopian Tube | Ovarian Epithelial Tumor | High-Grade Serous Ovarian Cancer | HGSOC |
| ACH-000002 | HL-60 | Myeloid | Acute Myeloid Leukemia | AML with Myelodysplasia-Related Changes | AMLMRC |
| ACH-000003 | CACO2 | Bowel | Colorectal Adenocarcinoma | Colon Adenocarcinoma | COAD |
| ACH-000004 | HEL | Myeloid | Acute Myeloid Leukemia | AML, NOS | AMLNOS |
| ACH-000005 | HEL 92.1.7 | Myeloid | Acute Myeloid Leukemia | Acute Myeloid Leukemia | AML |


## 암종(OncotreeLineage) 분포

총 **34개 lineage**, 결측 13개

| lineage | 세포주 수 |
|---|---:|
| Lymphoid | 266 |
| Lung | 261 |
| Skin | 150 |
| CNS/Brain | 127 |
| Esophagus/Stomach | 104 |
| Bone | 101 |
| Soft Tissue | 99 |
| Bowel | 99 |
| Breast | 96 |
| Head and Neck | 94 |
| Myeloid | 88 |
| Ovary/Fallopian Tube | 76 |
| Kidney | 74 |
| Pancreas | 68 |
| Peripheral Nervous System | 62 |

(상위 15개만 표시 / 전체 34개)


## ⚠️ 주의사항

- 26Q1에서 **OncoTree 2025-10-09** 기준으로 재주석됐고 **CNS/Brain lineage가 대규모 재분류**됐다. 폐기된 OncoTree 코드를 쓰던 모델은 전부 재주석됐으므로, 암종 라벨은 항상 이 릴리스의 `Model.csv` 기준으로 다시 부여할 것.
- 세포주 이름 표기는 파일·출처마다 다르다. 반드시 `ModelID` 로 연결한다.
