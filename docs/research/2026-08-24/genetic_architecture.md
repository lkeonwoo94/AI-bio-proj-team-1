# 변이-암 관계는 monogenic / oligogenic / polygenic 중 무엇인가

## 질문

변이와 암은 monogenic 이야 oligogenic 이야 polygenic 이야?

## 답

일반적으로는 **polygenic(다인자성)**에 가깝다 — 다만 암은 이 세 범주로
깔끔히 나뉘는 게 아니라 스펙트럼이라 좀 더 풀어서 설명하는 게 정확하다.

### 왜 polygenic인가

- 암은 단일 유전자 하나의 변이로 발생하는 경우(monogenic — 예: 낭포성섬유증
  같은 멘델 유전병)가 거의 없다.
- 대신 driver mutation(TP53, KRAS, PIK3CA 등) + tumor suppressor 불활성화 +
  oncogene 활성화 + 유전체 불안정성(WGD/CIN/LOH, 이 프로젝트가 다루는 것) +
  epigenetic 변화 + 면역 회피 등 **여러 단계·여러 유전자·여러 기전이 누적**
  되어야 암이 형성된다 (Hanahan & Weinberg의 "Hallmarks of Cancer"가 이걸
  정리한 유명한 프레임워크).
- 이 프로젝트의 [Fig21](../../../results/figures/fig21_mutation_association.png)만
  봐도 WGD/CIN/LOH 각각에 유의하게 연관된 유전자가 28\~110개씩 나온다 —
  한두 개가 아니라 수십 개.

### 용어를 더 정확히 쓰면

- **Monogenic 암(드묾)**: 유전성 증후군의 경우 특정 단일 배선(germline)
  변이가 강한 위험을 준다 — 예: BRCA1/2(유방/난소암), TP53 생식세포 변이
  (리프라우메니 증후군), APC(가족성 용종증). 이런 경우도 "그 변이 하나가
  곧 암"은 아니고 위험도를 크게 높일 뿐, 실제 암 발생까지는 추가 체세포
  변이가 더 필요하다(그래서 완전히 monogenic이라 보기도 애매하다).
- **대부분의 산발성(sporadic) 암**: **oligogenic\~polygenic** — 소수의 강한
  driver(TP53, KRAS 등)가 핵심 역할을 하지만, 그 driver 하나만으로는
  부족하고 여러 개의 추가 변이·유전체 불안정성이 누적되어야 한다
  (multi-hit / multistep carcinogenesis 모델).
- 유전 가능한 암 **위험도**(risk) 자체는 GWAS 연구들이 polygenic risk
  score로 설명하는 게 표준 — 수백\~수천 개의 흔한 변이가 조금씩 위험을
  더하는 진짜 polygenic 구조.

### 요약

개별 암 발생 기전은 "몇 개의 강한 driver + 다수의 보조 변이"라는 의미에서
**oligogenic-to-polygenic**에 가깝고, 인구 집단 수준의 암 감수성(risk)은
명백히 **polygenic**이다. Monogenic은 유전성 증후군이라는 예외적 소수
사례에만 해당한다.

## Future approach — 이게 이 프로젝트에 갖는 의미

이 프로젝트는 지금까지 유전자 하나씩의 독립적 연관성(Fig21의 단변량
검정)이나 소수 유전자 패널(10\~30개, §16 이하 minimal panel 실험)로
WGD/CIN/LOH를 예측했다. 변이-암 관계가 polygenic이라는 사실은 이 접근의
두 가지 한계와 다음 방향을 시사한다.

1. **단변량 연관성 검정의 한계** — Fig21처럼 유전자를 하나씩 따로 검정하면
   유전자 간 상호작용(epistasis)이나 결합 효과를 놓친다. 지금 쓰는 RF/
   Elastic Net 같은 다변량 모델은 이미 이 문제를 어느 정도 완화하지만,
   "왜 이 조합이 함께 작동하는가"에 대한 명시적 상호작용 항은 다루지
   않는다.
2. **Polygenic risk score(PRS) 스타일 종합 스코어** — 지금의 이진
   분류/패널 접근 대신, 패널 유전자들의 mutation 여부에 가중치를 부여해
   더한 단일 연속 점수(PRS와 유사한 구조)를 만들고, 이 점수 하나로
   WGD/CIN/LOH를 얼마나 잘 설명하는지 보는 실험을 추가할 수 있다 —
   해석 가능성(가중치 = 유전자별 기여도)과 예측 성능을 동시에 얻는 방식.
3. **Oligogenic 조합 탐색** — 현재 minimal panel(10/20/30-gene)은 개별
   중요도 순위로만 유전자를 뽑는다. 대신 2\~3개 유전자의 **조합**이
   단일 유전자보다 표현형을 더 잘 가르는지(상호작용 효과) 탐색해볼 수
   있다 — 예: TP53 + ARID1A 동시 변이가 개별 변이보다 CIN을 더 잘
   예측하는지.

세 방향 모두 아직 구현하지 않은 후속 실험 아이디어로, 실제 착수 전
Fig21/22(연관성 검정)와 §16(minimal panel) 결과를 참고 자료로 삼으면 된다.
