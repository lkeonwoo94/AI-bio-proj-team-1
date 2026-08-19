# Candidate Minimal Mutation Biomarker Panel (2026-08-19 기준)

08-16의 Day 11/12 결과(§26③④, "Day 11/12 Random Forest 재검증")와
08-19의 후속 실험(CIN 회귀 기반 패널, TCGA 외부 검증)을 모두 반영해
후보 패널을 하나로 정리한다. 이 문서는 **새 실험이 아니라 기존 근거를
종합한 결론 문서**다 — 각 수치의 원출처는 표에 링크했다.

---

## 1. 최종 후보 패널

**핵심 축(3표현형 공통, 근거 최상위) — 4개**

`TP53`(damaging+hotspot), `ID3`, `BRAF`(hotspot), `CREBBP`

**표현형 특이 축(근거 상위) — 4개**

| 유전자 | 표현형 | 역할 |
| --- | --- | --- |
| `TERT`(hotspot) | WGD | telomerase 역전사효소 — promoter hotspot 로 telomere 유지, 노화 신호 우회 |
| `RB1` | CIN | G1/S checkpoint tumor suppressor — 소실 시 분열 통제 상실 |
| `PIK3CA`(hotspot) | CIN | PI3K 촉매 subunit — hotspot 변이로 증식 신호 과다 전달 |
| `PITX1` | LOH | 발생 전사인자 겸 tumor suppressor — RAS 신호 억제 관련 |

이 8개가 **현재 근거 수준에서 제시할 수 있는 candidate panel의 전부**다.
아래 §2의 근거표를 기준으로 이 8개를 골랐다 — README §21의 표현대로
"고정된 10개 패널"이 아니라 **합의 유전자(consensus) 중심**으로 제시한다
(08-16 §26④의 판단을 그대로 따름).

---

## 2. 근거표 — fold·모델·selection 방법을 넘어 몇 번이나 재확인됐는가

| 유전자 | fold 반복 (EN/RF, "Day 11/12 RF 재검증") | RF 설명력 %(WGD / CIN / LOH) | CIN 회귀 재확인 | TCGA 외부 지지 | 비고 |
| --- | ---: | ---: | :---: | :---: | --- |
| `TP53`(damaging) | 1.00 / 1.00 | **15.3% / 14.1% / 14.4%** | ✅ | △ (하한추정치, missense 근사 한계) | 세 표현형 전부 평균 순위 1위 |
| `TP53`(hotspot) | 0.60 / 1.00 | 9.4% / 7.7% / 7.5% | — | — | |
| `ID3` | 1.00 / 1.00 | 1.6% / 1.6% / 1.5% | ✅ | — | |
| `BRAF`(hotspot) | 1.00 / 1.00 | 2.8% / 1.6% / 0.8% | ✅ | — | |
| `CREBBP` | 0.93 / 1.00 | 0.9% / 0.9% / 0.7% | ✅ | — | WGD·LOH 5/5, CIN 4/5(EN 기준) |
| `RB1` | 0.80 / 1.00 | 1.0% / 1.8% / 1.7% | ✅ | — | CIN 특이(§26③) |
| `TERT`(hotspot) | 0.67 / 0.87 | 3.2% / 1.9% / 0.3% | ✅ | — | WGD 특이(§26③), CIN 회귀에서도 재확인 |
| `PITX1` | 0.67 / 0.93 | 0.5% / 0.7% / 0.9% | — (CIN 회귀만 검증, LOH 회귀는 안 함) | — | LOH 특이(§26③) |
| `PIK3CA`(hotspot) | * | 0.4% / 1.0% / 0.2% | ✅ | — | CIN 특이(§26③) — EN 단독 fold 선택에서는 5/5였으나 8-gene 모델합의표엔 없음, 이번 회차 CIN 회귀로 cross-model 근거 보강 |

\* `PIK3CA` 는 원래 Elastic Net 단독 CIN 특이 유전자(§26③, fold 선택빈도
1.0)로 확인됐고, "모델 간 합의" 8-gene 표(EN·RF 분류만 비교)에는
포함되지 않았다. 이번 회차 CIN 회귀 기반 selection(EN reg·RF reg 모두)
에서 재확인되어 분류-회귀 두 방법을 넘는 근거를 추가로 확보했다 —
자세한 내용은
[additional_results.md §2 후속](additional_results.md#후속--cin-회귀-기반-최소-패널-한계-6-후속).

**"RF 설명력 %"** 열은 Random Forest 의 impurity-based feature
importance(`feature_importances_`, 표현형별 outer 5-fold 평균)로,
한 fold 안에서 전체 feature(필터 통과 후 \~1,200\~1,700개)의 importance
합이 100%가 되도록 정규화된 값이다(`scripts/07_aggregate_selection.py`
가 저장한 `day11_selection_random_forest_{target}.csv` 의
`mean_importance` 컬럼, "Day 11/12 Random Forest 재검증" 절과 같은
산출물). `TP53`(damaging+hotspot) 둘이 합쳐 세 표현형 모두 20% 대를
차지해 압도적이고, 그다음 유전자부터는 급격히 줄어 1\~3%대에서
서로 촘촘히 몰린다 — "Day 11/12 RF 재검증"의 "① importance 가 상위
소수에만 집중되고 나머지는 완만한 꼬리를 이룬다"는 관찰과 정확히
일치한다. 즉 **핵심 축(TP53) 하나가 나머지 7개를 합친 것보다도 큰
설명력을 갖고, 나머지는 "그 다음으로 반복 재현되는" 수준이지
개별적으로 TP53 에 필적하는 설명력을 갖는 것은 아니다.**

**"CIN 회귀 재확인"** 열은 08-19 이번 회차에 실행한 CIN 회귀 기반
패널(`scripts/28_cin_regression_panel.py`)의 10개 패널에 그 유전자가
포함됐는지를 뜻한다 — 분류(이진화)와 무관한 별도 방법으로 다시 뽑아도
나온 유전자라는 의미다. LOH/WGD 는 회귀 재검증을 하지 않았다(LOH 는
회귀 검증에서 이진화 손실이 없었던 표현형이라 동기가 약했고, WGD 는
원래부터 이진 라벨이라 회귀 대상이 아니다).

**"TCGA 외부 지지"** 열은 유전자 단위로 검증된 것이 아니다 — TCGA
검증(`scripts/21_tcga_validation.py`)은 damaging feature 전체를 입력으로
쓴 모델 수준 비교이며, 개별 유전자의 기여도를 분리해서 보지 않았다.
`TP53` 만 별도로 damaging 근사 비율을 비교했고(DepMap 57.8% vs TCGA
12.4%), 그 격차가 방법론적 한계(missense 미포착)임을 확인했다 — 즉
"△"는 완전한 지지가 아니라 "방향은 유지되지만 근사 방식의 한계 안에서"
라는 뜻이다. 나머지 7개 유전자는 TCGA 로 개별 검증되지 않았다.

---

## 3. 이 패널이 뜻하는 것 / 뜻하지 않는 것

**뜻하는 것**

* 위 8개 유전자는 서로 다른 4가지 축(outer fold, 분류 모델 종류
  [Elastic Net vs Random Forest], 선택 방법 [분류 vs 회귀], 원논문 지식과의
  방향 일치)에서 반복적으로 재확인됐다 — 단발성 결과가 아니다.
* `TP53`/`ID3`/`BRAF`/`CREBBP` 4개는 세 표현형 모두에서, 나머지 4개는
  최소 하나의 표현형에서 강한 일관성을 보인다.

**뜻하지 않는 것**

* **임상 진단용 바이오마커가 아니다.** 성능 자체가 acceptable
  구간(ROC-AUC 0.73\~0.77)에 그치고, 유병률 대비 이득과 확률 보정이
  제한적이다(08-16 "이 결론의 한계" 1번).
* **범암종에서 동일하게 작동한다는 근거가 없다.** lineage 를 분리하면
  성능이 떨어지고, 그 편차의 원인은 규명되지 않았다(08-19
  additional_results.md §1). 이 패널을 특정 암종에 적용할 때는 그
  암종에서 신호가 존재하는지 별도로 확인해야 한다.
* **TCGA 로 패널 전체가 검증된 것이 아니다.** WGD 하나, damaging-only
  근사, 유전자별 분해 없이 모델 수준으로만 검증됐다(08-19
  additional_results.md §5).
* **패널 안정성은 완전(Jaccard 1.0)하지 않다.** "Day 11/12 RF 재검증"에
  따르면 fold 두 개를 비교하면 10개 중 평균 7.5개(RF)\~5.8개(EN)만
  겹친다 — 위 8개는 그 흔들림 속에서도 상대적으로 안정적인 축일 뿐,
  "이 8개 외에는 무의미하다"는 뜻이 아니다.
* **기능 설명은 통계적 연관에 대한 사후 해석이다.** 본 연구가 그
  기전을 직접 검증하지는 않았다(08-16 §27 각주와 동일한 단서).

---

## 4. 패널에서 제외한 것과 이유

* **Pathway 단위 재집계(11 gene set)** — 성능이 6/6 조합 전부
  하락했다(-0.028\~-0.049). 유전자 정체성 정보를 뭉개는 재집계라
  패널 후보로 부적절하다(additional_results.md §3).
* **Mutation signature(96-class)** — 성능은 개선됐지만(5/6 조합) 이건
  "어떤 유전자에 변이가 있는가"가 아니라 "어떤 종류의 변이 발생
  과정이었는가"를 보는 **다른 축의 정보**다. 유전자 단위 biomarker
  panel과 같은 표에 놓을 수 없어 이 문서에서는 제외했다 — 대신
  `T[C>A]C` 등 signature 자체의 후보 class 는
  additional_results.md §4 후속 절에 별도로 정리돼 있다. 향후 두 축을
  합친 "혼합 패널"(유전자 + signature class)을 시도해볼 여지는 남아있다
  (08-19 final_conclusion.md "남은 과제").
* **§26③의 나머지 표현형 특이 유전자**(`NF2`, `CCND3`, `LRP1B`,
  `TGFBR2`, `SLFN11`, `MUC19`, `ABCB5`) — Elastic Net 단독 fold 선택
  (5/5)에서는 나왔지만 Random Forest 모델 합의표나 회귀 재검증으로
  교차 확인되지 않아 이번 "최종 후보"에서는 제외했다. 근거가 아예
  없는 것은 아니므로 "2차 후보"로는 08-16 §26③·§27 을 참고할 수 있다.

---

## 5. 재현

```bash
python scripts/07_aggregate_selection.py --model random_forest
python scripts/08_panel_curve.py --model random_forest
python scripts/14_panel_stability_explain.py --model random_forest
python scripts/28_cin_regression_panel.py
python scripts/21_tcga_validation.py
```

원출처: [2026-08-16/final_conclusion.md §26③④, "Day 11/12 Random Forest 재검증"](../2026-08-16/final_conclusion.md),
[2026-08-19/additional_results.md](additional_results.md),
[2026-08-19/final_conclusion.md](final_conclusion.md)
