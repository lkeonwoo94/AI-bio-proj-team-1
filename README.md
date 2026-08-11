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

이 프로젝트는 성격이 다른 두 데이터를 씁니다. **조심해야 할 지점이 서로 반대입니다.**

| | 위험 지점 | 한 줄 요약 |
|---|---|---|
| **ADNI** | 파일이 밖으로 나가는 것 | 재배포 자체가 금지 |
| **DepMap** | 리포트에 라이선스를 잘못 적는 것 | 파일 공유는 괜찮지만 표기에 주의 |

### ADNI — 재배포 자체가 금지

**ADNI**(Alzheimer's Disease Neuroimaging Initiative) 연구 데이터의 표준 다운로드 번들입니다. 파일명이 말해주듯 **재배포 금지** 조건이 붙은 자료이며, 대부분의 CSV가 `22Jan2026` 릴리스 날짜를 달고 있습니다.

| 하지 말 것 | 해도 되는 것 |
|---|---|
| 원본 ZIP / CSV / `.rda` 커밋 | 분석 **코드** 커밋 |
| 개인 식별 가능 파생물 업로드 | 집계·요약 통계, 그림·표 (개인 식별 불가한 경우) |

커밋뿐 아니라 외부 공유(메신저, 클라우드, 스크린샷 포함)도 하지 않습니다.
- **Jupyter 노트북은 커밋 전 반드시 출력(output)을 지웁니다.** 출력 셀에 개인 데이터가 그대로 남습니다.
- 커밋 전 확인: `git status` 에 데이터 파일이 보이면 그대로 멈추고 팀에 알릴 것.


### DepMap — 재배포보다 **라이선스 표기**가 문제

DepMap은 ADNI와 달리 연구 목적 재배포 제한이 느슨합니다. 대신 **2026년에 약관이 바뀌어** AI 모델 학습에 관한 조항이 새로 생겼습니다.

> The data made available on this website were generated for research purposes and are not intended for clinical or commercial uses, including direct sale, incorporation into a product, or **the use of the data to train, develop, or enhance machine learning or AI models other than for internal research use** (each a "Commercial Use"). For clarity, machine learning and AI models are permitted to be utilized with or on the Data **for your own internal use, or shared for non-profit research purposes**, including for process optimization and analysis. Commercial Use of the Data is not permitted under these terms and may require a separate license agreement from Broad or its contributors.
>
> — DepMap 현행 이용약관. DepMap 개발자가 [포럼 4652](https://forum.depmap.org/t/4652)에서 인용 (2026-07-14)

요약하면:

- 연구 목적으로 생성된 데이터이며 임상·상업적 용도를 의도하지 않습니다. 여기에는 직접 판매, 제품에의 편입, 그리고 **내부 연구용을 벗어난 목적으로 ML·AI 모델을 학습·개발·강화하는 데 데이터를 쓰는 것**이 포함되고, 각각 "Commercial Use"로 규정됩니다.
- 단, ML·AI 모델을 **자체 내부 용도로 사용하거나 비영리 연구 목적(공정 최적화·분석 포함)으로 공유하는 것은 명시적으로 허용**됩니다.
- **→ 수업 프로젝트 / 비영리 연구 목적의 모델 학습·공유는 허용됩니다. 우리 용도는 문제없습니다.**

| 하지 말 것 | 해도 되는 것 |
|---|---|
| ❌ "CC BY 4.0이라 재배포 제한 없음" 이라고 표기 | 위 **영문 원문**을 근거로 라이선스 기재 (한국어 요약은 편의용) |
| 대용량 원본 CSV 커밋 (발현 파일 하나가 500 MB+) | 학습한 모델·집계 결과를 비영리 연구 목적으로 공유 |
| 릴리스명 없이 "DepMap 데이터" 라고만 기재 | 릴리스명(`DepMap Public 26Q1`)·다운로드 날짜·실제 파일명 명시 |

기타 알아둘 것:

- **25Q2 이후 본 릴리스는 figshare에 미러링되지 않습니다.** 과거 데이터는 figshare / AWS Open Data에 남아 있지만, 최신 릴리스는 포털에서 파일 단위로 받아야 합니다.
- 포털에 Cloudflare 캡차가 걸려 있어 **자동 다운로드가 불가능**합니다. 사람이 브라우저로 받아야 합니다.
- 릴리스마다 **파일명이 바뀝니다.** 25Q3에서 Omics 파일명 체계가 통째로 개편돼 구 이름이 삭제됐습니다. 26Q1 파일 목록 정본: [DepMap 데이터 전반 조사](docs/research/2026-08-13/depmap_overview/lkeonwoo94.md) (3. 바뀐 파일명 · 4. 전체 파일 85개 · 6. 사용 조건) — 검증 경위는 [AI 질답 정리 Q2](docs/research/2026-08-13/depmap_gpt_qna/lkeonwoo94.md#q2-depmap-26q1-실제-파일명-검증--아래-내용이-사실인지-확인해줘)


---

## ADNI 데이터 개요

| 항목 | 값 |
|---|---|
| 파일명 | `ADNI_data_Do_NOT_redistribute.zip` |
| 크기 | 1,136,659,190 바이트 (약 1.14 GB) |
| 형식 | ZIP 압축 파일 |
| 체크섬 | `2a3579bb…f39df61f` (SHA-256) |


<details>
<summary>[접기/펼치기] ADNI 데이터 더 보기... </summary>

## ADNI 내부 구조

최상위에는 카테고리별 ZIP 12개가 중첩되어 있고, 그 안에 총 **283개 파일(CSV 185개, PDF 81개)** 이 들어 있습니다.

| 카테고리 | 내용 | 압축 해제 크기 | 파일 수 | CSV | PDF |
|---|---|---:|---:|---:|---:|
| [Quick_Start](docs/adni/quick_start.md) | 전체 변수 데이터 사전 + 퀵스타트 가이드. **[필드 수가 가장 많은 테이블 기재](docs/adni/quick_start.md#도메인별-규모)** | 7.4 MB | 2 | 1 | 1 |
| [Study_Info](docs/adni/study_info.md) | 단계별 Procedures Manual/CRF + `ADNIMERGE2` R 패키지 | 169.9 MB | 21 | 3 | 14 |
| [Test_Data_for_Challenges](docs/adni/test_data_for_challenges.md) | 챌린지용 별도 테스트 세트 | 57.6 MB | 4 | 0 | 0 |
| [Subject_Characteristics](docs/adni/subject_characteristics.md) | 인구학·가족력·거주지 특성 | 6.0 MB | 9 | 8 | 1 |
| [Assessments](docs/adni/assessments.md) | 인지·기능 평가 척도 (MoCA, ADAS, FAQ, ECog 등) | 91.0 MB | 52 | 45 | 7 |
| [Remotely_Collected_Data](docs/adni/remotely_collected_data.md) | ADNI4 원격(RMT) 트랙 스크리닝·인구학·ECog·Storyteller | 61.9 MB | 9 | 7 | 2 |
| [ADSP_PHC](docs/adni/adsp_phc.md) | ADSP 조화 인지 점수(harmonized composite) | 451.2 MB | 29 | 21 | 7 |
| [Medical_History](docs/adni/medical_history.md) | 병력, 병용약물, 이상반응 | 46.4 MB | 16 | 16 | 0 |
| [Neuropathology_Results](docs/adni/neuropathology_results.md) | 부검 신경병리 소견 | 0.3 MB | 2 | 1 | 1 |
| [Curated_Data___Docs](docs/adni/curated_data_docs.md) | ADNI-DIAN 비교 연구용 큐레이션 서브셋 | 2.2 MB | 2 | 1 | 0 |
| [Imaging](docs/adni/imaging.md) | MRI 부피·위축도, amyloid PET SUVR 등 영상 파생 지표 | 541.1 MB | 125 | 78 | 42 |
| [Genetic](docs/adni/genetic.md) | TOMM40, 다유전자 위험 점수(PHS), 텔로미어, tau-PET GWAS | 160.5 MB | 12 | 4 | 6 |




---

## ADNI 참고 링크

- ADNI 공식: <https://adni.loni.usc.edu/>
- 데이터 다운로드(LONI IDA): <https://ida.loni.usc.edu/>
- ADNIMERGE2 문서: <https://atri-biostats.github.io/ADNIMERGE2>

</details>

---

## DepMap 데이터 개요

암세포주 유전자 의존성 데이터입니다. **ADNI와는 별개 트랙**으로, 항암 주제(발현 → CRISPR 의존성 예측)에 사용합니다.

| 항목 | 값 |
|---|---|
| 릴리스 | `DepMap Public 26Q1` (2026-04-01, 최신) |
| 받은 구성 | C-1 최소 구성 5개 파일 |
| 총 크기 | 746,423,423 바이트 (약 746 MB) |
| 원본 위치 | `adni-shared/raw/DepMap/` — **레포 밖** (git 추적 안 함) |
| 무결성 | md5 5/5 매니페스트 일치 ✅ |
| **학습 가능 표본 (n)** | **1,140** 세포주 (발현 ∩ CRISPR ∩ Model) |

<details>
<summary>[접기/펼치기] DepMap 데이터 더 보기... </summary>

## DepMap 파일 구성

각 파일의 shape·결측률·값 분포·주의사항은 아래 설명서에 있습니다. 설명서는 `scripts/depmap_profile.py` 가 원본에서 자동 생성합니다.

| 파일 | 역할 | shape | 크기 | 설명서 |
|---|---|---|---:|---|
| `CRISPRGeneEffect.csv` | 출력 Y — Chronos gene effect | 1,208 × 18,531 | 440.6 MB | [열기](docs/depmap/crispr_gene_effect.md) |
| `OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv` | 입력 X — log2(TPM+1) 발현 | 1,775 × 19,220 | 305.0 MB | [열기](docs/depmap/omics_expression_tpm_logp1_human_protein_coding_genes.md) |
| `Model.csv` | 메타데이터 · 조인 키 | 2,154 × 49 | 697.5 KB | [열기](docs/depmap/model.md) |
| `CRISPRInferredCommonEssentials.csv` | 보조 · 타깃 필터 | 1,827 × 1 | 25.0 KB | [열기](docs/depmap/crispr_inferred_common_essentials.md) |
| `README.txt` | DepMap 공식 릴리스 설명 | — | 47.3 KB | (원본 그대로) |

→ **[docs/depmap/](docs/depmap/README.md)** 에 교집합·유전자 겹침·암종 분포·조인 규약 정리

## DepMap 데이터 규모

| 항목 | 값 |
|---|---|
| 발현 (`IsDefaultEntryForModel` 필터 후) | 1,719 세포주 |
| CRISPR gene effect | 1,208 세포주 |
| **교집합 = 학습 표본 n** | **1,140 세포주 / 29개 lineage** |
| 공통 유전자 (발현 ∩ CRISPR) | 18,463 |
| common essential (타깃에서 제외 대상) | 1,827 |
| **선택적 의존 유전자 (제외 후 std > 0.25)** | **681** ← 실질 학습 대상 |


## DepMap 참고 링크

- DepMap 포털: <https://depmap.org/portal/>
- 데이터 다운로드(All Data): <https://depmap.org/portal/data_page/?tab=allData>
- 26Q1 릴리스 노트: <https://forum.depmap.org/t/4606>
- 파일 목록 API (캡차 없음): <https://depmap.org/portal/api/no-captcha/download/files>
- 26Q1 파일 목록 정본: [DepMap 데이터 전반 조사](docs/research/2026-08-13/depmap_overview/lkeonwoo94.md) (3. 바뀐 파일명 · 4. 전체 파일 85개)
- 최소 구성(C-1) 선정 근거: [AI 질답 정리 Q3](docs/research/2026-08-13/depmap_gpt_qna/lkeonwoo94.md#q3-그럼-최소한으로-받아야-하는-데이터가-뭐야)

</details>

---

## 폴더 구조

```
AI-bio-proj-team-1/
├── data/
│   ├── raw/          # 원본 ADNI 데이터 (수정 금지, git 추적 안 함)
│   ├── interim/       # 전처리 중간 산출물 (git 추적 안 함)
│   └── processed/     # 분석·모델 입력용 최종 데이터 (git 추적 안 함)
├── notebooks/         # 탐색적 분석용 Jupyter 노트북 (출력 정책은 아래 참고)
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
└── docs/              # 프로젝트 문서
    ├── adni/             # ADNI 데이터 사전·가이드
    ├── depmap/           # DepMap 데이터 설명서 (scripts/depmap_profile.py 자동 생성)
    ├── meetings/         # 회의록 (YYYY-MM-DD.md, TEMPLATE.md 참고)
    └── research/         # 각자 조사·탐색 내용 (YYYY-MM-DD/주제/깃허브ID.md)
```

- `data/`, `raw/`, `interim/`, `processed/` 는 `.gitignore`에서 통째로 제외됩니다. **원본·파생 데이터는 절대 커밋하지 않습니다.**
- `docs/depmap/` 은 **자동 생성물이라 직접 수정하지 않습니다.** 내용을 고치려면 `scripts/depmap_profile.py` 의 `NOTES` 를 수정하고 다시 실행하세요.
- **노트북 출력은 데이터에 따라 정책이 다릅니다.**
  - **ADNI 노트북 — 커밋 전 출력을 지웁니다.** DUA 상 재배포가 금지된 데이터라, 표·그림에 값이 남으면 그 자체가 재배포입니다.
  - **DepMap 노트북 — 출력을 그대로 둡니다.** CC BY 4.0 공개 데이터라 제약이 없고, 설명용 노트북은 출력이 있어야 읽힙니다.
- `results/tables/*.csv` 는 `*.csv` 전역 제외 규칙의 **예외로 추적합니다.** 문서가 본문에서 직접 링크하는 산출물이라 빠지면 링크가 깨집니다. 원본·파생 데이터는 여전히 `data/`·`raw/` 규칙으로 제외됩니다.
- 노트북에서 검증된 로직은 `src/`로 옮겨 재사용합니다.
- 빈 폴더는 `.gitkeep`으로 구조만 git에 유지합니다.

