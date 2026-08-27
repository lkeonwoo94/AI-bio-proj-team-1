# TCGA 검증의 "근사값"은 어떻게 낸 것인가

팀원·교수님 질문: **TCGA 일반화 검증에서 쓴 근사값을 어떻게 낸 것인가?**

## 한 줄 답

DepMap 의 `damaging` 판정(VEP LofTool 기반 `LikelyLoF`)에 해당하는 컬럼이
TCGA MC3 MAF 에는 없어서, **MAF 의 variant class 중 표준 truncating 계열만
damaging 으로 세는 방식으로 근사**했다. 근사한 것은 이 한 가지뿐이고,
**WGD 라벨은 근사가 아니다**(ABSOLUTE 결과의 실제 값을 그대로 쓴다).

## 왜 근사가 필요했나

| | DepMap | TCGA (MC3 MAF) |
| --- | --- | --- |
| damaging 판정 | `LikelyLoF` 플래그 (VEP LofTool) | **없음** — variant class 문자열만 있음 |
| hotspot 판정 | `Hotspot` 플래그 | **없음** (큐레이션 hotspot DB 필요) |
| WGD 라벨 | `OmicsGlobalSignatures.WGD` | ABSOLUTE `Genome doublings` |

DepMap 이 쓰는 판정 플래그가 TCGA 쪽에 그대로 존재하지 않는다. 그래서
두 코호트를 같은 feature 종류로 맞추려면 TCGA 쪽을 재구성해야 했다.

## 정확히 무엇을 근사했나

`src/data/tcga.py` 의 다음 집합에 속하는 variant class 만 damaging 1 로 센다.

```python
LOF_CLASSES = {
    "Frame_Shift_Del", "Frame_Shift_Ins", "Nonsense_Mutation",
    "Splice_Site", "Translation_Start_Site", "Nonstop_Mutation",
}
```

* `In_Frame_Del` / `In_Frame_Ins` 는 **제외**한다 — reading frame 을 보존하므로
  표준 LoF 정의에 들어가지 않는다.
* `Missense_Mutation` 도 제외된다. 이게 이 근사의 가장 큰 한계다(아래 참고).
* **hotspot 채널은 아예 만들지 않았다.** 그래서 비교 기준이 되는 DepMap 성능도
  hotspot 을 뺀 **damaging-only** 로 다시 계산한 값을 쓴다
  (`scripts/21_tcga_validation.py` 1단계). 같은 조건끼리 비교하기 위해서다.

근사가 아닌 것:

* **WGD 라벨** — ABSOLUTE 의 `Genome doublings` 컬럼이 이미 doubling 횟수(0/1/2)라,
  DepMap 과 같은 정의로 맞추려고 `>= 1` 을 WGD+ 로 이진화만 했다.
* **barcode 매칭** — ABSOLUTE 와 MC3 는 barcode 뒤쪽(plate/center 코드)이 서로
  달라 전체 문자열로 join 하면 10,642개 중 12개만 맞는다. TCGA 데이터 병합의
  표준 관례대로 **앞 15자**(`TCGA-3A-A9IR-01A`)로 잘라 맞춰 91%(9,651개)가
  매칭된다. 이건 근사가 아니라 관례적 정규화다.

## 이 근사가 얼마나 어긋나는가 — TP53 으로 본 검산

| | DepMap | TCGA |
| --- | ---: | ---: |
| TP53 damaging 보유 비율 | **57.8%** | **12.4%** |

같은 유전자인데 5배 가까이 차이난다. 원인은 생물학이 아니라 근사 방식이다.
TP53 은 우성음성(dominant-negative) **missense** 가 주된 불활성화 경로인
대표 유전자인데, truncating-only 근사는 그걸 하나도 못 잡는다.

| TP53 변이 건수 | Missense | truncating(근사에 잡히는 것) |
| --- | ---: | ---: |
| 검증 코호트(10,261명) 기준 | 2,786 | 1,375 |
| MC3 MAF 전체 기준 | 2,927 | 1,449 |

즉 **TCGA 쪽 damaging 이 실제보다 과소 계상**돼 있다.

## 그래서 결과를 어떻게 읽어야 하나

| 단계 | ROC-AUC | n |
| --- | ---: | ---: |
| DepMap 내부 (damaging-only, random 5-fold) | 0.762 | 1,631 |
| TCGA 외부 검증 | 0.594 | 10,261 |

하락폭 \-0.168 을 **"세포주에서 환자 종양으로 일반화 실패"로 단정하면 안 된다.**
TCGA 쪽 입력 feature 자체가 위 근사 때문에 정보를 잃은 상태라, 이 값은
일반화 성능의 **하한**에 가깝다. 다만 "근사 때문이다"라는 것도 아직 가설이며,
missense 를 포함한 판정(예: VEP/PolyPhen 재주석)으로 다시 만들어 비교해야
확정된다 — 남은 과제다.

CIN/LOH 는 TCGA 검증을 하지 못했다. 대응 지표(aneuploidy score, LOH fraction)가
확보한 ABSOLUTE 파일에 없다.

## 재현

```bash
python scripts/21_tcga_validation.py     # 내부 baseline + 외부 검증
python scripts/22_plot_tcga_validation.py  # Figure 11 (TP53 비율은 원본에서 계산)
```

Figure 11 의 TP53 비율은 예전에 스크립트에 하드코딩돼 있었는데(이 질문이 나온
이유이기도 하다), 지금은 `data/` 가 있으면 매번 원본에서 다시 계산한다.

더 자세한 내용:
[docs/gdc/tcga_data_summary.md](../../gdc/tcga_data_summary.md) §4,
`src/data/tcga.py` docstring.
