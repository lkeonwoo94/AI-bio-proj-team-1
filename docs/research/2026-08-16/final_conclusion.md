# 최종 결론 (README §26 · §27)

DepMap Public 26Q1 / 1,631 세포주 / hotspot 554 + damaging 19,578 feature /
lineage 32종 / nested CV (outer 5 × inner 5)

---

# §26. 최종 결론에서 답해야 하는 다섯 질문

## ① DNA mutation 만으로 WGD/CIN/LOH 를 예측할 수 있었는가?

**부분적으로 가능하다. 세 표현형 모두 무작위보다 확실히 높지만 실용 수준은 아니다.**

최고 성능(Random Forest, random 5×5 nested CV):

| 표현형 | ROC-AUC | PR-AUC | Balanced Acc | Brier |
| --- | ---: | ---: | ---: | ---: |
| WGD | 0.765 | 0.841 | 0.715 | 0.204 |
| CIN | 0.734 | 0.706 | 0.678 | 0.216 |
| LOH | 0.730 | 0.696 | 0.676 | 0.217 |

세 표현형 중 **WGD 가 가장 잘 예측된다.** 다만 WGD 의 PR-AUC 0.841 을
CIN/LOH 의 0.70 과 직접 비교하면 안 된다. WGD+ 가 65.2% 로 다수 클래스라
무작위 분류기의 PR-AUC 기저선이 이미 0.65 이기 때문이다. CIN/LOH 는
중앙값 이진화로 기저선이 0.50 이다. **표현형 간 비교는 ROC-AUC 로 한다.**

Balanced accuracy 가 0.68\~0.72 라는 것은, 임의의 세포주에서 WGD 여부를
맞힐 확률이 10번 중 7번 정도라는 뜻이다.

이 수치를 평가할 때 **ROC-AUC 자체보다 유병률 대비 이득을 봐야 한다.**
WGD 는 양성이 65.2% 이므로 모두 WGD+ 로 찍기만 해도 정확도 65.2% 가 나온다.
모델의 balanced accuracy 0.715 는 그보다 낫지만 격차가 크지 않다.
Brier 도 0.20 대로 확률 보정이 좋지 않다. 즉 **신호는 분명히 존재하지만
그 신호로 개별 세포주의 상태를 판정하기에는 부족하다**는 것이 정확한 서술이다.

## ② 어떤 모델이 가장 안정적인 성능을 보였는가?

**Random Forest.** 세 표현형 모두에서 1위였고 fold 간 편차도 작았다.

| 모델 | 평균 ROC-AUC | 표준편차 |
| --- | ---: | ---: |
| **Random Forest** | **0.743** | 0.019 |
| XGBoost | 0.738 | 0.016 |
| CatBoost | 0.730 | 0.028 |
| Elastic Net | 0.714 | 0.034 |
| Logistic | 0.693 | 0.027 |
| Multi-task ANN | 0.681 | 0.020 |

세 가지를 함께 읽어야 한다.

**비선형 모델이 선형 모델을 일관되게 앞선다** (RF/XGB/CatBoost 0.73\~0.74 vs
Logistic 0.69).
변이 간 interaction 이 실제로 존재한다는 뜻이다. 다만 그 이득은 0.05 정도로,
"선형으로 충분하지 않다" 보다는 "약간의 비선형 구조가 있다" 에 가깝다.

**Multi-task ANN 이 최하위다 — RQ4 에 대한 부정적 결과.** 세 표현형의
Spearman 상관이 0.62\~0.77 로 낮지 않은데도 공유 표현이 개별 모델을 이기지
못했다. 이를 "공유 신호가 없다" 로 읽어서는 안 된다. 샘플 1,631 개에 필터
후 feature 2,000 여 개인 조건은 MLP 에게 불리하고, 본 연구는 torch 대신
sklearn MLPClassifier 로 구현해 구조 탐색 폭도 좁았다. **"이 설정에서는
multi-task 학습의 이득이 관측되지 않았다"** 가 정확한 서술이다.

## ③ 어떤 mutation 이 반복적으로 중요한 feature 로 선택되었는가?

Elastic Net 으로 outer 5 fold 각각의 training data 에서 feature selection 을
반복한 결과, 5/5 fold 에서 선택된 유전자는
WGD 12개 / CIN 5개 / LOH 9개였다.

**세 표현형 공통 후보** (표는 fold 선택 빈도, 1.0 = 5/5 전 fold):

| 유전자 | 유형 | WGD | CIN | LOH |
| --- | --- | ---: | ---: | ---: |
| `TP53` | damaging | 1.0 | 1.0 | 1.0 |
| `ID3` | damaging | 1.0 | 1.0 | 1.0 |
| `BRAF` | hotspot | 1.0 | 1.0 | 1.0 |
| `CREBBP` | damaging | 1.0 | **0.8** | 1.0 |

`TP53`/`ID3`/`BRAF` 만 세 표현형 모두 전 fold(5/5) 선택이다. `CREBBP` 는
WGD·LOH 는 전 fold(5/5)지만 CIN 은 4/5 로, 완전한 "전 fold 공통"은 아니다.

**표현형 특이적:**

* WGD — `TERT`(hotspot), `NF2`, `CCND3`, `LRP1B`, `TGFBR2`
* CIN — `RB1`, `PIK3CA`(hotspot), `SLFN11`
* LOH — `NF2`, `PITX1`, `MUC19`, `ABCB5`

`TP53` 은 세 표현형 모두에서 평균 순위 1.0, 순위 표준편차 0.0 이었다.
즉 어느 fold 에서도 예외 없이 1위였다. TP53 이 유전체 불안정성의 핵심
유전자라는 기존 지식과 일치하므로, 파이프라인이 의미 있는 신호를 잡고
있다는 방향성 검증(sanity check)으로 볼 수 있다.

`RB1`(CIN/LOH), `TERT`(WGD/CIN) 처럼 표현형 쌍에만 걸리는 유전자가 있다는
점은, 세 표현형을 하나의 '유전체 불안정성 점수' 로 합치지 않은 README §2 의
설계가 타당했음을 뒷받침한다.

## ④ 전체 mutation 을 몇 개까지 줄여도 성능이 유지되었는가?

**성능만 보면 10개로 충분하다. 그러나 그 10개가 무엇인지는 fold 마다 다르다.**

| 패널 | WGD | CIN | LOH |
| --- | ---: | ---: | ---: |
| 5개 | 0.709 (95%) | 0.655 (96%) | 0.666 (94%) |
| **10개** | **0.727 (97%)** | **0.674 (99%)** | **0.669 (94%)** |
| 20개 | 0.730 (97%) | 0.667 (98%) | 0.666 (94%) |
| 50개 | 0.707 (94%) | 0.654 (96%) | 0.657 (92%) |
| 전체 (\~2,000) | 0.749 | 0.681 | 0.711 |

성능 곡선이 **단조롭지 않다.** 50개가 10\~20개보다 낮은데, 패널 크기가
바뀔 때마다 inner CV 가 규제 강도를 다시 고르기 때문으로 보인다.
"50개가 10개보다 나쁘다" 가 아니라 **"10개 이후로는 평평하다"** 로 읽는다.

**안정성 (fold 간 Jaccard 유사도):**

| 패널 | WGD | CIN | LOH |
| --- | ---: | ---: | ---: |
| 5개 | 0.56 | 0.44 | 0.48 |
| 10개 | 0.41 | 0.33 | 0.30 |
| 20개 | 0.37 | 0.25 | 0.20 |
| 50개 | 0.28 | 0.23 | 0.24 |

10개 패널에서 fold 두 개를 비교하면 겹치는 유전자가 **3분의 1 남짓**이다.
20개 패널에서 5개 fold 전부에 등장한 유전자는 WGD 7개 / CIN 4개 / LOH 3개뿐이다.

* WGD — `TP53`(damaging), `TP53`(hotspot), `BRAF`(hotspot), `TERT`(hotspot),
  `ID3`, `CREBBP`, `LRP1B`
* CIN — `TP53`, `BRAF`(hotspot), `TERT`(hotspot), `ID3`
* LOH — `TP53`, `NF2`, `ID3`

**결론: 신호는 소수의 핵심 유전자 + 다수의 교체 가능한 주변 유전자 구조다.**
README §25 의 "작은 패널 성능 유지" 와 "신호가 여러 유전자에 분산" 이
섞인 중간 형태이며, §18 의 안정성 기준을 충족한다고 보기는 어렵다.
따라서 **고정된 10개 패널을 제시하기보다 위의 합의 유전자(consensus)를
핵심 축으로 제시**하는 것이 데이터에 충실하다. (Random Forest 로 재검증한
결과 이 불안정성은 Elastic Net 특유의 현상에 가까웠다 — 한계 5번 및
"Day 11/12 Random Forest 재검증" 절 참조.)

## ⑤ 이 결과가 다른 cancer lineage 에서도 유지되었는가?

**아니다. 세 표현형 모두 lineage 를 분리하면 성능이 떨어진다.**

Random CV vs lineage GroupKFold (Elastic Net):

| 표현형 | Random | GroupKFold | 차이 |
| --- | ---: | ---: | ---: |
| WGD | 0.749 | 0.687 | −0.062 |
| CIN | 0.681 | 0.635 | −0.046 |
| LOH | 0.711 | 0.642 | −0.069 |

Leave-One-Lineage-Out (24종, 세포주 20개 미만 8종 제외):

| 표현형 | 평균 | 중앙값 | IQR | 0.5 미만 |
| --- | ---: | ---: | --- | ---: |
| WGD | 0.638 | 0.637 | 0.587–0.706 | 3 / 24종 |
| CIN | 0.576 | 0.570 | 0.500–0.632 | **6 / 24종** |
| LOH | 0.617 | 0.586 | 0.554–0.688 | 3 / 24종 |

**왜 특정 암종에서 무너지는지는 설명하지 못했다.**

처음에는 lineage 별 WGD+ 기저율 차이(전체 65.2%)를 원인으로 의심했다.
Lung 89.3% → AUC 0.449, Pancreas 91.3% → 0.509 처럼 기저율이 극단적인
암종에서 성능이 낮았기 때문이다.

그러나 24 종 전체에서 검정한 결과 **이 가설은 지지되지 않는다.**

| 검정 | Spearman rho | p |
| --- | ---: | ---: |
| WGD+ 기저율 편차 vs LOLO AUC | +0.037 | 0.865 |
| 세포주 수 vs LOLO AUC | +0.095 | 0.658 |

명확한 반례가 있다. Fibroblast 는 WGD+ 가 6.5% 로 편차가 가장 큰 축에
속하는데 AUC 는 0.853 으로 상위권이다. Thyroid 역시 기저율 82.6% 에서
AUC 0.882 다. 반대로 Eye 는 기저율이 50.0% 로 전체 평균에 가까운데도
AUC 0.314 로 최저다.

즉 **암종별 성능 편차는 기저율로도, 표본 크기로도 설명되지 않는다.**

**세 가지 추가 가설도 검정했으나 모두 기각됐다.** TP53 이 가장 중요한
단일 유전자이므로, lineage 안에서 TP53 변이율이 0% 나 100% 에 가까우면
(그 lineage 안에서는 변별력이 없으므로) 성능이 낮을 것이라는 가설과,
단순히 세포주당 mutation 개수(burden)가 적어 정보가 부족한 lineage 일
것이라는 가설을 세웠다.

| 검정 | Spearman rho | p |
| --- | ---: | ---: |
| TP53 변이율 vs LOLO AUC | +0.148 | 0.491 |
| 세포주당 평균 mutation burden vs LOLO AUC | −0.201 | 0.347 |
| TP53 변이율의 극단성(0/1 에 가까움) vs LOLO AUC | +0.216 | 0.311 |

다섯 가설(기저율, 표본 크기, TP53 변이율, mutation burden, TP53 변이율의
극단성) 전부 유의하지 않다. 단순한 단변량 교란변수로는 설명되지 않는다는
점이 그만큼 더 확실해졌다 — 다만 lineage 수가 24 개뿐이라(|rho|>0.4 는
되어야 p<0.05) 통계적 검정력 자체가 낮다는 한계는 남는다.

다섯 가설을 한 그림으로 모은 것이 Figure 8 이다
(`results/figures/fig8_lineage_hypotheses.png`,
`python scripts/16_plot_lineage_hypotheses.py`). 어느 패널에서도
뚜렷한 추세선이 보이지 않고, Fibroblast·Thyroid(위쪽 성공 사례)와
Eye·Lung(아래쪽 실패 사례)이 x축 위치와 무관하게 흩어져 있다는 점이
"단순 교란변수로 설명되지 않는다"는 결론을 시각적으로 뒷받침한다.

재현: `python scripts/15_lineage_hypothesis_test.py`

**후속 분석(암종 내부 학습)으로 한 가지는 배제했다.** 세포주 60개 이상인
9종에서 그 암종 데이터만으로 학습·평가한 결과, 내부 학습이 LOLO 를
앞서지 못했다 (평균 차이 WGD −0.046, CIN +0.011, LOH −0.018; CIN/LOH 는
LOLO 와 동일한 label 정의를 쓰도록 암종 외부에서 threshold 를 계산).

따라서 성능 편차는 **암종 간 전이의 실패가 아니다.** LOLO 에서 무너지는
암종은 내부에서 학습해도 무너진다 (Lung WGD: LOLO 0.449, 내부 0.494).
**일부 암종에는 mutation-only 로 학습 가능한 신호가 애초에 없다**는 쪽에
가까우며, 암종별 맞춤 패널로 해결될 문제가 아니다.
자세한 내용은 `lineage_specific_models.md` 참조.

GroupKFold 감소폭은 CIN 이 가장 작지만(−0.046) LOLO 평균은 CIN 이 가장
낮다(0.576). 두 결과가 모순은 아니다. GroupKFold 는 fold 안에 여러 암종이
섞여 완충되는 반면 LOLO 는 한 암종만 남기므로 훨씬 가혹하다.

**따라서 본 연구의 결과는 pan-cancer biomarker 가 아니라
lineage-dependent candidate 로 기술해야 한다** (README §25 시나리오 3).

---

# §27. 최종 결론문

본 연구에서는 DepMap Public 26Q1 의 hotspot 및 damaging mutation 정보만을
이용하여 암세포주의 whole genome doubling(WGD), chromosomal instability(CIN),
loss of heterozygosity(LOH) 상태를 예측하였다. 세 표현형이 모두 관측된
1,631 개 세포주를 대상으로 hotspot 554 개와 damaging 19,578 개 유전자를
입력으로 사용하였으며, copy number, ploidy, gene expression, TMB 는 정답
정보를 간접적으로 제공할 위험이 있어 주 모델의 입력에서 제외하였다.

Logistic Regression, Elastic Net, Random Forest, XGBoost, CatBoost 및
multi-task ANN 을 동일한 nested cross-validation(outer 5 × inner 5) 조건에서
비교하였다.
희귀 변이 제거, CIN/LOH 이진화 threshold, hyperparameter, feature selection,
분류 threshold 는 모두 각 training fold 내부에서만 결정하였고 outer test
데이터는 어떤 단계에도 관여하지 않았다.

**예측 성능.** Random Forest 가 세 표현형 모두에서 가장 높았으며
ROC-AUC 는 WGD 0.765, CIN 0.734, LOH 0.730 이었다. 비선형 모델(RF/XGBoost/
CatBoost, 평균 0.73\~0.74)이 선형 모델(평균 0.69\~0.71)보다 일관되게 앞섰으나
그 차이는 0.05 내외였다. XGBoost 와 CatBoost 는 같은 gradient boosted
trees 계열임에도 성능이 거의 동일했는데(0.738 vs 0.730), 이는 CatBoost 의
강점인 categorical feature 처리가 0/1 binary feature 로만 구성된 본
데이터에서는 발휘될 여지가 없었기 때문으로 보인다. 세 표현형 간 Spearman
상관이 0.62\~0.77 로 낮지 않았음에도 multi-task ANN 은 개별 모델을 넘어서지
못하여, 본 설정에서는 표현형 간 공유 표현의 이득이 관측되지 않았다.

**중요 변이.** 각 fold 의 training data 에서 feature selection 을 반복한
결과 `TP53`(damaging), `ID3`, `BRAF`(hotspot) 가 세 표현형 모두에서
전 fold 선택되었고, `CREBBP` 도 WGD·LOH 는 전 fold, CIN 은 4/5 fold 로
근접한 공통 후보였다. 특히 `TP53` 은 세 표현형 모두 평균 순위 1.0
(순위 표준편차 0.0)으로 예외 없이 1위였다. 표현형 특이적으로는 WGD 에서
`TERT`(hotspot)와 `NF2`, CIN 에서 `RB1` 과 `PIK3CA`(hotspot), LOH 에서
`NF2` 와 `PITX1` 이 반복 선택되었다.

**최소 패널.** 5, 10, 20, 50 개 변이로 구성한 축소 모델을 전체 모델과
동일한 outer test set 에서 비교한 결과, 10 개 패널이 전체 모델 성능의
94\~99% 를 유지하였고 그 이상 늘려도 성능이 증가하지 않았다. 그러나 fold
간 패널 구성의 Jaccard 유사도가 10 개 기준 0.30\~0.41 에 그쳐, 어떤 유전자
조합으로 그 성능에 도달하는지는 학습 데이터에 따라 달라졌다. 이는 예측에
필요한 정보가 소수의 핵심 유전자와 다수의 교체 가능한 주변 유전자에
분산되어 있음을 시사한다. 따라서 본 연구는 고정된 10 개 패널을 제시하는
대신, 모든 fold 에서 합의된 핵심 유전자(WGD 7 개, CIN 4 개, LOH 3 개)를
후보의 중심축으로 제시한다.

**일반화.** lineage 를 분리한 검증에서 세 표현형 모두 성능이 감소하였다
(GroupKFold −0.046 \~ −0.069). Leave-One-Lineage-Out 에서는 평균 ROC-AUC 가
WGD 0.638, CIN 0.576, LOH 0.617 로 더 낮았고, 24 개 암종 중 WGD 3 종,
CIN 6 종, LOH 3 종에서 무작위 수준(0.5) 미만이었다. 암종별 성능 편차는
매우 컸으나(WGD 기준 0.314\~0.882), 그 편차는 lineage 별 표현형 기저율
차이로도(Spearman rho +0.037, p=0.865) 표본 크기로도(rho +0.095, p=0.658)
설명되지 않았다. 따라서 본 연구에서 도출된 변이 신호는 범암종에서
동일하게 작동하는 biomarker 라기보다 **lineage 의존적 후보**로 해석하는
것이 타당하며, 어떤 암종에서 작동하고 어떤 암종에서 실패하는지의
기전은 규명하지 못하였다.

**결론.** 본 연구는 DNA mutation 만으로 유전체 불안정성 상태를 ROC-AUC
0.73\~0.77 수준까지 예측할 수 있음을 보였으며, 예측에 필요한 정보를 약 10 개
변이로 축약해도 성능의 대부분이 유지됨을 확인하였다. 다만 축약된 패널의
구성이 학습 데이터에 따라 달라지고 암종 간 일반화가 제한적이라는 점에서,
본 결과는 **candidate minimal mutation biomarker panel** 로서 다음 조건을
명시하여 제시한다.

* 핵심 축: `TP53`, `ID3`, `BRAF`(hotspot), `CREBBP` (세 표현형 공통) 및
  표현형 특이 유전자 (`TERT`, `NF2`, `RB1`, `PIK3CA`, `PITX1`)
  * `TP53` — 대표적 tumor suppressor. DNA 손상 시 세포주기를 멈추거나
    세포사멸을 유도; 소실되면 손상된 세포가 그대로 분열해 유전체
    불안정성이 누적된다.
  * `ID3` — 전사인자 활성을 억제하는 조절인자(bHLH 계열 억제자); 세포
    분화·증식 균형에 관여하며 여러 암에서 변이가 보고된다.
  * `BRAF`(hotspot) — MAPK 신호전달의 kinase. V600E 등 특정 위치 변이로
    항상 활성화되어 증식 신호를 지속적으로 내보낸다.
  * `CREBBP` — 히스톤 아세틸화를 통한 전사 공활성인자(chromatin
    remodeling); 소실 시 DNA 손상 반응·세포주기 조절 유전자의 발현이
    흐트러진다.
  * `TERT`(WGD 특이) — telomerase 역전사효소. 프로모터 hotspot 변이로
    발현이 늘면 telomere 가 과도하게 유지되어 세포가 정상적으로 멈춰야
    할 노화 신호를 우회한다 — WGD 세포의 생존과 관련이 깊다.
  * `NF2`(WGD/LOH 특이) — Merlin 단백질을 만드는 tumor suppressor; 세포
    접촉 억제와 증식 신호 조절에 관여하며 소실 시 염색체 분리 이상과도
    연관된다.
  * `RB1`(CIN/LOH 특이) — 세포주기 checkpoint(G1/S) 를 통제하는 대표적
    tumor suppressor. 소실되면 분열 시점 통제가 풀려 염색체 불안정성과
    직결된다.
  * `PIK3CA`(CIN 특이, hotspot) — PI3K 신호전달의 촉매 subunit. hotspot
    변이로 항상 활성화되어 증식·생존 신호를 과다하게 전달한다.
  * `PITX1`(LOH 특이) — 발생 과정의 전사인자이자 tumor suppressor 로도
    보고됨; RAS 신호 억제와 관련되어 소실 시 증식 억제가 풀린다.

  (기능 설명은 일반적으로 알려진 역할을 요약한 것으로, 본 연구가 그
  기전을 직접 검증하지는 않았다 — Day 11 반복 feature selection 으로
  얻은 통계적 연관일 뿐이다.)
* 적용 범위: DepMap 세포주 코호트 내부 검증 결과이며, 암종 간 일반화는
  확인되지 않음
* 성능 수준: 판별력은 acceptable 구간(ROC-AUC 0.73–0.77)이나, WGD 유병률
  65.2% 대비 이득이 제한적이고 확률 보정(Brier 0.20 대)이 좋지 않아
  개별 세포주 판정 용도로는 불충분

해당 패널은 임상 진단용 확정 바이오마커가 아니라 DepMap 내부 검증을 통해
도출된 연구용 후보이며, 향후 독립 코호트와 실험적 검증이 필요하다.
특히 lineage 별 기저율 차이를 통제한 재분석과, 본 연구에서 제외한
MSI·gene expression 을 포함한 확장 분석이 후속 과제로 남는다.

---

## 이 결론의 한계

1. **성능 수준을 어디에 견줄 것인가.** ROC-AUC 에는 보편적인 "실용 임계"
   가 없다. 널리 인용되는 Hosmer-Lemeshow 관례(0.7–0.8 acceptable,
   0.8–0.9 excellent)로는 본 결과 0.73–0.77 이 acceptable 구간에 든다.
   임상에서 쓰이는 예측 모델 중에도 0.70–0.80 대가 적지 않으므로
   "임계 미달" 이라고 단정할 근거는 없다.

   다만 본 결과를 진단 성능으로 읽어서는 안 되는 이유는 따로 있다.
   WGD 는 유병률이 65.2% 여서 **모두 WGD+ 로 예측만 해도 정확도 65.2%**
   가 나오며, 모델의 balanced accuracy 는 0.715 로 그 위 이득이 크지 않다.
   또한 Brier 가 0.204–0.217 로 확률 예측의 보정이 좋지 않아, 위험 층화
   용도로 쓰기에도 부적합하다. **AUC 가 아니라 유병률 대비 이득과 보정이
   본 결과의 실질적 제약이다.**

   애초에 본 연구의 질문은 임상 도구 개발이 아니라 "DNA 변이만으로
   예측 가능한가" 이므로, 비교 기준은 임상 임계가 아니라 (a) 유병률
   기저선, (b) CNV/ploidy 등 제외한 모달리티를 넣었을 때의 상승폭,
   (c) CIN/LOH 중앙값 이진화가 버린 정보량이 만드는 상한이어야 한다.
2. **패널 안정성이 기준 미달이다.** README §18 의 네 기준 중 '안정성' 을
   충족하지 못했으므로 단일 고정 패널을 주장하지 않았다.
3. **암종별 성능 편차의 원인을 좁혔지만 규명하지는 못했다.** LOLO
   성능은 암종에 따라 0.314\~0.882 로 갈렸다. 시도한 다섯 가지 단변량
   가설(기저율 편차, 표본 크기, TP53 변이율, mutation burden, TP53
   변이율의 극단성) 모두 유의한 상관을 보이지 않았다(|rho| 최대 0.216,
   모두 p>0.3). 암종 내부 학습 분석으로 '전이 실패' 가설도 배제했다
   (내부 학습이 LOLO 를 앞서지 못함). 즉 **단순한 단변량 교란변수로는
   설명되지 않는다는 것은 상당히 확실해졌지만, 왜 어떤 암종에는 신호가
   있고 어떤 암종에는 없는지는 여전히 규명하지 못했다.** lineage 가
   24개뿐이라 통계적 검정력 자체가 낮고(|rho|>0.4 는 되어야 유의), 암종
   내부 학습 분석도 세포주가 60\~226 개로 작아 fold 간 표준편차 중앙값이
   0.123 에 달했으므로, 소폭의 차이는 애초에 잡음과 구분되지 않는다.
4. **multi-task ANN 의 탐색이 얕다.** torch 없이 sklearn MLPClassifier 로
   구현해 구조·정규화 탐색 폭이 좁았다. RQ4 의 부정적 결과는 이 한계 안에서
   해석해야 한다.
5. ~~Day 12 패널 분석은 Elastic Net 기준이다.~~ **[해소] Random Forest 로
   재검증 완료.** 방향은 같고 안정성은 오히려 RF 가 더 좋다 — 아래 참조.
6. **CIN 을 Elastic Net 으로 볼 때는 이진화 손실이 있다.** 회귀로
   재검증한 결과 RF/CIN, RF/LOH, EN/LOH 세 조합은 이진화 손실이
   거의 없었지만(±0.02), EN/CIN 만 회귀 rho 가 분류(환산)보다
   +0.091 높았다. §26③·④ 의 CIN 관련 feature selection·패널 결과
   (모두 Elastic Net 기준)는 이 손실을 어느 정도 안고 있을 수 있다 —
   "CIN 이진화로 정보를 버렸는가" 절 참조.

---

## Day 11/12 Random Forest 재검증

한계 5번을 직접 확인했다. 성능 1위 모델(Random Forest, §26②)로 feature
selection(Day 11)과 패널 곡선(Day 12)을 다시 돌려 Elastic Net 결과와
비교했다.

### 패널 성능 — 방향은 동일

| | WGD 전체→10개 | CIN 전체→10개 | LOH 전체→10개 |
| --- | --- | --- | --- |
| Elastic Net | 0.749→0.727 (97.1%) | 0.681→0.674 (99.0%) | 0.711→0.669 (94.1%) |
| Random Forest | 0.765→0.729 (95.3%) | 0.734→0.682 (92.9%) | 0.730→0.687 (94.1%) |

두 모델 모두 "10개로 93\~99% 유지"라는 §26④ 결론을 그대로 지지한다.
모델을 바꿔도 최소 패널의 성능 유지율 자체는 바뀌지 않는다.

### 패널 안정성 — RF 가 더 안정적이다 (예상 밖 발견)

10개 패널의 fold 간 Jaccard 유사도:

| | WGD | CIN | LOH |
| --- | ---: | ---: | ---: |
| Elastic Net | 0.410 | 0.332 | 0.295 |
| **Random Forest** | **0.607** | **0.520** | **0.544** |

세 표현형 모두 RF 가 크게 앞선다. 즉 §26④ 에서 지적한 "패널 구성이
fold 마다 달라진다"는 문제는 **mutation 신호 자체의 한계라기보다 Elastic
Net 의 L1 선택 절차가 상대적으로 불안정한 것에 가깝다.** RF 의
impurity-based importance 가 resampling 에 덜 민감하기 때문으로 보인다.
따라서 §26④ 의 "안정성 기준 미달" 평가는 **모델을 Random Forest 로
바꾸면 상당 부분 완화된다** — 다만 여전히 1.0(완전 일치)에는 못 미친다.

#### 왜 1.0 이 안 되는가

Jaccard 0.61(WGD)은 절대 수치로 보면 낮아 보이지만, 실제로는 **fold
두 개를 비교하면 10개 중 평균 7.5개가 겹친다**는 뜻이다(EN 은 5.8개).
"패널이 완전히 다르다"가 아니라 "핵심은 고정되고 가장자리 2\~3자리만
흔들린다"에 가깝다.

| | WGD | CIN | LOH |
| --- | ---: | ---: | ---: |
| Elastic Net (10개 중 평균 겹침) | 5.8 | 4.9 | 4.5 |
| Random Forest (10개 중 평균 겹침) | 7.5 | 6.8 | 7.0 |

완전한 1.0 이 안 되는 데는 두 가지 구조적 이유가 있다.

**① importance 가 상위 소수에만 집중되고 나머지는 완만한 꼬리를 이룬다.**
RF 의 WGD importance 를 순위별로 보면:

| 순위 | 유전자 | 평균 importance | 순위 표준편차 |
| --- | --- | ---: | ---: |
| 1 | `TP53`(damaging) | 0.153 | 0.0 |
| 2 | `TP53`(hotspot) | 0.094 | 0.0 |
| 3–4 | `TERT`, `BRAF` | 0.028–0.032 | 0.55 |
| 6 | `ID3` | 0.016 | 1.41 |
| 8–10 | `LRP1B`, `TTN`, `KRAS`, `CREBBP` | 0.009–0.013 | 3–5 |

1·2 위(TP53 hotspot/damaging)는 importance 가 압도적으로 커서 순위
표준편차가 0 — 매 fold 예외 없이 1·2 위다. 그러나 6 위쯤부터는 값이
0.009\~0.016 사이에 촘촘히 몰리고 순위 표준편차도 3\~5 로 커진다. 이런
완만한 꼬리 구조에서는 top-10 의 경계선 유전자들이 데이터가 조금만
달라져도 순위가 뒤집힌다.

**② outer 5-fold 라서 fold 간 training data 자체가 75% 만 겹친다.**
전체 1,631 개 중 test 가 약 326 개씩이므로, 서로 다른 두 outer fold 의
training set 은 979/1,305 ≈ **75%** 만 공유한다. 나머지 25% 가 다른
세포주로 채워지는데, mutation 자체가 희소해서(필터 통과 후 feature
상당수가 10\~30 개 세포주에서만 관측, §Day4 EDA) 이 25% 차이가 경계선
유전자의 순위를 흔들기에 충분하다.

**즉 0.61 은 "핵심 3\~4개는 완전히 고정, 나머지 6\~7자리는 구조적으로
흔들릴 수밖에 없는 조건에서 나온 사실상의 상한에 가까운 값"이다.**
fold 간 데이터 중복률을 인위적으로 높이거나(fold 수를 늘려 leave-one-out
에 가깝게) mutation 자체가 덜 희소해야 더 오를 여지가 있는데, 둘 다 본
데이터셋의 근본 제약이지 모델 선택으로 해결될 문제가 아니다. 고정 패널
대신 합의 유전자를 제시하는 §26④ 의 판단이 이 관찰과 일치한다.

재현: `python scripts/14_panel_stability_explain.py --model random_forest`

### 모델 간 합의 유전자 — 진짜 consensus panel

fold 뿐 아니라 **모델까지 넘어** 두 방법 모두에서 평균 선택빈도 0.6 이상인
유전자:

| 유전자 | Elastic Net | Random Forest |
| --- | ---: | ---: |
| `TP53`(damaging) | 1.00 | 1.00 |
| `ID3`(damaging) | 1.00 | 1.00 |
| `BRAF`(hotspot) | 1.00 | 1.00 |
| `CREBBP`(damaging) | 0.93 | 1.00 |
| `RB1`(damaging) | 0.80 | 1.00 |
| `TP53`(hotspot) | 0.60 | 1.00 |
| `PITX1`(damaging) | 0.67 | 0.93 |
| `TERT`(hotspot) | 0.67 | 0.87 |

이 8개는 fold 도, 모델도 넘어 반복적으로 뽑히는 유전자다. §26③·§27 의
"핵심 축"(TP53/ID3/BRAF/CREBBP)이 여기서도 상위권을 유지하며, RB1·
TP53(hotspot)·PITX1·TERT 가 모델 간 합의로 새로 추가된다. **candidate
minimal panel 을 제시할 때 이 8개를 최우선으로 삼는 것이 Elastic Net
단일 모델 기준보다 근거가 강하다.**

재현: `python scripts/07_aggregate_selection.py --model random_forest`,
`python scripts/08_panel_curve.py --model random_forest`. Figure 4/5 는
이제 모델명이 파일명에 들어간다
(`fig4_selection_stability_{model}.png`, `fig5_panel_curve_{model}.png`).

---

## 암종별 성능 편차 — 무엇을 시도했고 어디서 멈췄는가

"보완해야 할 점" 4번(암종에 따라 예측 성능 차이가 큼, 유효한 mutation
패턴이 존재하는 암종을 확인 필요)에 대한 실험 결과를 모은다. §26⑤ 의
진단·후속 실험(암종 내부 학습)·가설 검정을 한곳에 정리한 것으로, 각
실험의 원 출처는 §26⑤ 와 `lineage_specific_models.md` 를 참고한다.

### 1단계 — 편차가 실재한다는 진단

lineage 를 분리해 검증하면 성능이 떨어진다 (random 5×5 CV 대비
GroupKFold 는 −0.046\~−0.069, §26⑤). Leave-One-Lineage-Out(LOLO,
24종)에서는 암종별 ROC-AUC 가 0.314\~0.882 로 매우 크게 갈린다 — WGD
기준 3종, CIN 기준 6종이 무작위 수준(0.5) 미만이다.

**Random Forest 로도 같은 진단이 나온다.** GroupKFold 감소폭은 WGD
−0.065, CIN −0.056, LOH −0.047 로 Elastic Net(−0.062/−0.046/−0.069)과
방향·크기가 비슷하다. RF 의 LOLO 최저 암종도 겹친다 — Eye(WGD 0.188,
LOH 0.129), Lung(WGD 0.443), Pancreas(WGD 0.437) 로 Elastic Net 이
지목한 Eye·Lung·Cervix·Pancreas 와 대체로 일치한다. 즉 편차 자체는
모델을 가리지 않는 현상이다.

### 2단계 — "해당 암종만으로 다시 학습해도 개선 안 됨" 확인

세포주 60개 이상 9종에서 그 암종 데이터만으로 학습·평가한 결과(암종
내부 학습), LOLO 를 앞서지 못했다(평균 차이 WGD −0.046, CIN +0.011,
LOH −0.018 — CIN/LOH 는 LOLO 와 동일 label 정의로 맞춤). Lung 의 WGD 는
LOLO 0.449, 내부 학습 0.494 로 **둘 다 무작위 수준**이다. 즉 "다른
암종으로 배워서 전이가 안 되는 것"이 아니라 **"그 암종 안에 애초에
mutation-only 로 학습 가능한 신호가 없는 것"** 에 가깝다는 뜻이다
(Figure 7, `lineage_specific_models.md`).

### 3단계 — 왜 어떤 암종엔 신호가 없는지, 다섯 가설 검정

"어떤 암종에서 mutation 패턴이 유효한가"를 직접 설명해 줄 후보 변수를
다섯 개 시험했다. WGD 기준으로는 전부 기각됐다(Figure 8, §26⑤).

| 가설 | Spearman rho | p |
| --- | ---: | ---: |
| WGD+ 기저율 편차 | +0.037 | 0.865 |
| 세포주 수 | +0.095 | 0.658 |
| TP53 변이율 | +0.148 | 0.491 |
| 세포주당 평균 mutation burden | −0.201 | 0.347 |
| TP53 변이율의 극단성 | +0.216 | 0.311 |

Fibroblast(TP53 변이율 10%, AUC 0.85)와 Thyroid(70%, AUC 0.88)가 거의
반대되는 TP53 변이율에서 똑같이 높은 성능을 보이는 것처럼, 어느 변수를
기준으로 봐도 성공/실패 사례가 뒤섞여 나타난다(Figure 8).

**Random Forest, 그리고 CIN·LOH 까지 넓혀 총 6개 조합(2모델×3표현형)
으로 재검정했다.** ③④⑤ 세 가설의 Spearman rho(p):

| 가설 | EN/WGD | EN/CIN | EN/LOH | RF/WGD | RF/CIN | RF/LOH |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| TP53 변이율 | +0.148 (.491) | −0.201 (.347) | +0.177 (.407) | +0.249 (.241) | +0.014 (.949) | +0.107 (.619) |
| mutation burden | −0.201 (.347) | +0.143 (.504) | +0.390 (.059) | −0.024 (.910) | +0.190 (.375) | **+0.416 (.043)** |
| TP53 변이율 극단성 | +0.216 (.311) | +0.324 (.123) | +0.258 (.223) | +0.289 (.171) | +0.301 (.153) | **+0.406 (.049)** |

18번 검정 중 16번은 기존과 같이 기각이다. 굵게 표시한 RF/LOH 의 두
항목만 raw p<0.05 다. **다만 이걸 "발견"으로 읽으면 안 된다.** 이
표만으로 18번, Figure 8 재현까지 포함하면 30번 가까운 검정을 했고
Bonferroni 보정 기준(α=0.05/30≈0.0017)에는 두 값 다 한참 못 미친다.
α=0.05 에서 30번 검정하면 우연히 1\~2 번은 p<0.05 가 나오는 게
정상이므로, 이 결과는 그 기대치 안에 있다.

다만 완전히 무시하기도 애매한 구석이 있다. mutation burden 가설은
LOH 에서 EN(+0.390, p=.059)과 RF(+0.416, p=.043)가 **같은 방향, 비슷한
크기로 나온다** — 다른 조합들처럼 모델 바꾸면 부호까지 흔들리는 것과는
다르다. 이게 진짜 신호인지, 아니면 LOH 라벨이 median split 이라 CIN
보다 클래스 균형이 더 타이트해서 생기는 통계적 우연인지는 지금 데이터
(lineage 24개)로 구분할 수 없다. **결론을 바꾸지 않되, LOH 의 mutation
burden 관련성은 추가 확인이 필요한 약한 신호로 따로 기록해 둔다.**

Figure 8 은 6개 조합 전부 저장했다
(`fig8_lineage_hypotheses_{elastic_net,random_forest}_{wgd,cin,loh}.png`).


### 결론 — 원인 규명은 못 했지만 범위는 좁혔다

**"어떤 암종에서 mutation 패턴이 유효한지"는 예측할 수 없다는 것이
현재까지의 결론이다.** 단순 단변량 교란변수(기저율, 표본 크기, 가장
중요한 유전자의 변이율과 그 극단성, 전체 mutation burden) 로는 설명되지
않는다는 점은 상당히 확실해졌으나, 진짜 원인은 규명하지 못했다. lineage
가 24종뿐이라 통계적 검정력 자체가 낮고(|rho|>0.4 는 되어야 유의),
암종 내부 학습도 세포주가 60\~226 개로 작아 fold 간 표준편차 중앙값이
0.123 에 달해 소폭의 차이는 잡음과 구분되지 않는다. 이 이상의 규명은
더 많은 세포주 확보나 lineage 특이적 상호작용을 볼 수 있는 다른 종류의
분석이 필요하며, 본 연구의 데이터 범위 안에서는 답하기 어렵다.

재현: `python scripts/09_lineage_validation.py --model {elastic_net,random_forest}`,
`python scripts/11_lineage_specific.py`,
`python scripts/15_lineage_hypothesis_test.py --model {elastic_net,random_forest} --target {wgd,cin,loh}`,
`python scripts/16_plot_lineage_hypotheses.py --model {elastic_net,random_forest} --target {wgd,cin,loh}`.

---

## CIN/LOH 이진화가 정보를 버리는가 — 회귀로 직접 검증

"보완해야 할 점" 5번(CIN/LOH 를 high/low 로 나누면서 정보가 손실됨,
회귀로 실제 연속값을 예측해 분류 결과와 비교 필요)에 대한 실험이다.

### 무엇을 했는가

같은 mutation feature 로 CIN·LoHFraction 의 **연속값을 직접 회귀
예측**했다(Elastic Net regression, Random Forest regressor — 기존
분류 모델과 계열을 맞춤). Pipeline 구조(희귀 변이 필터, outer 5-fold)는
분류와 동일하게 유지했다. 다만 지금까지의 lineage 실험과 달리 random
split 만 썼다 — 이진화 손실 여부를 확인하는 것이 목적이라 검증 방식을
동시에 바꾸지 않았다.

### 결과

| 표현형 | 모델 | 분류 ROC-AUC | 회귀 R² | 회귀 Spearman rho |
| --- | --- | ---: | ---: | ---: |
| CIN | Elastic Net | 0.681 | 0.227 | 0.453 |
| CIN | Random Forest | 0.734 | 0.267 | 0.488 |
| LoHFraction | Elastic Net | 0.711 | 0.155 | 0.431 |
| LoHFraction | Random Forest | 0.730 | 0.170 | 0.451 |

ROC-AUC 와 Spearman rho 는 척도가 달라 직접 등치할 수 없다. 방향을
가늠하기 위해 AUC 를 `2×(AUC-0.5)` 로 rho 와 같은 0\~1 스케일에
**근사 환산**해서 비교했다(엄밀한 통계적 등가는 아니다, Figure 9).

| 표현형 | 모델 | 분류(환산) | 회귀 rho | 차이 |
| --- | --- | ---: | ---: | ---: |
| CIN | Elastic Net | 0.362 | 0.453 | **+0.091** |
| CIN | Random Forest | 0.468 | 0.488 | +0.020 |
| LoHFraction | Elastic Net | 0.422 | 0.431 | +0.009 |
| LoHFraction | Random Forest | 0.460 | 0.451 | −0.009 |

### 해석

**세 조합은 거의 차이가 없고(±0.02), CIN + Elastic Net 한 조합만
회귀가 뚜렷이 높다(+0.091).** 즉:

* Random Forest 는 CIN·LOH 어느 쪽에서도 이진화로 정보를 거의
  잃지 않는다 — 비선형 모델이 중앙값 근처의 애매한 경계를 이미 어느
  정도 잘 처리하고 있었다는 뜻으로 읽을 수 있다.
* LoHFraction 은 모델과 무관하게 이진화 손실이 거의 없다.
* **CIN 을 선형 모델(Elastic Net)로 볼 때만 이진화가 신호를 깎아
  먹는다.** CIN 분포가 이봉형(Figure 2)이라는 점과 맞물려 볼 수 있다
  — 중앙값 근처에 세포주가 상대적으로 적어 median split 자체는
  덜 위험하지만, 선형 모델이 그 비선형적인 분포 형태를 이진화 이후에는
  더 못 살리는 것으로 보인다.

**결론을 바꾸지는 않는다.** §26①의 "제한적으로 가능하다"는 판단은
회귀로 봐도 유지된다(R² 0.15\~0.27 은 여전히 중간 정도의 설명력이다).
다만 **Elastic Net 기반 CIN 패널(§26③·④)은 이진화 손실을 어느 정도
안고 있을 수 있다**는 점을 한계로 추가한다 — 향후 회귀 기반 feature
selection 으로 CIN 패널을 다시 뽑아보는 것이 자연스러운 후속 과제다.

Figure 9(`fig9_regression_vs_classification.png`)에 네 조합을 나란히
그렸다.

재현: `python scripts/17_regression_vs_classification.py`,
`python scripts/18_plot_regression_vs_classification.py`.

---

## Related Work

본 연구와 정확히 같은 과제 — **DepMap mutation-only 로 WGD/CIN/LOH 를
예측** — 를 다룬 선행 연구나 Kaggle 챌린지는 찾지 못했다. 대신 인접한
연구들을 참고로 남긴다.

* **[Whole-genome doubling confers unique genetic vulnerabilities on tumour cells (Nature, 2021)](https://www.nature.com/articles/s41586-020-03133-3)**
  \~10,000개 종양 샘플과 \~600개 세포주의 essentiality 데이터로 WGD 가
  만드는 공통 유전적 특징과 취약점을 분석. WGD 상태 자체는 copy number
  데이터로 확정하고 그 이후 결과를 분석하는 연구라, 본 연구처럼 "mutation
  만으로 WGD 를 예측할 수 있는가" 를 묻지는 않는다.
  **알고리즘 / 점수**: 예측 모델이 아니다 — CRISPR essentiality 스크린으로
  WGD+ 대 WGD− 세포주 간 유전자 의존도 차이를 통계적으로 비교하는
  연구라 algorithm·AUC 개념 자체가 해당하지 않는다.

* **[MEDICC2: whole-genome doubling aware copy-number phylogenies (Genome Biology, 2022)](https://genomebiology.biomedcentral.com/articles/10.1186/s13059-022-02794-9)**
  Haplotype-specific copy-number 데이터로 종양의 진화 계통수와 WGD 시점을
  추론하는 방법론. copy number 를 직접 입력으로 쓰므로 WGD 와 사실상
  같은 정보를 보는 것에 가깝다 — 본 연구가 CNV/ploidy 를 §7 에서 의도적으로
  제외한 이유(순환논리·정답 누출)와 맞닿아 있다.
  **알고리즘 / 점수**: Minimum-Event Distance(MED) 기반 동적계획법으로
  WGD-aware phylogeny 를 추론. 분류 모델이 아니라 AUC 는 없으나,
  2,778개 종양에서 WGD 검출 정확도 **98.8%** 를 보고했다 — copy number 를
  직접 쓰면 거의 정답에 가까운 정확도가 나온다는 뜻이며, 이는 mutation-only
  로 정면돌파하는 본 연구와의 난이도 격차를 보여준다.

* **[An original aneuploidy-related gene model for predicting lung adenocarcinoma survival (Scientific Reports, 2024)](https://www.nature.com/articles/s41598-024-58020-y)**
  Aneuploidy 관련 유전자의 **발현량**으로 위험 점수를 만들어 생존을 예측.
  본 연구와 입력 모달리티(발현 vs mutation 유무)와 과제(생존 예측 vs 직접
  표현형 분류)가 다르지만, **정보가 더 풍부한 입력(연속형 발현량)을 쓰고도
  비슷한 구간에서 막힌다는 점**은 본 연구의 mutation-only 결과가 유사한
  상한 근처에 있다는 정황 근거가 된다.
  **알고리즘 / 점수**: LASSO Cox regression 으로 후보 유전자를 추리고
  stepwise multivariate Cox regression 으로 6-gene risk score(ARS)를
  구성. GEO 외부 검증 코호트(GSE41613)에서 1년/3년/5년 생존 예측
  time-dependent AUC **0.70 / 0.81 / 0.77**, TCGA 학습 코호트에서는
  전 시점 AUC > 0.6 으로 보고.

* **[MSI, Ploidy & Mutational Burden — DepMap Sanger 문서](https://depmap.sanger.ac.uk/documentation/cell-models/msi-ploidy-mutational-burden/)**
  DepMap 세포주의 MSI·ploidy·TMB 데이터 설명 문서. 직접적인 예측 연구는
  아니지만, 본 연구가 §7 에서 제외한 지표들의 정의와 배포처를 확인하는
  데 참고했다.
  **알고리즘 / 점수**: 해당 없음 — 데이터 정의 문서.

### 이 검색에서 얻은 것

명시적인 "mutation-only → 유전체 불안정성" 벤치마크는 없었지만, 두 가지
정황은 확인했다.

1. **입력 정보량과 성능이 정직하게 비례한다.** copy number 를 직접 쓰는
   MEDICC2 는 WGD 검출 정확도 98.8% 로 사실상 정답에 가깝고, 연속형
   발현량을 쓰는 aneuploidy risk model 은 AUC 0.70\~0.81, mutation
   유무(0/1)만 쓰는 본 연구는 ROC-AUC 0.73\~0.77 이다. 입력이 풍부해질수록
   성능이 올라가는 자연스러운 흐름이며, 본 연구의 결과가 mutation-only
   라는 제약 안에서 특별히 낮은 편은 아니라는 뜻이다.
2. 선행 연구들은 개별 유전자 컬럼이 아니라 **더 뭉뚱그린 단위**를 입력으로
   쓰는 경우가 많다. 이는 알고리즘을 바꾸는 것도, 새 데이터원(CNV·발현 등)을
   추가하는 것도 아니다 — **같은 mutation 정보를 사람이 아는 생물학적
   그룹으로 미리 재집계**하는 feature engineering 이다. 본 연구가
   §26②·Figure 3 에서 확인한 "모델을 바꿔도 같은 신호만 본다"(RF/XGBoost/
   CatBoost feature importance 상관 0.56\~0.61)는 결과와 상충하지 않는다 —
   모델이 아니라 입력의 재집계 단위를 바꾸는 시도이기 때문이다.

   구체적으로는 두 방향이 있는데 실행 가능성이 다르다.
   * **Pathway 단위 mutation burden** — 지금 가진 이진 행렬(유전자×세포주)
     그대로, 외부 gene-set 주석(예: MSigDB, DNA repair/cell cycle
     카테고리)만 있으면 바로 만들 수 있다. 20,132 개 유전자를 수십 개
     pathway 로 묶어 sparsity 를 줄이는 방식이며 새 데이터 다운로드가
     필요 없다.
   * **Mutation signature(trinucleotide context)** — 애초에 실행 불가능한
     것으로 정정한다. 본 연구가 받은 `OmicsSomaticMutationsMatrix{Hotspot,
     Damaging}.csv` 는 이미 유전자×세포주 이진 행렬로 집계된 파일이라
     염색체·위치·염기(Chrom/Pos/Ref/Alt) 정보가 사라져 있다. trinucleotide
     context 를 계산하려면 DepMap 이 별도로 배포하는 원시 MAF 파일
     (`OmicsSomaticMutations.csv`, `OmicsSomaticMutationsMAF.maf`)을 추가로
     받아야 하며, 이는 지금 파이프라인에 바로 끼워 넣을 수 있는 재집계가
     아니라 **별도 데이터 확보가 선행되어야 하는 확장 과제**다.

---

## Future Work

Related Work 절에서 확인한 두 방향을 실행 가능성 순으로 정리한다.

### 1. ~~Pathway 단위 mutation burden~~ **[실행 완료 — 음성 결과]**

**무엇을**: 20,132 개 유전자 컬럼을 MSigDB Hallmark 또는 KEGG 의 생물학적
경로(DNA damage repair, cell cycle checkpoint, chromatin remodeling 등)로
묶어, "이 세포주가 이 경로 유전자 중 몇 개에 damaging/hotspot mutation 을
가졌는가" 를 새 feature 로 만든다.

**왜 유효한가**: 지금 가진 데이터(`cohort.X`)만으로 되는 재집계다. gene-set
주석은 표현형과 무관한 정적 메타데이터라 새로 받아도 §13 누출 위험이 없다.
sparsity 문제(hotspot 554개 중 10개 이상 세포주에서 관측되는 건 36개뿐)를
정면으로 줄이는 접근이라, 지금까지 모델을 5개나 바꿔도 0.73\~0.77 에서
움직이지 않은 천장(§26②, RF/XGBoost/CatBoost feature importance 상관
0.56\~0.61)을 뚫을 실질적 후보다.

**절차**:
1. MSigDB(C2 curated 또는 Hallmark) 에서 DNA repair·cell cycle·chromatin
   관련 gene set 목록을 받는다.
2. `src/features/` 에 `pathway_aggregate.py` 를 추가해 유전자 컬럼을
   pathway 컬럼으로 접는 transformer 를 만든다 (`RareMutationFilter` 와
   같은 자리, Pipeline 안에 넣어 fold 마다 일관되게 적용).
3. 기존 `05_run_cv.py` 파이프라인을 그대로 재사용해 pathway 표현과
   유전자 표현의 성능을 같은 nested CV 조건에서 비교한다.

**예상 소요**: 반나절 내외 — 기존 인프라(nested CV, 모델, 평가)를 그대로
쓰고 feature 변환 단계만 추가하면 된다.

**실행 결과**: MSigDB Hallmark 5개(DNA Repair, G2-M Checkpoint, E2F
Targets, Mitotic Spindle, p53 Pathway) + KEGG 6개(DNA repair 세부 경로:
BER/MMR/NER/HR/NHEJ/Fanconi anemia) — Enrichr 공개 미러에서 gene-set
목록을 받아 hotspot/damaging 분리 시 22개 feature 로 접었다(대부분
90%+ 매칭). 유전자 단위(필터 후 \~2,062개)와 같은 random 5-fold 조건에서
비교했다(Figure 10).

| 표현형 | 모델 | 유전자 단위 | Pathway(22개) | 차이 |
| --- | --- | ---: | ---: | ---: |
| WGD | Logistic | 0.723 | 0.674 | -0.049 |
| CIN | Logistic | 0.672 | 0.643 | -0.029 |
| LOH | Logistic | 0.683 | 0.648 | -0.035 |
| WGD | Random Forest | 0.765 | 0.720 | -0.045 |
| CIN | Random Forest | 0.734 | 0.691 | -0.043 |
| LOH | Random Forest | 0.730 | 0.702 | -0.028 |

**6개 조합 전부 pathway 쪽이 낮다(-0.028\~-0.049).** "sparsity 를 줄이면
천장을 뚫는다"는 가설은 기각됐다. 원인은 짐작대로다 — TP53 이 유전자
단위에서 압도적 1위 신호였는데(§26③), pathway 로 묶으면 "TP53 이 속한
DNA Repair 경로 안 mutation 비율"이 되어 나머지 100여 개 약한 신호
유전자와 평균 내지듯 희석된다. **정보 손실이 sparsity 완화 이득보다
컸다.** 이 결과는 오히려 "핵심 신호가 소수의 특정 유전자에 집중되어
있다"는 §26③·④의 기존 결론을 다른 각도에서 재확인해 준다.

재현: `python scripts/19_pathway_representation.py`,
`python scripts/20_plot_pathway_vs_gene.py`.

### 2. Mutation signature — 원시 MAF 파일 확보 (확장 과제)

**무엇을**: DepMap 이 별도로 배포하는 `OmicsSomaticMutations.csv`
(MAF-like, `Chrom`/`Pos`/`Ref`/`Alt` 컬럼 포함) 또는
`OmicsSomaticMutationsMAF.maf` 를 받아 trinucleotide context 를 계산하고,
COSMIC SBS mutational signature exposure 를 세포주별 feature 로 쓴다.

**왜 다른 과제로 분리했는가**: 지금 가진 `OmicsSomaticMutationsMatrix
{Hotspot,Damaging}.csv` 는 이미 유전자×세포주 이진 행렬로 집계되어 위치·
염기 정보가 사라진 상태라, 이 접근은 기존 파이프라인에 재집계 단계 하나를
추가하는 정도로 끝나지 않는다 — **원시 파일을 새로 받고, 대용량 MAF 파싱과
signature 추출(예: `SigProfilerExtractor`, `deconstructSigs`) 을 별도로
구축**해야 한다.

**절차**:
1. `OmicsSomaticMutations.csv` 다운로드 (용량이 커서 `data/depmap/README.md`
   에 안내만 추가하고 git 추적은 하지 않는다 — 기존 데이터 관리 방식과 동일).
2. 세포주별로 SBS signature exposure 를 계산해 새 feature 행렬을 만든다.
3. 1번(pathway)과 마찬가지로 기존 nested CV 파이프라인에 대체 입력으로
   붙여 성능을 비교한다.

**예상 소요**: 1번보다 크다 — 대용량 파일 처리와 signature 추출 도구 도입이
새로 필요하다. **1번(pathway)을 먼저 시도해 sparsity 완화만으로 천장이
뚫리는지 확인한 뒤, 뚫리지 않을 경우에 착수하는 순서를 권장한다.**

### 3. 독립 코호트 검증 — 한계 6번(§26⑤, "이 결론의 한계") 후속

**무엇을**: DepMap 세포주 내부 cross-validation 만으로는 "확정적인
바이오마커"라 부를 수 없다는 지적(README §27)에 대해, 외부 데이터로
재현성을 확인한다. 실행 가능성 순으로 세 옵션이 있다.

**① DepMap 다른 릴리스 — 가장 쉬움, 다만 진짜 독립은 아님.** 지금 쓰는
26Q1 대신 더 오래되거나 최신인 릴리스를 하나 더 받는다. 파일 형식이
완전히 동일해 `configs/data.yaml` 의 `data_root` 만 바꾸면 되고, 코드
수정이 거의 없다. 릴리스 사이에 새로 추가된 세포주로 지금 모델을
평가하면 "시간적으로 미래 데이터에도 통하는가"를 볼 수 있다. 다만
같은 파이프라인·상당수 겹치는 세포주라 진짜 독립 코호트는 아니다.

**② TCGA — 진짜 독립 코호트, 작업량 있음.** 세포주가 아니라 환자
종양 조직이라 도메인이 다르지만, 그래서 오히려 "진짜" 독립 검증이
된다.

* **Mutation**: [GDC MC3 MAF](https://gdc.cancer.gov/about-data/publications/mc3-2017)
  또는 [cBioPortal](https://www.cbioportal.org) 에서 study 별 MAF 를
  받는다. 유전자 심볼(HUGO)이 같아 hotspot/damaging 매핑이 비교적
  수월하다.
* **WGD/ploidy 라벨**: PanCanAtlas 의 ABSOLUTE 알고리즘 결과
  ([Taylor et al. 2018, Cancer Cell](https://www.sciencedirect.com/science/article/pii/S1535610818301119))
  가 ploidy·WGD count·purity 를 이미 계산해 supplementary table 로
  공개돼 있다. CIN·LOH 에 대응하는 지표(aneuploidy score, LOH
  fraction)도 같은 논문 계열에 있다.
* **작업량**: (a) MAF 를 지금 쓰는 hotspot/damaging 이진 행렬 형식으로
  재가공, (b) TCGA barcode ↔ WGD 라벨 매핑, (c) §9.2/§9.3 의 필터링
  기준을 TCGA 에 맞게 재검토. 반나절\~하루 정도 코드 작업.
* **장점**: 세포주(in vitro)에서 학습한 것이 실제 환자 종양(in vivo)
  에도 통하는지 보이면 결론의 설득력이 크게 올라간다. TCGA 는 lineage
  (암종)가 훨씬 다양해 "암종별 성능 편차" 절(§26⑤)도 더 넓은 범위에서
  재검증할 수 있다.

**③ Sanger Cell Model Passports / GDSC — 파이프라인 강건성 확인용.**
DepMap 과 겹치는 세포주를 **독자적인 mutation calling 파이프라인**으로
처리한 데이터다. 진짜 독립 코호트라기보다는 "같은 생물학적 샘플, 다른
처리 과정"이라 **우리 결과가 DepMap 특정 변이 콜링 방식에 과적합된 게
아닌지** 확인하는 용도에 가깝다. TCGA 만큼의 독립성은 없다.

**권장 순서**: 시간이 없으면 ①로 재현성만 빠르게 확인하고, 제대로
검증하려면 ②(TCGA)를 받는다. MC3 MAF 는 공개 API 로 승인 없이 바로
받을 수 있고 용량도 크지 않다(수백 MB). ③은 ①②를 먼저 마친 뒤
여유가 있을 때 시도한다.

#### 실행 결과 — ②(TCGA) WGD 외부 검증

`mc3.v0.2.8.PUBLIC.maf.gz`(753MB)와 ABSOLUTE ploidy/WGD 결과
(`TCGA_mastercalls.abs_tables_JSedit.fixed.txt`)를 받아 실행했다.
CIN/LOH 대응 지표(Taylor et al. 2018 supplementary table)는 페이월로
정확한 테이블 번호를 확인하지 못해 **WGD 만** 검증했다.

**barcode 매핑 함정**: ABSOLUTE 와 MC3 는 서로 다른 시퀀싱 플레이트/
센터에서 만들어져 전체 barcode 로 join 하면 10,642개 중 12개만
매칭된다. TCGA 데이터 종류 간 병합의 표준 관례대로 앞 15자(참가자+
샘플타입)로 잘라서 맞추면 91%(9,651\~10,261개)가 매칭된다.

**설계**: hotspot 에 대응하는 TCGA 데이터가 없어(큐레이션 hotspot DB
필요, §7 논의와 같은 이유) damaging feature 만으로 비교했다. DepMap 의
`LikelyLoF` 판정을 표준 truncating variant class(frameshift/nonsense/
splice site/start loss/stop loss)로 근사했다. 공통 유전자는 16,245개
(DepMap 19,578, TCGA 18,948 중 교집합).

| 단계 | ROC-AUC | n |
| --- | ---: | ---: |
| DepMap 내부(damaging-only, random 5-fold) | 0.762 | 1,631 |
| **TCGA 외부 검증**(DepMap 전체로 학습 → TCGA 예측) | **0.594** | 10,261 |

무작위 수준(0.5)은 넘지만 **내부 대비 크게 떨어진다(−0.168)**(Figure 11).

**다만 이 하락폭을 그대로 "일반화 실패"로 읽으면 안 된다.** TP53
damaging(근사) 비율이 DepMap 57.8% vs TCGA 12.4% 로 코호트 간 격차가
매우 크다. 원인을 추적해보니 **방법론적 문제였다** — TCGA MAF 에서
TP53 은 missense 변이가 2,927건으로 압도적인데, truncating-only 근사
기준은 이를 전혀 잡지 못하고 nonsense/frameshift/splice 계열 1,448건만
포착한다. TP53 은 우성음성(dominant-negative) 기전의 missense 돌연변이가
주된 불활성화 경로인 대표적 유전자라, 이 근사가 **가장 중요한 단일
유전자의 신호를 3분의 2 가까이 놓친 것**이다(Figure 11b).

**결론**: TCGA 외부 검증 ROC-AUC 0.594 는 실제 일반화 성능의 **하한
추정치에 가깝다** — 진짜 값은 이보다 높을 가능성이 크지만, missense
pathogenicity 를 제대로 반영하는 분류기(예: PolyPhen/SIFT/REVEL 점수
활용) 없이는 정확한 값을 알 수 없다. 그럼에도 **내부(0.762)와 완전히
같은 수준일 가능성은 낮다** — 세포주와 실제 종양은 순도(purity),
이질성(heterogeneity), 배양 조건에 따른 선택압이 다르므로 어느 정도의
일반화 격차는 예상된 결과다. "세포주에서 배운 신호가 실제 환자
종양에도 어느 정도(무작위보다는 뚜렷이 높게) 옮겨가지만 완전히
같지는 않다"가 현재 근거로 뒷받침되는 가장 정확한 서술이다.

재현: `python scripts/21_tcga_validation.py`,
`python scripts/22_plot_tcga_validation.py`. 원본 데이터는
`data/gdc/`(git 미추적, `data/depmap/` 과 같은 방식)에 둔다.
