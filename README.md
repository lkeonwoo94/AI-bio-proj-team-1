# AI-bio-proj-team-1

윤석현교수님과 함께하는 AI 바이오데이터 실습 1조

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

## 카테고리별 상세

각 카테고리를 풀어 확인한 결과는 별도 문서로 정리했습니다.

| 문서 | 카테고리 | 내용 |
|---|---|---|
| [quick_start.md](quick_start.md) | Quick_Start (7.4 MB) | 데이터 사전 `DATADIC` 34,930행 — 336개 테이블 전 변수 정의, 조회 방법 |
| [study_info.md](study_info.md) | Study_Info (169.9 MB) | 프로토콜 PDF, `ADNIMERGE2` R 패키지 217개 테이블, `ADSL` 코호트 요약, 조인 함정 |

나머지 카테고리(Imaging, Genetic, Assessments, ADSP_PHC 등)는 아직 풀지 않았습니다.
확인하는 대로 같은 형식으로 문서를 추가합니다.

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
