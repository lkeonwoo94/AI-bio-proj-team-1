# Quick_Start — 데이터 사전 (DATADIC)

번들 `Quick_Start.zip` (7.4 MB, 파일 2개) 의 압축 해제 결과입니다.

> 전체 번들 구조는 [README.md](README.md) · Study_Info 카테고리는 [study_info.md](study_info.md)

**데이터 구조 파악의 출발점.** 어떤 CSV의 어떤 컬럼이 무슨 뜻인지 모를 때 여기서 조회합니다.

---

## 디렉터리 내용

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

---

## DATADIC 컬럼 구조

13개 컬럼 중 항상 채워지는 것은 `TBLNAME`/`FLDNAME` 둘뿐입니다. 나머지는 결측이 흔합니다.

| 컬럼 | 채워진 행 | 고유값 | 의미 |
|---|---:|---:|---|
| `TBLNAME` | 34,930 | 336 | 테이블(=CSV 파일) 이름 |
| `FLDNAME` | 34,930 | 18,223 | 변수명 |
| `CRFNAME` | 34,801 | 362 | 수집에 쓰인 증례기록서 이름 |
| `TEXT` | 34,007 | 15,788 | 변수 설명문 |
| `TYPE` | 34,382 | 51 | 자료형 |
| `LENGTH` | 27,841 | 182 | 자릿수 |
| `PHASE` | 20,440 | 17 | 해당 ADNI 단계 |
| `UNITS` | 15,775 | 151 | 단위 |
| `CODE` | 15,444 | 1,177 | 코딩값 정의 |
| `STATUS` | 5,006 | 13 | 변수 상태 |
| `MAPPING_NOTES` | 2,323 | 122 | 매핑 시 주의사항 |
| `DD_CRF_VERSION` | 1,225 | 12 | CRF 버전 |
| `CODE_CHANGES` | 102 | 2 | 코드 변경 여부 플래그 |

`FLDNAME` 고유값이 18,223개인데 전체가 34,930행인 이유는 **같은 변수명이 여러 테이블에 등장**하기 때문입니다
(`RID`, `VISCODE` 같은 키 컬럼). 조회할 때 `TBLNAME` 과 함께 걸러야 합니다.

`CRFNAME` ↔ `TBLNAME` 은 1:1이 아닙니다. CRF 하나가 여러 테이블로 갈라진 경우 11건,
테이블 하나에 여러 CRF가 매핑된 경우 39건 (각각 최대 3개).

### TYPE 값

| 값 | 행 수 | 의미 |
|---|---:|---|
| `N` / `NUMERIC` | 13,649 / 6,044 | 수치형 |
| `T` / `TEXT` | 3,699 / 773 | 문자열 |
| `-4` | 7,007 | **결측 표시 sentinel** |
| `S` | 625 | 선택형 |
| `D` | 608 | 날짜 |

> **`-4` 주의.** ADNI 전반에서 `-4` 는 결측을 뜻하는 sentinel입니다.
> `TYPE` 에 7,007건, `UNITS` 에 4,421건 나타납니다. 수치로 읽으면 평균이 망가지므로
> 분석 전에 `NA` 로 치환해야 합니다.

### STATUS — 변수 상태

29,924행은 비어 있고(정상 변수), 나머지가 특수 상태입니다.

| 상태 | 행 수 | 뜻 |
|---|---:|---|
| Archived | 3,507 | 보관 처리 — 최신 릴리스에서는 갱신되지 않음 |
| Redacted | 1,208 | **삭제됨** — 개인정보 보호를 위해 값이 비워짐 |
| Mapped | 115 | 다른 변수로 매핑됨 |
| Code Harmonized | 76 | 단계 간 코딩값 통일 |
| Harmonized | 32 | 단계 간 변수 통일 |
| Pending Harmonization | 21 | 통일 작업 대기 |
| Deprecated | 18 | 사용 중단 |

`Redacted` 가 몰린 테이블: `ADAS` 463 · `NEUROEXM` 70 · `PHYSICAL` 69 · `MMSE` 65 · `RORR` 44 · `MRIMETA` 43.
ADAS와 MMSE의 문항 수준 데이터가 대거 삭제되어 있으므로, 문항별 분석을 계획한다면 먼저 확인이 필요합니다.

`MAPPING_NOTES` 상위 항목이 그 이유를 설명합니다:

- 673건 — 자유 기술 항목은 개인·사이트 정보 검토 대기로 삭제
- 477건 — ADAS 문항 수준 및 하위 점수 삭제
- 299 / 293건 — 데이터 입력·수정 타임스탬프, 종단 해석에는 무관
- 72건 — `1=Correct; 2=Incorrect` → `0=0 - Incorrect; 1=1 - Correct` 로 코드 통일

### UNITS 상위

`mm^3` 1,439 · `mm` 1,416 · `mm3` 1,394 · `ml / 100g tissue / min` 907 · `mm2` 722 · `nM` 638 · `Normalized Counts` 581.

> `mm^3` 과 `mm3` 이 **표기만 다른 같은 단위**로 병존합니다. 부피 변수를 단위로 필터링할 때 둘 다 잡아야 합니다.
> `ml / 100g tissue / min` 은 ASL 관류(CBF), `nM` 은 CSF/혈장 바이오마커 농도입니다.

---

## 도메인별 규모

`CRFNAME` 키워드로 분류한 결과입니다 (한 테이블이 여러 도메인에 걸칠 수 있어 합계는 336을 넘습니다).

| 도메인 | 테이블 | 필드 |
|---|---:|---:|
| 바이오마커 (CSF·혈장·프로테오믹스·메타볼로믹스·리피도믹스) | 82 | 7,898 |
| MRI (FreeSurfer·부피·피질·ASL·DTI) | 50 | 8,016 |
| PET (AV45·AV1451·FBB·PIB·FDG) | 31 | 4,546 |
| 인지검사 (ADAS·MMSE·MoCA·RAVLT·Trail) | 22 | 2,513 |
| 유전 (GWAS·APOE·SNP·다유전자점수) | 8 | 291 |

필드 수 상위 테이블은 오믹스 계열이 압도적입니다.

| 테이블 | 필드 | 설명 |
|---|---:|---|
| `EMORY_CSF_TMT_MS` | 3,914 | Emory CSF TMT 질량분석 프로테오믹스 |
| `ADMC_DUKE_SERUM_METABOLON_HD4` | 1,358 | Duke 비표적 혈청 메타볼로믹스 |
| `ADMCLIPIDOMICSMEIKLELABLONG` | 789 | Meikle lab 종단 리피도믹스 |
| `NEUROPATH` | 734 | NACC 신경병리 양식 v11 |
| `UCSFASLFS` | 700 | ASL 관류 CBF, FreeSurfer ROI별 |
| `UCBERKELEYAV45_8MM` | 601 | amyloid PET SUVR |
| `UCBERKELEYAV1451_8MM` | 584 | tau PET SUVR |

---

## 조인 키 보유 현황

336개 테이블 중 각 키를 가진 테이블 수입니다.

| 키 | 보유 테이블 | 형식 |
|---|---:|---|
| `RID` | 311 | 정수 (예: `2`) |
| `VISCODE` | 264 | 문자 (예: `bl`, `m06`) |
| `VISCODE2` | 227 | 문자, 단계 간 통일 버전 |
| `EXAMDATE` | 193 | 날짜 |
| `PTID` | 133 | 문자 (예: `011_S_0002`) |
| `PHASE` | 24 | 문자 |
| `USUBJID` | **0** | — |

> **`RID` 가 사실상 표준 키**입니다 (311/336). `USUBJID` 는 원본 CSV 어디에도 없고
> `ADNIMERGE2` 패키지 테이블에만 존재합니다 — 두 계통을 섞을 때 변환이 필요한 이유입니다
> (자세한 내용은 [study_info.md](study_info.md) 참고).

### PHASE 태그 분포

| 태그 | 행 수 |
|---|---:|
| 미태깅 | 14,490 |
| `[ADNI1,GO,2,3]` | 4,159 |
| `ADNI3` | 2,828 |
| `ADNI1` | 2,582 |
| `ADNI4` | 2,385 |
| `[ADNI1,GO,2]` | 2,066 |
| `ADNI2` | 2,039 |
| `ADNIGO` | 1,783 |
| 기타 다단계 조합 | 2,598 |

미태깅 14,490행(41%)은 외부 연구실이 제공한 오믹스·영상 테이블이 특정 프로토콜에 묶이지 않기 때문입니다.
