# DepMap DNA 변이 기반 유전체 불안정성 예측 및 최소 Mutation Biomarker Panel 발굴

**영문 제목**
*Machine Learning–Based Prediction of Genomic Instability and Identification of a Candidate Minimal Mutation Biomarker Panel Using DepMap Data*

---

## 1. 프로젝트 핵심 주제

DepMap 암세포주의 **hotspot 및 damaging mutation 정보만을 이용하여 WGD, CIN, LOH와 같은 유전체 불안정성 상태를 예측**하고, 예측에 반복적으로 기여하는 변이를 선별하여 **적은 수의 유전자로 구성된 후보 mutation biomarker panel**을 도출한다.

핵심 질문은 다음 두 가지이다.

1. **DNA mutation만으로 WGD, CIN, LOH 상태를 예측할 수 있는가?**
2. **전체 mutation 정보를 사용하지 않고도 소수의 유전자만으로 예측 성능을 대부분 유지할 수 있는가?**

연구의 중심은 약물반응 분석이 아니라,

> **Mutation → WGD/CIN/LOH prediction → Important mutation selection → Minimal biomarker panel**

의 흐름으로 설정한다.

---

# 2. 연구 배경

암세포에서는 염색체 수와 구조가 불안정해지는 다양한 형태의 유전체 불안정성이 발생한다.

본 프로젝트에서는 그중 다음 세 가지 표현형을 분석한다.

### WGD: Whole Genome Doubling

암세포의 전체 유전체가 한 차례 이상 복제되어 염색체 세트가 증가한 상태이다.

### CIN: Chromosomal Instability

염색체가 지속적으로 잘못 분리되거나 구조적으로 변화하여 염색체 수와 구성이 불안정한 상태이다.

### LOH: Loss of Heterozygosity

한 유전자 좌위에서 존재하던 두 대립유전자 중 하나가 소실되어 유전적 다양성이 감소한 상태이다.

WGD, CIN, LOH는 서로 관련될 수 있지만 동일한 현상은 아니다.

따라서 하나의 통합된 ‘유전체 불안정성’ 점수로 합치기보다는,

* WGD
* CIN
* LOH

각각을 **별도의 예측 대상**으로 분석한다.

---

# 3. 연구 목적

본 연구의 목적은 크게 세 단계로 구성한다.

### 목적 1. Mutation으로 WGD/CIN/LOH 예측

DepMap의 hotspot 및 damaging mutation 정보를 입력값으로 사용하여 각 암세포주의

* WGD + / −
* CIN high / low
* LOH high / low

상태를 머신러닝으로 예측한다.

---

### 목적 2. WGD/CIN/LOH 예측에 중요한 mutation 발굴

머신러닝 모델에서 반복적으로 선택되는 mutation을 확인한다.

예를 들어 특정 유전자 변이가 여러 cross-validation fold에서 지속적으로 WGD 예측에 기여한다면 해당 유전자를 **WGD 관련 후보 mutation biomarker**로 볼 수 있다.

단, 단일 모델에서 중요도가 높게 나온 것만으로 후보를 선정하지 않는다.

다음 요소를 함께 평가한다.

* 반복 선택 빈도
* feature importance 또는 coefficient
* fold 간 순위 안정성
* 예측 성능 기여
* lineage가 달라져도 유지되는지 여부

---

### 목적 3. 최소 Mutation Biomarker Panel 도출

전체 mutation feature를 사용하는 모델과

* 5개
* 10개
* 20개
* 50개

mutation으로 구성한 축소 모델을 비교한다.

이를 통해

> **몇 개의 mutation만 사용해도 전체 mutation 모델의 예측력을 대부분 유지할 수 있는가?**

를 확인한다.

최종 결과는 임상 확정 진단 패널이 아니라,

**candidate minimal mutation biomarker panel**

로 제시한다.

---

# 4. 전체 연구 질문

## RQ1

### Hotspot/damaging mutation만으로 WGD를 예측할 수 있는가?

입력:

DNA mutation

출력:

WGD + / −

---

## RQ2

### Hotspot/damaging mutation만으로 CIN을 예측할 수 있는가?

입력:

DNA mutation

출력:

CIN high / low

---

## RQ3

### Hotspot/damaging mutation만으로 LOH를 예측할 수 있는가?

입력:

DNA mutation

출력:

LOH high / low

---

## RQ4

### WGD, CIN, LOH가 공유하는 mutation 신호가 존재하는가?

WGD, CIN, LOH를 각각 독립적으로 예측하는 모델과 함께 multi-task 모델을 비교한다.

세 표현형 사이에 공통되는 mutation pattern이 있다면 공유층을 사용하는 multi-task ANN이 이를 활용할 가능성이 있다.

단, ANN이 반드시 가장 높은 성능을 보여야 하는 것은 아니다.

---

## RQ5

### 어떤 mutation이 예측에 반복적으로 기여하는가?

Cross-validation 과정에서 반복적으로 선택되는 mutation을 확인한다.

단일 fold에서 한 번 선택된 유전자가 아니라 여러 학습 데이터 조합에서 안정적으로 선택되는 mutation을 우선한다.

---

## RQ6

### 몇 개의 mutation까지 줄여도 예측력이 유지되는가?

다음 모델을 비교한다.

> 전체 mutation
> ↓
> 50개
> ↓
> 20개
> ↓
> 10개
> ↓
> 5개

성능이 거의 감소하지 않는 가장 작은 크기를 **최소 패널 후보 크기**로 평가한다.

---

# 5. 연구 가설

### 가설 1

특정 hotspot 및 damaging mutation 조합에는 WGD, CIN, LOH 상태를 구분할 수 있는 정보가 포함되어 있을 것이다.

### 가설 2

WGD, CIN, LOH는 서로 다른 표현형이지만 일부 공통된 mutation pattern을 공유할 수 있다.

### 가설 3

전체 mutation 중 일부 유전자는 여러 fold에서 반복적으로 선택되며 예측에 상대적으로 큰 기여를 할 것이다.

### 가설 4

전체 mutation을 모두 사용하지 않고도 일부 핵심 mutation만으로 전체 모델 성능의 상당 부분을 유지할 수 있을 것이다.

가설은 검증 대상이며 결과를 미리 전제하지 않는다.

---

# 6. 필수 데이터

## 6.1 Mutation 데이터

### `OmicsSomaticMutationsMatrixHotspot.csv`

역할:

**Hotspot mutation feature**

각 세포주에서 특정 유전자에 hotspot mutation이 존재하는지를 나타내는 입력 데이터로 사용한다.

---

### `OmicsSomaticMutationsMatrixDamaging.csv`

역할:

**Damaging mutation feature**

단백질 기능에 영향을 줄 가능성이 있는 damaging mutation 정보를 입력 feature로 사용한다.

---

## 6.2 유전체 불안정성 데이터

### `OmicsGlobalSignatures.csv`

역할:

**WGD / CIN / LOH 정답 label 생성**

이 파일에서 실제 WGD, CIN, LOH 관련 column을 확인한다.

최종적으로 다음 label을 구성한다.

* WGD + / −
* CIN high / low
* LOH high / low

실제 column명, 값의 의미, 범위, 결측값 처리 방법은 다운로드한 데이터의 data dictionary에서 확인한다.

---

## 6.3 세포주 정보

### `Model.csv`

역할:

* ModelID 확인
* cancer lineage 확인
* mutation 데이터와 phenotype 데이터 연결

특히 lineage는 모델의 일반화 가능성을 평가하는 데 사용한다.

---

# 7. 사용하지 않는 데이터

최종 biomarker panel은 반드시 **mutation-only**로 평가한다.

따라서 다음 정보는 주 모델의 입력 feature로 사용하지 않는다.

### CNV

WGD, CIN과 직접적으로 연결될 가능성이 높아 정답 정보를 간접적으로 제공할 위험이 있다.

### Ploidy

WGD와 직접적으로 연관된 정보이므로 입력 feature로 사용하지 않는다.

### Gene expression

선택적 확장 분석으로 사용할 수 있지만 최소 mutation panel 성능에는 포함하지 않는다.

### TMB

주 분석에서는 제외하며 필요할 경우 별도의 sensitivity analysis로만 사용한다.

---

# 8. 데이터 구조

최종 분석 테이블의 개념적인 형태는 다음과 같다.

| ModelID | TP53_hotspot | ATM_damaging | ARID1A_damaging | ... | WGD |  CIN |  LOH | Lineage |
| ------- | -----------: | -----------: | --------------: | --- | --: | ---: | ---: | ------- |
| A       |            1 |            0 |               1 | ... |   1 | high | high | Lung    |
| B       |            0 |            1 |               0 | ... |   0 |  low | high | Breast  |
| C       |            1 |            0 |               0 | ... |   1 | high |  low | Colon   |

X:

**Mutation**

Y:

**WGD / CIN / LOH**

Lineage:

**일반화 성능 확인을 위한 그룹 정보**

---

# 9. 데이터 전처리

## 9.1 ModelID 기준 결합

Mutation, Global Signature, Model 데이터를 ModelID 기준으로 결합한다.

확인할 항목:

* 중복 ModelID
* 누락 ModelID
* 데이터 간 교집합
* 최종 사용 가능한 세포주 수

---

## 9.2 Mutation feature 통합

Hotspot과 damaging mutation 정보를 통합한다.

두 feature를 구분하여 유지할 수 있다.

예:

* TP53_hotspot
* TP53_damaging

동일 유전자에서 hotspot과 damaging 정보가 겹치는 경우 처리 규칙을 사전에 결정한다.

---

## 9.3 희귀 mutation 제거

대부분의 세포주에서 0인 mutation은 머신러닝 학습에 거의 기여하지 않을 수 있다.

따라서 일정 빈도 이하 mutation을 제거할 수 있다.

중요한 원칙은 **빈도 기준을 전체 데이터에서 계산해서는 안 된다는 것**이다.

각 training fold에서 mutation 빈도를 계산하고 해당 기준을 validation/test에 그대로 적용한다.

---

# 10. WGD/CIN/LOH Label 생성

## WGD

가능한 경우 기존 binary 정보를 이용하여

* WGD+
* WGD−

로 구분한다.

---

## CIN

연속형 score 형태라면

* CIN-high
* CIN-low

로 변환한다.

---

## LOH

연속형 score 형태라면

* LOH-high
* LOH-low

로 변환한다.

CIN과 LOH의 high/low threshold는 전체 데이터에서 결정하지 않는다.

각 outer training fold 안에서 threshold를 결정한 뒤 validation/test 데이터에는 동일한 기준을 적용한다.

---

# 11. 머신러닝 분석

복잡한 모델 하나만 사용하는 대신 여러 모델을 동일한 데이터 split에서 비교한다.

## 기본 모델

### Logistic Regression

가장 단순한 baseline model.

Mutation과 phenotype 사이의 선형적인 관계를 평가할 수 있다.

---

### LASSO / Elastic Net

많은 mutation 가운데 중요한 feature를 선택하는 데 유용하다.

최소 biomarker panel 선정과 연결하기 쉽다.

---

### Random Forest

Mutation 간 비선형 관계와 interaction을 반영할 수 있다.

---

### XGBoost

복잡한 mutation pattern을 학습할 수 있는 비선형 모델이다.

---

### Multi-task ANN

공유 hidden layer 이후

* WGD head
* CIN head
* LOH head

를 두는 구조를 사용한다.

개념적으로 다음과 같다.

**Mutation input**

↓

**Shared representation**

↙ ↓ ↘

**WGD / CIN / LOH**

목적은 세 표현형이 공유하는 mutation 신호가 존재하는지를 확인하는 것이다.

---

# 12. 모델 검증 전략

이 프로젝트에서 모델 종류보다 중요한 부분이다.

## Outer CV

최종 모델의 성능 평가에 사용한다.

Outer test 데이터는 모델 학습이나 feature selection 과정에 사용하지 않는다.

---

## Inner CV

다음 항목을 결정한다.

* hyperparameter
* feature selection
* classification threshold
* panel size

즉,

**모델을 만드는 과정은 inner CV**

**최종 성적표는 outer CV**

라고 이해하면 된다.

---

# 13. 데이터 누출 방지

다음 작업은 반드시 training fold 안에서만 수행한다.

* 희귀 mutation 제거
* scaling
* feature selection
* hyperparameter tuning
* CIN/LOH threshold 결정
* classification threshold 결정
* biomarker panel 선정

예를 들어 전체 데이터를 먼저 살펴보고 가장 중요한 10개 유전자를 선정한 뒤 cross-validation을 하면 안 된다.

시험 데이터의 정보를 미리 본 것과 같은 효과가 생길 수 있기 때문이다.

---

# 14. 평가 지표

표현형마다 다음 성능을 평가한다.

### ROC-AUC

전체적인 분류 능력 평가.

### PR-AUC

WGD+ 등 특정 class의 수가 적을 경우 특히 중요하다.

### Balanced Accuracy

class imbalance가 존재할 때 유용하다.

### Sensitivity

실제 양성 가운데 모델이 양성으로 맞힌 비율.

### Specificity

실제 음성 가운데 모델이 음성으로 맞힌 비율.

### F1-score

Precision과 recall의 균형을 평가한다.

### Calibration

모델이 출력한 확률을 실제 확률처럼 신뢰할 수 있는지를 평가한다.

단일 metric만으로 모델을 선정하지 않는다.

---

# 15. Lineage 기반 검증

DepMap에는 다양한 암종의 세포주가 포함되어 있다.

따라서 mutation 모델이 실제로 WGD/CIN/LOH를 학습한 것이 아니라

> “이 mutation pattern은 폐암에서 많다”

같은 암종 정보를 학습했을 가능성을 확인해야 한다.

이를 위해 lineage 기반 검증을 수행한다.

---

## Lineage GroupKFold

같은 lineage가 training과 test에 동시에 포함되지 않도록 분리한다.

---

## Leave-One-Lineage-Out

예를 들어 Lung lineage 전체를 test로 두고 나머지 암종으로 학습한다.

이를 통해

> 새로운 암종에서도 mutation biomarker가 작동하는가?

를 확인한다.

Random CV에서는 성능이 높지만 lineage CV에서 크게 감소한다면 해당 biomarker는 **암종 의존적 신호일 가능성**이 있다.

---

# 16. Biomarker 후보 선정

최소 패널 선정의 핵심은 단순 feature importance 순위가 아니다.

각 outer fold의 training data에서 feature selection을 반복한다.

그 결과 각 유전자에 대해 다음 정보를 저장한다.

* 몇 개 fold에서 선택되었는가
* 평균 중요도
* 중요도 순위
* WGD/CIN/LOH 중 어떤 phenotype에 기여했는가
* lineage validation에서도 유지되는가

예를 들어 다음과 같은 결과를 만들 수 있다.

| Gene   | WGD 선택 빈도 | CIN 선택 빈도 | LOH 선택 빈도 | 평균 순위 |
| ------ | --------: | --------: | --------: | ----: |
| Gene A |       90% |       70% |       20% |     3 |
| Gene B |       80% |       10% |       60% |     5 |
| Gene C |       20% |       85% |       75% |     6 |

반복적으로 선택되는 유전자를 우선 biomarker 후보로 고려한다.

---

# 17. 최소 Mutation Panel 선정

후보 유전자를 기반으로 다음 크기의 모델을 만든다.

### Panel 1

Top 5 genes

### Panel 2

Top 10 genes

### Panel 3

Top 20 genes

### Panel 4

Top 50 genes

### Reference

전체 mutation

그리고 동일한 outer test set에서 평가한다.

---

# 18. 최소 패널 선정 기준

목표는 무조건 가장 작은 패널을 만드는 것이 아니다.

다음 네 가지를 함께 본다.

### 1. 예측 성능

전체 모델과 비교했을 때 성능이 얼마나 유지되는가?

### 2. 안정성

Cross-validation을 반복했을 때 동일한 유전자가 선택되는가?

### 3. Lineage generalization

새로운 lineage에서도 성능이 유지되는가?

### 4. Panel size

비슷한 성능이라면 더 작은 패널을 선호한다.

따라서

> **성능 + 안정성 + 일반화 + 패널 크기**

의 균형으로 최종 패널을 결정한다.

---

# 19. 예상 결과 예시

가상의 결과가 다음과 같다고 가정한다.

| Panel    | WGD AUC | CIN AUC | LOH AUC |
| -------- | ------: | ------: | ------: |
| 전체       |    0.86 |    0.81 |    0.79 |
| 50 genes |    0.86 |    0.80 |    0.79 |
| 20 genes |    0.84 |    0.79 |    0.78 |
| 10 genes |    0.83 |    0.78 |    0.77 |
| 5 genes  |    0.74 |    0.69 |    0.70 |

이 경우에는

> **10~20개 mutation으로 전체 모델의 예측력을 상당 부분 유지할 가능성이 있다.**

라고 해석할 수 있다.

반대로 20개 이하에서 성능이 크게 감소하면 억지로 최소 패널을 만들지 않는다.

> **WGD/CIN/LOH 관련 mutation 신호가 여러 유전자에 분산되어 있어 소수 패널로 축소하기 어렵다.**

는 것도 충분히 의미 있는 결과이다.

---

# 20. 최종 결과물

프로젝트 종료 시 최소한 다음 결과를 제시한다.

## 결과 1. WGD 예측 성능

각 머신러닝 모델의 성능 비교.

## 결과 2. CIN 예측 성능

각 머신러닝 모델의 성능 비교.

## 결과 3. LOH 예측 성능

각 머신러닝 모델의 성능 비교.

## 결과 4. Multi-task 모델 비교

WGD/CIN/LOH를 동시에 학습하는 것이 개별 모델보다 유리한지 확인.

## 결과 5. 중요 mutation 후보

반복 feature selection 결과.

## 결과 6. Minimal panel curve

5 / 10 / 20 / 50 / 전체 mutation 모델 성능 비교.

## 결과 7. Lineage validation

새로운 암종에서도 모델이 작동하는지 평가.

## 결과 8. Candidate minimal mutation biomarker panel

최종 후보 유전자 목록.

---

# 21. 필수 시각화

최종 발표에서는 다음 그림을 우선한다.

### Figure 1. 연구 전체 흐름

**Mutation → WGD/CIN/LOH → Feature selection → Minimal panel**

### Figure 2. WGD/CIN/LOH 분포

세 phenotype의 class distribution.

### Figure 3. 모델 성능 비교

Logistic / Elastic Net / RF / XGBoost / ANN의 ROC-AUC 및 PR-AUC.

### Figure 4. Biomarker selection stability

유전자별 fold 선택 빈도.

### Figure 5. Panel size–performance curve

X축:

5 / 10 / 20 / 50 / All genes

Y축:

예측 성능.

이 그림이 최소 패널 결과의 가장 중요한 시각화가 된다.

### Figure 6. Lineage CV 결과

Random CV와 lineage-based CV 성능 비교.

---

# 22. 14일 분석 일정

## Day 1

데이터 확인.

* 실제 파일명
* 데이터 버전
* ModelID
* WGD/CIN/LOH 관련 column
* lineage column

확정.

---

## Day 2

Mutation / Global Signature / Model 데이터 로드 및 QC.

* 중복
* 결측
* ModelID 교집합

확인.

---

## Day 3

Hotspot + damaging mutation matrix 구축.

WGD/CIN/LOH 및 lineage 정보 결합.

---

## Day 4

WGD/CIN/LOH 분포와 mutation 빈도 QC.

Cross-validation 구조 확정.

---

## Day 5

Nested CV pipeline 구축.

Training fold 내부에서

* threshold
* mutation filtering
* feature selection

이 수행되는지 확인.

---

## Day 6

Logistic Regression baseline 모델.

---

## Day 7

LASSO / Elastic Net 모델.

---

## Day 8

Random Forest / XGBoost 모델.

---

## Day 9

Multi-task ANN 모델.

---

## Day 10

전체 모델 성능 비교.

* ROC-AUC
* PR-AUC
* balanced accuracy
* F1
* calibration

정리.

---

## Day 11

Fold별 feature selection 결과 집계.

반복적으로 선택되는 mutation 후보 확인.

---

## Day 12

5 / 10 / 20 / 50 / 전체 mutation panel 비교.

---

## Day 13

Lineage GroupKFold 및 Leave-One-Lineage-Out 검증.

최소 패널 안정성 확인.

---

## Day 14

결과 통합.

* 최종 biomarker 후보
* panel size
* 성능
* 안정성
* lineage generalization
* 한계

정리 및 발표자료 작성.

---

# 23. 프로젝트 우선순위

## Must-have

1. Hotspot/damaging mutation matrix 구축
2. WGD/CIN/LOH label 생성
3. Logistic 또는 Elastic Net baseline
4. 최소 1개 비선형 모델 비교
5. Nested CV
6. Training-fold 내부 feature selection
7. WGD/CIN/LOH별 예측 성능
8. 반복 feature selection
9. 5/10/20/50/전체 panel 비교
10. Lineage 기반 validation
11. Mutation-only 최종 panel

---

## Nice-to-have

* Multi-task ANN
* MSI 확장
* Gene expression 추가 비교
* WGD/CIN/LOH 8개 조합 분석
* SHAP 등 추가 model interpretation

시간이 부족하면 Nice-to-have 항목부터 제외한다.

---

# 24. 약물반응 분석의 위치

약물반응 분석은 본 연구의 필수 축에서 제외하고 **후속 확장 연구**로 둔다.

최소 mutation panel을 먼저 확보한 뒤,

> “이 패널로 예측된 WGD/CIN/LOH 상태가 특정 약물 반응과도 연결되는가?”

를 추가적으로 분석할 수 있다.

따라서 본 프로젝트의 완성 여부는 약물반응 분석 성공 여부와 무관하다.

핵심 산출물은

> **WGD/CIN/LOH를 예측하는 mutation signature와 candidate minimal mutation biomarker panel**

이다.

---

# 25. 결과 해석 시나리오

## 예측 성능 높음 + 작은 패널 성능 유지

가장 이상적인 결과이다.

> Hotspot/damaging mutation에는 WGD/CIN/LOH 상태를 구분하는 신호가 존재하며, 일부 mutation만으로 전체 모델 성능의 상당 부분을 유지할 수 있었다.

최소 biomarker panel 후보를 제시한다.

---

## 예측 성능 높음 + 작은 패널 성능 감소

Mutation으로 WGD/CIN/LOH는 예측 가능하지만 정보가 여러 유전자에 분산되어 있을 가능성이 있다.

최소 패널을 무리하게 제시하지 않는다.

---

## Random CV 높음 + Lineage CV 낮음

Mutation signal이 특정 암종에 의존할 가능성이 있다.

범암종 biomarker라고 주장하지 않고 lineage-dependent candidate라고 해석한다.

---

## 전체 예측 성능 낮음

Hotspot/damaging mutation만으로 WGD/CIN/LOH를 안정적으로 복원하기 어렵다는 결과이다.

이 역시 의미 있는 결과이며 mutation-only 접근의 한계를 보여준다.

---

# 26. 최종 결론에서 답해야 하는 질문

프로젝트 종료 시 다음 다섯 가지를 명확히 답할 수 있어야 한다.

### ①

**DNA mutation만으로 WGD/CIN/LOH를 예측할 수 있었는가?**

### ②

**어떤 모델이 가장 안정적인 성능을 보였는가?**

### ③

**어떤 mutation이 반복적으로 중요한 feature로 선택되었는가?**

### ④

**전체 mutation을 몇 개까지 줄여도 성능이 유지되었는가?**

### ⑤

**이 결과가 다른 cancer lineage에서도 유지되었는가?**

---

# 27. 권장 최종 결론문 구조

본 연구에서는 DepMap의 hotspot 및 damaging mutation 정보를 이용하여 WGD, CIN, LOH 상태를 예측하였다. Logistic Regression, LASSO/Elastic Net, Random Forest, XGBoost 및 multi-task ANN을 동일한 검증 조건에서 비교하고, lineage 기반 검증을 통해 암종 간 일반화 가능성을 평가하였다.

또한 각 cross-validation fold에서 반복적으로 선택되는 mutation을 집계하여 WGD, CIN, LOH 예측에 기여하는 후보 유전자를 선별하였다. 이후 5, 10, 20, 50개 mutation으로 구성된 축소 모델과 전체 mutation 모델을 nested cross-validation 환경에서 비교하여 예측력과 안정성을 유지할 수 있는 최소 panel 크기를 평가하였다.

최종적으로 본 연구는 **DNA mutation만으로 유전체 불안정성 상태를 어느 수준까지 예측할 수 있는지 평가하고, 예측에 필요한 정보를 소수의 mutation으로 축약할 수 있는지를 검증하여 candidate minimal mutation biomarker panel을 제시하는 것**을 목표로 한다.

해당 패널은 임상 진단용 확정 바이오마커가 아니라 DepMap 내부 검증을 통해 도출된 연구용 후보이며, 향후 독립 코호트와 실험적 검증이 필요하다.

---

# 28. 저장소 구조

```
.
├── configs/
│   ├── data.yaml          # 데이터 경로·파일명·릴리스 버전
│   └── experiment.yaml    # CV, label, feature, panel, metric 설정
├── docs/
│   ├── depmap/            # 데이터 사전 (컬럼 의미, 값 범위)
│   ├── meetings/
│   └── research/
├── notebooks/             # 탐색·발표용. 로직은 src/ 를 import 한다
├── results/
│   ├── figures/           # Figure 1~6 (§21)
│   └── tables/            # 성능·선택빈도·패널 비교 표
├── scripts/               # 01~10 파이프라인 단계 (scripts/README.md 참고)
├── src/
│   ├── config.py          # 설정 로딩, 데이터 경로 해석
│   ├── data/              # 로딩·ModelID 병합 (§9.1)
│   ├── labels/            # WGD/CIN/LOH label 생성 (§10)
│   ├── features/          # mutation matrix, 희귀 변이 필터 (§9.2-9.3)
│   ├── cv/                # nested CV, lineage split (§12, §15)
│   ├── models/            # logistic, enet, RF, XGB, ANN (§11)
│   ├── selection/         # 반복 feature selection 집계 (§16)
│   ├── panel/             # 최소 패널 구성·비교 (§17-18)
│   ├── evaluation/        # 성능 지표, calibration (§14)
│   └── viz/               # 그림 생성 (§21)
└── tests/
```

## 데이터 위치

원본 DepMap CSV 는 용량이 크므로 저장소에 넣지 않는다.
`configs/data.yaml` 의 `data_root` 가 가리키는 저장소 밖 디렉터리에 두고,
환경변수 `DEPMAP_DATA_ROOT` 로 각자 위치를 덮어쓴다.

```bash
python scripts/01_check_data.py
```

로 필요한 파일이 갖춰졌는지 먼저 확인한다.

## 누출 방지가 구조에 반영된 지점

`labels`, `features`, `cv` 를 별도 모듈로 분리한 이유는 §13 때문이다.
threshold 결정, 희귀 변이 필터, feature selection 은 모두 fold 를 인자로 받는
함수여야 하며, 전체 데이터를 한 번에 보는 전처리 함수를 만들지 않는다.

---

# 핵심 프로젝트 구조

**DepMap Hotspot / Damaging Mutation**

↓

**WGD / CIN / LOH Prediction**

↓

**Model Comparison**

↓

**Repeated Feature Selection**

↓

**Mutation Biomarker Candidates**

↓

**5 / 10 / 20 / 50 / All Comparison**

↓

**Lineage Validation**

↓

## **Candidate Minimal Mutation Biomarker Panel**
