# OmicsGlobalSignatures.csv

DepMap Public 26Q1. WGD / CIN / LOH 정답 label 의 출처.

## 형태

3,044 행 × 12 컬럼. **행 단위는 세포주가 아니라 시퀀싱 프로파일이다.**
고유 `ModelID` 는 1,968 개뿐이므로 그대로 쓰면 같은 세포주가 여러 번 들어간다.

```python
sig = sig[sig.IsDefaultEntryForModel == "Yes"]   # 1,968 행, ModelID 유일
```

`IsDefaultEntryForModel` 은 불리언이 아니라 **문자열 `"Yes"` / `"No"`** 다.
`== True` 로 거르면 조용히 0 행이 되므로 주의한다.

## 컬럼

| 컬럼 | 용도 | 비고 |
| --- | --- | --- |
| `ModelID` | 병합 키 | |
| `SequencingID`, `ModelConditionID` | 프로파일 식별자 | 사용 안 함 |
| `IsDefaultEntryForModel` | 세포주당 대표 프로파일 | `"Yes"` 로 필터 |
| `IsDefaultEntryForMC` | 조건당 대표 프로파일 | 사용 안 함 |
| **`WGD`** | **RQ1 label** | 0 / 1 binary |
| **`CIN`** | **RQ2 label** | 연속형 0 \~ 0.859 |
| **`LoHFraction`** | **RQ3 label** | 연속형 0 \~ 0.930 |
| `Ploidy` | 사용 안 함 | 1.67 \~ 5.00. WGD 와 직결되어 feature 제외 (README §7) |
| `Aneuploidy` | 사용 안 함 | 0 \~ 39 정수. arm-level 이상 개수 |
| `MSIScore` | 사용 안 함 | 확장 분석 후보 (README §23 Nice-to-have) |

## 값 분포 (default 프로파일 기준)

* 결측: WGD / CIN / LoHFraction / Ploidy / Aneuploidy 가 **동일한 337 행에서 함께 결측**
  → 세 표현형 모두 사용 가능한 세포주는 1,631 개
* `WGD`: 1 이 1,064 (65.2%), 0 이 567 (34.8%)
  → **WGD− 가 소수 클래스다.** README §14 가 가정한 방향과 반대이므로
  PR-AUC 의 positive class 정의를 명시해야 한다.
* `CIN`: 중앙값 0.533
* `LoHFraction`: 중앙값 0.187

## 이진화

`CIN` 과 `LoHFraction` 은 연속형이므로 high / low 로 변환한다.
threshold 는 **각 training fold 안에서** 계산하고 validation / test 에 그대로
적용한다 (README §10, §13). 전체 데이터에서 중앙값을 구하면 누출이다.
