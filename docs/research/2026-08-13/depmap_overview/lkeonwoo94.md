# DepMap 데이터 전반 조사

- **작성자:** @lkeonwoo94
- **날짜:** 2026-08-11
- **관련 TODO:** [2026-08-07](../../../meetings/2026-08-07.md)

## 조사 배경

- DepMap 데이터로 어떤 프로젝트가 가능한지 파악하기 위한 데이터 전반 조사.
- 조사 도중 **AI(GPT/Claude)가 알려준 파일명이 다수 틀린 것**을 발견했다. 25Q3에서 Omics 파일명 체계가 대대적으로 개편됐는데 학습 데이터가 그 이전(24Q2~25Q2) 기준이라 구버전 이름을 그대로 답한 것이다. 게다가 DepMap 포털이 2026년 중 Cloudflare 캡차를 걸어 파일 목록을 프로그래밍 방식으로 볼 수 없게 되면서, AI들이 "확인 못 했다"며 추측으로 답하는 상황이었다.
- → **공식 파일 목록을 직접 받아 대조**한 결과를 이 문서에 정리한다.
- 검증 경위와 AI 답변 원문은 [AI 질답 정리 Q2](../depmap_gpt_qna/lkeonwoo94.md#q2-depmap-26q1-실제-파일명-검증--아래-내용이-사실인지-확인해줘) 참고.

> **이 문서가 26Q1 파일 목록의 정본이다.** 파일명·용량·링크는 여기서만 관리하고, 다른 문서는 이 문서를 참조한다.

## 내용

### 1. 파일 목록을 직접 받는 법 (캡차 없음)

포털 UI와 `https://depmap.org/portal/api/download/files` 는 캡차 뒤에 있지만,
2026-07-14에 DepMap이 **캡차 없는 엔드포인트**를 열었다.

```bash
curl -s "https://depmap.org/portal/api/no-captcha/download/files" -o depmap_files.csv
```

- 컬럼: `release, release_date, filename, md5_hash`
- 캡차 있는 원본과 내용 동일하되 **`url` 컬럼만 빠져 있다** → 목록 확인·버전 추적은 되지만 자동 다운로드는 안 된다.
- 파일 실물은 포털에서 캡차를 한 번 통과한 뒤 받아야 한다.
- 2026-08-11 기준 전체 1,436개 파일 / `DepMap Public 26Q1` 85개.

> 출처: DepMap 포럼 [Provide an open endpoint for latest version retrieval](https://forum.depmap.org/t/4652) (DepMap 개발자 pmontgom 답변).
> 캡차를 건 이유는 트래픽 폭증에 따른 egress 비용. Bearer 토큰 방식 API 키는 **26Q3 릴리스 이후** 목표라고 밝힘.

**릴리스 목록 확인:**

```bash
python3 -c "
import csv, collections
rows = list(csv.DictReader(open('depmap_files.csv')))
for (rel, d), n in sorted(collections.Counter((r['release'], r['release_date']) for r in rows).items(),
                          key=lambda x: x[0][1], reverse=True)[:15]:
    print(d, '|', n, '|', rel)
"
```

### 2. 릴리스 현황 (2026-08-11 기준)

| 릴리스 | 공개일 | 파일 수 | 비고 | 포털 | 릴리스 노트 |
|---|---|---|---|---|---|
| `DepMap Public 26Q1` | 2026-04-01 | 85 | **최신 본 릴리스.** 26Q2는 아직 없음 | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1) | [노트](https://forum.depmap.org/t/4606) |
| `Harmonized Public Proteomics 26Q1` | 2026-03-01 | 5 | Olink / Sanger MS 단백체 | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=Harmonized+Public+Proteomics+26Q1) | — |
| `NextGen Model Manuscript 2026` | 2026-07-16 | 56 | 논문 부속 데이터 | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=NextGen+Model+Manuscript+2026) | — |
| `DepMap Public 25Q3` | 2025-09-25 | 76 |  | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+25Q3) | [노트](https://forum.depmap.org/t/4476) |
| `Biogrid 25Q3` | 2025-09-01 | 19 | BioGRID ORCS 스크린 22개 (TKOv3/Brunello) | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=Biogrid+25Q3) | — |
| `DepMap Public 25Q2` | 2025-06-27 | 81 | 구·신 파일명 병행 전환 릴리스 | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+25Q2) | [노트](https://forum.depmap.org/t/4257) |
| `Harmonized PRISM Repurposing Secondary Screen 25Q2` | 2025-03-11 | 7 | **용량-반응 AUC/IC50** | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=Harmonized+PRISM+Repurposing+Secondary+Screen+25Q2) | — |
| `Harmonized GDSC 25Q2` | 2025-03-11 | 14 | GDSC1/GDSC2 | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=Harmonized+GDSC+25Q2) | — |
| `Harmonized CTD^2 25Q2` | 2025-03-11 | 7 | CTRP | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=Harmonized+CTD%5E2+25Q2) | — |
| `PRISM Primary Repurposing DepMap Public 24Q2` | 2024-05-28 | 11 | PRISM primary 최신. **figshare 미러 있음** | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=PRISM+Primary+Repurposing+DepMap+Public+24Q2) · [figshare](https://figshare.com/articles/dataset/Repurposing_Public_24Q2/25917643) | — |

**릴리스 주기가 불규칙하다.** 25Q2(6월) → 25Q3(9월) → 26Q1(4월). 25Q4는 없다.

### 3. 25Q3에서 바뀐 파일명 (가장 중요)

⚠️ 25Q3 릴리스 노트: *"중복을 피하고 사용 편의를 위해 Omics 출력을 정리했다. 25Q3부터 profile 단위 출력은 더 이상 호스팅하지 않는다."*

| 24Q2 / 24Q4 이름 | **26Q1 이름** |
|---|---|
| `OmicsExpressionProteinCodingGenesTPMLogp1.csv` | `OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv` |
| `OmicsExpressionAllGenesTPMLogp1Profile.csv` | `OmicsExpressionTPMLogp1HumanAllGenes.csv` |
| `OmicsExpressionProteinCodingGenesTPMLogp1BatchCorrected.csv` | **삭제됨** (25Q2에서 제거, 대체 없음) |
| `OmicsCNGene.csv` | `OmicsCNGeneWGS.csv` |
| `OmicsAbsoluteCNGene.csv` | **폐기됨** (24Q4 이후 미제공) |
| `OmicsSignatures.csv` | `OmicsGlobalSignatures.csv` |
| `OmicsSomaticMutationsMAFProfile.maf` | `OmicsSomaticMutationsMAF.maf` |
| `AchillesHighVarianceGenes.csv` | `AchillesHighVarianceGeneControls.csv` |
| `OmicsDefaultModelProfiles.csv` | **폐기됨** → `OmicsProfiles.csv` 의 `is_default_entry` 컬럼으로 대체 |

25Q2는 **구·신 이름이 둘 다 존재하는 전환 릴리스**였고, 25Q3에서 구 이름이 잘렸다.
→ 25Q2 이하 기준으로 쓰인 코드·블로그·AI 답변은 26Q1에서 전부 깨진다.

### 4. DepMap Public 26Q1 전체 파일 (85개)

> **\* 용량 컬럼은 참고치다.** 26Q1의 실제 용량은 캡차 뒤의 API(`size` 필드)에만 있어 확인할 수 없다.
> 표의 값은 **figshare에 미러링된 24Q4 실측치**이며, 26Q1은 세포주가 늘어 이보다 다소 크다.
> 24Q4에 대응 파일이 없는 항목(Brunello/TKOv3, WGS CN, Subtype 계열 등)은 `—` 로 뒀다.
> 링크는 포털 All Data 탭에서 해당 파일이 선택된 상태로 열린다 — **캡차를 한 번 통과해야 한다.**

#### 4-1. CRISPR — 모델 단위 (학습에 쓸 것)

| 파일 | 내용 | 용량* | 링크 |
|---|---|---|---|
| `CRISPRGeneEffect.csv` | **Chronos gene effect. 우리 프로젝트의 Y.** 0 = 무영향, −1 = pan-essential 중앙값 | 429 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=CRISPRGeneEffect.csv) |
| `CRISPRGeneDependency.csv` | 위를 0~1 의존 확률로 변환. 이진 분류 헤드용 라벨 | 421 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=CRISPRGeneDependency.csv) |
| `CRISPRGeneEffectUncorrected.csv` | library correction 적용 전 | 418 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=CRISPRGeneEffectUncorrected.csv) |
| `CRISPRInferredCommonEssentials.csv` | 이 릴리스에서 common essential로 추론된 유전자 목록 | 21 KB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=CRISPRInferredCommonEssentials.csv) |
| `CRISPRScreenMap.csv` | 모델 ↔ 스크린 매핑 | 36 KB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=CRISPRScreenMap.csv) |
| `CRISPRConfounders.csv` | 교란 변수 | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=CRISPRConfounders.csv) |
| `CRISPRInferredLibraryEffect.csv` | Chronos가 추정한 라이브러리 효과 | 1.3 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=CRISPRInferredLibraryEffect.csv) |
| `CRISPRInitialOffset.csv` | Chronos 초기 오프셋 | 8.2 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=CRISPRInitialOffset.csv) |
| `CRISPRInferredGuideEfficacy.csv` | guide별 절단 효율 추정치 | 7.7 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=CRISPRInferredGuideEfficacy.csv) |
| `CRISPRInferredModelGrowthRate.csv` | 세포주별 증식률 추정치 | 41 KB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=CRISPRInferredModelGrowthRate.csv) |
| `CRISPRInferredModelEfficacy.csv` | 세포주별 Cas9 효율 추정치 | 41 KB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=CRISPRInferredModelEfficacy.csv) |
| `CRISPRInferredSequenceOverdispersion.csv` | 시퀀싱 과분산 추정치 | 149 KB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=CRISPRInferredSequenceOverdispersion.csv) |

#### 4-2. CRISPR — 스크린 단위 (학습에 쓰면 안 됨)

| 파일 | 내용 | 용량* | 링크 |
|---|---|---|---|
| `ScreenGeneEffect.csv` | 스크린 단위 gene effect. **같은 모델이 여러 행으로 중복 등장** | 507 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=ScreenGeneEffect.csv) |
| `ScreenGeneEffectUncorrected.csv` | 보정 전 | 496 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=ScreenGeneEffectUncorrected.csv) |
| `ScreenGeneDependency.csv` | 스크린 단위 의존 확률 | 500 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=ScreenGeneDependency.csv) |
| `ScreenNaiveGeneScore.csv` | Chronos 미적용 단순 점수 | 504 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=ScreenNaiveGeneScore.csv) |
| `ScreenSequenceMap.csv` | 스크린 ↔ 시퀀싱 런 ↔ 모델 ↔ 라이브러리 대응표 | 347 KB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=ScreenSequenceMap.csv) |

#### 4-3. CRISPR — 대조군 / QC

| 파일 | 내용 | 용량* | 링크 |
|---|---|---|---|
| `AchillesCommonEssentialControls.csv` | Hart·Blomen essential 교집합. **양성 대조군** | 17 KB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=AchillesCommonEssentialControls.csv) |
| `AchillesNonessentialControls.csv` | Hart reference nonessential. **음성 대조군** | 11 KB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=AchillesNonessentialControls.csv) |
| `AchillesHighVarianceGeneControls.csv` | 세포주 간 분산이 큰 유전자 목록 | 7 KB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=AchillesHighVarianceGeneControls.csv) |
| `AchillesScreenQCReport.csv` | 스크린 단위 QC 지표 | 327 KB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=AchillesScreenQCReport.csv) |
| `AchillesSequenceQCReport.csv` | 시퀀싱 런 단위 QC 지표 | 460 KB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=AchillesSequenceQCReport.csv) |

#### 4-4. CRISPR — 원시 데이터 (라이브러리 5종)

| 파일 | 내용 | 용량* | 링크 |
|---|---|---|---|
| `AvanaRawReadcounts.csv` | Avana(Cas9) sgRNA × 시퀀스 원시 리드카운트 | 1.0 GB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=AvanaRawReadcounts.csv) |
| `AvanaLogfoldChange.csv` | Avana log fold change | 3.4 GB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=AvanaLogfoldChange.csv) |
| `AvanaGuideMap.csv` | Avana guide ↔ 유전자 매핑, `UsedByChronos` 플래그 | 16 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=AvanaGuideMap.csv) |
| `OmicsGuideMutationsBinaryAvana.csv` | Avana guide 위치의 변이 여부 | 648 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsGuideMutationsBinaryAvana.csv) |
| `KYRawReadcounts.csv` | KY(Sanger Yusa) 원시 리드카운트 | 479 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=KYRawReadcounts.csv) |
| `KYLogfoldChange.csv` | KY log fold change | 1.6 GB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=KYLogfoldChange.csv) |
| `KYGuideMap.csv` | KY guide 매핑 | 5.9 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=KYGuideMap.csv) |
| `OmicsGuideMutationsBinaryKY.csv` | KY guide 위치 변이 여부 | 363 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsGuideMutationsBinaryKY.csv) |
| `HumagneRawReadcounts.csv` | Humagne-CD(Cas12a) 원시 리드카운트 | 16 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=HumagneRawReadcounts.csv) |
| `HumagneLogfoldChange.csv` | Humagne log fold change | 49 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=HumagneLogfoldChange.csv) |
| `HumagneGuideMap.csv` | Humagne guide 매핑. 25Q2에서 9개 guide가 `UsedByChronos=False` 처리됨 | 5.6 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=HumagneGuideMap.csv) |
| `OmicsGuideMutationsBinaryHumagne.csv` | Humagne guide 위치 변이 여부 | 348 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsGuideMutationsBinaryHumagne.csv) |
| `BrunelloRawReadcounts.csv` | Brunello 원시 리드카운트 (BioGRID ORCS 유래, 25Q3 신규) | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=BrunelloRawReadcounts.csv) |
| `BrunelloLogfoldChange.csv` | Brunello log fold change | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=BrunelloLogfoldChange.csv) |
| `BrunelloGuideMap.csv` | Brunello guide 매핑 | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=BrunelloGuideMap.csv) |
| `OmicsGuideMutationsBinaryBrunello.csv` | Brunello guide 위치 변이 여부 | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsGuideMutationsBinaryBrunello.csv) |
| `TKOv3RawReadcounts.csv` | TKOv3 원시 리드카운트 (BioGRID ORCS 유래, 25Q3 신규) | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=TKOv3RawReadcounts.csv) |
| `TKOv3LogfoldChange.csv` | TKOv3 log fold change | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=TKOv3LogfoldChange.csv) |
| `TKOv3GuideMap.csv` | TKOv3 guide 매핑 | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=TKOv3GuideMap.csv) |
| `OmicsGuideMutationsBinaryTKOv3.csv` | TKOv3 guide 위치 변이 여부 | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsGuideMutationsBinaryTKOv3.csv) |

#### 4-5. 발현 (RNA-seq)

| 파일 | 내용 | 용량* | 링크 |
|---|---|---|---|
| `OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv` | **입력 X.** log2(TPM+1), 단백질코딩 유전자 | 507 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv) |
| `OmicsExpressionTPMLogp1HumanProteinCodingGenesStranded.csv` | 위의 stranded 버전 | 204 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsExpressionTPMLogp1HumanProteinCodingGenesStranded.csv) |
| `OmicsExpressionTPMLogp1HumanAllGenes.csv` | log2(TPM+1), 전체 유전자 | 1.0 GB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsExpressionTPMLogp1HumanAllGenes.csv) |
| `OmicsExpressionTPMLogp1HumanAllGenesStranded.csv` | 위의 stranded 버전 | 360 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsExpressionTPMLogp1HumanAllGenesStranded.csv) |
| `OmicsExpressionExpectedCountHumanProteinCodingGenes.csv` | Salmon expected count, 단백질코딩 | 447 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsExpressionExpectedCountHumanProteinCodingGenes.csv) |
| `OmicsExpressionExpectedCountHumanProteinCodingGenesStranded.csv` | stranded | 167 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsExpressionExpectedCountHumanProteinCodingGenesStranded.csv) |
| `OmicsExpressionExpectedCountHumanAllGenes.csv` | Salmon expected count, 전체 | 447 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsExpressionExpectedCountHumanAllGenes.csv) |
| `OmicsExpressionExpectedCountHumanAllGenesStranded.csv` | stranded | 167 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsExpressionExpectedCountHumanAllGenesStranded.csv) |
| `OmicsExpressionRawReadCountHumanProteinCodingGenes.csv` | STAR 고유정렬 리드 원시 카운트, 단백질코딩 | 480 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsExpressionRawReadCountHumanProteinCodingGenes.csv) |
| `OmicsExpressionRawReadCountHumanProteinCodingGenesStranded.csv` | stranded | 192 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsExpressionRawReadCountHumanProteinCodingGenesStranded.csv) |
| `OmicsExpressionRawReadCountHumanAllGenes.csv` | STAR 원시 카운트, 전체 | 480 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsExpressionRawReadCountHumanAllGenes.csv) |
| `OmicsExpressionRawReadCountHumanAllGenesStranded.csv` | stranded | 192 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsExpressionRawReadCountHumanAllGenesStranded.csv) |
| `OmicsExpressionEffectiveLengthHumanProteinCodingGenes.csv` | 유효 길이 (TPM 재계산용), 단백질코딩 | 671 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsExpressionEffectiveLengthHumanProteinCodingGenes.csv) |
| `OmicsExpressionEffectiveLengthHumanProteinCodingGenesStranded.csv` | stranded | 671 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsExpressionEffectiveLengthHumanProteinCodingGenesStranded.csv) |
| `OmicsExpressionEffectiveLengthHumanAllGenes.csv` | 유효 길이, 전체 | 671 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsExpressionEffectiveLengthHumanAllGenes.csv) |
| `OmicsExpressionEffectiveLengthHumanAllGenesStranded.csv` | stranded | 671 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsExpressionEffectiveLengthHumanAllGenesStranded.csv) |
| `OmicsExpressionTranscriptTPMLogp1HumanAllGenes.csv` | **전사체 단위** log2(TPM+1). 26Q1 최대 파일 | 4.2 GB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsExpressionTranscriptTPMLogp1HumanAllGenes.csv) |
| `OmicsExpressionTranscriptTPMLogp1HumanAllGenesStranded.csv` | stranded | 1.6 GB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsExpressionTranscriptTPMLogp1HumanAllGenesStranded.csv) |
| `OmicsExpressionTranscriptExpectedCountHumanAllGenes.csv` | 전사체 단위 expected count | 1.9 GB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsExpressionTranscriptExpectedCountHumanAllGenes.csv) |
| `OmicsExpressionTranscriptExpectedCountHumanAllGenesStranded.csv` | stranded | 729 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsExpressionTranscriptExpectedCountHumanAllGenesStranded.csv) |
| `OmicsExpressionTranscriptEffectiveLengthHumanAllGenes.csv` | 전사체 단위 유효 길이 | 671 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsExpressionTranscriptEffectiveLengthHumanAllGenes.csv) |
| `OmicsExpressionTranscriptEffectiveLengthHumanAllGenesStranded.csv` | stranded | 671 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsExpressionTranscriptEffectiveLengthHumanAllGenesStranded.csv) |

#### 4-6. 변이

| 파일 | 내용 | 용량* | 링크 |
|---|---|---|---|
| `OmicsSomaticMutationsMatrixDamaging.csv` | **입력.** LoF 판정 변이 행렬 | 148 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsSomaticMutationsMatrixDamaging.csv) |
| `OmicsSomaticMutationsMatrixHotspot.csv` | **입력.** hotspot 변이 행렬. KRAS G12C·BRAF V600E 같은 활성화 변이는 여기에만 있음 | 4.2 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsSomaticMutationsMatrixHotspot.csv) |
| `OmicsSomaticMutations.csv` | variant 단위 long format (행렬로 압축되기 전) | 339 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsSomaticMutations.csv) |
| `OmicsSomaticMutationsMAF.maf` | MAF 포맷 | 98 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsSomaticMutationsMAF.maf) |

#### 4-7. Copy number

| 파일 | 내용 | 용량* | 링크 |
|---|---|---|---|
| `OmicsCNGeneWGS.csv` | **주 파일.** WGS 기반 유전자 단위 상대 CN. ⚠️ log2 아님 — 세포주 자신의 ploidy 대비 **선형 비율**, `~1.0 = 변화 없음` | 1.4 GB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsCNGeneWGS.csv) |
| `PortalOmicsCNGeneLog2.csv` | 포털 표시용 log2 스케일. log2가 필요하면 이쪽 | 1.4 GB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=PortalOmicsCNGeneLog2.csv) |
| `OmicsCNSegmentsWGS.csv` | WGS 세그먼트 단위 CN | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsCNSegmentsWGS.csv) |
| `OmicsCNGeneMC_WES.csv` | WES 기반 (구 파이프라인). ⚠️ **WGS와 섞어 쓰지 말 것** | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsCNGeneMC_WES.csv) |

#### 4-8. 기타 Omics

| 파일 | 내용 | 용량* | 링크 |
|---|---|---|---|
| `OmicsFusionFiltered.csv` | 유전자 융합 콜 (Arriba 2.5.0), 유전자쌍 수준 요약 | 11 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsFusionFiltered.csv) |
| `OmicsFusionFilteredSupplementary.csv` | 융합 전체 출력 (breakpoint 단위) | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsFusionFilteredSupplementary.csv) |
| `OmicsInferredMolecularSubtypes.csv` | 추론된 분자 아형 (MSI 등) | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsInferredMolecularSubtypes.csv) |
| `OmicsGlobalSignatures.csv` | 유전체 시그니처 | 132 KB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsGlobalSignatures.csv) |
| `OmicsMicrosatelliteRepeats.csv` | 마이크로새틀라이트 반복 | 93 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsMicrosatelliteRepeats.csv) |
| `OmicsProfiles.csv` | 모델 ↔ omics 프로파일 매핑. `is_default_entry` 컬럼 포함 | 255 KB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=OmicsProfiles.csv) |

#### 4-9. 메타데이터 / 참조

| 파일 | 내용 | 용량* | 링크 |
|---|---|---|---|
| `Model.csv` | **세포주 메타데이터.** ModelID, OncotreeLineage/PrimaryDisease/Subtype, 배양 조건 등 | 646 KB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=Model.csv) |
| `ModelCondition.csv` | 모델의 실험 조건(ModelConditionID) 단위 메타데이터 | 219 KB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=ModelCondition.csv) |
| `Gene.csv` | Gene symbol ↔ Ensembl ↔ Entrez ↔ HGNC 매핑 | 17 MB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=Gene.csv) |
| `PortalCompounds.csv` | 화합물 메타데이터. CompoundID, target 유전자, MOA, SMILES 등 | 692 KB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=PortalCompounds.csv) |
| `SubtypeMatrix.csv` | 암종·아형 one-hot 행렬. **lineage 베이스라인에 바로 사용 가능** | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=SubtypeMatrix.csv) |
| `SubtypeTree.csv` | 아형 계층 구조. OncoTree 2025-10-09 기준 | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=SubtypeTree.csv) |
| `README.txt` | 파일별 행·열 의미, 단위, 결측 처리. **먼저 읽을 것** | 43 KB | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=README.txt) |

### 5. 약물 반응 (별도 릴리스)

DepMap Public 26Q1에는 약물 반응 데이터가 **들어있지 않다.** 릴리스가 따로 돈다.

#### 5-1. PRISM primary — `PRISM Primary Repurposing DepMap Public 24Q2` (2024-05-28)

**이 릴리스는 figshare에 통째로 올라와 있어 캡차 없이 바로 받을 수 있다.**
📦 [figshare — Repurposing Public 24Q2 (전체 파일 목록·일괄 다운로드)](https://figshare.com/articles/dataset/Repurposing_Public_24Q2/25917643)

용량은 figshare API에서 가져온 **실측 정확값**이다.

| 파일 | 내용 | 용량 | 포털 | figshare |
|---|---|---|---|---|
| `Repurposing_Public_24Q2_Extended_Primary_Data_Matrix.csv` | **타깃 후보.** cell line × compound LFC 행렬 | 72 MB | [포털](https://depmap.org/portal/data_page/?tab=allData&releasename=PRISM+Primary+Repurposing+DepMap+Public+24Q2&filename=Repurposing_Public_24Q2_Extended_Primary_Data_Matrix.csv) | [직접 다운로드](https://ndownloader.figshare.com/files/46630984) |
| `Repurposing_Public_24Q2_LFC_COLLAPSED.csv` | 같은 값 long format (replicate median-collapse) | 150 MB | [포털](https://depmap.org/portal/data_page/?tab=allData&releasename=PRISM+Primary+Repurposing+DepMap+Public+24Q2&filename=Repurposing_Public_24Q2_LFC_COLLAPSED.csv) | [직접 다운로드](https://ndownloader.figshare.com/files/46631056) |
| `Repurposing_Public_24Q2_LFC.csv` | collapse 전 replicate 단위 LFC | 479 MB | [포털](https://depmap.org/portal/data_page/?tab=allData&releasename=PRISM+Primary+Repurposing+DepMap+Public+24Q2&filename=Repurposing_Public_24Q2_LFC.csv) | [직접 다운로드](https://ndownloader.figshare.com/files/46630987) |
| `Repurposing_Public_24Q2_Treatment_Meta_Data.csv` | **화합물 메타데이터 (target·MOA).** 「왜 듣는가」를 하려면 필수 | 2 MB | [포털](https://depmap.org/portal/data_page/?tab=allData&releasename=PRISM+Primary+Repurposing+DepMap+Public+24Q2&filename=Repurposing_Public_24Q2_Treatment_Meta_Data.csv) | [직접 다운로드](https://ndownloader.figshare.com/files/46631146) |
| `Repurposing_Public_24Q2_Cell_Line_Meta_Data.csv` | 세포주 메타데이터 | 157 KB | [포털](https://depmap.org/portal/data_page/?tab=allData&releasename=PRISM+Primary+Repurposing+DepMap+Public+24Q2&filename=Repurposing_Public_24Q2_Cell_Line_Meta_Data.csv) | [직접 다운로드](https://ndownloader.figshare.com/files/46630978) |
| `Repurposing_Public_24Q2_Extended_Primary_Compound_List.csv` | 화합물 목록 | 720 KB | [포털](https://depmap.org/portal/data_page/?tab=allData&releasename=PRISM+Primary+Repurposing+DepMap+Public+24Q2&filename=Repurposing_Public_24Q2_Extended_Primary_Compound_List.csv) | [직접 다운로드](https://ndownloader.figshare.com/files/46630981) |
| `Repurposing_Public_24Q2_LMFI_NORMALIZED.csv` | 정규화된 원시 형광값 | 668 MB | [포털](https://depmap.org/portal/data_page/?tab=allData&releasename=PRISM+Primary+Repurposing+DepMap+Public+24Q2&filename=Repurposing_Public_24Q2_LMFI_NORMALIZED.csv) | [직접 다운로드](https://ndownloader.figshare.com/files/46631059) |
| `Repurposing_Public_24Q2_LMFI_matrix.csv` | 원시 형광값 행렬 | 109 MB | [포털](https://depmap.org/portal/data_page/?tab=allData&releasename=PRISM+Primary+Repurposing+DepMap+Public+24Q2&filename=Repurposing_Public_24Q2_LMFI_matrix.csv) | [직접 다운로드](https://ndownloader.figshare.com/files/46631125) |
| `Repurposing_Public_24Q2_QC_table.csv` | QC 지표 | 3 MB | [포털](https://depmap.org/portal/data_page/?tab=allData&releasename=PRISM+Primary+Repurposing+DepMap+Public+24Q2&filename=Repurposing_Public_24Q2_QC_table.csv) | [직접 다운로드](https://ndownloader.figshare.com/files/46631128) |
| `Repurposing_Public_24Q2_Readme.txt` | PRISM 실험 설계·처리 절차 설명. **먼저 읽을 것** | 13 KB | [포털](https://depmap.org/portal/data_page/?tab=allData&releasename=PRISM+Primary+Repurposing+DepMap+Public+24Q2&filename=Repurposing_Public_24Q2_Readme.txt) | [직접 다운로드](https://ndownloader.figshare.com/files/46631143) |
| `README.txt` | 릴리스 공통 README | 10 KB | [포털](https://depmap.org/portal/data_page/?tab=allData&releasename=PRISM+Primary+Repurposing+DepMap+Public+24Q2&filename=README.txt) | [직접 다운로드](https://ndownloader.figshare.com/files/46630975) |

단일 농도 스크린이다. (구체적 농도·세포주 수·화합물 수는 **미검증** — `Repurposing_Public_24Q2_Readme.txt` 와 실제 shape으로 확인할 것)

#### 5-2. 용량-반응 (AUC/IC50) — `Harmonized PRISM Repurposing Secondary Screen 25Q2` (2025-03-11)

**Corsello 2020 레거시 figshare를 쓸 필요 없다.** DepMap이 표준 스키마로 재처리한 버전이 있다.
이쪽은 figshare 미러가 없어 포털에서만 받을 수 있고, 용량도 확인 불가다.

| 파일 | 내용 | 용량* | 링크 |
|---|---|---|---|
| `REPURPOSINGLog2IC50Matrix.csv` | cell line × compound log2(IC50) 행렬 | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=Harmonized+PRISM+Repurposing+Secondary+Screen+25Q2&filename=REPURPOSINGLog2IC50Matrix.csv) |
| `REPURPOSINGAUCMatrix.csv` | **cell line × compound AUC 행렬.** 용량-반응 요약값, 타깃으로 쓰기 가장 편함 | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=Harmonized+PRISM+Repurposing+Secondary+Screen+25Q2&filename=REPURPOSINGAUCMatrix.csv) |
| `REPURPOSINGLog2ViabilityConditions.csv` | 위 행렬의 조건(농도·화합물) 주석 | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=Harmonized+PRISM+Repurposing+Secondary+Screen+25Q2&filename=REPURPOSINGLog2ViabilityConditions.csv) |
| `REPURPOSINGLog2ViabilityCollapsedMatrix.csv` | replicate 통합 log2 생존율 | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=Harmonized+PRISM+Repurposing+Secondary+Screen+25Q2&filename=REPURPOSINGLog2ViabilityCollapsedMatrix.csv) |
| `REPURPOSINGResponseCurves.csv` | 곡선 적합 파라미터 (상·하한, 기울기 등) | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=Harmonized+PRISM+Repurposing+Secondary+Screen+25Q2&filename=REPURPOSINGResponseCurves.csv) |
| `REPURPOSINGLog2ViabilityMatrix.csv` | 농도별 log2 생존율 (replicate 단위) | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=Harmonized+PRISM+Repurposing+Secondary+Screen+25Q2&filename=REPURPOSINGLog2ViabilityMatrix.csv) |
| `REPURPOSINGLog2ViabilityCollapsedConditions.csv` | 위 행렬의 조건 주석 | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=Harmonized+PRISM+Repurposing+Secondary+Screen+25Q2&filename=REPURPOSINGLog2ViabilityCollapsedConditions.csv) |

#### 5-3. 같은 스키마의 다른 약물 데이터셋 (교차검증용)

아래 두 릴리스는 5-2와 **파일 구성·컬럼 규격이 동일**하다. 약물 반응 타깃을 PRISM 하나로 묶지 않고
3개 소스로 확장하거나 교차 검증할 수 있다.

**`Harmonized GDSC 25Q2`** (2025-03-11, 14개)

| 파일 | 내용 | 용량* | 링크 |
|---|---|---|---|
| `GDSC1Log2ViabilityCollapsedMatrix.csv` | GDSC1 replicate 통합 log2 생존율 | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=Harmonized+GDSC+25Q2&filename=GDSC1Log2ViabilityCollapsedMatrix.csv) |
| `GDSC2Log2ViabilityCollapsedConditions.csv` | GDSC2 replicate 통합 생존율 조건 주석 | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=Harmonized+GDSC+25Q2&filename=GDSC2Log2ViabilityCollapsedConditions.csv) |
| `GDSC2Log2ViabilityMatrix.csv` | GDSC2 농도별 log2 생존율 | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=Harmonized+GDSC+25Q2&filename=GDSC2Log2ViabilityMatrix.csv) |
| `GDSC1Log2ViabilityConditions.csv` | GDSC1 생존율 조건 주석 | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=Harmonized+GDSC+25Q2&filename=GDSC1Log2ViabilityConditions.csv) |
| `GDSC1Log2ViabilityCollapsedConditions.csv` | GDSC1 replicate 통합 생존율 조건 주석 | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=Harmonized+GDSC+25Q2&filename=GDSC1Log2ViabilityCollapsedConditions.csv) |
| `GDSC1Log2IC50Matrix.csv` | GDSC1 log2(IC50) 행렬 | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=Harmonized+GDSC+25Q2&filename=GDSC1Log2IC50Matrix.csv) |
| `GDSC1ResponseCurves.csv` | GDSC1 곡선 적합 파라미터 | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=Harmonized+GDSC+25Q2&filename=GDSC1ResponseCurves.csv) |
| `GDSC2Log2ViabilityConditions.csv` | GDSC2 생존율 조건 주석 | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=Harmonized+GDSC+25Q2&filename=GDSC2Log2ViabilityConditions.csv) |
| `GDSC2Log2IC50Matrix.csv` | GDSC2 log2(IC50) 행렬 | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=Harmonized+GDSC+25Q2&filename=GDSC2Log2IC50Matrix.csv) |
| `GDSC2AUCMatrix.csv` | GDSC2 AUC 행렬 | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=Harmonized+GDSC+25Q2&filename=GDSC2AUCMatrix.csv) |
| `GDSC2Log2ViabilityCollapsedMatrix.csv` | GDSC2 replicate 통합 log2 생존율 | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=Harmonized+GDSC+25Q2&filename=GDSC2Log2ViabilityCollapsedMatrix.csv) |
| `GDSC1AUCMatrix.csv` | GDSC1 AUC 행렬 | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=Harmonized+GDSC+25Q2&filename=GDSC1AUCMatrix.csv) |
| `GDSC1Log2ViabilityMatrix.csv` | GDSC1 농도별 log2 생존율 | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=Harmonized+GDSC+25Q2&filename=GDSC1Log2ViabilityMatrix.csv) |
| `GDSC2ResponseCurves.csv` | GDSC2 곡선 적합 파라미터 | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=Harmonized+GDSC+25Q2&filename=GDSC2ResponseCurves.csv) |

**`Harmonized CTD^2 25Q2`** (2025-03-11, 7개) — CTRP

| 파일 | 내용 | 용량* | 링크 |
|---|---|---|---|
| `CTRPLog2ViabilityCollapsedMatrix.csv` | replicate 통합 log2 생존율 | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=Harmonized+CTD%5E2+25Q2&filename=CTRPLog2ViabilityCollapsedMatrix.csv) |
| `CTRPLog2IC50Matrix.csv` | log2(IC50) 행렬 | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=Harmonized+CTD%5E2+25Q2&filename=CTRPLog2IC50Matrix.csv) |
| `CTRPLog2ViabilityConditions.csv` | 생존율 조건 주석 | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=Harmonized+CTD%5E2+25Q2&filename=CTRPLog2ViabilityConditions.csv) |
| `CTRPLog2ViabilityMatrix.csv` | 농도별 log2 생존율 | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=Harmonized+CTD%5E2+25Q2&filename=CTRPLog2ViabilityMatrix.csv) |
| `CTRPResponseCurves.csv` | 곡선 적합 파라미터 | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=Harmonized+CTD%5E2+25Q2&filename=CTRPResponseCurves.csv) |
| `CTRPLog2ViabilityCollapsedConditions.csv` | replicate 통합 생존율 조건 주석 | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=Harmonized+CTD%5E2+25Q2&filename=CTRPLog2ViabilityCollapsedConditions.csv) |
| `CTRPAUCMatrix.csv` | AUC 행렬 | — | [열기](https://depmap.org/portal/data_page/?tab=allData&releasename=Harmonized+CTD%5E2+25Q2&filename=CTRPAUCMatrix.csv) |

### 6. 데이터 사용 조건 (2026년에 바뀜)

⚠️ DepMap 개발자가 [포럼 4652](https://forum.depmap.org/t/4652)에서 인용한 현행 이용약관:

> 이 데이터는 연구 목적으로 생성되었으며 임상·상업적 용도를 의도하지 않는다. 여기에는 직접 판매, 제품에의 편입, 그리고 **내부 연구용을 제외한 목적으로 머신러닝·AI 모델을 학습·개발·강화하는 데 데이터를 사용하는 것**이 포함된다(각각 "Commercial Use"). 명확히 하자면, ML·AI 모델을 **자체 내부 용도로 또는 비영리 연구 목적(공정 최적화·분석 포함)으로 공유하는 것은 허용**된다. 상업적 사용은 허용되지 않으며 Broad 또는 기여자와의 별도 라이선스 계약이 필요할 수 있다.

- **수업 프로젝트 / 비영리 연구 목적의 모델 학습·공유는 허용된다.** 우리 용도는 문제없음.
- 다만 "CC BY 4.0이므로 재배포 제한 없음"이라는 통념은 **신규 데이터에는 더 이상 맞지 않는다.** 발표·리포트에 라이선스를 적을 때 주의.
- 과거 데이터는 figshare / AWS Open Data에 올라가 있으나, **25Q2 이후 본 릴리스는 figshare에 미러링되지 않는다.**

### 7. 다운로드 전 알아둘 것

1. **조인 키는 `ModelID`** (`ACH-XXXXXX`). 레거시 PRISM(Corsello)은 `depmap_id` 컬럼명을 쓴다.
2. **유전자 컬럼은 `SYMBOL (ENTREZID)` 형태** → 파싱 필요.
3. **25Q3부터 omics 테이블에 메타데이터 컬럼이 붙는다:** `ModelID`, `IsDefaultEntryForModel`, `ModelConditionID`, `IsDefaultForMC`, `SequencingID`. 한 모델이 여러 행을 가질 수 있고 포털 표시값은 `IsDefaultEntryForModel == "Yes"` 인 행이다. **행렬로 바로 읽지 말고 필터링 먼저** — 안 하면 중복 세포주가 학습셋에 들어간다.
4. **반드시 같은 릴리스로 통일.** 약물 반응만 릴리스가 다르므로(24Q2/25Q2 ↔ 26Q1), 암종 라벨은 26Q1 `Model.csv` 기준으로 재부여할 것.
5. `CRISPRGeneEffect.csv`에 NaN 존재 (라이브러리별 유전자 커버리지 차이). 25Q2 노트에 따르면 Humagne/KY에만 있는 유전자는 현재 drop 상태.
6. 용량은 발현 파일이 대부분. 원시 리드카운트까지 받으면 수십 GB.
7. **발현 파일은 Stranded / 비-Stranded 두 종류가 있고 공식 권장이 없다.** DepMap이 25Q2 노트에서 "strandedness 외의 배치 효과 요인을 보정할 방법을 탐색 중"이라고 밝힌 상태. 어느 쪽을 썼는지 반드시 기록할 것. 배치보정판은 25Q2에서 제거됐고 대체 파일이 없다.

## 결론 / 다음 액션

- **26Q1 파일명은 위 [4](#4-depmap-public-26q1-전체-파일-85개) 가 실측 기준이다.** AI가 알려주는 DepMap 파일명은 25Q2 이하 기준일 가능성이 높으니 그대로 믿지 말 것.
- 이 문서는 **어떤 파일이 있는지**까지만 다룬다. 우리 프로젝트가 **실제로 받아야 할 최소 구성과 다운로드 체크리스트**는 [AI 질답 정리 Q3(C-1~C-6)](../depmap_gpt_qna/lkeonwoo94.md#q3-그럼-최소한으로-받아야-하는-데이터가-뭐야) 에 있다.
- [ ] 26Q2 릴리스가 나오면 [1](#1-파일-목록을-직접-받는-법-캡차-없음) 의 엔드포인트로 파일명 변경 여부 재확인 → 바뀌었으면 [3](#3-25q3에서-바뀐-파일명-가장-중요) · [4](#4-depmap-public-26q1-전체-파일-85개) 갱신

### 검증에 쓴 출처

- [DepMap 26Q1 릴리스 노트](https://forum.depmap.org/t/4606) (2026-04-01)
- [DepMap 25Q3 릴리스 노트](https://forum.depmap.org/t/4476) (2025-09-25)
- [DepMap 25Q2 릴리스 노트](https://forum.depmap.org/t/4257) (2025-06-05)
- [캡차 없는 파일 목록 엔드포인트 + 라이선스](https://forum.depmap.org/t/4652) (2026-07-14)
- [OmicsCNGeneWGS 값 해석](https://forum.depmap.org/t/4656) (2026-07-17)
- [절대 CN 폐기 안내](https://forum.depmap.org/t/4665) (2026-08-06)
- `https://depmap.org/portal/api/no-captcha/download/files` (2026-08-11 취득)
