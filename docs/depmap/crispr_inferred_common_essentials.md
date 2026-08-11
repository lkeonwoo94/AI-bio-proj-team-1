# CRISPRInferredCommonEssentials.csv

> ⚠️ **이 문서는 `scripts/depmap_profile.py` 가 자동 생성합니다. 직접 수정하지 마세요.**
> 설명·주의사항을 고치려면 스크립트의 `NOTES` 를, 측정값을 갱신하려면 스크립트를 다시 실행하세요.
> 생성 시각: 2026-08-11 17:23 KST

이 릴리스에서 **거의 모든 세포주에 필수**로 추론된 유전자 목록. 리보솜·프로테아좀·스플라이싱 등 세포 생존의 기본 기계에 해당한다.


## 기본 정보

| 항목 | 값 |
|---|---|
| 릴리스 | `DepMap Public 26Q1` (2026-04-01) |
| 원본 경로 | `raw/DepMap/CRISPRInferredCommonEssentials.csv` |
| 파일 크기 | 25,021 B (25.0 KB) |
| md5 | `f9b12f368abf7684fcd97af31e8a39a2` ✅ 매니페스트 일치 |
| 역할 | **보조 · 타깃 필터** |
| 다운로드 | [포털](https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+26Q1&filename=CRISPRInferredCommonEssentials.csv) |
| shape | **1,827 행 × 1 열** |
| 컬럼명 | `Essentials` (단일 컬럼) |
| 값 형식 | `SYMBOL (ENTREZID)` — 예: `AAMP (14)` |

## 데이터 샘플

앞 8행 (전체 1,827행):

| Essentials |
|---|
| AAMP (14) |
| AARS1 (16) |
| AARS2 (57505) |
| AATF (26574) |
| ABCB7 (22) |
| ABCE1 (6059) |
| ABCF1 (23) |
| ABT1 (29777) |


## ⚠️ 주의사항

- **이 목록을 타깃에서 빼지 않으면 성능 지표가 부풀려진다.** 정의상 세포주 간 분산이 거의 없어서, 모델이 세포주 정보를 전혀 쓰지 않고도 맞출 수 있는 성분이 들어간다.
- 포함/제외한 두 설정의 성능 지표는 서로 직접 비교되지 않는다. 반드시 어느 쪽인지 명시할 것.


## 로딩 예제

```python
import pandas as pd

ce = set(pd.read_csv("raw/DepMap/CRISPRInferredCommonEssentials.csv")["Essentials"])
selective = gene_effect.drop(columns=[c for c in gene_effect.columns if c in ce])
```
