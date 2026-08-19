# Pathway gene set 목록 (`pathway_genesets.json`)

Pathway 단위 mutation burden 재집계(`src/features/pathway_aggregate.py`,
`docs/research/2026-08-19/additional_results.md` §3)에 쓴 gene set 원본
출처를 기록한다. 이 파일은 데이터가 아니라 **표현형과 무관한 정적
메타데이터**라 `data/` 와 달리 git 에 그대로 추적한다.

## 출처

MSigDB 정식 사이트(gsea-msigdb.org)는 다운로드에 가입이 필요해, 같은
gene set 라이브러리를 미러링해 API 로 제공하는
[Enrichr](https://maayanlab.cloud/Enrichr/) 를 통해 우회 확보했다.

| 컬렉션 | Enrichr 라이브러리명 | 포함한 것 |
| --- | --- | --- |
| MSigDB Hallmark | `MSigDB_Hallmark_2020` | G2-M Checkpoint, E2F Targets, p53 Pathway, Mitotic Spindle, DNA Repair — 5개 |
| KEGG | `KEGG_2021_Human` | DNA repair 세부 경로 6개 (BER/MMR/NER/HR/NHEJ/Fanconi anemia) |

Enrichr 는 라이브러리 전체를 텍스트로 내려주는 공개 API 를 제공한다.
같은 방식으로 다시 받을 수 있다(정확한 다운로드 시점의 커맨드 자체는
따로 기록해두지 않았다 — 아래는 동일한 라이브러리를 재현하는 표준
엔드포인트다):

```bash
curl -s "https://maayanlab.cloud/Enrichr/geneSetLibrary?mode=text&libraryName=MSigDB_Hallmark_2020" \
  -o msigdb_hallmark_2020.gmt
curl -s "https://maayanlab.cloud/Enrichr/geneSetLibrary?mode=text&libraryName=KEGG_2021_Human" \
  -o kegg_2021_human.gmt
```

각 줄이 `gene_set_name\t설명\tGENE1\tGENE2\t...` 형식(GMT)인 라이브러리
전체에서, 본 연구는 DNA damage repair·cell cycle·chromatin remodeling
과 관련된 11개 gene set 만 선별해 `pathway_genesets.json` 으로 정리했다
— 라이브러리 전체(수백 개 gene set)를 다 쓰면 pathway 수가 너무 많아져
sparsity 완화라는 애초 목적과 어긋난다.

## 포함된 gene set (11개)

| Gene set | 유전자 수 |
| --- | ---: |
| HALLMARK_G2-M_Checkpoint | 200 |
| HALLMARK_E2F_Targets | 200 |
| HALLMARK_p53_Pathway | 200 |
| HALLMARK_Mitotic_Spindle | 199 |
| HALLMARK_DNA_Repair | 150 |
| KEGG_Fanconi_anemia_pathway | 54 |
| KEGG_Nucleotide_excision_repair | 47 |
| KEGG_Homologous_recombination | 41 |
| KEGG_Base_excision_repair | 33 |
| KEGG_Mismatch_repair | 23 |
| KEGG_Non-homologous_end-joining | 13 |

`src/features/pathway_aggregate.py:load_genesets()` 가 이 파일을 읽는다.
유전자 심볼 매칭률(DepMap feature 이름과의 교집합)은 대부분 90% 이상 —
자세한 실행 결과와 해석은
`docs/research/2026-08-19/additional_results.md` §3, 입력 통계는
`docs/depmap/input_data_summary.md` §5 참고.

## 재현/갱신 시 주의

* Enrichr 라이브러리는 시간이 지나면 개정될 수 있다(`_2020`, `_2021`
  같은 버전 접미사가 그 흔적). 완전히 동일한 목록을 재현하려면 라이브러리
  버전 접미사까지 맞춰야 한다.
* gene set 매핑은 fold 와 무관한 고정 값이므로 nested CV 파이프라인
  안에서 다시 계산할 필요가 없다 — `PathwayAggregator.fit()` 이 매 fold
  마다 하는 일은 "이 파일의 유전자 목록과 그 fold 의 입력 컬럼의
  교집합"을 구하는 것뿐이다(§13 누출 위험 없음, docstring 참고).
