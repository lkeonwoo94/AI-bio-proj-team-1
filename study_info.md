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

CSV 3개는 운영성 자료:

| 파일 | 크기 | 내용 |
|---|---:|---|
| `DELMRSCANS_22Jan2026.csv` | 10,324 × 5 | **삭제된 MRI 스캔 목록** — 영상 분석 시 제외 대상 |
| `PIFINAL_22Jan2026.csv` | 1,583 × 13 | site별 QC 플래그 |
| `RORR_22Jan2026.csv` | 34 × 28 | 결과 통보 요청 |

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

## 함정 두 가지

1. **`ADSL` 에는 `RID` 컬럼이 없습니다.** 참가자 키가 `USUBJID`/`SUBJID`인데
   원본 CSV들은 `RID`/`PTID`를 씁니다. 조인 전에 키 매핑이 필요합니다.
2. **`DX` 결측 2,116명(41%)** 은 진단 정보가 없어서가 아니라 `ADSL`이 특정 시점 스냅샷이기 때문입니다.
   종단 진단 이력은 `DXSUM` 계열 테이블에서 가져오세요.
