# TCGA/GDC 입력 데이터 요약

DepMap 세포주가 아닌 실제 환자 종양(TCGA) 데이터다. WGD 외부 검증
(`docs/research/2026-08-19/additional_results.md` §5, 한계 6번 후속)에만
쓴다. 원본 파일 다운로드 방법은 `data/gdc/README.md` 참고 — 이 문서는
파일 자체의 row/col, 매칭률, 라벨 분포를 다룬다.

재현: `python scripts/21_tcga_validation.py`

---

## 1. 원본 파일

| 파일 | 내용 | 크기 |
| --- | --- | ---: |
| `mc3.v0.2.8.PUBLIC.maf.gz` | 전체 TCGA somatic mutation MAF | 753MB |
| `TCGA_mastercalls.abs_tables_JSedit.fixed.txt` | ABSOLUTE ploidy/purity/WGD 결과 | — |

DepMap 의 hotspot/damaging 이진 행렬과 달리 **원시 MAF** 라 위치·염기
정보가 살아있다(`Chrom`/`Pos`/`Ref`/`Alt`/`Variant_Classification`).

## 2. barcode 매칭

ABSOLUTE 의 `sample` 컬럼과 MAF 의 `Tumor_Sample_Barcode` 는 시퀀싱
플레이트/센터 코드가 달라 전체 문자열로 join 하면 10,642개 중 **12개**
만 매칭된다. TCGA 데이터 종류 간 병합의 표준 관례대로 barcode 앞
15자(참가자+샘플타입, 예: `TCGA-3A-A9IR-01A`)로 잘라서 맞추면:

| 매칭 방식 | 매칭 수 / 전체 | 매칭률 |
| --- | --- | ---: |
| 전체 barcode 그대로 | 12 / 10,642 | 0.1% |
| **앞 15자 절단** | **9,651\~10,261 / 10,642** | **91%** |

정확한 매칭 수는 이후 단계(라벨 결측 제거, 유전자 교집합)에 따라
9,651\~10,261 사이에서 조금씩 달라진다. 최종 검증에 쓰인 표본 수는
**10,261**.

## 3. WGD 라벨 (ABSOLUTE `Genome doublings` 컬럼)

DepMap 의 WGD 와 같은 정의로 맞추기 위해 `Genome doublings >= 1` 을
WGD+ 로 이진화한다.

| 항목 | DepMap | TCGA |
| --- | ---: | ---: |
| n | 1,631 | 10,261 |
| WGD+ 비율 | 65.2% | 35.8% |

두 코호트의 WGD+ 비율 자체가 크게 다르다(65.2% vs 35.8%). 이 차이의
원인(세포주 배양 과정에서의 선택압, 코호트 구성 암종의 차이, WGD 판정
알고리즘의 차이 등)은 본 연구에서 검증하지 않았다 — 라벨 기저율이
이만큼 다르다는 사실 자체가 외부 검증 해석 시 참고할 배경이라는
정도로만 기록해 둔다.

## 4. Mutation feature — damaging-only 근사

hotspot 에 대응하는 TCGA 데이터가 없어(큐레이션 hotspot DB 필요)
**damaging feature 만** 비교했다. DepMap 의 `LikelyLoF` 판정(VEP
LofTool 기반)을 TCGA MAF 의 표준 truncating variant class 로 근사한다.

```python
LOF_CLASSES = {
    "Frame_Shift_Del", "Frame_Shift_Ins", "Nonsense_Mutation",
    "Splice_Site", "Translation_Start_Site", "Nonstop_Mutation",
}
```

| 항목 | 값 |
| --- | ---: |
| DepMap damaging 유전자 수 | 19,578 |
| TCGA MAF 유전자 수(HUGO 심볼) | 18,948 |
| **공통 유전자(feature 로 사용)** | **16,245** |

| 유전자 | DepMap damaging(근사) 비율 | TCGA damaging(근사) 비율 |
| --- | ---: | ---: |
| `TP53` | 57.8% | 12.4% |

TP53 하나만 봐도 두 코호트 간 격차가 크다. 원인은 생물학이 아니라
근사 방식의 한계다 — TCGA MC3 MAF 에서 TP53 은 missense 변이가
2,927건으로 압도적인데, truncating-only 근사는 이를 전혀 잡지 못하고
nonsense/frameshift/splice 계열 1,448건만 포착한다(TP53 은
우성음성(dominant-negative) missense 가 주된 불활성화 경로인 대표
유전자). 즉 TCGA 쪽 damaging 근사가 실제보다 낮게 잡혀 있다 — 이 격차가
외부 검증 ROC-AUC 를 하한 쪽으로 끌어내리는 주 원인으로 추정된다.
해석은 [additional_results.md §5](../research/2026-08-19/additional_results.md)
참고.

## 5. 최종 검증 코호트 (요약)

| 항목 | 값 |
| --- | --- |
| n (barcode 매칭 + 라벨 완비) | 10,261 |
| feature 차원 (damaging, 공통 유전자) | 16,245 |
| WGD+ 비율 | 35.8% |
| 라벨 | WGD 만 (CIN/LOH 대응 지표는 확보하지 못함 — §"남은 과제") |

CIN/LOH 에 대응하는 지표(aneuploidy score, LOH fraction)는 Taylor et
al. 2018(Cancer Cell) supplementary table 에 있을 것으로 보이나
페이월로 정확한 테이블 번호를 확인하지 못했다 — 받으면 이 문서와
`src/data/tcga.py` 를 갱신한다.
