# 입력 데이터 요약 통계

코호트 병합 전, 원본 파일 단위의 row/col 과 분포. `IsDefaultEntryForModel`
필터는 적용했지만(세포주당 1행) ModelID 교집합은 아직 걷지 않은 상태 —
즉 §9.1 병합 이전, 파일별 원상태 기준이다. 병합 후 최종 코호트(1,631 세포주,
20,132 feature)는 `docs/depmap/mutation_matrix.md` 와
`docs/depmap/global_signatures.md` 참고.

재현: `scripts/13_data_summary.py`

---

## 1. Mutation matrix — 입력 feature (X)

| 파일 | row (raw) | row (default) | col (=feature 차원) | dtype |
| --- | ---: | ---: | ---: | --- |
| `OmicsSomaticMutationsMatrixHotspot.csv` | 3,044 | 1,968 | 554 | int (변이 개수) |
| `OmicsSomaticMutationsMatrixDamaging.csv` | 3,044 | 1,968 | 19,578 | int (변이 개수) |

row 는 세포주당 대표 시퀀싱 프로파일(`IsDefaultEntryForModel=="Yes"`)로
필터링한 값이다. col 은 앞의 메타 컬럼 6개(`Unnamed: 0`, `SequencingID`,
`ModelID`, `ModelConditionID`, `IsDefaultEntryForModel`, `IsDefaultEntryForMC`)
를 제외한 실제 유전자 feature 수 — 곧 입력 벡터의 차원이다.

### 셀 값 분포 (전체 원소 기준, 1,968 × col 개의 셀)

| 파일 | min | max | mean | var | 1인 비율(이진화 후) |
| --- | ---: | ---: | ---: | ---: | ---: |
| hotspot | 0 | 2 | 0.00468 | 0.00716 | 0.343% |
| damaging | 0 | 2 | 0.00338 | 0.00392 | 0.310% |

원본 값은 변이 개수(0, 1, 드물게 2)이며, 대부분의 셀이 0인 극도로 희소한
행렬이다. 본 분석은 `> 0` 으로 이진화해 존재 여부만 사용한다
(`src/data/io.py:load_mutation`). 평균이 곧 전체 인구에서 변이가 관측될
"셀 단위" 확률이며, 개별 유전자의 관측 빈도는 `eda_mutation_frequency.csv`
(feature 별)를 따로 참고한다 — 유전자마다 편차가 매우 크다(§Day4 EDA,
필터 `>=10` 세포주 적용 시 hotspot 554→36, damaging 19,578→2,026).

---

## 1-b. 학습 직전 X — `cohort.X` (병합·이진화 완료, fold 필터 이전)

`src/data/merge.py:load_cohort()` 가 hotspot/damaging 을 ModelID 교집합으로
결합하고 `> 0` 이진화까지 마친 표. 실제로 `run_nested_cv()` 에 넘어가는
행렬이며, 여기서 outer/inner fold 로 나뉜 뒤에야 `RareMutationFilter` 가
적용된다(§13 누출 방지 — 필터 기준은 fold 마다 다시 계산되므로 이 표에는
아직 반영되어 있지 않다).

| 구분 | row | col(=차원) | dtype | min | max | mean | var | 양성비율 |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| **전체 X** | 1,631 | 20,132 | int8 (0/1) | 0 | 1 | 0.002741 | 0.002733 | 0.274% |
| ├ hotspot 구간 | 1,631 | 554 | int8 (0/1) | 0 | 1 | 0.003292 | 0.003282 | 0.329% |
| └ damaging 구간 | 1,631 | 19,578 | int8 (0/1) | 0 | 1 | 0.002725 | 0.002718 | 0.273% |

메모리 31.3 MB (`int8` dtype, dense 배열 기준). `y` 는 `(1631, 3)`
(WGD/CIN/LoHFraction, 아직 CIN·LOH 는 연속형 원값), `groups` 는 lineage
32종.

### 1번 절과의 차이

1번 절은 hotspot/damaging 을 **각 파일 단독으로**, ModelID 교집합을 걷기
전(1,968 세포주) 값이다. 1-b 는 두 파일을 **합치고 라벨 결측(337행)까지
제거한 후**(1,631 세포주) 값이라 row 가 더 적다. 값 자체(dtype, min, max,
mean, var)가 크게 다르지 않은 것은 병합으로 빠진 337개 세포주의 mutation
분포가 전체와 특별히 다르지 않다는 뜻이다.

### 여기서 한 단계 더 — fold 안의 실제 학습 입력

이 표는 `RareMutationFilter` 적용 **이전** 상태다. 실제 매 outer fold 의
training 데이터에서는 희귀 변이가 제거되어 열 수가 1,162~1,671 개로
줄어든다(`cv_random_*.csv` 의 `n_features_kept` 컬럼, 모델·fold·표현형마다
다름 — 필터 기준(`min_mutation_count=10`)이 training 세포주 구성에 따라
달라지기 때문이다). 이 값은 fold 마다 다시 계산되므로 "학습 직전 X" 로
단일하게 고정할 수 없다 — 그 자체가 §13 누출 방지의 핵심이다.

### 컬럼(유전자) 기준 Top 10 — 분산 상위

앞의 통계는 20,132개 컬럼 전체를 뭉뚱그린 값이라 개별 컬럼의 모습을 감춘다.
이진 변수의 분산은 `p(1-p)` 이므로 `mean`(=양성비율)이 0.5 에 가까울수록
`var` 도 커진다 — 즉 "가장 자주 관측되면서 정보량이 큰" 유전자를 분산 기준
정렬로 뽑을 수 있다.

| column | dtype | min | max | mean | var |
| --- | --- | ---: | ---: | ---: | ---: |
| `TP53 (7157)_hotspot` | int8 | 0 | 1 | 0.4672 | 0.2489 |
| `TP53 (7157)_damaging` | int8 | 0 | 1 | 0.5782 | 0.2439 |
| `TERT (7015)_hotspot` | int8 | 0 | 1 | 0.1484 | 0.1264 |
| `TTN (7273)_damaging` | int8 | 0 | 1 | 0.1281 | 0.1117 |
| `CDKN2A (1029)_damaging` | int8 | 0 | 1 | 0.1110 | 0.0987 |
| `KRAS (3845)_hotspot` | int8 | 0 | 1 | 0.1104 | 0.0982 |
| `PTEN (5728)_damaging` | int8 | 0 | 1 | 0.0871 | 0.0795 |
| `BRAF (673)_hotspot` | int8 | 0 | 1 | 0.0834 | 0.0764 |
| `KMT2D (8085)_damaging` | int8 | 0 | 1 | 0.0809 | 0.0744 |
| `RB1 (5925)_damaging` | int8 | 0 | 1 | 0.0760 | 0.0702 |

`TP53` 이 hotspot·damaging 두 컬럼 모두 압도적 1·2위다 (damaging 컬럼은
전체 세포주의 57.8% 에서 관측). 20,132개 feature 중 대부분이 §Day4 EDA 의
희귀 변이 제거 기준(`>=10` 세포주)에도 못 미치는 것과 대비된다 — 이
표는 그 반대편 극단, 즉 "가장 흔한" 유전자들이다.

TP53·TERT·KRAS·BRAF·PTEN·RB1·CDKN2A 는 모두 범암종에서 널리 알려진
tumor suppressor/oncogene 이며, `TP53` 은 Day 11 반복 feature selection
(`final_conclusion.md` §26-③)에서도 세 표현형(WGD/CIN/LOH) 모두 전 fold
1순위로 뽑힌 유전자와 정확히 일치한다. 즉 "가장 자주 관측되는 변이"와
"모델이 실제로 중요하다고 고르는 변이"가 겹친다는 방향성 검증이 된다.

재현: `scripts/13_data_summary.py` 의 `cohort_matrix_stats()` (또는 아래 스니펫).

```python
from src.data.merge import load_cohort
X = load_cohort().X          # (1631, 20132), int8, 0/1
X.to_numpy().mean(), X.to_numpy().var()
```

---

## 2. OmicsGlobalSignatures.csv — 정답 label (y)

row (raw) 3,044 / row (default, ModelID 유일) 1,968 / col 12

| 컬럼 | dtype | n(비결측) | 결측 | min | max | mean | var |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| **WGD** | float64 (0/1) | 1,631 | 337 | 0.000 | 1.000 | 0.6524 | 0.2269 |
| **CIN** | float64 | 1,631 | 337 | 0.000 | 0.8593 | 0.4601 | 0.0610 |
| **LoHFraction** | float64 | 1,631 | 337 | 0.000 | 0.9299 | 0.2102 | 0.0263 |
| Ploidy | float64 | 1,631 | 337 | 1.6728 | 4.9948 | 2.9993 | 0.6839 |
| Aneuploidy | float64 | 1,631 | 337 | 0 | 39 | 16.538 | 103.35 |
| MSIScore | float64 | 1,968 | 0 | 0.300 | 93.22 | 6.037 | 254.66 |

굵게 표시한 세 컬럼이 실제 예측 대상이다. 나머지(Ploidy, Aneuploidy,
MSIScore)는 README §7 에 따라 feature/label 어느 쪽에도 쓰지 않는
참고용 컬럼이다 (Ploidy·Aneuploidy 는 WGD/CIN 과 직결되어 정답 누출 위험,
MSIScore 는 확장 분석 후보).

세 예측 대상 모두 **동일한 337 행에서 함께 결측**되어 있어, 코호트
병합 시 결측 제거 한 번으로 세 라벨이 동시에 빠진다.

### 읽는 법

* **WGD** — 이미 0/1 binary. mean 0.6524 는 곧 양성 비율(65.2%)이며
  var 0.2269 는 베르누이 분산 `p(1-p)` 와 정확히 일치한다
  (0.6524 × 0.3476 = 0.2268).
* **CIN, LoHFraction** — 0~1 범위의 연속 지표. var 가 작다는 것은
  (CIN 0.061, LOH 0.026) 대부분 값이 평균 근처에 몰려 있다는 뜻이 아니라
  0~1 스케일 자체가 좁기 때문이다 — 표준편차로 보면 CIN 0.247, LOH 0.162 로
  꽤 넓게 퍼져 있다. 실제 형태는 `fig2_phenotype_distribution.png` 참고
  (CIN 은 이봉형, LOH 는 0 근처에 치우침).
* **Aneuploidy** — var 가 103 으로 크게 튀는 것은 정수 스케일(0~39)이
  다른 컬럼보다 훨씬 넓기 때문이다. 표준편차 10.17.
* **MSIScore** — var 254 로 가장 크다. 범위(0.3~93.2)와 표준편차(15.96)가
  다른 컬럼과 자릿수 자체가 달라, 그대로 모델에 섞으면 스케일링 없이는
  지배적인 feature 가 된다 (현재는 아예 쓰지 않으므로 해당 없음).

---

## 3. Model.csv — 세포주 메타 (그룹 변수)

row 2,154 / col 49

수치형 컬럼 4개만 통계가 유의미하다 (나머지는 범주형/텍스트/ID 문자열).

| 컬럼 | dtype | min | max | mean | std |
| --- | --- | ---: | ---: | ---: | ---: |
| Age | float64 | 0.0 | 94.0 | 47.17 | 22.20 |
| WTSIMasterCellID | float64 | 1.0 | 2266.0 | 1086.32 | 658.76 |
| COSMICID | float64 | 683,665 | 2,054,094 | 996,989.6 | 227,515.9 |

`WTSIMasterCellID`, `COSMICID` 는 외부 데이터베이스 식별자일 뿐 생물학적
의미의 수치가 아니다. 본 분석에서 실제로 쓰는 컬럼은 `ModelID`(병합 키)와
`OncotreeLineage`(범주형, 34종 — lineage 분포는
`qc_lineage_counts.csv` 참고)뿐이다.

---

## 4. 병합 후 최종 코호트 (요약)

4개 파일을 ModelID 교집합으로 묶고 라벨 결측을 제거하면:

| 항목 | 값 |
| --- | --- |
| row (세포주) | 1,631 |
| col — feature (X) | 20,132 (hotspot 554 + damaging 19,578) |
| col — label (y) | 3 (WGD, CIN, LoHFraction) |
| 그룹 변수 | OncotreeLineage, 32종 |

X 의 값 분포(dtype/min/max/mean/var)는 **1-b 절**에 상세히 정리했다.
자세한 병합 과정은 `docs/depmap/mutation_matrix.md` 와
`src/data/merge.py` 참고.
