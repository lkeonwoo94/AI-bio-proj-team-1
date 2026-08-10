# AI-bio-proj-team-1

윤석현교수님과 함께하는 AI 바이오데이터 실습 1조

| GitHub | 역할 |
|---|---|
| [wjo9956](https://github.com/wjo9956) | 팀원 |
| [hyunhee1123](https://github.com/hyunhee1123) | 팀원 |
| [psh03](https://github.com/psh03) | 팀원 | 
| [lkeonwoo94](https://github.com/lkeonwoo94) | github admin |
| [mlbi](https://github.com/combio-dku) | advisor | 

---

## ⚠️ 데이터 취급 주의사항
**ADNI**(Alzheimer's Disease Neuroimaging Initiative) 연구 데이터의 표준 다운로드 번들입니다. 파일명이 말해주듯 **재배포 금지** 조건이 붙은 자료이며, 대부분의 CSV가 `22Jan2026` 릴리스 날짜를 달고 있습니다.

| 하지 말 것 | 해도 되는 것 |
|---|---|
| 원본 ZIP / CSV / `.rda` 커밋 | 분석 **코드** 커밋 |
| 개인 식별 가능 파생물 업로드 | 집계·요약 통계, 그림·표 (개인 식별 불가한 경우) |


- **Jupyter 노트북은 커밋 전 반드시 출력(output)을 지웁니다.** 출력 셀에 개인 데이터가 그대로 남습니다.
- 커밋 전 확인: `git status` 에 데이터 파일이 보이면 그대로 멈추고 팀에 알릴 것.

---

## ADNI 데이터 개요

| 항목 | 값 |
|---|---|
| 파일명 | `ADNI_data_Do_NOT_redistribute.zip` |
| 크기 | 1,136,659,190 바이트 (약 1.14 GB) |
| 형식 | ZIP 압축 파일 |
| 업로드 | 2026-08-07 07:48 UTC (사용자 업로드) |
| 체크섬 | `2a3579bb…f39df61f` (SHA-256) |


## 내부 구조

최상위에는 카테고리별 ZIP 12개가 중첩되어 있고, 그 안에 총 **283개 파일(CSV 185개, PDF 81개)** 이 들어 있습니다.

| 카테고리 | 압축 해제 크기 | 파일 수 | CSV | PDF |
|---|---:|---:|---:|---:|
| Quick_Start | 7.4 MB | 2 | 1 | 1 |
| Study_Info | 169.9 MB | 21 | 3 | 14 |
| Test_Data_for_Challenges | 57.6 MB | 4 | 0 | 0 |
| Assessments | 91.0 MB | 52 | 45 | 7 |
| Subject_Characteristics | 6.0 MB | 9 | 8 | 1 |
| Imaging | 541.1 MB | 125 | 78 | 42 |
| ADSP_PHC | 451.2 MB | 29 | 21 | 7 |
| Genetic | 160.5 MB | 12 | 4 | 6 |
| Remotely_Collected_Data | 61.9 MB | 9 | 7 | 2 |
| Medical_History | 46.4 MB | 16 | 16 | 0 |
| Curated_Data___Docs | 2.2 MB | 2 | 1 | 0 |
| Neuropathology_Results | 0.3 MB | 2 | 1 | 1 |


카테고리별 내용:

- **[Quick_Start](docs/quick_start.md)** — `DATADIC_21Jan2026.csv`(전체 변수 데이터 사전)와 퀵스타트 가이드. **데이터 구조 파악의 출발점**, **[필드 수가 가장 많은 테이블 기재](docs/quick_start.md#도메인별-규모)**
- **[Study_Info](docs/study_info.md)** — 단계별 Procedures Manual/CRF PDF와 `ADNIMERGE2.tar.gz` R 패키지. **실제 분석은 여기서 시작.**

- **[Test_Data_for_Challenges_…](docs/test_data_for_challenges.md)** — 챌린지용 별도 테스트 세트(추가 중첩 압축).
- **[Assessments](docs/assessments.md)** — MoCA, ADAS, FAQ, ECog(본인/보호자) 등 인지·기능 평가 척도.
- **[ADSP_PHC](docs/adsp_phc.md)** — Alzheimer's Disease Sequencing Project 조화 인지 점수(harmonized composite).
- **[Subject_Characteristics](docs/subject_characteristics.md)** — 인구학 정보(`PTDEMOG`), 가족력(`FHQ`, `FAMHXPAR`), 거주지 특성(`ADI`, `RURALITY`).
- **[Medical_History](docs/medical_history.md)** — 병력, 병용약물, 이상반응.
- **[Neuropathology_Results](docs/neuropathology_results.md)** — 부검 신경병리 소견 `NEUROPATH_22Jan2026.csv`.
- **[Curated_Data___Docs](docs/curated_data_docs.md)** — ADNI-DIAN 비교 연구용 큐레이션 서브셋.
- **[Remotely_Collected_Data](docs/remotely_collected_data.md)** — ADNI4 원격(RMT) 트랙 스크리닝·인구학·ECog·Storyteller 검사.

- **[Imaging](docs/imaging.md)** — MRI 부피(`UCSDVOL`, `UCSFSNTVOL`, `BSI`), 위축도(`UCSFATRPHY`), amyloid PET SUVR(`PIBPETSUVR`) 등 영상 파생 지표.
- **[Genetic](docs/genetic.md)** — APOE 인접 `TOMM40`, Desikan lab 다유전자 위험 점수(PHS), 텔로미어 비율, tau-PET GWAS 요약통계.



---

## 참고 링크

- ADNI 공식: <https://adni.loni.usc.edu/>
- 데이터 다운로드(LONI IDA): <https://ida.loni.usc.edu/>
- ADNIMERGE2 문서: <https://atri-biostats.github.io/ADNIMERGE2>

