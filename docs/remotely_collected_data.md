# Remotely_Collected_Data — 원격(RMT) 수집 데이터

ADNI4부터 도입된 **원격 참여(Remote Monitoring/Testing, RMT)** 트랙 데이터입니다.
참가자가 병원 방문 없이 온라인/앱으로 참여하는 프로토콜(`ADNI4_RMT_*`)에서 수집됩니다.


## 파일별 내용

| 파일 | 내용 |
|---|---|
| `REMOTE_DATADIC_22Jan2026.csv` | 원격 트랙 전용 데이터 사전 |
| `RMT_Screening_22Jan2026.csv` | 원격 스크리닝 |
| `RMT_PTDEMOG_22Jan2026.csv` | 원격 참가자 인구학 정보 ([Subject_Characteristics](subject_characteristics.md)의 `PTDEMOG`와 대응하는 원격판) |
| `RMT_APOERES_22Jan2026.csv` | 원격 트랙에서 확인한 APOE 유전형 결과 |
| `RMT_ECOG12PT_22Jan2026.csv` / `RMT_ECOG12SP_22Jan2026.csv` | 원격 ECog-12 (본인/파트너 보고) — [Assessments](assessments.md)의 `ECOG12PT`/`ECOG12SP`와 같은 척도의 원격 수집판 |
| `RMT_STORYTELLER_22Jan2026.csv` | "Storyteller" 원격 인지검사 과제 (내러티브/언어 기반 검사로 추정) |

## Methods PDF

- `ADNI4_RMT_Methods_20241209.pdf` — 원격 수집 전반 방법론
- `ADNI4_RMT_STORYTELLER_METHODS_20250512.pdf` — Storyteller 과제 방법론

## 참고

- 대면 방문 없이 수집되므로 데이터 품질·결측 패턴이 대면 데이터([Assessments](assessments.md), [Medical_History](medical_history.md))와 다를 수 있습니다. 원격/대면 트랙을 구분하는 변수(`RID`/`PTID` + 방문 유형)를 확인하고 분석하는 것을 권장합니다.
- ADNI4에서 새로 생긴 트랙이라 이전 단계(ADNI1~3) 참가자에게는 해당 데이터가 없습니다.
