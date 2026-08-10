# Medical_History — 병력·병용약물·이상반응

참가자의 의학적 배경과 연구 참여 중 발생한 이상반응·병용약물을 추적하는 테이블입니다.

## 구성 요소

| 파일 | 내용 |
|---|---|
| `MEDHIST_22Jan2026.csv` | 기저 병력(Medical History) — 스크리닝 시 조사한 과거 질환 |
| `INITHEALTH_22Jan2026.csv` | 초기 건강 평가 |
| `PHYSICAL_22Jan2026.csv` | 신체 검진 |
| `NEUROEXM_22Jan2026.csv` | 신경학적 검진 |
| `VITALS_22Jan2026.csv` / `AV45VITALS_22Jan2026.csv` | 활력징후 (일반 / AV45 PET 방문 시) |
| `ADNI2_ECG_22Jan2026.csv` | ADNI2 심전도 |
| `BACKMEDS_22Jan2026.csv` | 배경 약물(baseline concomitant meds) |
| `RECCMEDS_22Jan2026.csv` | 추적 병용약물(recurring concomitant meds) — `ADNIMERGE2`에도 동일 계열(`RECCMEDS`, 77,466행)이 있어 원본 대응 |
| `RECMHIST_22Jan2026.csv` | 추적 병력(recurring medical history) |
| `RECADV_22Jan2026.csv` / `ADVERSE_22Jan2026.csv` | 이상반응(Adverse Event) — 추적/원본 |
| `RECBLLOG_22Jan2026.csv` | 추적 검사실(blood/lab) 로그 |
| `BLSCHECK_22Jan2026.csv` | 채혈(blood sample) 체크리스트 |
| `ANTIAMYTX_22Jan2026.csv` | 항아밀로이드 치료(Anti-Amyloid Treatment) 이력 — 최근 항체 치료제(레카네맙 등) 도입 이후 중요도 상승 |
| `AV45FOLLOW_22Jan2026.csv` | AV45(Florbetapir) PET 방문 후속 조치 |

## 참고

- 병용약물·이상반응은 원본(`MEDHIST`, `ADVERSE`)과 추적판(`REC*`) 두 계열로 나뉘어 있어, 분석 시 어느 쪽이 표준 종단 테이블인지 확인이 필요합니다. `ADNIMERGE2`의 정리된 버전([study_info.md](study_info.md))을 우선 참고하는 것을 권장합니다.
- `ANTIAMYTX`는 항아밀로이드 항체 치료가 인지 궤적에 미치는 영향을 볼 때 공변량/층화 변수로 유용합니다.
