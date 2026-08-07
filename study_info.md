# Study_Info — 프로토콜 문서와 ADNIMERGE2

번들 `Study_Info.zip` (169.9 MB, 파일 21개) 의 압축 해제 결과입니다.

> 전체 번들 구조는 [README.md](README.md) · Quick_Start 카테고리는 [quick_start.md](quick_start.md)

**실제 분석은 여기서 시작합니다.** 안에 든 `ADNIMERGE2.tar.gz` 가 이 번들 전체의 핵심입니다.

---

## 디렉터리 내용

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

CSV 3개는 운영성 자료입니다 (아래 [운영성 CSV 3개](#운영성-csv-3개) 절 참고).

## ADNIMERGE2 R 패키지 — 여기가 핵심

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

---

## 운영성 CSV 3개

PDF 위주인 이 카테고리에서 실제 데이터는 CSV 3개뿐이며, 모두 분석 대상이 아니라 **분석 전 확인용**입니다.

### `DELMRSCANS_22Jan2026.csv` — 삭제된 MRI 스캔 (10,324 × 5)

| 컬럼 | 내용 |
|---|---|
| `SUBJECTID` | 참가자 ID (`035_S_6730` 형식) |
| `SCANDATE` | 촬영일 |
| `SERIESDSCR` | 시퀀스 설명 |
| `IMAGEID` | 영상 ID |
| `DELETEDATE` | 삭제일 |

참가자 1,083명의 스캔이 삭제됐고 삭제일은 2012-01-27 ~ 2026-01-21에 걸쳐 있습니다.
삭제가 많은 시퀀스는 기능적 MRI 계열입니다 — `Axial fcMRI (EYES OPEN)` 816건,
`MoCoSeries` 652건, `Axial MB rsfMRI (EYES OPEN) (MSV22)` 593건, `Axial rsfMRI EYES OPEN MSV21` 591건,
`3 Plane Localizer` 554건.

> **영상 분석 시 이 목록을 먼저 제외하세요.** 다른 테이블에 남아 있는 `IMAGEID` 중
> 여기 있는 것은 실제 영상이 존재하지 않습니다.

### `PIFINAL_22Jan2026.csv` — 연구책임자 최종 확인 (1,583 × 13)

ADNI3 전용이며 사이트 58곳, 참가자 1,583명이 1행씩 들어 있습니다.
`PIFINAL` 필드는 "본인의 개인 서명임을 확인한다"는 전자서명 항목이고,
`FINALCOMM` 은 코멘트입니다. `HAS_QC_ERROR` 는 전 행이 비어 있어 QC 오류로 표시된 건이 없습니다.
분석에는 쓰이지 않습니다.

### `RORR_22Jan2026.csv` — 연구결과 통보 요청 (34 × 28)

참가자에게 개별 연구 결과를 알려준 기록입니다. 34건뿐입니다.

- `TYPE` — 통보한 결과 종류: 1=구조 MRI, 2=기능 MRI, 3=Florbetapir PET amyloid, 4=PIB PET, 5=FDG PET, 6=CSF 바이오마커, 7=유전, 8=인지검사 등
- `REQUESTED` — 요청자: 1=참가자, 2=가족/친구/연구 파트너, 3=담당 의사, 4=기타
- `CONSENT` — 동의 주체: 1=참가자, 2=가족/친구/연구 파트너, 3=기타

실제 분포는 요청자의 절반가량이 참가자 본인(16/34), 동의도 참가자 본인이 20건입니다.

---

## `ADSL` 코호트 상세

### 결측 41%의 정체 — 스냅샷이 아니라 미등록자

`ADSL` 5,146행 중 `DX`, `EDUC`, `CDRSB`, `MMSCORE` 가 일제히 약 41% 비어 있습니다.
`ENRLFL`(등록 여부)와 교차하면 원인이 드러납니다.

| | `DX` 있음 | `DX` 결측 |
|---|---:|---:|
| `ENRLFL = Y` (등록) | 3,030 | 2 |
| `ENRLFL` 결측 (미등록) | 0 | 2,114 |

**결측은 전부 미등록자입니다.** `ADSL` 은 스크리닝을 받은 5,146명 전체를 담고 있고,
그중 실제 연구에 등록된 사람은 **3,032명**입니다. 나머지 2,114명은 스크리닝 단계에서
탈락했거나 등록 전에 중단한 사람들이라 기저 평가 자체가 없습니다.

> **분석 코호트는 `ENRLFL == "Y"` 로 걸러야 합니다.** 이 필터를 적용하면 결측률이 정상으로 돌아옵니다.

| 변수 | 전체 5,146명 | 등록자 3,032명 |
|---|---:|---:|
| `DX` | 41.1% 결측 | **0.1%** |
| `EDUC` | 41.1% | **0.1%** |
| `CDRSB` | 41.1% | **0.1%** |
| `MMSCORE` | 41.2% | **0.2%** |
| `APOE` | 41.5% | **12.4%** |
| `AMYSTAT` | 68.7% | **46.9%** |

`APOE` 12.4%와 `AMYSTAT` 46.9%는 필터 후에도 남는 진짜 결측입니다.
유전형 검사와 amyloid PET을 모든 참가자가 받지는 않았기 때문입니다.

`BMI` 는 등록 여부와 무관하게 99.2%가 비어 있어(n=39) 사실상 쓸 수 없습니다.

### 등록자 3,032명 프로파일

| 단계 | CN | MCI | 치매 | 계 |
|---|---:|---:|---:|---:|
| ADNI1 | 229 | 397 | 193 | 819 |
| ADNIGO | 1 | 128 | 0 | 129 |
| ADNI2 | 295 | 344 | 151 | 790 |
| ADNI3 | 378 | 244 | 74 | 696 |
| ADNI4 | 312 | 225 | 59 | 596 |

- **연령** 72.2 ± 7.6세 · **교육** 16.0 ± 2.8년
- **성별** 여성 1,529 / 남성 1,503 (거의 균형)
- **APOE** ε3/ε3 1,243 · ε3/ε4 896 · ε4/ε4 248 · ε2/ε3 198 · ε2/ε4 62 · ε2/ε2 9 (결측 376)
- **Amyloid** Elevated 691 / Non-elevated 920 (결측 1,421)
- **PET 추적자** Florbetapir(FBP) 1,150 · Florbetaben(FBB) 461

단계가 진행될수록 치매 비율이 낮아집니다 (ADNI1 23.6% → ADNI4 9.9%).
후기 단계가 전임상·초기 단계 참가자 모집으로 방향을 옮겼기 때문입니다.

### 연구 규모

- **등록 기간** 2005-09-07 ~ 2025-09-18 (20년)
- **사이트** 112곳
- **사망 확인** 259명 (`DTHFL == "Yes"`)
- **연구 종료일 기록** 1,179명

---

## 함정 세 가지

1. **`ADSL` 에는 `RID` 컬럼이 없습니다.** 참가자 키가 `USUBJID`(`ADNI-001-00221` 형식)인데
   원본 CSV 계열은 `RID`(정수) / `PTID`(`011_S_0002` 형식)를 씁니다.
   실제로 원본 CSV 336개 테이블 중 `USUBJID` 를 가진 것은 **0개**이고 `RID` 는 311개입니다.
   두 계통을 조인하려면 `ADNI-###-` 접두사를 떼어 정수로 바꿔야 합니다
   (패키지의 `convert_usubjid_to_rid()` 가 이 작업을 합니다).

2. **`DX` 결측 2,116명(41%)은 미등록자입니다.** 진단 정보가 누락된 것이 아니라
   스크리닝 탈락자라 기저 평가 자체가 없습니다. `ENRLFL == "Y"` 로 걸러 3,032명을 분석 코호트로 삼으세요.
   방문별 종단 진단 이력은 `DXSUM` 테이블(15,881행)에 따로 있습니다.

3. **`-4` 는 결측입니다.** ADNI 전반에서 쓰이는 sentinel 값으로, 데이터 사전에만
   `TYPE` 7,007건·`UNITS` 4,421건 등장합니다. 수치로 그대로 읽으면 평균과 분산이 왜곡되므로
   불러온 직후 `NA` 로 치환해야 합니다.
