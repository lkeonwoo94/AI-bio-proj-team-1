# 보완해야 할 점 (팀 리뷰, 2026-08-18)

Day 1\~13 결과물에 대해 팀에서 받은 리뷰 원문을 정리한다. 각 항목이
이후 어떻게 다뤄졌는지는 항목마다 대응 문서를 링크했다 — 이 문서
자체는 지적 사항만 기록하고 대응 내용은 고치지 않는다.

---

## 1. 최고 성능 모델과 바이오마커 선정 모델이 다름

* WGD/CIN/LOH 예측 성능은 **Random Forest** 가 가장 우수했으나,
  핵심 mutation 선정과 최소 패널 평가는 **Elastic Net** 을 기준으로
  수행함.
* → 따라서 현재 도출된 중요 mutation 과 최소 패널이 Random Forest 에서도
  동일하게 재현되는지 확인이 필요함.
* **Random Forest 기반 feature importance 및 5/10/20/50개 패널 성능을
  추가 검증하고 Elastic Net 결과와 비교** 해 보기.

| Figure | 분석 목적 | 사용 모델 |
| --- | --- | --- |
| Fig. 3 | 모델 성능 비교 → Random Forest 성능이 가장 높음 | Logistic, Elastic Net, RF, XGBoost, ANN |
| Fig. 4 | 반복적으로 선택되는 mutation 확인 | Elastic Net |
| Fig. 5 | 최소 mutation panel 평가 | Elastic Net |
| Fig. 6 | 암종을 나눴을 때 성능이 유지되는지 검증 | Elastic Net |
| Fig. 7 | 암종별로 따로 학습하면 성능이 좋아지는지 확인 | Random Forest |

Fig. 4\~6 은 Elastic Net 사용, Fig. 3·7 은 Random Forest 사용 — **Elastic
Net 을 사용한 이유는? Random Forest 기반으로 검증 필요.**

---

## 2. 정보 수정 필요 — Figure 4 그래프와 `docs/research/day1-13_results.md` 파일 내용 불일치

Figure 4 의 TP53, ID3, BRAF, CREBBP 가 세 표현형 모두에서 5/5 fold
반복 선택됨 →

> TP53 damaging, ID3 damaging, BRAF hotspot 은 WGD, CIN, LOH 세
> 표현형 모두에서 5/5 fold 반복 선택되었다. CREBBP damaging 은 WGD 와
> LOH 에서 5/5, CIN 에서는 4/5 fold 에서 선택되었다. 라고 수정하는게
> 맞는 것인지?

Figure 4 그래프와 텍스트 내용 중 무엇이 맞는지 검증 필요 — 텍스트에는
CREBBP 가 WGD·LOH → 1.0 이고, CIN → 0.8 로 나와 있음.

전 fold(5/5)에서 선택된 유전자:

* 세 표현형 공통: TP53(damaging), ID3, BRAF(hotspot), CREBBP
* WGD 특이: TERT(hotspot), NF2, CCND3, LRP1B, TGFBR2
* CIN 특이: RB1, PIK3CA(hotspot), SLFN11
* LOH 특이: NF2, PITX1, MUC19, ABCB5

(첨부 그래프: Figure 4. 반복 feature selection 안정성 — Elastic Net,
outer 5-fold, CIN 상위 15개 표시. CREBBP(damaging) 막대가 0.8 지점에서
끝나 있어 표에 적힌 "전 fold(5/5)" 서술과 불일치.)

---

## 3. 최소 mutation panel 의 구성이 안정적이지 않음

* 약 10개의 mutation 만으로 전체 모델 성능의 **94\~99%** 를 유지했으나,
  데이터 분할에 따라 선택되는 mutation 조합이 달라짐.
* 10개 패널의 fold 간 Jaccard 유사도는 WGD 0.41, CIN 0.33, LOH 0.30 으로
  낮은 편.
* **보완**: 여러 fold 와 모델에서 반복적으로 선택되는 mutation 을
  중심으로 consensus candidate panel 구성 필요.

---

## 4. 암종에 따라 예측 성능 차이가 큼

* Lineage 를 분리해 검증했을 때 성능이 감소했으며, Leave-One-Lineage-Out
  에서도 암종별 ROC-AUC 편차가 크게 나타남.
* 일부 암종은 해당 암종 데이터만으로 다시 학습해도 성능이 개선되지 않아,
  유전자 변이 정보만으로 WGD/CIN/LOH 를 구분하기 어려운 암종이 존재할
  가능성이 있음.
* **보완**: 암종별 성능 차이가 발생하는 원인을 추가 분석하고, 어떤
  암종에서 해당 mutation 패턴이 유효한지 확인 필요.

---

## 5. CIN 과 LOH 를 high/low 로 나누면서 정보가 일부 손실됨

* CIN 과 LOH 는 원래 연속형 값이지만 중앙값을 기준으로 high/low 로
  구분하여 분류 모델을 학습함.
* 중앙값 부근의 세포주는 실제 값이 비슷하더라도 서로 다른 그룹으로
  분류될 수 있음.
* **보완**: CIN 과 LOH 의 실제 연속값을 예측하는 회귀 분석을 추가하여
  현재 분류 결과와 비교.

---

## 6. 독립 데이터에서의 검증이 필요함

* 현재 결과는 DepMap 1,631개 세포주 내부의 cross-validation 결과임.
* 따라서 도출된 mutation 후보를 확정적인 바이오마커로 해석하기에는
  한계가 있음.
* **보완**: 독립적인 암세포주 데이터 또는 다른 코호트에서 재현성을
  확인하고, 향후 실험적 검증 필요.

---

## 대응 현황

| 항목 | 대응 문서 |
| --- | --- |
| 1. RF 기준 재검증 | [2026-08-16/final_conclusion.md — "Day 11/12 Random Forest 재검증"](../2026-08-16/final_conclusion.md#day-1112-random-forest-재검증) |
| 2. Figure 4 vs 텍스트 불일치 | [2026-08-16/final_conclusion.md §26③](../2026-08-16/final_conclusion.md) (CREBBP WGD·LOH 1.0 / CIN 0.8 로 수정 확인) |
| 3. 최소 패널 불안정 | [2026-08-16/final_conclusion.md §26④, "Day 11/12 RF 재검증"의 모델 간 합의 유전자](../2026-08-16/final_conclusion.md) |
| 4. 암종별 성능 편차 | [2026-08-19/additional_results.md §1](../2026-08-19/additional_results.md) |
| 5. CIN/LOH 이진화 손실 | [2026-08-19/additional_results.md §2](../2026-08-19/additional_results.md) |
| 6. 독립 코호트 검증 | [2026-08-19/additional_results.md §5 (TCGA)](../2026-08-19/additional_results.md) |
