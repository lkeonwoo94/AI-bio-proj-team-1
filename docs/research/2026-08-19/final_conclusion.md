# 최종 결론 갱신 (2026-08-19)

[2026-08-16/final_conclusion.md](../2026-08-16/final_conclusion.md) 의
§26·§27·"이 결론의 한계"·"Day 11/12 Random Forest 재검증"은 그대로
유효하다. 이 문서는 그 이후 진행한 다섯 개 실험(암종별 편차 후속 검정,
CIN/LOH 회귀 검증, Pathway/Signature/TCGA — Future Work 실행)의 결과를
반영해 결론을 갱신한다. 상세 데이터·표·해석은
[additional_results.md](additional_results.md) 를 참고한다.

---

## 갱신된 결론 요약

### 암종별 성능 편차 — 여전히 원인 미상, 범위만 좁힘

08-16 §26⑤ 에서 남겨둔 질문("어떤 암종에서 mutation 패턴이 유효한가")에
Random Forest 로 재검정을 확장하고 mutation burden 가설을 추가했다.
18번의 검정 중 16번은 기각, RF/LOH 두 항목만 raw p<0.05 였으나
Bonferroni 보정(α≈0.0017)에는 못 미쳐 우연 범위 안이다. 다만 LOH 의
mutation burden 관련성(EN +0.390, RF +0.416, 같은 방향·비슷한 크기)은
모델이 바뀌어도 부호가 유지되는 유일한 케이스라, "결론은 안 바뀌지만
계속 지켜볼 약한 신호"로 기록해 둔다.

**결론은 08-16 과 동일하다 — 단순 단변량 교란변수로는 설명되지 않으며,
진짜 원인은 규명하지 못했다.** (상세: [additional_results.md §1](additional_results.md#-암종별-성능-편차--무엇을-시도했고-어디서-멈췄는가))

### CIN/LOH 이진화 손실 — 대체로 없음, EN/CIN 만 예외

회귀로 직접 검증한 결과 CIN·LOH·Random Forest 세 조합은 이진화 손실이
거의 없었다(±0.02). **CIN 을 Elastic Net(선형)으로 볼 때만** 이진화가
신호를 깎아 먹는다(+0.091). 08-16 §26①의 "제한적으로 가능하다"는 판단은
회귀로도 유지되며, Elastic Net 기반 CIN 패널(§26③·④)만 이 손실을
어느 정도 안고 있을 수 있다는 것이 새로 추가된 한계다. (상세:
[additional_results.md §2](additional_results.md#-cinloh-이진화가-정보를-버리는가--회귀로-직접-검증))

### Future Work 3건 실행 결과 — pathway 음성, signature 양성, TCGA 하한추정

08-16 문서가 "Related Work" 절에서 제안했던 세 방향을 모두 실행했다.

| 실험 | 결과 | 핵심 수치 |
| --- | --- | --- |
| Pathway 단위 mutation burden | **음성** | 6/6 조합 하락 (-0.028\~-0.049) |
| Mutation signature(96-class) | **양성** | 5/6 조합 개선 (최대 +0.039, CIN 에서 가장 큼) |
| TCGA 독립 코호트 검증(WGD) | **하한 추정치** | 내부 0.762 → 외부 0.594 (−0.168, 방법론적 과소추정 포함) |

**Pathway 대 Signature 가 정반대로 나온 것 자체가 흥미로운 결과다.**
정보를 유전자 정체성 축으로 뭉뚱그리면(pathway) 손실이 크고, 다른 축
(mutational process)을 새로 더하면(signature) 이득이 난다 — "핵심 신호가
소수의 특정 유전자에 집중돼 있다"는 08-16 §26③·④ 결론과 일관된다.

**TCGA 결과는 일반화 실패로 단정할 수 없다.** TP53 truncating-only 근사가
missense 기반 불활성화(TCGA TP53 변이의 대다수)를 놓쳐 가장 중요한
유전자의 신호를 상당 부분 잃었기 때문에, 0.594 는 진짜 일반화 성능의
하한이지 상한이 아니다. (상세:
[additional_results.md §3–5](additional_results.md#-pathway-단위-mutation-burden--실행-결과-음성))

---

## 이 결론의 한계 (갱신)

08-16 문서의 한계 목록 중 이번 실험으로 상태가 바뀐 두 항목만 갱신한다
— 나머지(1, 2, 4)는 08-16 그대로 유효하다.

3. **암종별 성능 편차의 원인.** ~~규명하지 못했다~~ → **여전히
   규명하지 못했다.** 검정 범위를 6개 모델×표현형 조합으로 넓혔지만
   결론은 바뀌지 않았다. LOH 의 mutation burden 관련성만 "지켜볼 약한
   신호"로 추가.
6. **CIN 이진화 손실.** ~~미해결~~ **[해소]** 회귀로 직접 검증 완료 —
   EN/CIN 한 조합만 손실 있음, 나머지는 무시할 수준.

**새로 추가된 한계 (Future Work 실행분):**

7. **TCGA 외부 검증은 WGD 만, 그마저도 하한 추정치다.** CIN/LOH 대응
   지표는 페이월로 확보하지 못했다. TP53 근사 방식이 missense 를
   놓쳐 실제 일반화 성능보다 낮게 나왔을 가능성이 크다 — 정확한 값은
   missense pathogenicity 분류기 없이는 알 수 없다.
8. **Mutation signature 는 원시 96-class 분포이지 정식 NMF 분해가
   아니다.** 5/6 조합 개선이라는 표본도 작아 다른 seed·fold 에서
   재현되는지 확인하지 않았고, 이 96개 feature 를 최소 패널 분석에
   아직 연결하지 못했다.

---

## 남은 과제

* CIN 패널을 회귀 기반 feature selection 으로 다시 뽑아보기 (한계 6 후속)
* Mutation signature(96개)를 §26③·④ 의 패널 selection 에 결합해보기
* TCGA missense pathogenicity 점수(PolyPhen/SIFT/REVEL)를 반영해 TCGA
  검증을 더 정확한 값으로 재추정하기
* CIN/LOH 에 대응하는 TCGA aneuploidy score/LOH fraction 확보(페이월
  뒤 supplementary table 접근이 필요)
