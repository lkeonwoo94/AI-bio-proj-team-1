# Quick_Start — 데이터 사전 (DATADIC)

## PDF
이 페이지는 **ADNI(Alzheimer’s Disease Neuroimaging Initiative)** 연구의 빠른 시작 가이드입니다. 

**ADNI 연구 개요**
- ADNI 연구는 2004년부터 지속되어 왔으며, ADNI1, ADNIGO, ADNI2, ADNI3, ADNI4의 5단계로 구성되어 있습니다.  
- 연구 목적은 알츠하이머병 관련 데이터를 수집하고 분석하는 것입니다.  
- 데이터에는 뇌영상(MRI, PET), 병리 슬라이드, 생체표지자(biomarker) 등이 포함됩니다.

**데이터 접근 방법**
- 데이터는 **[IDA(ADNI Image & Data Archive)](https://ida.loni.usc.edu/)** 웹사이트에서 다운로드할 수 있습니다.  
- “Study Files” 섹션에서 “Search and Download” 기능을 통해 접근 가능합니다.


**파일 구성**
- 각 데이터 유형별로 파일이 구분되어 있습니다:
  - **Diagnosis**: 진단 데이터(Assessments.zip → Diagnostic Summary)
  - **Demographics**: 참가자 정보 (Subject Characteristics.zip → SubjectDemographics → Subject Demographics)
  - **Cognitive Assessments**: 인지 평가 결과 (Assessments.zip → Neuropsychological)
  - **Biospecimen Results**: 생체표본 분석 결과 (ApoE4 Genotyping, Biofluid)
  - **MRI Measurements**: MRI 측정값 (Imaging.zip)
  - **PET Measurements**: PET 측정값 (Imaging.zip)

**주의 사항**
- 파일 이름에는 프로젝트 코드(PID), 방문 코드(VISCODE), 연구 ID(RID)가 포함되어 있습니다.  
- EXAMDATE, SCANDATE 등의 필드를 활용해 종단(longitudinal) 분석을 수행할 수 있습니다.
서 조회합니다.

---

## DATADIC.csv 
`DATADIC_21Jan2026.csv` = **34,930행 × 13열**의 전체 데이터 사전.

| column_name    | semantic        | column_type | min                                                                                         | max                                                                                                                                                                                                                                                                                                                                                                                                                                      | approx_unique | count | null_percentage |
| -------------- | --------------- | ----------- | ------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------: | ----: | --------------: |
| PHASE          | 해당 ADNI 단계      | VARCHAR     | ADNI1                                                                                       | [ADNIGO,2]                                                                                                                                                                                                                                                                                                                                                                                                                               |            17 | 34930 |           41.48 |
| CRFNAME        | 수집에 쓰인 증례기록서 이름 | VARCHAR     | -4                                                                                          | sPAP Avid ADNI Florbetapir summaries                                                                                                                                                                                                                                                                                                                                                                                                     |           344 | 34930 |            0.37 |
| TBLNAME        | 테이블(=CSV 파일) 이름 | VARCHAR     | ADAS                                                                                        | npiq                                                                                                                                                                                                                                                                                                                                                                                                                                     |           318 | 34930 |            0.00 |
| FLDNAME        | 변수명             | VARCHAR     | 3RD_VENTRICLE                                                                               | wvDMN_to_wpDMN                                                                                                                                                                                                                                                                                                                                                                                                                           |         18266 | 34930 |            0.00 |
| TEXT           | 변수 설명문          | VARCHAR     | P01375                                                                                      | zolpidem ;CHEM_ID: 100004174 ;LIB_ID: 400 ;COMP_ID: 62976 ;CHRO_LIB_ENTRY_ID: 221394 ;CHEMICAL_NAME: zolpidem ;SHORT_NAME: zolpidem ;RI: 3346 ;MASS: 308.17574 ;SUPER_PATHWAY: Xenobiotics ;SUB_PATHWAY: Drug - Psychoactive ;PATHWAY_SORTORDER: 5888 ;PATHWAY_STATUS: ;TYPE: NAMED ;INCHIKEY: ;SMILES: CN(C(CC1=C(C2=CC=C(C=C2)C)N=C3C=CC(C)=CN13)=O)C ;CAS: 82626-48-0 ;CHEMSPIDER: ;KEGG: ;HMDB: ;PUBCHEM: ;PLATFORM: LC/MS Pos Early |         13863 | 34930 |            2.64 |
| TYPE           | 자료형             | VARCHAR     | -4                                                                                          | varchar                                                                                                                                                                                                                                                                                                                                                                                                                                  |            45 | 34930 |            1.57 |
| LENGTH         | 자릿수             | VARCHAR     | 3 Characters                                                                                | Min=70; Max=250; Step=1                                                                                                                                                                                                                                                                                                                                                                                                                  |           183 | 34930 |           20.29 |
| DD_CRF_VERSION | CRF 버전          | VARCHAR     | annual                                                                                      | v4                                                                                                                                                                                                                                                                                                                                                                                                                                       |            13 | 34930 |           96.49 |
| CODE           | 코딩값 정의          | VARCHAR     | (-1) Not assessed; (0) No medical abnormalities found; (1) Medical abnormalities identified | year, 8888=not applicable; 9999=unknown                                                                                                                                                                                                                                                                                                                                                                                                  |          1432 | 34930 |           54.93 |
| UNITS          | 단위              | VARCHAR     | %                                                                                           | years                                                                                                                                                                                                                                                                                                                                                                                                                                    |           152 | 34930 |           54.84 |
| STATUS         | 변수 상태           | VARCHAR     | Archived                                                                                    | TEXT Harmonized                                                                                                                                                                                                                                                                                                                                                                                                                          |            13 | 34930 |           85.67 |
| CODE_CHANGES   | 코드 변경 여부 플래그    | BOOLEAN     | true                                                                                        | true                                                                                                                                                                                                                                                                                                                                                                                                                                     |             1 | 34930 |           99.71 |
| MAPPING_NOTES  | 매핑 시 주의사항       | VARCHAR     | ADAS Item Level and Sub Scores Redacted                                                     | Updates applied on a subset of records following review of data frozen up to Oct 6, 2025                                                                                                                                                                                                                                                                                                                                                 |           130 | 34930 |           93.35 |


-  PHASE 태그 분포 미태깅 14,490행(41%)은 외부 연구실이 제공한 오믹스·영상 테이블이 특정 프로토콜에 묶이지 않기 때문입니다.
- **`-4` 주의.** ADNI 전반에서 `-4` 는 결측을 뜻하는 sentinel입니다. `TYPE` 에 7,007건, `UNITS` 에 4,421건 나타납니다. 수치로 읽으면 평균이 망가지므로 분석 전에 `NA` 로 치환해야 합니다.
- `FLDNAME` 고유값이 18,223개인데 전체가 34,930행인 이유는 **같은 변수명이 여러 테이블에 등장**하기 때문입니다
(`RID`, `VISCODE` 같은 키 컬럼). 조회할 때 `TBLNAME` 과 함께 걸러야 합니다.

- `CRFNAME` ↔ `TBLNAME` 은 1:1이 아닙니다. CRF 하나가 여러 테이블로 갈라진 경우 11건,
테이블 하나에 여러 CRF가 매핑된 경우 39건 (각각 최대 3개).




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


