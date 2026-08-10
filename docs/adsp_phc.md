# ADSP_PHC — 조화 인지·바이오마커 표현형 (Harmonized Cognition)

Alzheimer's Disease Sequencing Project(ADSP)에서 여러 코호트(ADNI 포함)를 가로질러
**조화(harmonized)** 시킨 인지 점수와 영상·바이오마커 파생 지표 모음입니다.
원본 검사별 raw 데이터가 아니라, 코호트 간 비교가 가능하도록 통계적으로 맞춰 놓은
2차 가공 지표라는 점이 특징입니다.


## 구성 요소

각 지표마다 데이터 CSV와 `_DATADIC` 데이터 사전 CSV가 짝을 이루고, 별도 Methods PDF가 산출 방법을 설명합니다.

| 파일(접두) | 내용 |
|---|---|
| `ADSP_PHC_COGN` | 조화 인지 복합 점수 (Executive/Memory 등) |
| `ADSP_PHC_BIOMARKER` | 조화 바이오마커 요약 지표 |
| `ADSP_PHC_CVRF` | 심혈관 위험 요인(Cardiovascular Risk Factor) 조화 지표 |
| `ADSP_PHC_T1_FS` / `ADSP_PHC_T1_MUSE` | T1 MRI 기반 FreeSurfer / MUSE 파이프라인 파생 지표 |
| `ADSP_PHC_FLAIR` | FLAIR MRI 파생 지표(백질 병변 등) |
| `ADSP_PHC_PET_Amyloid_*` | Amyloid PET 조화 지표 (Simple/Detailed 두 버전) |
| `ADSP_PHC_PET_Tau_*` | Tau PET 조화 지표 (Simple/Detailed 두 버전) |
| `ADSP_PHC_DTI_*` | 확산텐서영상(DTI) 조화 지표 — `ADSP_PHC_DTI_20250515.zip` 안에 실제 CSV, 별도로 한 번 더 풀어야 함 |

## 참고

- 각 Methods PDF에 산출 파이프라인·버전·QC 기준이 상세히 설명돼 있어, 논문 Methods 절 인용 시 참고합니다.
- Simple/Detailed로 나뉜 PET 지표는 Simple이 요약(region 단위), Detailed가 세부(voxel/ROI별) 버전으로 추정되며, 사용 전 각 DATADIC과 Methods PDF로 확인이 필요합니다.
- `ADSP_PHC_DTI_20250515.zip`은 아직 안쪽 압축을 풀지 않았습니다. 필요 시 추가로 해제합니다.
