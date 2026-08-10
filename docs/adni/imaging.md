# Imaging — 영상(MRI/PET) 파생 지표

원본 DICOM/NIfTI 영상이 아니라, 각 처리 파이프라인(UCSF, UCSD, UPenn, Berkeley, Mayo 등
협력 랩)이 영상에서 뽑아낸 **파생 지표(볼륨, SUVR, 피질두께 등) 테이블**과 그 산출 방법론 PDF
모음입니다. CSV 78개, PDF 42개.

## 지표 그룹 (양식별)

### 구조 MRI — 부피/위축도

| 파일(접두) | 내용 |
|---|---|
| `UCSDVOL` | UCSD MRI 부피 측정 |
| `UCSFFSX*` (FSX, FSX51, FSX6, FSX7, FSX51_ADNI1_3T) | UCSF FreeSurfer 버전별 피질/피질하 분할 지표 — 버전이 여러 개라 분석 시 어떤 버전을 쓸지 통일 필요 |
| `UCSFFSL*` (FSL, FSL51, FSL51ALL, FSL51Y1) | UCSF FreeSurfer Longitudinal 파이프라인 |
| `UCSFSNTVOL` | UCSF 해마 등 특정 구조물 부피(SNT) |
| `UCSFATRPHY` | UCSF 위축도(atrophy) 지표 |
| `BSI` / `FOXLABBSI` | Boundary Shift Integral — 종단 뇌 위축 측정 |
| `TBM_*` / `MAYOADIRL_MRI_TBMSYN` | Tensor-Based Morphometry (Mayo, SyN 알고리즘) |
| `TCV` | Total Cranial Vault (두개내 용적) |
| `UCD_WMH` / `UCD_ADNI1_WMH` | UC Davis 백질고신호강도(White Matter Hyperintensity) |
| `MRI_INFARCTS` | MRI 상 뇌경색 소견 |
| `UPENNROI_MARS`, `UPENNSPARE_AD`, `UPENNSPARE_MCI` | UPenn ROI 및 SPARE-AD/MCI 판별점수 |
| `ADNI_PICSLASHS` | PICSL ASHS 해마 아영역 분할 |
| `MRIQSM` | 정량적 자화율맵핑(QSM) |

### 기능/확산 MRI

| 파일(접두) | 내용 |
|---|---|
| `MAYOADIRL_MRI_FMRI_*` | Mayo 기능적 MRI(rs-fMRI) 지표 |
| `MAYOADIRL_MRI_MCH` | Mayo MCH(추정: 미세혈관/microhemorrhage 관련, 확인 필요) |
| `DTIROI_MEAN` / `DTIROI_ROBUSTMEAN` / `ADNI_DTIROI_V1` | 확산텐서영상 ROI 평균 지표 |
| `UCSFASLFS*` / `UCSFASLQC` | UCSF ASL(동맥스핀표지) 관류 지표·QC |
| `UASPMVBM` | ASL 기반 SPM VBM(복셀기반 형태계측) |

### PET — Amyloid

| 파일(접두) | 내용 |
|---|---|
| `AV45QC` / `AV45META` | Florbetapir(AV45) PET QC/메타데이터 |
| `PIBQC` / `PIBMETA` / `PIBPETSUVR` | PIB(Pittsburgh Compound-B) PET QC·SUVR |
| `AMYQC` / `AMYMETA` | Amyloid PET(통합) QC/메타 |
| `UCBERKELEY_AMY_6MM` | UC Berkeley Amyloid PET 6mm 스무딩 SUVR |
| `SPAP_AVID_FLORBETAPIR` | 표준 Amyloid 처리 파이프라인(Avid Florbetapir) |
| `CROSSVAL` | 트레이서 간 교차검증(cross-validation) |

### PET — Tau / FDG

| 파일(접두) | 내용 |
|---|---|
| `TAUQC` / `TAUMETA` | Tau PET QC/메타데이터 |
| `UCBERKELEY_TAU_6MM` / `UCBERKELEY_TAUPVC_6MM` | UC Berkeley Tau PET SUVR (부분용적보정 포함/미포함) |
| `UCBERKELEYFDG_8mm` | FDG(포도당대사) PET SUVR |
| `NYUFDGHIP` | NYU FDG 해마 지표 |

### PET — BAI/NMRC 계열 (다중 트레이서 통합)

`BAIMRINMRC`, `BAINMRC`, `BAIPETNMRC`, `BAIPETNMRCAV45`, `BAIPETNMRCFDG`, `BAIPETNMRCFTP` —
Berkeley/BAI 그룹의 MRI-PET 정합 및 트레이서별(AV45/FDG/Flortaucipir) 수치 요약.

### 메타/QC/운영

`MRIMETA`, `MRI3META`, `PETMETA`, `PETMETA3`, `PETMETA_ADNI1`, `PETMETA_ADNIGO2`, `PETC3`,
`MRIQC`, `PETQC`, `MRIPROT`, `MRIFind`, `MRIREAD`, `MRINCLUSIO`, `MRINFQ`, `MRIB1CALIB`,
`MRIMPPRO`, `MRIMPRANK`, `MRISERIAL`, `Changed_Study_ID_Listing` — 스캔 프로토콜, QC 통과 여부,
스캐너 보정, 참가자 ID 변경 이력 등 영상 자체보다는 **스캔 운영/품질 관리용** 테이블.

## 중첩 압축·기타 대용량 파일

- `AV45_Niftii_Templates.zip` — Amyloid PET 표준 템플릿 NIfTI
- `ADNI3_diffusion_gradients_{GE,Philips,Siemens}.zip` — 스캐너 제조사별 DTI gradient 테이블
- `ADNI_HHP_Training_Set.zip` — 특정 파이프라인(HHP) 학습용 세트

## Methods PDF (42개)

파이프라인별 방법론 문서가 대부분입니다 (UCSF FreeSurfer/ASL, UPenn 계층적 분할, Berkeley
Amyloid/Tau/FDG, Mayo QC/BSI/MCH/TBM, BAI-PET-NMRC 트레이서별, UC Davis WMH, DTI 방법 등).
사용하는 지표의 산출 파이프라인에 맞는 PDF를 먼저 확인하는 것을 권장합니다.

## 참고

- **동일 지표라도 랩·버전·파이프라인별로 여러 CSV가 존재**합니다 (예: FreeSurfer만 FSX/FSX51/FSX6/FSX7/FSL/FSL51 등 6종 이상). 분석 전 어떤 버전을 표준으로 쓸지 팀 내 합의가 필요합니다.
- QC 컬럼(`*QC` 파일)으로 스캔 통과 여부를 먼저 걸러야 신뢰할 수 있는 지표만 남습니다.
- `RID`/`PTID`와 `VISCODE`(방문 코드)로 다른 카테고리 및 종단 시점과 조인합니다.
