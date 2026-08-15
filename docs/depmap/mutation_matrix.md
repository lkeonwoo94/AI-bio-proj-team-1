# OmicsSomaticMutationsMatrix{Hotspot,Damaging}.csv

DepMap Public 26Q1. 입력 feature 의 출처.

## 형태

| 파일 | 크기 | 행 | 유전자 |
| --- | --- | --- | --- |
| `...MatrixHotspot.csv` | 6.6 MB | 3,044 | 554 |
| `...MatrixDamaging.csv` | 228 MB | 3,044 | 19,577 |

두 파일 모두 `OmicsGlobalSignatures.csv` 와 같은 3,044 행 구조이며,
`IsDefaultEntryForModel == "Yes"` 로 걸러 1,968 세포주가 된다.

## 앞쪽 6 개는 유전자가 아니다

```
Unnamed: 0, SequencingID, ModelID, ModelConditionID,
IsDefaultEntryForModel, IsDefaultEntryForMC
```

`index_col=0` 으로 읽으면 행 번호가 인덱스가 되고 `ModelID` 가 feature 로
섞여 들어간다. 반드시 `ModelID` 를 명시적으로 키로 지정하고 메타 컬럼을
제외한다. 목록은 `configs/experiment.yaml` 의 `features.meta_columns` 에 있다.

## 값

유전자별 변이 개수(정수). 0 이 대부분이며 1 이상이 변이 존재를 뜻한다.
본 분석은 존재 여부만 쓰므로 `> 0` 으로 이진화한다.

## 희박성 — 설계에 영향을 주는 지점

최종 코호트(1,631 세포주) 기준으로 hotspot 554 개 유전자 중
**10 개 이상 세포주에서 관측되는 것은 36 개뿐이다.**

즉 README §9.3 의 희귀 변이 제거를 적용하면

* hotspot: 554 → 수십 개
* damaging: 19,577 → 수천 개

로 **양쪽 규모가 100 배 가까이 벌어진다.** 두 행렬을 그대로 이어붙이면
damaging 이 feature 공간을 지배한다. 그럼에도 `merge_rule: keep_separate`
를 택한 이유는 hotspot 과 damaging 이 같은 유전자에서도 생물학적 의미가
다르기 때문이다 (기능 획득 vs 기능 상실). 대신 다음으로 대응한다.

* 접미사 `_hotspot` / `_damaging` 로 구분해 해석 가능성을 유지한다.
* 규제 모델(Elastic Net)과 트리 모델이 feature 수 차이에 어떻게 반응하는지
  Day 10 비교에서 확인한다.
* 최소 패널(§17)에서 hotspot 유래 유전자가 살아남는지를 별도로 본다.
