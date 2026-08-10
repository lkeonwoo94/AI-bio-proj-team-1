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
| 체크섬 | `2a3579bb…f39df61f` (SHA-256) |


## 내부 구조

최상위에는 카테고리별 ZIP 12개가 중첩되어 있고, 그 안에 총 **283개 파일(CSV 185개, PDF 81개)** 이 들어 있습니다.

| 카테고리 | 내용 | 압축 해제 크기 | 파일 수 | CSV | PDF |
|---|---|---:|---:|---:|---:|
| [Quick_Start](docs/quick_start.md) | 전체 변수 데이터 사전 + 퀵스타트 가이드. **[필드 수가 가장 많은 테이블 기재](docs/quick_start.md#도메인별-규모)** | 7.4 MB | 2 | 1 | 1 |
| [Study_Info](docs/study_info.md) | 단계별 Procedures Manual/CRF + `ADNIMERGE2` R 패키지 | 169.9 MB | 21 | 3 | 14 |
| [Test_Data_for_Challenges](docs/test_data_for_challenges.md) | 챌린지용 별도 테스트 세트 | 57.6 MB | 4 | 0 | 0 |
| [Subject_Characteristics](docs/subject_characteristics.md) | 인구학·가족력·거주지 특성 | 6.0 MB | 9 | 8 | 1 |
| [Assessments](docs/assessments.md) | 인지·기능 평가 척도 (MoCA, ADAS, FAQ, ECog 등) | 91.0 MB | 52 | 45 | 7 |
| [Remotely_Collected_Data](docs/remotely_collected_data.md) | ADNI4 원격(RMT) 트랙 스크리닝·인구학·ECog·Storyteller | 61.9 MB | 9 | 7 | 2 |
| [ADSP_PHC](docs/adsp_phc.md) | ADSP 조화 인지 점수(harmonized composite) | 451.2 MB | 29 | 21 | 7 |
| [Medical_History](docs/medical_history.md) | 병력, 병용약물, 이상반응 | 46.4 MB | 16 | 16 | 0 |
| [Neuropathology_Results](docs/neuropathology_results.md) | 부검 신경병리 소견 | 0.3 MB | 2 | 1 | 1 |
| [Curated_Data___Docs](docs/curated_data_docs.md) | ADNI-DIAN 비교 연구용 큐레이션 서브셋 | 2.2 MB | 2 | 1 | 0 |
| [Imaging](docs/imaging.md) | MRI 부피·위축도, amyloid PET SUVR 등 영상 파생 지표 | 541.1 MB | 125 | 78 | 42 |
| [Genetic](docs/genetic.md) | TOMM40, 다유전자 위험 점수(PHS), 텔로미어, tau-PET GWAS | 160.5 MB | 12 | 4 | 6 |




---

## 참고 링크

- ADNI 공식: <https://adni.loni.usc.edu/>
- 데이터 다운로드(LONI IDA): <https://ida.loni.usc.edu/>
- ADNIMERGE2 문서: <https://atri-biostats.github.io/ADNIMERGE2>

---

## 폴더 구조

```
AI-bio-proj-team-1/
├── data/
│   ├── raw/          # 원본 ADNI 데이터 (수정 금지, git 추적 안 함)
│   ├── interim/       # 전처리 중간 산출물 (git 추적 안 함)
│   └── processed/     # 분석·모델 입력용 최종 데이터 (git 추적 안 함)
├── notebooks/         # 탐색적 분석용 Jupyter 노트북 (커밋 전 출력 지우기)
├── src/               # 재사용 코드 모듈
│   ├── preprocessing/    # 데이터 로딩·전처리
│   ├── features/        # 피처 엔지니어링
│   ├── models/           # 모델 정의·학습
│   └── viz/              # 시각화 함수
├── scripts/           # 파이프라인 실행용 CLI 스크립트
├── results/
│   ├── figures/        # 그림 (개인 식별 불가한 것만)
│   └── tables/          # 집계·요약 표
├── models/            # 학습된 모델 가중치·체크포인트 (대용량은 git 추적 안 함)
├── configs/           # 실험 설정 (yaml 등)
├── tests/             # 테스트 코드
└── docs/              # 프로젝트 문서, 데이터 사전 등
```

- `data/`, `raw/`, `interim/`, `processed/` 는 `.gitignore`에서 통째로 제외됩니다. **원본·파생 데이터는 절대 커밋하지 않습니다.**
- 노트북에서 검증된 로직은 `src/`로 옮겨 재사용합니다.
- 빈 폴더는 `.gitkeep`으로 구조만 git에 유지합니다.

