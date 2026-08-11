# DepMap 데이터 설명서

> ⚠️ **이 폴더의 문서는 `scripts/depmap_profile.py` 가 자동 생성합니다. 직접 수정하지 마세요.**
> 생성 시각: 2026-08-11 17:23 KST · 릴리스: `DepMap Public 26Q1` (2026-04-01)

```bash
python3 scripts/depmap_profile.py
```

라이선스·취급 주의사항은 [저장소 README](../../README.md) 의 「⚠️ 데이터 취급 주의사항」 절 참고.
26Q1 파일 목록 정본은 [DepMap 데이터 전반 조사](../research/2026-08-13/depmap_overview/lkeonwoo94.md), 최소 구성(C-1) 선정 근거는 [AI 질답 정리 Q3](../research/2026-08-13/depmap_gpt_qna/lkeonwoo94.md#q3-그럼-최소한으로-받아야-하는-데이터가-뭐야) 참고.

## 파일 목록 (C-1 최소 구성)

| 파일 | 역할 | shape | 크기 | 설명서 |
|---|---|---|---:|---|
| `CRISPRGeneEffect.csv` | 출력 Y | 1,208 × 18,531 | 440.6 MB | [열기](crispr_gene_effect.md) |
| `OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv` | 입력 X | 1,775 × 19,220 | 305.0 MB | [열기](omics_expression_tpm_logp1_human_protein_coding_genes.md) |
| `Model.csv` | 메타데이터 · 조인 키 | 2,154 × 49 | 697.5 KB | [열기](model.md) |
| `CRISPRInferredCommonEssentials.csv` | 보조 · 타깃 필터 | 1,827 × 1 | 25.0 KB | [열기](crispr_inferred_common_essentials.md) |
| `README.txt` | DepMap 공식 릴리스 설명 | — | 47.3 KB | (원본 그대로) |

## 교집합 — 실제 학습 가능한 표본 수

| 항목 | 값 |
|---|---|
| 발현 (필터링 후) | 1,719 |
| CRISPR gene effect | 1,208 |
| Model.csv | 2,154 |
| 발현 ∩ CRISPR | 1,140 |
| **3개 전부 (= n)** | **1,140** |
| CRISPR에 있으나 발현에 없음 | 68 |
| CRISPR에 있으나 Model.csv에 없음 | 0 |

## 유전자 축 겹침

| 항목 | 값 |
|---|---|
| 발현 유전자 | 19,215 |
| CRISPR 유전자 | 18,531 |
| 공통 | 18,463 |
| CRISPR에만 있음 | 68 |
| 발현에만 있음 | 752 |

## 교집합 1,140개의 암종 분포

총 **29개 lineage**.

| lineage | 세포주 수 |
|---|---:|
| Lung | 123 |
| Lymphoid | 94 |
| CNS/Brain | 84 |
| Skin | 74 |
| Head and Neck | 63 |
| Esophagus/Stomach | 62 |
| Bowel | 59 |
| Ovary/Fallopian Tube | 56 |
| Breast | 51 |
| Soft Tissue | 49 |
| Bone | 49 |
| Pancreas | 46 |
| Myeloid | 43 |
| Peripheral Nervous System | 40 |
| Biliary Tract | 34 |
| Bladder/Urinary Tract | 34 |
| Uterus | 34 |
| Kidney | 32 |
| Liver | 25 |
| Pleura | 21 |
| Cervix | 18 |
| Eye | 15 |
| Thyroid | 11 |
| Prostate | 10 |
| Ampulla of Vater | 5 |
| Testis | 4 |
| Vulva/Vagina | 2 |
| Fibroblast | 1 |
| Adrenal Gland | 1 |

⚠️ **5개 lineage는 세포주가 10개 미만**(Ampulla of Vater 5, Testis 4, Vulva/Vagina 2, Fibroblast 1, Adrenal Gland 1). leave-one-lineage-out 평가는 표본이 충분한 상위 lineage로 한정해야 한다.

## 조인 규약

- 조인 키는 `ModelID` (`ACH-XXXXXX`). 세포주 이름으로 조인하지 말 것.
- 유전자 컬럼은 `SYMBOL (ENTREZID)` 형식. symbol만 필요하면 `c.split(" (")[0]`.
- 발현은 `IsDefaultEntryForModel == "Yes"` 필터가 **선행**되어야 한다.
- 교집합 확정 후 모든 테이블의 행 순서를 명시적으로 동일하게 맞출 것.
