# Subject_Characteristics — 인구학·가족력·거주지 특성

## 구성 요소

| 파일 | 내용 |
|---|---|
| `PTDEMOG_22Jan2026.csv` | 참가자 인구학 정보 (성별, 인종/민족, 학력, 결혼상태 등) — 가장 기본이 되는 테이블 |
| `FHQ_22Jan2026.csv` | 가족력 설문(Family History Questionnaire) 원자료 |
| `RECFHQ_22Jan2026.csv` | 가족력 설문 추적판(recurring) |
| `FAMHXPAR_22Jan2026.csv` | 부모(parent)의 치매/알츠하이머 병력 |
| `FAMHXSIB_22Jan2026.csv` | 형제자매(sibling)의 치매/알츠하이머 병력 |
| `ADI_22Jan2026.csv` | Area Deprivation Index — 거주지 사회경제적 박탈 지수 (우편번호 기반) |
| `RURALITY_22Jan2026.csv` | 거주지 도시/농촌 구분 지표 |
| `AMAS_22Jan2026.csv` | — 목적 확인 필요(약어 미상, 설문/척도로 추정) |

## Methods PDF

- `ADNI_RURALITY_METHODS_20251031.pdf` — 도시/농촌 구분 지표 산출 방법론

## 참고

- `ADI`, `RURALITY`는 개인정보가 아니라 **거주지 기반 사회적 결정요인(social determinants of health)** 지표라 인지 저하의 환경적 요인 분석에 유용합니다.
- 가족력은 원자료(`FHQ`)와 추적판(`RECFHQ`), 그리고 부모/형제자매로 세분화된 별도 테이블(`FAMHXPAR`/`FAMHXSIB`)로 나뉘어 있어 조인 시 구조 확인이 필요합니다.
- `PTDEMOG`는 [Remotely_Collected_Data](remotely_collected_data.md)의 `RMT_PTDEMOG`와 대응하는 대면 트랙 버전입니다.
