# Assessments — 인지·기능·심리 평가 척도

참가자에게 직접 실시한 인지검사, 보호자/본인 대상 설문, 정신건강·기능평가 등
**설문·검사 원자료(raw instrument data)** 모음입니다. CSV 45개, PDF 7개.

## 주요 척도별 파일

| 파일(접두) | 척도 | 내용 |
|---|---|---|
| `MMSE` | Mini-Mental State Exam | 전반적 인지 선별검사 |
| `MOCA` | Montreal Cognitive Assessment | 인지 선별검사 (MMSE 대체/보완) |
| `ADAS` | Alzheimer's Disease Assessment Scale | 인지 하위척도 (`ADSXLIST`, `EMBICqCP` 관련) |
| `CDR` | Clinical Dementia Rating | 치매 중증도 (Sum of Boxes 포함) |
| `FAQ` | Functional Activities Questionnaire | 일상생활 기능 평가 |
| `NPI` / `NPIQ` | Neuropsychiatric Inventory (Questionnaire) | 정신행동증상 |
| `GDSCALE` | Geriatric Depression Scale | 노인우울척도 |
| `ECOGPT` / `ECOGSP` / `ECOG12PT` / `ECOG12SP` | Everyday Cognition | 본인(PT)/보호자(SP) 보고 일상 인지기능, 12문항 축약판 포함 |
| `NEUROBAT` | Neuropsychological Battery | 신경심리검사 종합 배터리 (기억·언어·실행기능 등) |
| `DXSUM` | Diagnosis Summary | 방문별 진단 이력 (CN/MCI/치매) — 종단 진단의 원천 |
| `CCI` / `FCI` | Cognitive/Functional Change Index | 인지·기능 변화 지수 |
| `STAIAD` | State-Trait Anxiety Inventory | 불안 척도 |
| `PSS` | Perceived Stress Scale | 지각된 스트레스 |
| `RYFF` | Ryff Psychological Well-Being | 심리적 안녕감 |
| `IES` | Impact of Event Scale | 외상 사건 영향 |
| `CSSRSAD` | Columbia Suicide Severity Rating Scale | 자살 위험 평가 |
| `AMNART` | American National Adult Reading Test | 병전 지능 추정 |
| `MODHACH` | Modified Hachinski Ischemic Score | 혈관성 치매 감별 |
| `WATC` | — | 워치/웨어러블 관련 검사로 추정 (확인 필요) |
| `UWNPSYCHSUM` | UW Neuropsych Summary | 워싱턴대 신경심리 요약점수 |
| `BLCHANGE` | Baseline Change | 기저 대비 변화 |

## BHR (Brain Health Registry) 계열

원격/온라인 코호트인 BHR 관련 파일이 별도로 묶여 있습니다.

- `BHR_22Jan2026.csv`, `BHR_MEMTRAX_22Jan2026.csv` — BHR MemTrax 온라인 기억검사
- `BHR_BASELINE_QUESTIONNAIRE_*`, `BHR_LONGITUDINAL_QUESTIONNAIRE_*` — 기저/추적 설문
- `BHR_EVERYDAY_COGNITION_*`, `BHR_SP_EVERYDAY_COGNITION_*` — 본인/파트너(SP) ECog
- `BHR_SP_ADL_*`, `BHR_SP_FAQ_*`, `BHR_SP_CAREGIVER_BURDEN_*` — 파트너 보고 일상기능·돌봄부담
- `BHR_SP_INITIAL_*`, `BHR_SP_RELATIONSHIP_*`, `BHR_SP_STUDY_CONFIRMATION_*` — 파트너 등록 정보

## 기타

- `CBBRESULTS`, `CBBCOMP` — Cogstate Brief Battery(컴퓨터 기반 인지검사) 결과·완료 여부
- `ADNI_CBBRESULTS_22Jan2026.csv` — 위와 별도 표기된 CBB 결과 파일 (파일명 확인 필요)
- `PEDQCV`, `ITEM` — 세부 목적 확인 필요 (문항 수준 데이터로 추정)
- Methods PDF 7개: ADAS-Cog 방법론, BHR MemTrax, Cogstate 설명, 인지 방법론(심리측정) 총론, UWNPSYCHSUM 방법론 등

## 참고

- 척도 대부분이 방문(VISCODE)별 종단 반복측정입니다. `RID`/`PTID`로 다른 카테고리와 조인 가능합니다.
- 본인 보고(PT)와 보호자/파트너 보고(SP)가 짝을 이루는 척도(ECog 등)는 응답 주체 차이에 유의해야 합니다.
