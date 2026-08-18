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

## 4. 병합 후 최종 코호트 (참고)

4개 파일을 ModelID 교집합으로 묶고 라벨 결측을 제거하면:

| 항목 | 값 |
| --- | --- |
| row (세포주) | 1,631 |
| col — feature (X) | 20,132 (hotspot 554 + damaging 19,578) |
| col — label (y) | 3 (WGD, CIN, LoHFraction) |
| 그룹 변수 | OncotreeLineage, 32종 |

자세한 병합 과정은 `docs/depmap/mutation_matrix.md` 와
`src/data/merge.py` 참고.
