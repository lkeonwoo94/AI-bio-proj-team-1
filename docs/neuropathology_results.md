# Neuropathology_Results — 부검 신경병리 소견


## 구성 요소

- `NEUROPATH_22Jan2026.csv` — 사망 후 부검을 통해 확인된 신경병리 소견(예: 아밀로이드 플라크, 신경섬유매듭(NFT) 병기, 루이소체, 혈관병리 등으로 추정). 용량이 작은 만큼 부검에 동의하고 실제 부검이 이루어진 소수 참가자만 포함됩니다.
- `ADNI_Neuropathology_Core_Methods_FINAL_20221114.pdf` — 신경병리 코어의 평가 방법론(채점 기준, Braak stage 등 표준 프로토콜 설명 추정).

## 참고

- 부검 데이터는 표본 수가 매우 적어(전체 코호트 대비) 단독 통계분석보다는, 생전 바이오마커([Imaging](imaging.md), [Genetic](genetic.md))와의 대조·검증(gold standard 비교) 용도로 주로 쓰입니다.
- `RID`/`PTID`로 다른 카테고리와 조인해 생전 amyloid/tau PET 소견과 부검 소견을 비교하는 분석이 전형적입니다.
