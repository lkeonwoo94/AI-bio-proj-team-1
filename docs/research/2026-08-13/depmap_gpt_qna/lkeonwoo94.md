# AI에게 물어본 질답 정리 (DepMap)

- **관련 TODO:** [2026-08-07](../../../meetings/2026-08-07.md)

## 조사 배경

- 회의에서 정한 TODO: AI(GPT 등)에게 아래를 물어보고 답변 정리
  1. 이 데이터로 무엇을 할 수 있는지
  2. 데이터 설명 요청
  3. 구상 중인 모델이 반응할지(적합한지) 문의

---

## Q1. ADNI로 "유전자 발현으로 CRISPR 의존성 예측"이 가능한지
- **작성자:** @lkeonwoo94
- **날짜:** 2026-08-10
- **질문:** 지금까지 조사한 ADNI 데이터로 회의에서 정한 아이디어 1(유전자 발현 → CRISPR 의존성 예측)을 진행할 수 있는지 검토 요청
- **답변자:** Claude (Claude Code)
- **답변 시각:** 2026-08-10 18:30 KST

### A-1. ADNI로는 불가능 — 트랙이 다름

데이터가 부족한 게 아니라 **정답(label)에 해당하는 것이 아예 없다.**

- CRISPR 의존성(gene effect)은 **암세포주에 CRISPR 넉아웃을 걸고 증식을 측정한 실험값**이다. ADNI는 살아있는 사람을 추적하는 관찰 코호트 연구라 이런 실험값이 존재할 수 없다.
- ADNI `Genetic/` 에 있는 것은 TOMM40 유전형, 다유전자 위험점수(PHS), 텔로미어 길이, tau-PET GWAS 요약치 수준이다 ([genetic.md](../../../adni/genetic.md)). 세포주 단위 발현 매트릭스도, 넉아웃 스크린도 없다.

→ **ADNI 트랙과 DepMap 트랙은 완전히 별개.** 주제를 항암(DepMap)으로 정했으므로 ADNI 문서화는 일단락하고 DepMap 데이터로 넘어가야 한다.

### A-2. 아이디어 1 자체는 실현 가능 (DepMap 기준)

회의에서 나온 후보 중 **가장 현실적인 선택**이다. 다만 "모델을 돌리는 것"은 쉽고, **"평가를 제대로 하는 것"에서 성패가 갈린다.** 잘못 평가하면 R² 0.9가 나오는데 전부 허수인, 함정이 유명한 벤치마크다.

또한 이 주제는 **이미 잘 닦여 있는 길**이다. DepMap이 분기마다 Predictability 모델 결과를 함께 배포하고, Dempster et al. (2020) 등 레퍼런스 논문도 있다. 새로운 발견을 노리기는 어렵지만, **비교 기준이 명확하다는 점은 수업 프로젝트에서는 오히려 장점**이다. "우리 모델이 DepMap 공식 베이스라인 대비 어떤가"로 바로 프레이밍할 수 있다.

### A-3. 필요한 데이터 (2026-08-10 기준 아직 미다운로드)

> **2026-08-11 수정.** 아래 파일명은 최초 작성 시 24Q2~25Q2 기준으로 적혀 있었으나, **25Q3에서 Omics 파일명 체계가 바뀌어 구 이름이 전부 삭제**됐다. 실제 26Q1 파일 목록을 받아 대조한 결과로 교체했다. 검증 경위는 아래 [Q2](#q2-depmap-26q1-실제-파일명-검증--아래-내용이-사실인지-확인해줘), 26Q1 전체 파일 목록은 [DepMap 데이터 전반 조사 4](../depmap_overview/lkeonwoo94.md#4-depmap-public-26q1-전체-파일-85개) 참고.

**대상 릴리스: DepMap Public 26Q1 (2026-04-01, 최신)**

| 파일 | 역할 | 대략 규모 |
|---|---|---|
| `CRISPRGeneEffect.csv` | **출력 Y** — Chronos gene effect | 약 1,100~1,200 세포주 × 약 18,000 유전자 |
| `OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv` | **입력 X** — log2(TPM+1) 발현 | 약 1,400~1,500 세포주 × 약 19,000 유전자 |
| `Model.csv` | 세포주 메타데이터 (OncotreeLineage = 암종) | 작음 |
| `SubtypeMatrix.csv` | 암종·아형 one-hot — A-4 ④ 베이스라인에 바로 사용 | 작음 |
| `CRISPRInferredCommonEssentials.csv` | common essential 목록 — A-4 ③ 3분류에 사용 | 작음 |
| `OmicsCNGeneWGS.csv`, `OmicsSomaticMutationsMatrix{Damaging,Hotspot}.csv` | 추가 입력 (2단계) | 중~대 |

**옛 이름 → 26Q1 이름** (구 이름으로는 파일을 찾을 수 없음)

| 구 이름 (~25Q2) | 26Q1 |
|---|---|
| `OmicsExpressionProteinCodingGenesTPMLogp1.csv` | `OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv` |
| `OmicsCNGene.csv` | `OmicsCNGeneWGS.csv` |

- 발현 ∩ CRISPR 교집합이 실제 학습 가능한 세포주 수이며 **대략 1,000~1,100개**. 이것이 우리의 **n**이다.
- 위 숫자는 릴리스마다 바뀌므로 다운로드 시점에 확인할 것. **반드시 같은 분기 릴리스로 통일**해서 받는다(섞으면 세포주 ID가 맞지 않음).
- Chronos 값 해석: **0 = 넉아웃해도 멀쩡, -1 = 공통 필수 유전자의 중앙값 수준으로 죽음.** 음수로 갈수록 의존성이 크다.

**다운로드 전 주의 3가지**

1. **발현 파일은 Stranded / 비-Stranded 두 종류가 있고 공식 권장이 없다.** DepMap이 25Q2 노트에서 "strandedness 외의 배치 효과 요인을 보정할 방법을 탐색 중"이라고 밝힌 상태. 어느 쪽을 썼는지 반드시 기록할 것. 배치보정판은 25Q2에서 제거됐고 대체 파일이 없다.
2. **`OmicsCNGeneWGS.csv`는 log2가 아니다.** 해당 세포주 자신의 ploidy 대비 **선형 비율**이라 `~1.0 = 변화 없음`이며, 4배체 세포주에서 4카피인 유전자도 1.0이 된다. log2가 필요하면 `PortalOmicsCNGeneLog2.csv`를 쓴다.
3. **25Q3부터 omics 테이블에 메타데이터 컬럼이 붙는다** (`ModelID`, `IsDefaultEntryForModel`, `ModelConditionID`, `IsDefaultEntryForMC`, `SequencingID`). 한 모델이 여러 행을 가질 수 있으므로 `IsDefaultEntryForModel == "Yes"` 로 먼저 필터링해야 한다. 안 하면 중복 세포주가 학습셋에 들어가 A-4 (부수) 항목의 누출이 그대로 발생한다.

### A-4. 이 주제의 진짜 함정 4가지

**① 전역 R²로 평가하면 안 된다 (가장 흔한 실패)**
18,000개 유전자 중 대부분은 모든 세포주에서 gene effect가 거의 0으로 붙박이다. 세포×유전자 쌍을 전부 모아 R²를 계산하면 모델이 "유전자별 평균"만 외워도 0.9가 넘는다. 아무것도 예측하지 못한 것이다.
→ **평가는 반드시 유전자별로, 세포주 축을 따라 Pearson r을 계산**하고 그 분포를 본다.

**② "유전자별 평균 예측" 베이스라인을 반드시 이겨야 한다**
위와 같은 이유로 이 베이스라인이 매우 강하다. 명시적으로 넣고 비교하지 않으면 결과 해석이 불가능하다.

**③ 예측 가능한 유전자는 소수 — 그게 정상이고, 그게 결과다**
교차검증에서 r > 0.5로 예측되는 유전자는 전체의 몇 % 수준(수백 개)에 그친다. 이를 "실패"로 볼 게 아니라 **"어떤 유전자가 예측 가능한가"를 찾아내는 것 자체가 결과물**이다. 따라서 처음부터 유전자를 세 부류로 나눠 따로 보고한다.

- 공통 필수(common essential) — 분산이 없어 예측이 무의미
- **선택적 의존(selective) — 분산 큰 상위 약 1,500~2,000개. 여기가 전장(戰場)**
- 비발현/무의존 — 사실상 상수

**④ 암종(lineage)만으로 맞히는 것을 발현의 공로로 착각하기 쉽다**
"흑색종 세포주면 SOX10에 의존한다" 같은 것은 발현을 보지 않고 암종만 알아도 맞힌다.
→ **암종 원핫만 넣은 베이스라인**을 따로 돌려, 발현이 그 위에 얹어주는 증분을 보여야 의미가 있다.

**(부수) 분할은 반드시 세포주 단위로.** (gene, cell) 쌍 단위로 섞어 나누면 같은 세포주가 train/test에 동시에 들어가 누출된다.

### A-5. 권장 설계

**모델** — 딥러닝은 1단계에서 비추천. n≈1,000에 p≈19,000이라 **Elastic Net이 DepMap 공식 베이스라인이자 실제로 가장 강한 축**이다. XGBoost는 비교군, MLP/Multi-task는 그 다음. 회의록의 "구현 난이도 낮고 해석 용이"라는 판단은 정확하며, 그것이 성립하는 것은 선형 모델로 갈 때다.

**계산량 주의** — 18,000개 유전자 각각에 ElasticNetCV를 돌리면 CPU로 매우 오래 걸린다. **선택적 의존 유전자 약 1,500개로 한정**하면 몇 시간 안에 끝난다. 처음부터 전체를 돌릴 생각은 하지 않는 편이 좋다.

**단계**

1. 데이터 수령 후 교집합 세포주 확정 → parquet 변환 (CSV를 그대로 반복 로딩하면 너무 느림)
2. gene effect 분산 기준으로 타깃 유전자 선별 + 3분류 라벨링
3. 베이스라인 3종 (유전자별 평균 / 암종만 / 자기 자신 발현만)
4. Elastic Net → 유전자별 r 분포 보고
5. 잘 맞는 유전자의 상위 계수 확인 — 여기서 **자기 자신 발현이나 패럴로그(SMARCA2↔SMARCA4, ARID1A↔ARID1B 등)가 잡히면 파이프라인이 정상 작동한다는 신호**다. 새 발견이 아니라 검증 지표로 사용한다.

---


## Q2. DepMap 26Q1 실제 파일명 검증 — 아래 내용이 사실인지 확인해줘

- **작성자:** @lkeonwoo94
- **날짜:** 2026-08-11
- **질문:** 별도로 GPT/Claude 에 물어본 DepMap 다운로드 가이드(아래 접힌 원문)가 26Q1 기준으로 맞는지 검증 요청
- **답변자:** Claude (Claude Code)
- **답변 시각:** 2026-08-11 KST

**질문 배경**

- 위 [A-3](#a-3-필요한-데이터-2026-08-10-기준-아직-미다운로드) 및 별도로 GPT에 물어본 답변에서 **다운로드할 파일명이 다수 틀린 것**을 발견.
- 원인: 25Q3에서 Omics 파일 이름 체계가 대대적으로 바뀌었는데, 학습 데이터가 그 이전(24Q2~25Q2) 기준이라 구버전 이름을 그대로 답한 것.
- DepMap 포털이 2026년 중 Cloudflare 캡차를 걸어서 파일 목록을 프로그래밍 방식으로 볼 수 없게 됐고, 그래서 AI들이 "확인 못 했다"며 추측으로 답하는 상황.
- → **공식 파일 목록을 직접 받아서 대조**한 결과를 여기 남긴다.

<details>
<summary>접기/펼치기</summary>


판단·추천 레이어를 빼고, 해당되는 파일을 층위별로 전부 나열하는 형태로 다시 정리할게. 무엇을 고를지는 네가 결정하는 걸로.

**파일명 검증 안내:** 26Q1 파일 목록을 직접 열어보지 못했어(포털 봇 확인). 아래 파일명 중 릴리스 노트·논문에서 실제로 확인된 것은 ✅, 이전 릴리스 기준이라 26Q1에서 이름이 바뀌었을 수 있는 것은 ◻로 표시했어. ◻는 릴리스 페이지 목록에서 대조해줘.

---

**릴리스 현황 (사실)**

- **DepMap Public 26Q1** — 최신. 2026년 4월 1일 공개
- **PRISM Repurposing Public 24Q2** — PRISM 공개 최신. DepMap 본 릴리스와 주기가 별개라 26Q1과 시점이 어긋남
- **PRISM Repurposing (Corsello 2020)** — primary/secondary 레거시 릴리스, figshare 상주
- 25Q2 이후 DepMap 본 릴리스는 figshare에 미러링되지 않고, 포털 Custom Downloads 탭도 세포주/유전자 필터를 걸어야 다중 파일을 받을 수 있음

---

**1. CRISPR 의존성 — 층위별 전체**

| 파일 | 단위 | 내용 | 링크 |
|---|---|---|---|
| ✅ `CRISPRGeneEffect.csv` | model × gene | Chronos 점수. 모델 단위로 통합됨. 0 = 무영향, −1 = pan-essential 중앙값 | [포털](https://depmap.org/portal/data_page/?file=CRISPRGeneEffect.csv&release=DepMap+Public+26Q1&tab=allData) |
| ✅ `CRISPRGeneEffectUncorrected.csv` | model × gene | 동일하되 보정 전 값 | [포털](https://depmap.org/portal/data_page/?file=CRISPRGeneEffectUncorrected.csv&release=DepMap+Public+26Q1&tab=allData) |
| ◻ `CRISPRGeneDependency.csv` | model × gene | Chronos 점수를 EM으로 0~1 의존 확률로 변환. 귀무 분포는 비발현 유전자와 nonessential 목록에서 잡음 | [포털](https://depmap.org/portal/data_page/?file=CRISPRGeneDependency.csv&release=DepMap+Public+26Q1&tab=allData) |
| ✅ `ScreenGeneEffect.csv` | **screen** × gene | 개별 스크린 단위. 한 모델이 Avana·KY·Humagne로 중복 스크리닝되면 각각 별도 행 | [포털](https://depmap.org/portal/data_page/?file=ScreenGeneEffect.csv&release=DepMap+Public+26Q1&tab=allData) |
| ✅ `ScreenGeneEffectUncorrected.csv` | screen × gene | 위의 보정 전 | [포털](https://depmap.org/portal/data_page/?file=ScreenGeneEffectUncorrected.csv&release=DepMap+Public+26Q1&tab=allData) |
| ✅ `ScreenSequenceMap.csv` | sequence | 스크린–시퀀싱 런–모델–라이브러리 대응표 | [포털](https://depmap.org/portal/data_page/?file=ScreenSequenceMap.csv&release=DepMap+Public+26Q1&tab=allData) |
| ◻ `AvanaRawReadcounts.csv` / `KYRawReadcounts.csv` / `HumagneRawReadcounts.csv` | sgRNA × sequence | 원시 NGS 리드카운트. Chronos 재현의 출발점 | [All Data 탭에서 검색](https://depmap.org/portal/data_page/?tab=allData) |
| ◻ `AvanaGuideMap.csv` 등 | sgRNA | guide–유전자 매핑, 라이브러리 설계 | 〃 |
| ◻ RNAi (`D2_combined_gene_dep_scores.csv`) | model × gene | DEMETER2 shRNA 넉다운 의존성. CRISPR와 별개 실험 | 〃 |

26Q1에서 Chronos의 library correction 범위가 "모든 라이브러리에 존재하는 유전자"에서 "2개 이상 screen batch에 존재하는 유전자"로 확장돼 `CRISPRGeneEffect.csv`·`ScreenGeneEffect.csv`의 library batch effect가 줄었고, 파일 포맷은 그대로야. Copy Number 결측으로 빠졌던 스크린 3건(SC-001956/957/958.AV01)이 복귀했어.

---

**2. Omics — 전체**

| 파일 | 내용 | 단위/스케일 | 링크 |
|---|---|---|---|
| ✅ `OmicsExpressionProteinCodingGenesTPMLogp1.csv` | 단백질코딩 RNA-seq 발현. GTEx 파이프라인 정량 | log2(TPM+1) | [포털](https://depmap.org/portal/data_page/?file=OmicsExpressionProteinCodingGenesTPMLogp1.csv&release=DepMap+Public+26Q1&tab=allData) |
| ◻ `OmicsExpressionTranscriptsTPMLogp1Profile.csv` | 전사체 단위 발현 | log2(TPM+1) | [All Data](https://depmap.org/portal/data_page/?tab=allData) |
| ✅ `OmicsSomaticMutationsMatrixDamaging.csv` | LoF 판정 변이 | 0/1/2 | [포털](https://depmap.org/portal/data_page/?file=OmicsSomaticMutationsMatrixDamaging.csv&release=DepMap+Public+26Q1&tab=allData) |
| ✅ `OmicsSomaticMutationsMatrixHotspot.csv` | hotspot 변이(활성화 변이 포함). 26Q1부터 HLA 유전자는 hotspot 제외 | 0/1/2 | [포털](https://depmap.org/portal/data_page/?file=OmicsSomaticMutationsMatrixHotspot.csv&release=DepMap+Public+26Q1&tab=allData) |
| ✅ `OmicsSomaticMutations.csv` / `OmicsSomaticMutationsMAFProfile.maf` | 변이 전체 롱포맷/MAF. 행렬로 압축되기 전 원본 | long | [All Data](https://depmap.org/portal/data_page/?tab=allData) |
| ✅ `OmicsCNGene.csv` | 유전자 단위 상대 copy number | log2(상대CN+1), 1 ≈ 2배체 | [포털](https://depmap.org/portal/data_page/?file=OmicsCNGene.csv&release=DepMap+Public+26Q1&tab=allData) |
| ◻ `OmicsAbsoluteCNGene.csv` | PureCN 기반 절대 copy number (24Q2 도입) | 정수 카피수 | [All Data](https://depmap.org/portal/data_page/?tab=allData) |
| ◻ `OmicsFusionFiltered.csv` | 융합 유전자 콜 | long | 〃 |
| ◻ `OmicsSignatures.csv` | 24Q2 도입 유전체 시그니처 (MSI, 변이 시그니처 등) | model × feature | 〃 |
| ✅ `harmonized_Olink_2023_best_dilution.csv` | Olink Explore HT 단백체. 161개 세포주, 24개 lineage. model_id × UniProt ID. 단백질별로 최적 희석배수 하나를 선택함. 이 데이터셋 일부 모델은 다른 omics·스크린 데이터가 없음 | model × protein | Harmonized Public Proteomics 26Q1 |
| ✅ `harmonized_Sanger_MS_2022.csv` | Gonçalves et al. 2022 질량분석 상대 정량. Cell Model Passports 출처 | model × protein | 〃 |

---

**3. PRISM 약물 반응**

**24Q2** — 📦 [figshare 전체 목록](https://figshare.com/articles/dataset/Repurposing_Public_24Q2/25917643)

| 파일 | 내용 | 링크 |
|---|---|---|
| ✅ `Repurposing_Public_24Q2_Extended_Primary_Data_Matrix.csv` | cell line × compound LFC **행렬** | [포털](https://depmap.org/portal/data_page/?file=Repurposing_Public_24Q2_Extended_Primary_Data_Matrix.csv&release=PRISM+Repurposing+Public+24Q2&tab=allData) |
| ✅ `Repurposing_Public_24Q2_LFC_COLLAPSED.csv` | 동일 값 **long format**. QC 통과 replicate median-collapse, 단일 농도 2.5 µM, DMSO 대비 | [포털](https://depmap.org/portal/data_page/?file=Repurposing_Public_24Q2_LFC_COLLAPSED.csv&release=PRISM+Repurposing+Public+24Q2&tab=allData) |
| ◻ treatment/compound metadata | 화합물별 target·MOA 주석 | figshare 목록에서 `Treatment`/`Compound` 포함 파일 확인 |

24Q2 = Repurposing-1M(1,280) + Repurposing-300(234), 총 1,514개 화합물 × 906개 세포주(859개 QC 통과), 2.5 µM 5일 처리, triplicate, 플레이트당 Bortezomib 20 µM 양성·DMSO 음성 대조. PR500A(부착) + PR500B(부착+부유) = PR1000 컬렉션이고, PR500B가 기존 패널에 새 subtype·lineage를 더함

**Secondary (Corsello 2020 레거시)** — 1,448개 화합물 × 499개 세포주, 10 µM부터 4배 희석 8단계 · [전체 목록](https://depmap.org/repurposing/)

| 파일 | 내용 | 링크 |
|---|---|---|
| `secondary-screen-readme.txt` | 처리 절차 | [7.5 KB](https://ndownloader.figshare.com/files/20238123) |
| `secondary-screen-dose-response-curve-parameters.csv` | IC50·EC50·AUC·상한/하한 | [252 MB](https://ndownloader.figshare.com/files/20237739) |
| `secondary-screen-replicate-collapsed-logfold-change.csv` | 농도별 LFC | [87 MB](https://ndownloader.figshare.com/files/20237757) |
| `secondary-screen-replicate-collapsed-treatment-info.csv` | 화합물 주석 | [3.6 MB](https://ndownloader.figshare.com/files/20237763) |
| `secondary-screen-cell-line-info.csv` | 세포주 주석 | [40 KB](https://ndownloader.figshare.com/files/20237769) |
| primary 계열 5종 | 4,518개 화합물 × 578/562개 세포주 | [같은 페이지](https://depmap.org/repurposing/) |

---

**4. 메타데이터·참조 목록**

| 파일 | 내용 | 링크 |
|---|---|---|
| ✅ `Model.csv` | 세포주 메타데이터. lineage, 원발 질환, OncoTree 코드, 배양 조건. 26Q1에서 OncoTree 2025-10-09 기준 재주석, CNS/Brain 대규모 재분류 | [포털](https://depmap.org/portal/data_page/?file=Model.csv&release=DepMap+Public+26Q1&tab=allData) |
| ◻ `OmicsProfiles.csv` / `OmicsDefaultModelProfiles.csv` | 모델–omics 프로파일 매핑. 25Q2·25Q3에서 갱신됨 | [All Data](https://depmap.org/portal/data_page/?tab=allData) |
| ✅ `AchillesCommonEssentialControls.csv` | Hart·Blomen essential 교집합. Chronos 의존 분포의 기준 | [포털](https://depmap.org/portal/data_page/?file=AchillesCommonEssentialControls.csv&release=DepMap+Public+26Q1&tab=allData) |
| ✅ `AchillesNonessentialControls.csv` | Hart reference nonessential. 귀무 분포의 기준 | [포털](https://depmap.org/portal/data_page/?file=AchillesNonessentialControls.csv&release=DepMap+Public+26Q1&tab=allData) |
| ◻ `CRISPRInferredCommonEssentials.csv` | 해당 릴리스에서 common essential로 추론된 유전자 목록 | [포털](https://depmap.org/portal/data_page/?file=CRISPRInferredCommonEssentials.csv&release=DepMap+Public+26Q1&tab=allData) |
| ◻ `AchillesHighVarianceGenes.csv` | 세포주 간 분산이 큰 유전자 목록 | [All Data](https://depmap.org/portal/data_page/?tab=allData) |

---

**5. 선택에 영향을 주는 사실들**

**조인 키** — `ModelID` (ACH-XXXXXX). 유전자 컬럼은 `SYMBOL (ENTREZID)` 형태라 파싱 필요. 레거시 PRISM(Corsello)은 `depmap_id` 컬럼명을 씀.

**커버리지** — CRISPR 스크린 모델 수 < 발현 프로파일 모델 수. PRISM 24Q2는 906개(QC 통과 859개). 세 데이터의 교집합이 실제 학습 샘플 수를 결정하고, Olink 단백체는 161개라 이걸 넣으면 교집합이 크게 줄어듦.

**스케일 방향** — PRISM LFC와 CRISPR gene effect 둘 다 음수 = 세포가 죽음/의존. 단 두 타깃의 분산 크기는 다름.

**결측** — `CRISPRGeneEffect.csv`에 NaN 존재(라이브러리별 유전자 커버리지 차이).

**common essential의 성질** — 이 유전자들은 정의상 세포주 간 분산이 거의 없음. 타깃에 포함하면 모델이 세포주 정보 없이도 예측 가능한 성분이 들어가고, 제외하면 예측 대상이 selective dependency로 좁혀짐. 두 설정의 성능 지표는 직접 비교되지 않음.

**model-level vs screen-level** — `CRISPRGeneEffect`는 모델당 1행, `ScreenGeneEffect`는 스크린당 1행. 후자를 쓰면 같은 모델이 중복 등장하므로 split 설계가 달라짐. 동시에 같은 모델의 스크린 간 차이는 측정 재현성의 경험적 범위를 준다.

**용량** — 발현 파일이 전체의 절반 이상. A/B/C 최소 구성 기준 대략 3~4 GB, 원시 리드카운트까지 포함하면 수십 GB.

**배포** — 26Q1은 파일 단위 개별 다운로드. PRISM 24Q2와 레거시 Corsello 릴리스는 figshare에서 일괄 가능.

</details>



### B. 검증 방법과 결과

**검증 방법 —** 포털 UI와 `https://depmap.org/portal/api/download/files` 는 캡차 뒤에 있지만,
2026-07-14에 DepMap이 **캡차 없는 엔드포인트**를 열었다. 이걸로 공식 파일 목록을 통째로 받아 대조했다.

```bash
curl -s "https://depmap.org/portal/api/no-captcha/download/files" -o depmap_files.csv
```

2026-08-11 기준 전체 1,436개 파일 / `DepMap Public 26Q1` 85개.
엔드포인트 상세·제약(‌`url` 컬럼 없음 → 자동 다운로드 불가)은 [overview 1](../depmap_overview/lkeonwoo94.md#1-파일-목록을-직접-받는-법-캡차-없음) 참고.

**결과 — 접힌 원문의 파일명은 상당수가 틀렸다.** 원인은 25Q3의 Omics 파일명 전면 개편이다.

| 접힌 원문의 이름 (~25Q2 기준) | 실제 26Q1 이름 |
|---|---|
| `OmicsExpressionProteinCodingGenesTPMLogp1.csv` ✅로 표기됨 | `OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv` |
| `OmicsCNGene.csv` ✅로 표기됨 | `OmicsCNGeneWGS.csv` (⚠️ log2 아님) |
| `OmicsSignatures.csv` | `OmicsGlobalSignatures.csv` |
| `OmicsSomaticMutationsMAFProfile.maf` | `OmicsSomaticMutationsMAF.maf` |
| `AchillesHighVarianceGenes.csv` | `AchillesHighVarianceGeneControls.csv` |
| `OmicsAbsoluteCNGene.csv` | **폐기됨** (24Q4 이후 미제공) |
| `OmicsDefaultModelProfiles.csv` | **폐기됨** → `OmicsProfiles.csv` 의 `is_default_entry` 컬럼 |
| `D2_combined_gene_dep_scores.csv` (RNAi) | 26Q1 릴리스에 없음 |

**주의할 점:** 원문이 ✅(릴리스 노트·논문에서 확인됨)로 표시한 항목 중에도 틀린 것이 있었다.
즉 **AI가 붙인 확신 표시 자체를 신뢰할 수 없다.** ◻만 대조하면 놓친다.

또한 원문의 "Corsello 2020 레거시 figshare를 써야 한다"는 안내도 불필요하다 —
DepMap이 표준 스키마로 재처리한 `Harmonized PRISM Repurposing Secondary Screen 25Q2` 가 있다.

> **26Q1 전체 파일 목록(85개)·릴리스 현황·용량·다운로드 링크·라이선스는 [DepMap 데이터 전반 조사](../depmap_overview/lkeonwoo94.md) 로 옮겼다. 그쪽이 정본이다.**
>
> - [1. 파일 목록을 직접 받는 법 (캡차 없음)](../depmap_overview/lkeonwoo94.md#1-파일-목록을-직접-받는-법-캡차-없음)
> - [2. 릴리스 현황](../depmap_overview/lkeonwoo94.md#2-릴리스-현황-2026-08-11-기준)
> - [3. 25Q3에서 바뀐 파일명](../depmap_overview/lkeonwoo94.md#3-25q3에서-바뀐-파일명-가장-중요)
> - [4. DepMap Public 26Q1 전체 파일 (85개)](../depmap_overview/lkeonwoo94.md#4-depmap-public-26q1-전체-파일-85개)
> - [5. 약물 반응 (별도 릴리스)](../depmap_overview/lkeonwoo94.md#5-약물-반응-별도-릴리스)
> - [6. 데이터 사용 조건](../depmap_overview/lkeonwoo94.md#6-데이터-사용-조건-2026년에-바뀜)
> - [7. 다운로드 전 알아둘 것](../depmap_overview/lkeonwoo94.md#7-다운로드-전-알아둘-것)

---

## Q3. 그럼 최소한으로 받아야 하는 데이터가 뭐야?

- **작성자:** @lkeonwoo94
- **날짜:** 2026-08-11
- **질문:** 그럼 최소한으로 받아야 하는 데이터가 뭐야? 표로 나타내줘. 파일명, 내용, 용량, 다운로드 링크
- **답변자:** Claude (Claude Code)
- **답변 시각:** 2026-08-11 KST

> **\* 용량은 참고치.** 26Q1 실측 용량은 캡차 뒤에만 있어 확인 불가. 값은 figshare에 미러링된 **24Q4 실측치**이며 26Q1은 이보다 다소 크다. 24Q4에 대응 파일이 없으면 `—`. 근거는 [DepMap 데이터 전반 조사 4](../depmap_overview/lkeonwoo94.md#4-depmap-public-26q1-전체-파일-85개).
> 다운로드 링크는 포털 All Data 탭이며 **캡차를 한 번 통과해야 한다.**

### C-1. 최소 구성 — 5개 파일, 약 0.95 GB

[A-5](#a-5-권장-설계)의 1단계(발현 → CRISPR 의존성, Elastic Net)를 돌리는 데 **이것만 있으면 된다.**

| 파일 | 내용 | 용량* | 다운로드 |
|---|---|---|---|
| `CRISPRGeneEffect.csv` | **출력 Y.** Chronos gene effect (model × gene). 0 = 무영향, −1 = pan-essential 중앙값 | 429 MB | [받기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=CRISPRGeneEffect.csv) |
| `OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv` | **입력 X.** log2(TPM+1) 단백질코딩 발현 | 507 MB | [받기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv) |
| `Model.csv` | 세포주 메타데이터. `OncotreeLineage` = 암종. 층화·그룹 분할·베이스라인에 필수 | 646 KB | [받기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=Model.csv) |
| `CRISPRInferredCommonEssentials.csv` | common essential 유전자 목록. **없으면 R²가 부풀려진다** | 21 KB | [받기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=CRISPRInferredCommonEssentials.csv) |
| `README.txt` | 행·열 의미, 단위, 결측 처리. 받자마자 읽을 것 | 43 KB | [받기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=README.txt) |

앞의 두 개가 전체 용량의 99%다. 나머지 3개는 합쳐서 1 MB도 안 되지만, **없으면 결과 해석 자체가 불가능**하다.

### C-2. 강력 권장 — 평가 설계에 필요 (+17 MB)

모델을 돌리는 데는 없어도 되지만, [A-4](#a-4-이-주제의-진짜-함정-4가지)의 함정을 피하려면 실질적으로 필요하다.

| 파일 | 내용 | 용량* | 다운로드 |
|---|---|---|---|
| `SubtypeMatrix.csv` | 암종·아형 one-hot. 「암종만으로 맞히는」 베이스라인을 바로 만들 수 있음 | — | [받기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=SubtypeMatrix.csv) |
| `AchillesCommonEssentialControls.csv` | Hart·Blomen essential. **양성 대조군** — 파이프라인 검증용 | 17 KB | [받기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=AchillesCommonEssentialControls.csv) |
| `AchillesNonessentialControls.csv` | Hart nonessential. **음성 대조군** | 11 KB | [받기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=AchillesNonessentialControls.csv) |
| `Gene.csv` | Gene symbol ↔ Ensembl/Entrez/HGNC 매핑. 유전자 컬럼 파싱이 꼬일 때 필요 | 17 MB | [받기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=Gene.csv) |

### C-3. 2단계 — 입력을 늘릴 때 (+2 GB)

1단계 결과가 나온 뒤에 받아도 늦지 않다. 특히 CN 파일이 1.4 GB로 무겁다.

| 파일 | 내용 | 용량* | 다운로드 |
|---|---|---|---|
| `OmicsSomaticMutationsMatrixHotspot.csv` | 활성화 변이(KRAS G12C, BRAF V600E 등). damaging에는 안 잡힘 | 4.2 MB | [받기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsSomaticMutationsMatrixHotspot.csv) |
| `OmicsSomaticMutationsMatrixDamaging.csv` | LoF 판정 변이 | 148 MB | [받기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsSomaticMutationsMatrixDamaging.csv) |
| `OmicsCNGeneWGS.csv` | 유전자 단위 상대 CN. ⚠️ log2 아님 — ploidy 대비 선형비, `~1.0` = 변화 없음 | 1.4 GB | [받기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsCNGeneWGS.csv) |
| `CRISPRGeneDependency.csv` | 0~1 의존 확률. 회귀 대신 분류로 갈 때의 라벨 | 421 MB | [받기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=CRISPRGeneDependency.csv) |

### C-4. 약물 반응까지 갈 경우 (선택)

멀티태스크(약물 + CRISPR 동시 예측)로 확장할 때만. **릴리스가 달라 세포주 교집합이 크게 줄어든다** — 먼저 교집합 수부터 세고 결정할 것.

| 파일 | 내용 | 용량* | 다운로드 |
|---|---|---|---|
| `REPURPOSINGAUCMatrix.csv` | **약물 타깃.** cell line × compound AUC 행렬 (용량-반응 기반) | — | [받기](https://depmap.org/portal/data_page/?tab=allData&releasename=Harmonized+PRISM+Repurposing+Secondary+Screen+25Q2&filename=REPURPOSINGAUCMatrix.csv) |
| `REPURPOSINGResponseCurves.csv` | 곡선 적합 파라미터. AUC 해석·QC용 | — | [받기](https://depmap.org/portal/data_page/?tab=allData&releasename=Harmonized+PRISM+Repurposing+Secondary+Screen+25Q2&filename=REPURPOSINGResponseCurves.csv) |
| `PortalCompounds.csv` | 화합물 메타데이터. target 유전자·MOA — 「왜 듣는가」에 필수 | 692 KB | [받기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=PortalCompounds.csv) |

### C-5. 받지 말 것

용량만 크고 이 프로젝트에 쓸 데가 없다.

| 파일 | 왜 안 받나 |
|---|---|
| `AvanaLogfoldChange.csv` (3.4 GB), `KYLogfoldChange.csv` (1.6 GB), `*RawReadcounts.csv` | Chronos 파이프라인 재현용. 우리는 이미 처리된 gene effect를 쓴다 |
| `OmicsExpressionTranscript*.csv` (4.2 GB) | 전사체 단위. 유전자 단위로 충분 |
| `ScreenGeneEffect.csv` 계열 | **같은 세포주가 중복 행으로 들어와 누출된다.** [overview 4-2](../depmap_overview/lkeonwoo94.md#4-2-crispr--스크린-단위-학습에-쓰면-안-됨) 참고 |
| `OmicsExpression{ExpectedCount,RawReadCount,EffectiveLength}*.csv` | TPM 재계산용 원자료 |

### C-6. 정리

| 단계 | 파일 수 | 누적 용량 | 무엇을 할 수 있나 |
|---|---|---|---|
| C-1 | 5 | ~0.95 GB | 발현 → CRISPR 의존성 예측 + 베이스라인 비교 |
| C-1 + C-2 | 9 | ~0.97 GB | 위 + 함정 4가지를 통제한 제대로 된 평가 |
| \+ C-3 | 13 | ~3 GB | 다중 오믹스 입력, 입력별 기여도 비교 |
| \+ C-4 | 16 | ~3 GB+ | 약물 반응 멀티태스크 |

**C-1 부터 받아서 교집합 세포주 수(n)를 먼저 확인하는 것을 권한다.** n이 예상보다 작으면 이후 설계가 통째로 바뀐다.

## 결론 / 다음 액션

- **AI가 알려주는 DepMap 파일명은 25Q2 이하 기준일 가능성이 높으니 그대로 믿지 말 것.** ✅(확인됨)로 표시한 항목도 틀렸다.
- 26Q1 파일명의 실측 정본은 [DepMap 데이터 전반 조사 4](../depmap_overview/lkeonwoo94.md#4-depmap-public-26q1-전체-파일-85개) 다. 파일명·용량·링크는 그 문서에서만 관리한다.
- [ ] 위 [C-1](#c-1-최소-구성--5개-파일-약-095-gb) 대로 26Q1 최소 구성 다운로드 → `data/raw/` 배치
- [ ] Stranded / 비-Stranded 중 무엇을 쓸지 결정 (양쪽 shape·상관 비교 후)
- [ ] `IsDefaultEntryForModel` 필터링 → 교집합 세포주 수 확정
- [ ] 약물 반응까지 확장할지 결정 (PRISM primary LFC vs Harmonized Secondary AUC)

> 검증에 쓴 출처(릴리스 노트·포럼 스레드)는 [DepMap 데이터 전반 조사 § 검증에 쓴 출처](../depmap_overview/lkeonwoo94.md#검증에-쓴-출처) 에 정리했다.
