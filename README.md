# AI-bio-proj-team-1

윤석현교수님과 함께하는 AI 바이오데이터 실습 1조

> **처음 오셨다면 → [quick_start.md](quick_start.md)**
> 데이터 배치부터 첫 분석까지 30분 코스. 이 README는 데이터 구조 레퍼런스입니다.

---

## ⚠️ 데이터 취급 규칙 (먼저 읽을 것)

이 프로젝트는 **ADNI**(Alzheimer's Disease Neuroimaging Initiative) 데이터를 사용합니다.
원본 파일명이 `ADNI_data_Do_NOT_redistribute.zip` 인 것에서 알 수 있듯 **재배포가 금지된 자료**입니다.

| 하지 말 것 | 해도 되는 것 |
|---|---|
| 원본 ZIP / CSV / `.rda` 커밋 | 분석 **코드** 커밋 |
| 참가자 수준(1인 1행) 데이터 커밋 | 집계·요약 통계 (셀 빈도 충분히 클 때) |
| 개인 식별 가능 파생물 업로드 | 그림·표 (개인 식별 불가한 경우) |
| Slack/메신저로 데이터 파일 전송 | LONI에서 각자 내려받기 |

- 데이터는 각자 [LONI IDA](https://ida.loni.usc.edu/)에서 내려받아 로컬 `data/` 에 둡니다.
- `.gitignore` 가 `*.zip`, `*.csv`, `*.rda`, `*.pdf`, `data/`, `adni/` 등을 차단하도록 설정돼 있습니다.
- **Jupyter 노트북은 커밋 전 반드시 출력(output)을 지웁니다.** 출력 셀에 개인 데이터가 그대로 남습니다.
- 커밋 전 확인: `git status` 에 데이터 파일이 보이면 그대로 멈추고 팀에 알릴 것.

---

## 데이터 개요

원본 번들: `ADNI_data_Do_NOT_redistribute.zip` — **1,136,659,190 바이트 (약 1.14 GB)**
SHA-256: `2a3579bb066c2b5fc73e46f6da13f5ea72d1bd81e31cf1011197ef81f39df61f`

### 최상위 구조 — 카테고리별 ZIP 12개 (이중 압축)

```
$ unzip -l ADNI_data_Do_NOT_redistribute.zip

        크기  수정일시           파일명
-----------  ----------------  ------------------------------------------------
451,175,566  2026-01-22 18:32  ADSP_PHC.zip
 91,014,203  2026-01-22 17:12  Assessments.zip
  2,221,635  2026-01-22 18:28  Curated_Data___Docs.zip
160,540,817  2026-01-22 18:28  Genetic.zip
541,136,776  2026-01-22 17:39  Imaging.zip
 46,362,851  2026-01-22 18:47  Medical_History.zip
    284,720  2026-01-22 18:51  Neuropathology_Results.zip
  7,410,942  2026-01-22 16:11  Quick_Start.zip
 61,900,845  2026-01-22 19:12  Remotely_Collected_Data.zip
169,887,411  2026-01-22 18:51  Study_Info.zip
  5,969,225  2026-01-22 18:48  Subject_Characteristics.zip
 57,628,527  2026-01-22 18:29  Test_Data_for_Challenges_except_imaging_vertices.zip
        106  2026-07-29 19:47  desktop.ini
-----------
1,595,533,624  (13개 항목, 압축 해제 기준)
```

카테고리 ZIP 안에 총 **283개 파일(CSV 185개, PDF 81개)** 이 들어 있습니다.

| 카테고리 | 압축 해제 | 파일 | CSV | PDF |
|---|---:|---:|---:|---:|
| Imaging | 541.1 MB | 125 | 78 | 42 |
| ADSP_PHC | 451.2 MB | 29 | 21 | 7 |
| Study_Info | 169.9 MB | 21 | 3 | 14 |
| Genetic | 160.5 MB | 12 | 4 | 6 |
| Assessments | 91.0 MB | 52 | 45 | 7 |
| Remotely_Collected_Data | 61.9 MB | 9 | 7 | 2 |
| Test_Data_for_Challenges | 57.6 MB | 4 | 0 | 0 |
| Medical_History | 46.4 MB | 16 | 16 | 0 |
| Quick_Start | 7.4 MB | 2 | 1 | 1 |
| Subject_Characteristics | 6.0 MB | 9 | 8 | 1 |
| Curated_Data___Docs | 2.2 MB | 2 | 1 | 0 |
| Neuropathology_Results | 0.3 MB | 2 | 1 | 1 |

카테고리별 내용:

- **Quick_Start** — `DATADIC_21Jan2026.csv`(전체 변수 데이터 사전)와 퀵스타트 가이드. **데이터 구조 파악의 출발점.**
- **Study_Info** — 단계별 Procedures Manual/CRF PDF와 `ADNIMERGE2.tar.gz` R 패키지. **실제 분석은 여기서 시작.**
- **Imaging** — MRI 부피(`UCSDVOL`, `UCSFSNTVOL`, `BSI`), 위축도(`UCSFATRPHY`), amyloid PET SUVR(`PIBPETSUVR`) 등 영상 파생 지표.
- **Genetic** — APOE 인접 `TOMM40`, Desikan lab 다유전자 위험 점수(PHS), 텔로미어 비율, tau-PET GWAS 요약통계.
- **Assessments** — MoCA, ADAS, FAQ, ECog(본인/보호자) 등 인지·기능 평가 척도.
- **ADSP_PHC** — Alzheimer's Disease Sequencing Project 조화 인지 점수(harmonized composite).
- **Medical_History** — 병력, 병용약물, 이상반응.
- **Subject_Characteristics** — 인구학 정보(`PTDEMOG`), 가족력(`FHQ`, `FAMHXPAR`), 거주지 특성(`ADI`, `RURALITY`).
- **Neuropathology_Results** — 부검 신경병리 소견 `NEUROPATH_22Jan2026.csv`.
- **Test_Data_for_Challenges_…** — 챌린지용 별도 테스트 세트(추가 중첩 압축).

> **참고**: ZIP이 이중 중첩이라 카테고리 ZIP을 한 번 더 풀어야 합니다.
> 1.14 GB 전체를 디스크에 풀 필요는 없고, 필요한 카테고리만 메모리에서 열어
> pandas로 바로 읽는 편이 빠릅니다 (아래 예제 참고).

---

## 압축 해제 결과 (Quick_Start, Study_Info)

현재까지 이 두 카테고리만 풀어 확인했습니다.

```
$ ls -al adni/
total 16
drwxr-xr-x  4 kali kali 4096 Aug  7 17:20 .
drwxr-xr-x 12 kali kali 4096 Aug  7 17:24 ..
drwxr-xr-x  2 kali kali 4096 Aug  7 17:20 Quick_Start
drwxr-xr-x  3 kali kali 4096 Aug  7 17:21 Study_Info
```

### Quick_Start — 파일 2개, 7.4 MB

```
$ ls -al adni/Quick_Start/
total 7248
drwxr-xr-x 2 kali kali    4096 Aug  7 17:20 .
drwxr-xr-x 4 kali kali    4096 Aug  7 17:20 ..
-rw-r--r-- 1 kali kali  162467 Aug  7 17:20 ADNI_Quickstart_Guide_20250527.pdf
-rw-r--r-- 1 kali kali 7248191 Aug  7 17:20 DATADIC_21Jan2026.csv
```

`DATADIC_21Jan2026.csv` = **34,930행 × 13열**의 전체 데이터 사전.
컬럼: `PHASE, CRFNAME, TBLNAME, FLDNAME, TEXT, TYPE, LENGTH, DD_CRF_VERSION, CODE, UNITS, STATUS, CODE_CHANGES, MAPPING_NOTES`
→ **336개 테이블**의 모든 변수 정의·자료형·코딩값·단위·단계별 코드 변경 이력.
어떤 CSV의 어떤 컬럼이 무슨 뜻인지 모를 때 여기서 조회합니다.

필드 수 상위 테이블 (오믹스 계열이 압도적):

| 테이블 | 필드 수 | 설명 |
|---|---:|---|
| `EMORY_CSF_TMT_MS` | 3,914 | Emory CSF TMT 질량분석 프로테오믹스 |
| `ADMC_DUKE_SERUM_METABOLON_HD4` | 1,358 | Duke 비표적 혈청 메타볼로믹스 |
| `ADMCLIPIDOMICSMEIKLELABLONG` | 789 | Meikle lab 종단 리피도믹스 |
| `NEUROPATH` | 734 | NACC 신경병리 양식 v11 |
| `UCSFASLFS` | 700 | ASL 관류 CBF, FreeSurfer ROI별 |
| `UCBERKELEYAV45_8MM` | 601 | amyloid PET SUVR |
| `UCBERKELEYAV1451_8MM` | 584 | tau PET SUVR |

`PHASE` 태그 분포: 단일 단계(ADNI1/GO/2/3/4 각 1.8k–2.8k), 다단계 공유 8,823, 미태깅 14,490.
미태깅이 많은 이유는 외부 연구실 제공 오믹스/영상 테이블이 특정 프로토콜에 묶이지 않기 때문입니다.

### Study_Info — 파일 21개, 169.9 MB

```
$ ls -al adni/Study_Info/
total 165968
drwxr-xr-x 3 kali kali     4096 Aug  7 17:21 .
drwxr-xr-x 4 kali kali     4096 Aug  7 17:20 ..
-rw-r--r-- 1 kali kali   173397 Aug  7 17:20 ADNI_1.5T_MRI_Standardized_Lists.zip
-rw-r--r-- 1 kali kali  2519112 Aug  7 17:20 ADNI1_CRFs_20180724.pdf
-rw-r--r-- 1 kali kali  5683046 Aug  7 17:20 ADNI1_Procedures_Manual.pdf
-rw-r--r-- 1 kali kali 31737490 Aug  7 17:20 ADNI2_Procedures_Manual.pdf
-rw-r--r-- 1 kali kali  8370046 Aug  7 17:20 ADNI3_Procedures_Manual_v3.0.pdf
-rw-r--r-- 1 kali kali    33088 Aug  7 17:20 ADNI_3T_MRI_Standardized_Lists.zip
-rw-r--r-- 1 kali kali  1245313 Aug  7 17:20 ADNI4_In_Clinic_Protocol_v2_20230215.pdf
-rw-r--r-- 1 kali kali  1365433 Aug  7 17:20 ADNI4_In_Clinic_Protocol_v3_20240415.pdf
-rw-r--r-- 1 kali kali  2372908 Aug  7 17:20 ADNI4_Procedures_Manual_v4.3_05MAR2025.pdf
-rw-r--r-- 1 kali kali   620339 Aug  7 17:20 ADNI4_Remote_Protocol_v2_20230505.pdf
-rw-r--r-- 1 kali kali   632325 Aug  7 17:20 ADNI4_Remote_Protocol_v3_20240220.pdf
-rw-r--r-- 1 kali kali   136307 Aug  7 17:20 Adni_Data_Matrix_20140527.pdf
-rw-r--r-- 1 kali kali  3960569 Aug  7 17:20 ADNI_GO_CRFs_20140606.pdf
-rw-r--r-- 1 kali kali 25831236 Aug  7 17:20 ADNI_GO_Procedures_Manual.pdf
drwxr-xr-x 9 kali kali     4096 Aug  7 17:21 ADNIMERGE2
-rw-r--r-- 1 kali kali   227053 Aug  7 17:20 ADNIMERGE2_R_Package_Methods_20260105.pdf
-rw-r--r-- 1 kali kali 82668578 Aug  7 17:20 ADNIMERGE2.tar.gz
-rw-r--r-- 1 kali kali   662973 Aug  7 17:20 ADNI_Methods_Template.docx
-rw-r--r-- 1 kali kali   710551 Aug  7 17:20 ADNI_Minimum_Metadata.pdf
-rw-r--r-- 1 kali kali   756169 Aug  7 17:20 DELMRSCANS_22Jan2026.csv
-rw-r--r-- 1 kali kali   172399 Aug  7 17:20 PIFINAL_22Jan2026.csv
-rw-r--r-- 1 kali kali     6201 Aug  7 17:20 RORR_22Jan2026.csv
```

대부분 PDF 14개(각 단계 Procedures Manual, CRF 서식, ADNI4 프로토콜, 최소 메타데이터 명세)와
방법론 기술용 Word 템플릿(`ADNI_Methods_Template.docx`)입니다. 논문 Methods 절 작성 시 인용할 원 문서.

CSV 3개는 운영성 자료:

| 파일 | 크기 | 내용 |
|---|---:|---|
| `DELMRSCANS_22Jan2026.csv` | 10,324 × 5 | **삭제된 MRI 스캔 목록** — 영상 분석 시 제외 대상 |
| `PIFINAL_22Jan2026.csv` | 1,583 × 13 | site별 QC 플래그 |
| `RORR_22Jan2026.csv` | 34 × 28 | 결과 통보 요청 |

### ADNIMERGE2 R 패키지 — 여기가 핵심

```
$ ls -al adni/Study_Info/ADNIMERGE2/
total 72
drwxr-xr-x 9 kali kali  4096 Aug  7 17:21 .
drwxr-xr-x 3 kali kali  4096 Aug  7 17:21 ..
drwxr-xr-x 2 kali kali  4096 Dec 18  2025 build
drwxr-xr-x 2 kali kali 12288 Dec 18  2025 data
-rw-r--r-- 1 kali kali  1133 Dec 18  2025 DESCRIPTION
drwxr-xr-x 4 kali kali  4096 Dec 18  2025 inst
-rw-r--r-- 1 kali kali    48 Jul 11  2025 LICENSE
drwxr-xr-x 3 kali kali 12288 Dec 18  2025 man
-rw-r--r-- 1 kali kali  3410 Nov 13  2025 NAMESPACE
-rw-r--r-- 1 kali kali   263 Sep 19  2025 NEWS.md
drwxr-xr-x 2 kali kali  4096 Dec 18  2025 R
-rw-r--r-- 1 kali kali  1123 Dec 18  2025 README.md
drwxr-xr-x 3 kali kali  4096 Sep 19  2025 tests
drwxr-xr-x 2 kali kali  4096 Dec 18  2025 vignettes
```

- ATRI Biostatistics 배포, **v0.1.1** (MIT, 2025-12-17 빌드)
- 업스트림: <https://github.com/atri-biostats/ADNIMERGE2>
- `data/` 에 **`.rda` 217개, 총 2,727,235행** — CDISC SDTM/ADaM 스타일 정리 완료
- **원본 CSV를 손으로 병합하지 말고 이 패키지를 쓰는 것이 정석입니다.**

행 수 상위 테이블:

| 테이블 | 행 × 열 | 내용 |
|---|---:|---|
| `LB` | 326,837 × 25 | 검사실 수치 |
| `ADQS` | 320,021 × 36 | 설문/척도 분석 데이터셋 |
| `QS` | 320,021 × 20 | 설문/척도 원자료 |
| `URMC_LABDATA` | 140,434 × 29 | URMC 검사 데이터 |
| `SC` | 129,462 × 16 | 스크리닝 |
| `VS` | 120,813 × 20 | 활력징후 |
| `MRIQC` | 90,250 × 26 | MRI 품질관리 |
| `RECCMEDS` | 77,466 × 38 | 병용약물 |

**`ADSL` (5,146행 × 55열)** — 참가자 1인당 1행인 subject-level 마스터 테이블. 여기서 시작하면 됩니다.

- **단계별 등록**: ADNI1 1,430 / ADNIGO 406 / ADNI2 1,293 / ADNI3 1,126 / ADNI4 891
- **기저 진단**: CN 1,215 / MCI 1,338 / 치매 477 / 미기록 2,116
- **연령** 71.9 ± 7.9세 (n=4,931) · **교육** 16.0 ± 2.8년 · **MMSE** 27.4 ± 2.6 · **CDR-SB** 1.39 ± 1.75
- **성별**: 여성 2,513 / 남성 2,422
- **APOE**: ε3/ε3 1,417 · ε3/ε4 1,016 · ε4/ε4 275 · ε2/ε3 219 · ε2/ε4 71 · ε2/ε2 10 (결측 2,138)
- **Amyloid**: Elevated 691 / Non-elevated 920 (결측 3,535)
- 내장 인지 변수: `ADASTT11/13`, `CDRSB`, `MMSCORE`, `MOCA`, `FAQTOTAL`, `RAVLTIMM/LRN/FG`, `TRABSCOR`, `MPACCDIGIT`, `MPACCTRAILSB`

`PACC`(19,571행) 같은 파생 복합점수 테이블과 함께 산출 코드(`R/pacc.R`, `R/score-function.R`,
`R/analysis-data-prep.R`)가 들어 있어 점수 계산 규칙을 그대로 재현할 수 있습니다.
`inst/doc/` 에 등록(ADNI-Enrollment)·종단분석(ADNI-Longitudinal) vignette도 있습니다.

### 함정 두 가지

1. **`ADSL` 에는 `RID` 컬럼이 없습니다.** 참가자 키가 `USUBJID`/`SUBJID`인데
   원본 CSV들은 `RID`/`PTID`를 씁니다. 조인 전에 키 매핑이 필요합니다.
2. **`DX` 결측 2,116명(41%)** 은 진단 정보가 없어서가 아니라 `ADSL`이 특정 시점 스냅샷이기 때문입니다.
   종단 진단 이력은 `DXSUM` 계열 테이블에서 가져오세요.

---

## 로컬 세팅

### 1. 데이터 배치

각자 LONI에서 내려받은 뒤 아래처럼 둡니다. `data/` 는 `.gitignore` 처리돼 있습니다.

```
AI-bio-proj-team-1/
├── data/                                    # git 추적 안 함
│   └── ADNI_data_Do_NOT_redistribute.zip
├── notebooks/
├── src/
├── results/
├── .gitignore
└── README.md
```

### 2. 카테고리 ZIP 열기 (전체 해제 없이)

```python
import zipfile, io, pandas as pd

outer = zipfile.ZipFile("data/ADNI_data_Do_NOT_redistribute.zip")

with outer.open("Quick_Start.zip") as f:
    inner = zipfile.ZipFile(io.BytesIO(f.read()))

with inner.open("DATADIC_21Jan2026.csv") as f:
    datadic = pd.read_csv(f, low_memory=False)

print(datadic.shape)   # (34930, 13)
```

### 3. ADNIMERGE2 불러오기

```r
# 한 번만: tar.gz 를 풀어 설치
install.packages("adni/Study_Info/ADNIMERGE2.tar.gz", repos = NULL, type = "source")

library(ADNIMERGE2)
data(ADSL)
dim(ADSL)   # 5146 x 55
```

설치 없이 `.rda` 만 직접 읽어도 됩니다:

```r
load("adni/Study_Info/ADNIMERGE2/data/ADSL.rda")
```

> `metacore` 네임스페이스 경고가 뜨지만 데이터 읽기에는 지장 없습니다.

---

## 참고 링크

- ADNI 공식: <https://adni.loni.usc.edu/>
- 데이터 다운로드(LONI IDA): <https://ida.loni.usc.edu/>
- ADNIMERGE2 문서: <https://atri-biostats.github.io/ADNIMERGE2>

## 팀

| GitHub | 역할 |
|---|---|
| `lkeonwoo94` | admin |
| `wjo9956` | 팀원 |
| `hyunhee1123` | 팀원 |
