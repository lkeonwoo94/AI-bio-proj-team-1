# Test_Data_for_Challenges_except_imaging_vertices — 챌린지용 테스트 데이터

이름 그대로 과거 공개 챌린지(대회)용으로 배포됐던 데이터 묶음입니다. 이름의
"except imaging vertices"는 영상 표면 정점(vertex) 단위 대용량 데이터는 제외됐다는 뜻입니다.
안의 파일 4개가 모두 추가 압축 상태라 필요할 때 한 번 더 풀어야 합니다.

## 구성 요소

| 파일 | 내용 |
|---|---|
| `AD1ChallengeImagingFiles.tgz` | 초기 AD 챌린지용 영상 파일 |
| `AD_Challenge_Training_Data_Clinical_Updated_7.22.2014.zip` | AD 챌린지 임상 학습 데이터 (2014년판) |
| `ADNI_QT-PAD.zip` | QT-PAD(Quantitative Translational Alzheimer's Disease) 챌린지 데이터 — 정량적 바이오마커·인지 예측 대회 |
| `tadpole_challenge_201911210.zip` | **TADPOLE Challenge** (2019) — ADNI 종단 데이터를 활용한 알츠하이머 진행 예측 국제 대회 데이터셋. 대회 자체가 유명해 벤치마크로 자주 인용됩니다. |

## 참고

- 모두 **이미 정리된 학습/테스트 스플릿**이 포함된 대회용 데이터라, 처음부터 모델을 만들어보거나 기존 공개 벤치마크(TADPOLE 등)와 비교하고 싶을 때 유용합니다.
- 원본 ADNI 테이블에서 직접 파생 변수를 만드는 대신, 이 챌린지 데이터의 전처리 방식을 참고할 수도 있습니다.
- 안쪽 압축을 풀지 않은 상태입니다. 실제 사용 시 필요한 챌린지 파일만 골라 추가로 해제하는 것을 권장합니다.
