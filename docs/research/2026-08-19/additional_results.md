# 추가 실험 결과 (2026-08-19)

[2026-08-16/final_conclusion.md](../2026-08-16/final_conclusion.md) 이후 진행한
다섯 개 실험의 상세 내용을 모은 문서다. 앞의 둘(①②)은 "보완해야 할 점" 4·5번에
대한 응답이고, 뒤의 셋(③④⑤)은 08-16 문서의 "Future Work" 절에서 실행 가능성
순으로 제안했던 항목을 실제로 실행한 결과다. 요약과 결론은
[final_conclusion.md](final_conclusion.md) 를 참고한다.

---

## ① 암종별 성능 편차 — 무엇을 시도했고 어디서 멈췄는가

"보완해야 할 점" 4번(암종에 따라 예측 성능 차이가 큼, 유효한 mutation
패턴이 존재하는 암종을 확인 필요)에 대한 실험 결과를 모은다. 08-16
문서 §26⑤ 의 진단·후속 실험(암종 내부 학습)·가설 검정을 한곳에 정리한
것으로, 각 실험의 원 출처는 08-16 §26⑤ 와 `lineage_specific_models.md`
를 참고한다.

### 1단계 — 편차가 실재한다는 진단

lineage 를 분리해 검증하면 성능이 떨어진다 (random 5×5 CV 대비
GroupKFold 는 −0.046\~−0.069, 08-16 §26⑤). Leave-One-Lineage-Out(LOLO,
24종)에서는 암종별 ROC-AUC 가 0.314\~0.882 로 매우 크게 갈린다 — WGD
기준 3종, CIN 기준 6종이 무작위 수준(0.5) 미만이다.

**Random Forest 로도 같은 진단이 나온다.** GroupKFold 감소폭은 WGD
−0.065, CIN −0.056, LOH −0.047 로 Elastic Net(−0.062/−0.046/−0.069)과
방향·크기가 비슷하다. RF 의 LOLO 최저 암종도 겹친다 — Eye(WGD 0.188,
LOH 0.129), Lung(WGD 0.443), Pancreas(WGD 0.437) 로 Elastic Net 이
지목한 Eye·Lung·Cervix·Pancreas 와 대체로 일치한다. 즉 편차 자체는
모델을 가리지 않는 현상이다.

### 2단계 — "해당 암종만으로 다시 학습해도 개선 안 됨" 확인

세포주 60개 이상 9종에서 그 암종 데이터만으로 학습·평가한 결과(암종
내부 학습), LOLO 를 앞서지 못했다(평균 차이 WGD −0.046, CIN +0.011,
LOH −0.018 — CIN/LOH 는 LOLO 와 동일 label 정의로 맞춤). Lung 의 WGD 는
LOLO 0.449, 내부 학습 0.494 로 **둘 다 무작위 수준**이다. 즉 "다른
암종으로 배워서 전이가 안 되는 것"이 아니라 **"그 암종 안에 애초에
mutation-only 로 학습 가능한 신호가 없는 것"** 에 가깝다는 뜻이다
(Figure 7, `lineage_specific_models.md`).

### 3단계 — 왜 어떤 암종엔 신호가 없는지, 다섯 가설 검정

"어떤 암종에서 mutation 패턴이 유효한가"를 직접 설명해 줄 후보 변수를
다섯 개 시험했다. WGD 기준으로는 전부 기각됐다(Figure 8, 08-16 §26⑤).

| 가설 | Spearman rho | p |
| --- | ---: | ---: |
| WGD+ 기저율 편차 | +0.037 | 0.865 |
| 세포주 수 | +0.095 | 0.658 |
| TP53 변이율 | +0.148 | 0.491 |
| 세포주당 평균 mutation burden | −0.201 | 0.347 |
| TP53 변이율의 극단성 | +0.216 | 0.311 |

Fibroblast(TP53 변이율 10%, AUC 0.85)와 Thyroid(70%, AUC 0.88)가 거의
반대되는 TP53 변이율에서 똑같이 높은 성능을 보이는 것처럼, 어느 변수를
기준으로 봐도 성공/실패 사례가 뒤섞여 나타난다(Figure 8).

**Random Forest, 그리고 CIN·LOH 까지 넓혀 총 6개 조합(2모델×3표현형)
으로 재검정했다.** ③④⑤ 세 가설의 Spearman rho(p):

| 가설 | EN/WGD | EN/CIN | EN/LOH | RF/WGD | RF/CIN | RF/LOH |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| TP53 변이율 | +0.148 (.491) | −0.201 (.347) | +0.177 (.407) | +0.249 (.241) | +0.014 (.949) | +0.107 (.619) |
| mutation burden | −0.201 (.347) | +0.143 (.504) | +0.390 (.059) | −0.024 (.910) | +0.190 (.375) | **+0.416 (.043)** |
| TP53 변이율 극단성 | +0.216 (.311) | +0.324 (.123) | +0.258 (.223) | +0.289 (.171) | +0.301 (.153) | **+0.406 (.049)** |

18번 검정 중 16번은 기존과 같이 기각이다. 굵게 표시한 RF/LOH 의 두
항목만 raw p<0.05 다. **다만 이걸 "발견"으로 읽으면 안 된다.** 이
표만으로 18번, Figure 8 재현까지 포함하면 30번 가까운 검정을 했고
Bonferroni 보정 기준(α=0.05/30≈0.0017)에는 두 값 다 한참 못 미친다.
α=0.05 에서 30번 검정하면 우연히 1\~2 번은 p<0.05 가 나오는 게
정상이므로, 이 결과는 그 기대치 안에 있다.

다만 완전히 무시하기도 애매한 구석이 있다. mutation burden 가설은
LOH 에서 EN(+0.390, p=.059)과 RF(+0.416, p=.043)가 **같은 방향, 비슷한
크기로 나온다** — 다른 조합들처럼 모델 바꾸면 부호까지 흔들리는 것과는
다르다. 이게 진짜 신호인지, 아니면 LOH 라벨이 median split 이라 CIN
보다 클래스 균형이 더 타이트해서 생기는 통계적 우연인지는 지금 데이터
(lineage 24개)로 구분할 수 없다. **결론을 바꾸지 않되, LOH 의 mutation
burden 관련성은 추가 확인이 필요한 약한 신호로 따로 기록해 둔다.**

Figure 8 은 6개 조합 전부 저장했다
(`fig8_lineage_hypotheses_{elastic_net,random_forest}_{wgd,cin,loh}.png`).

### 결론 — 원인 규명은 못 했지만 범위는 좁혔다

**"어떤 암종에서 mutation 패턴이 유효한지"는 예측할 수 없다는 것이
현재까지의 결론이다.** 단순 단변량 교란변수(기저율, 표본 크기, 가장
중요한 유전자의 변이율과 그 극단성, 전체 mutation burden) 로는 설명되지
않는다는 점은 상당히 확실해졌으나, 진짜 원인은 규명하지 못했다. lineage
가 24종뿐이라 통계적 검정력 자체가 낮고(|rho|>0.4 는 되어야 유의),
암종 내부 학습도 세포주가 60\~226 개로 작아 fold 간 표준편차 중앙값이
0.123 에 달해 소폭의 차이는 잡음과 구분되지 않는다. 이 이상의 규명은
더 많은 세포주 확보나 lineage 특이적 상호작용을 볼 수 있는 다른 종류의
분석이 필요하며, 본 연구의 데이터 범위 안에서는 답하기 어렵다.

재현: `python scripts/09_lineage_validation.py --model {elastic_net,random_forest}`,
`python scripts/11_lineage_specific.py`,
`python scripts/15_lineage_hypothesis_test.py --model {elastic_net,random_forest} --target {wgd,cin,loh}`,
`python scripts/16_plot_lineage_hypotheses.py --model {elastic_net,random_forest} --target {wgd,cin,loh}`.

---

## ② CIN/LOH 이진화가 정보를 버리는가 — 회귀로 직접 검증

"보완해야 할 점" 5번(CIN/LOH 를 high/low 로 나누면서 정보가 손실됨,
회귀로 실제 연속값을 예측해 분류 결과와 비교 필요)에 대한 실험이다.

### 무엇을 했는가

같은 mutation feature 로 CIN·LoHFraction 의 **연속값을 직접 회귀
예측**했다(Elastic Net regression, Random Forest regressor — 기존
분류 모델과 계열을 맞춤). Pipeline 구조(희귀 변이 필터, outer 5-fold)는
분류와 동일하게 유지했다. 다만 지금까지의 lineage 실험과 달리 random
split 만 썼다 — 이진화 손실 여부를 확인하는 것이 목적이라 검증 방식을
동시에 바꾸지 않았다.

### 결과

| 표현형 | 모델 | 분류 ROC-AUC | 회귀 R² | 회귀 Spearman rho |
| --- | --- | ---: | ---: | ---: |
| CIN | Elastic Net | 0.681 | 0.227 | 0.453 |
| CIN | Random Forest | 0.734 | 0.267 | 0.488 |
| LoHFraction | Elastic Net | 0.711 | 0.155 | 0.431 |
| LoHFraction | Random Forest | 0.730 | 0.170 | 0.451 |

ROC-AUC 와 Spearman rho 는 척도가 달라 직접 등치할 수 없다. 방향을
가늠하기 위해 AUC 를 `2×(AUC-0.5)` 로 rho 와 같은 0\~1 스케일에
**근사 환산**해서 비교했다(엄밀한 통계적 등가는 아니다, Figure 9).

| 표현형 | 모델 | 분류(환산) | 회귀 rho | 차이 |
| --- | --- | ---: | ---: | ---: |
| CIN | Elastic Net | 0.362 | 0.453 | **+0.091** |
| CIN | Random Forest | 0.468 | 0.488 | +0.020 |
| LoHFraction | Elastic Net | 0.422 | 0.431 | +0.009 |
| LoHFraction | Random Forest | 0.460 | 0.451 | −0.009 |

### 해석

**세 조합은 거의 차이가 없고(±0.02), CIN + Elastic Net 한 조합만
회귀가 뚜렷이 높다(+0.091).** 즉:

* Random Forest 는 CIN·LOH 어느 쪽에서도 이진화로 정보를 거의
  잃지 않는다 — 비선형 모델이 중앙값 근처의 애매한 경계를 이미 어느
  정도 잘 처리하고 있었다는 뜻으로 읽을 수 있다.
* LoHFraction 은 모델과 무관하게 이진화 손실이 거의 없다.
* **CIN 을 선형 모델(Elastic Net)로 볼 때만 이진화가 신호를 깎아
  먹는다.** CIN 분포가 이봉형(Figure 2)이라는 점과 맞물려 볼 수 있다
  — 중앙값 근처에 세포주가 상대적으로 적어 median split 자체는
  덜 위험하지만, 선형 모델이 그 비선형적인 분포 형태를 이진화 이후에는
  더 못 살리는 것으로 보인다.

**결론을 바꾸지는 않는다.** 08-16 §26①의 "제한적으로 가능하다"는
판단은 회귀로 봐도 유지된다(R² 0.15\~0.27 은 여전히 중간 정도의
설명력이다). 다만 **Elastic Net 기반 CIN 패널(08-16 §26③·④)은 이진화
손실을 어느 정도 안고 있을 수 있다**는 점을 한계로 추가한다 — 향후
회귀 기반 feature selection 으로 CIN 패널을 다시 뽑아보는 것이 자연스러운
후속 과제다.

Figure 9(`fig9_regression_vs_classification.png`)에 네 조합을 나란히
그렸다.

재현: `python scripts/17_regression_vs_classification.py`,
`python scripts/18_plot_regression_vs_classification.py`.

---

## ③ Pathway 단위 mutation burden — 실행 결과 (음성)

08-16 문서의 Related Work 절에서 확인한 "더 뭉뚱그린 재집계 단위" 두
방향 중 실행 가능성이 높다고 판단했던 것을 실제로 실행했다.

**무엇을**: 20,132 개 유전자 컬럼을 MSigDB Hallmark 또는 KEGG 의 생물학적
경로(DNA damage repair, cell cycle checkpoint, chromatin remodeling 등)로
묶어, "이 세포주가 이 경로 유전자 중 몇 개에 damaging/hotspot mutation 을
가졌는가" 를 새 feature 로 만들었다.

**왜 시도했는가**: 지금 가진 데이터(`cohort.X`)만으로 되는 재집계다. gene-set
주석은 표현형과 무관한 정적 메타데이터라 새로 받아도 §13 누출 위험이 없다.
sparsity 문제(hotspot 554개 중 10개 이상 세포주에서 관측되는 건 36개뿐)를
정면으로 줄이는 접근이라, 지금까지 모델을 5개나 바꿔도 0.73\~0.77 에서
움직이지 않은 천장(08-16 §26②, RF/XGBoost/CatBoost feature importance
상관 0.56\~0.61)을 뚫을 실질적 후보였다.

**절차**: MSigDB(C2 curated 또는 Hallmark) 의 DNA repair·cell cycle·chromatin
관련 gene set 목록을 받아 `src/features/pathway_aggregate.py` 에 유전자
컬럼을 pathway 컬럼으로 접는 transformer 를 만들고(`RareMutationFilter`
와 같은 자리, Pipeline 안에 넣어 fold 마다 일관되게 적용), 기존
`05_run_cv.py` 파이프라인으로 pathway 표현과 유전자 표현의 성능을
같은 nested CV 조건에서 비교했다.

**실행 결과**: MSigDB Hallmark 5개(DNA Repair, G2-M Checkpoint, E2F
Targets, Mitotic Spindle, p53 Pathway) + KEGG 6개(DNA repair 세부 경로:
BER/MMR/NER/HR/NHEJ/Fanconi anemia) — Enrichr 공개 미러에서 gene-set
목록을 받아 hotspot/damaging 분리 시 22개 feature 로 접었다(대부분
90%+ 매칭). 유전자 단위(필터 후 \~2,062개)와 같은 random 5-fold 조건에서
비교했다(Figure 10).

| 표현형 | 모델 | 유전자 단위 | Pathway(22개) | 차이 |
| --- | --- | ---: | ---: | ---: |
| WGD | Logistic | 0.723 | 0.674 | -0.049 |
| CIN | Logistic | 0.672 | 0.643 | -0.029 |
| LOH | Logistic | 0.683 | 0.648 | -0.035 |
| WGD | Random Forest | 0.765 | 0.720 | -0.045 |
| CIN | Random Forest | 0.734 | 0.691 | -0.043 |
| LOH | Random Forest | 0.730 | 0.702 | -0.028 |

**6개 조합 전부 pathway 쪽이 낮다(-0.028\~-0.049).** "sparsity 를 줄이면
천장을 뚫는다"는 가설은 기각됐다. 원인은 짐작대로다 — TP53 이 유전자
단위에서 압도적 1위 신호였는데(08-16 §26③), pathway 로 묶으면 "TP53 이
속한 DNA Repair 경로 안 mutation 비율"이 되어 나머지 100여 개 약한 신호
유전자와 평균 내지듯 희석된다. **정보 손실이 sparsity 완화 이득보다
컸다.** 이 결과는 오히려 "핵심 신호가 소수의 특정 유전자에 집중되어
있다"는 08-16 §26③·④의 기존 결론을 다른 각도에서 재확인해 준다.

재현: `python scripts/19_pathway_representation.py`,
`python scripts/20_plot_pathway_vs_gene.py`.

---

## ④ Mutation signature(96-class) — 실행 결과 (양성, pathway 와 정반대)

**무엇을**: DepMap 이 별도로 배포하는 원시 MAF(`OmicsSomaticMutations.csv`,
`Chrom`/`Pos`/`Ref`/`Alt` 컬럼 포함)를 받아 trinucleotide context 를
계산하고, COSMIC SBS mutational signature 를 세포주별 feature 로 썼다.

**왜 pathway 와 다른 과제로 분리했는가**: 기존 `OmicsSomaticMutationsMatrix
{Hotspot,Damaging}.csv` 는 이미 유전자×세포주 이진 행렬로 집계되어 위치·
염기 정보가 사라진 상태라, 이 접근은 기존 파이프라인에 재집계 단계 하나를
추가하는 정도로 끝나지 않는다 — 원시 파일을 새로 받고, 대용량 MAF 파싱과
signature 추출을 별도로 구축해야 했다.

**실행 방법**: `OmicsSomaticMutations.csv`(원시 MAF, 1,172,689행)를
받아 default 프로파일의 SNV 644,520건을 추렸다. SigProfilerExtractor
같은 무거운 signature 추출 도구는 쓰지 않고, hg38 참조 게놈(UCSC
2bit, 796MB)에서 변이 위치의 앞뒤 염기를 직접 읽어 COSMIC SBS 표준
96-class(치환 6종 × context 16종)로 분류한 뒤, 세포주별 비율 행렬(1,631
× 96)을 만들었다 — NMF 기반 signature 분해 없이 원시 96-class 분포
자체를 feature 로 썼다(`src/features/mutation_signature.py`).

이 계산은 fold 와 무관한 고정 매핑(참조 게놈 서열)이라 pathway 매핑과
같은 이유로 §13 누출 위험이 없다. 유전자 단위(필터 후 \~2,062개)와 같은
random 5-fold 조건에서 비교했다(Figure 12).

| 표현형 | 모델 | 유전자 단위 | Signature(96개) | 차이 |
| --- | --- | ---: | ---: | ---: |
| WGD | Logistic | 0.723 | 0.713 | -0.010 |
| CIN | Logistic | 0.672 | 0.711 | **+0.039** |
| LOH | Logistic | 0.683 | 0.693 | +0.010 |
| WGD | Random Forest | 0.765 | 0.770 | +0.005 |
| CIN | Random Forest | 0.734 | 0.762 | **+0.028** |
| LOH | Random Forest | 0.730 | 0.743 | +0.013 |

**6개 조합 중 5개가 개선됐다 — pathway 실험과 정반대다.** WGD/Logistic
한 조합만 소폭 하락(-0.010)이고, 나머지는 전부 양수, 특히 CIN 에서
뚜렷하다(+0.028\~+0.039). **96개라는 훨씬 적은 feature 수로 유전자
\~2,062개 수준의 성능을 냈다는 점이 핵심이다.**

pathway 집계가 실패한 것과 signature 가 성공한 것을 나란히 놓으면
이유가 분명해진다 — pathway 는 유전자 정체성 축(TP53 이 어떤 경로에
속하는가)을 뭉개서 정보를 잃었지만, signature 는 애초에 **다른 축의
정보**(어떤 변이 발생 과정이 이 세포주를 지배했는가 — 예: APOBEC
활성, mismatch repair 결손, 자외선 손상)를 담고 있다. 이 과정들은
유전체 불안정성과 기전적으로 연결되어 있어(예: MMR 결손은 그 자체로
불안정성의 원인) 유전자 단위 신호에 없던 것을 보탠 것으로 보인다.
CIN 에서 개선폭이 가장 큰 것도 이 해석과 맞는다 — CIN 은 애초에
"어떤 과정으로 염색체가 불안정해졌는가"라는 질문과 가장 가깝다.

**한계**: (1) NMF 기반 정식 SBS signature exposure(COSMIC 카탈로그
대비 분해)가 아니라 원시 96-class 분포다 — 더 정교한 분해를 거치면
추가로 개선될 수도 있다. (2) 6개 조합 중 5개라는 표본이 작아 우연의
여지가 있다 — 다른 seed·fold 구성에서도 재현되는지는 확인하지 않았다.
(3) 이 96개 feature 를 08-16 §26③·④ 의 반복 selection·최소 패널 분석에
아직 연결하지 않았다 — "패널에 signature feature 를 섞으면 더
나아지는가"는 열린 질문으로 남는다.

재현: `python scripts/23_build_mutation_signature.py`,
`python scripts/24_signature_representation.py`,
`python scripts/25_plot_signature_vs_gene.py`. 참조 게놈은
`data/reference/`(git 미추적)에 둔다.

---

## ⑤ TCGA 독립 코호트 검증 — 실행 결과 (하한 추정치)

08-16 문서 "이 결론의 한계" 6번(§27, "확정적인 바이오마커라 부를 수
없다")에 대한 후속 실험이다. DepMap 세포주 내부 cross-validation 만으로는
부족하다는 지적에 대해, 진짜 독립 코호트인 TCGA 로 재현성을 확인했다.

**데이터**: `mc3.v0.2.8.PUBLIC.maf.gz`(753MB, [GDC MC3 MAF](https://gdc.cancer.gov/about-data/publications/mc3-2017))와
ABSOLUTE ploidy/WGD 결과(`TCGA_mastercalls.abs_tables_JSedit.fixed.txt`,
[Taylor et al. 2018, Cancer Cell](https://www.sciencedirect.com/science/article/pii/S1535610818301119))를
받아 실행했다. CIN/LOH 대응 지표(같은 논문 supplementary table)는
페이월로 정확한 테이블 번호를 확인하지 못해 **WGD 만** 검증했다.

**barcode 매핑 함정**: ABSOLUTE 와 MC3 는 서로 다른 시퀀싱 플레이트/
센터에서 만들어져 전체 barcode 로 join 하면 10,642개 중 12개만
매칭된다. TCGA 데이터 종류 간 병합의 표준 관례대로 앞 15자(참가자+
샘플타입)로 잘라서 맞추면 91%(9,651\~10,261개)가 매칭된다.

**설계**: hotspot 에 대응하는 TCGA 데이터가 없어(큐레이션 hotspot DB
필요) damaging feature 만으로 비교했다. DepMap 의 `LikelyLoF` 판정을
표준 truncating variant class(frameshift/nonsense/splice site/start
loss/stop loss)로 근사했다. 공통 유전자는 16,245개(DepMap 19,578,
TCGA 18,948 중 교집합).

| 단계 | ROC-AUC | n |
| --- | ---: | ---: |
| DepMap 내부(damaging-only, random 5-fold) | 0.762 | 1,631 |
| **TCGA 외부 검증**(DepMap 전체로 학습 → TCGA 예측) | **0.594** | 10,261 |

무작위 수준(0.5)은 넘지만 **내부 대비 크게 떨어진다(−0.168)**(Figure 11).

**다만 이 하락폭을 그대로 "일반화 실패"로 읽으면 안 된다.** TP53
damaging(근사) 비율이 DepMap 57.8% vs TCGA 12.4% 로 코호트 간 격차가
매우 크다. 원인을 추적해보니 **방법론적 문제였다** — TCGA MAF 에서
TP53 은 missense 변이가 2,927건으로 압도적인데, truncating-only 근사
기준은 이를 전혀 잡지 못하고 nonsense/frameshift/splice 계열 1,448건만
포착한다. TP53 은 우성음성(dominant-negative) 기전의 missense 돌연변이가
주된 불활성화 경로인 대표적 유전자라, 이 근사가 **가장 중요한 단일
유전자의 신호를 3분의 2 가까이 놓친 것**이다(Figure 11b).

**결론**: TCGA 외부 검증 ROC-AUC 0.594 는 실제 일반화 성능의 **하한
추정치에 가깝다** — 진짜 값은 이보다 높을 가능성이 크지만, missense
pathogenicity 를 제대로 반영하는 분류기(예: PolyPhen/SIFT/REVEL 점수
활용) 없이는 정확한 값을 알 수 없다. 그럼에도 **내부(0.762)와 완전히
같은 수준일 가능성은 낮다** — 세포주와 실제 종양은 순도(purity),
이질성(heterogeneity), 배양 조건에 따른 선택압이 다르므로 어느 정도의
일반화 격차는 예상된 결과다. "세포주에서 배운 신호가 실제 환자
종양에도 어느 정도(무작위보다는 뚜렷이 높게) 옮겨가지만 완전히
같지는 않다"가 현재 근거로 뒷받침되는 가장 정확한 서술이다.

재현: `python scripts/21_tcga_validation.py`,
`python scripts/22_plot_tcga_validation.py`. 원본 데이터는
`data/gdc/`(git 미추적, `data/depmap/` 과 같은 방식)에 둔다.
