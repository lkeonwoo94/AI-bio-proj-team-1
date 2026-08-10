# Genetic — 유전 지표 (APOE 인접 유전자, 다유전자 위험점수, 텔로미어, GWAS)


## 데이터 파일

| 파일 | 내용 |
|---|---|
| `TOMM40_22Jan2026.csv` | `TOMM40` 유전자(19번 염색체, APOE 바로 옆) polyT 반복 다형성 — APOE와 연관불평형(LD) 관계라 독립 위험인자 논쟁이 있는 유전자 |
| `DESIKANLAB_22Jan2026.csv` | Desikan 연구실의 다유전자 위험 점수(Polygenic Hazard Score, PHS) — 발병 연령 예측용 GWAS 기반 점수 |
| `TS_RATIO_ADJ_22Jan2026.csv` | 텔로미어 길이 비율(Telomere/Single-copy gene ratio), 보정판 — 생물학적 노화 지표로 활용 |
| `ADNI_DNA_Source.csv` | 참가자별 DNA 시료 출처/채취 정보 |
| `ADNI_GO_2_GWAS_DNA_Source.xlsx` | ADNIGO/ADNI2 GWAS용 DNA 출처 (엑셀) |
| `ADNI_GWAS_Summary_Statistics_for_tauPET_20240822.zip` | Tau-PET 표현형에 대한 GWAS 요약통계(summary statistics) — 안쪽 압축 별도 해제 필요 |

## Methods / 배경 PDF

- `ADNI_Genetics_Info_March2011.pdf` — 유전 자료 수집 개요 총론
- `ADNI_TOMM40_Overview.pdf` — TOMM40 다형성 배경
- `ADNI_DNA_Telomere_Methods_04202017.pdf` — 텔로미어 측정 방법론
- `DesikanLab_Polygenic_Hazard_Score_Methods_20180730.pdf` — PHS 산출 방법론
- `ADNI_Methods_MAP2K3_20171218.pdf` — `MAP2K3` 유전자 관련 방법론 (신경염증 경로 후보 유전자)
- `ADNI_GWAS_Summary_Statistics_for_tauPET_Methods_20240822.pdf` — tau-PET GWAS 방법론

## 참고

- APOE 유전형 자체(ε2/ε3/ε4)는 이 카테고리가 아니라 `ADNIMERGE2`의 `ADSL` 등 파생 테이블에 이미 포함돼 있습니다 ([study_info.md](study_info.md) 참고). 이 카테고리는 APOE **외의** 유전 지표(TOMM40, PHS, 텔로미어, tau-PET GWAS) 중심입니다.
- GWAS 요약통계는 개인 수준이 아니라 SNP 단위 통계라 재배포 제약이 상대적으로 덜하지만, 그래도 원본 zip은 커밋하지 않습니다.
