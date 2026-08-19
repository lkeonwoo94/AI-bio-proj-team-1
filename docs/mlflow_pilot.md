# MLflow 추적 파일럿

`feature/mlflow-tracking-pilot` 브랜치. 기존 방식(파일명 prefix로
실험을 구분 — `day10_model_comparison.csv`, `day26_signature_panel_metrics.csv`
등)을 MLflow 로 대체할 수 있는지 평가하기 위한 최소 스캐폴딩이다.
**기존 스크립트(01\~36)는 전혀 건드리지 않았다** — 지금까지의 결과·문서·
재현 커맨드는 이 브랜치와 무관하게 그대로 유효하다.

## 왜 시도하나

파일명 컨벤션 방식은 실제로 사고를 냈다 — 07/08/09 스크립트를
`--model random_forest` 로 재실행했을 때 파일명에 모델명 suffix 가
없어 이전 Elastic Net 결과를 덮어썼고, git history 에서 복구해야 했다
(`08-16/final_conclusion.md` 작업 중 여러 번 발생). MLflow 는 run 마다
자동으로 격리되므로 이런 사고가 구조적으로 어려워진다는 가설을 검증한다.

## 구성

* `src/tracking/mlflow_utils.py` — 최소 wrapper. tracking URI 설정,
  experiment 이름 규칙, fold 지표 로깅 헬퍼.
* `scripts/37_mlflow_pilot.py` — `run_nested_cv()`(기존 §13 원칙 그대로)
  를 돌리고, 결과를 CSV 대신 MLflow run 으로 기록한다.

실험/run 이름 규칙:

* experiment: `"{target}_{representation}"` (예: `wgd_gene`)
* run: parent = 모델명, child = `fold{N}` (outer 5-fold 를 nested run 으로)

## 실행

```bash
# 최초 1회 — mlflow 는 .venv 에만 설치돼 있다(시스템 pip 는 PEP 668 로 막혀 있음)
.venv/bin/pip install mlflow

# 파일럿 실행 (기본: WGD만, Random Forest)
.venv/bin/python scripts/37_mlflow_pilot.py
.venv/bin/python scripts/37_mlflow_pilot.py --targets wgd cin loh   # 전체

# UI 로 확인 (http://127.0.0.1:5000)
.venv/bin/mlflow ui --backend-store-uri sqlite:///mlflow.db
```

tracking 데이터는 `mlflow.db`(SQLite, run/metric/param) 와 `mlruns/`
(artifact — CSV 등)에 로컬로 쌓인다. 둘 다 `.gitignore` 에 등록돼 있다
— `data/` 와 같은 이유로, 각자 로컬에서 스크립트를 다시 돌려 재현한다.

## 확인된 것

* WGD/Random Forest 로 실행한 결과, parent run 의 평균 지표
  (ROC-AUC 0.765, PR-AUC 0.841, Balanced Acc 0.715, Sensitivity 0.752,
  Specificity 0.677, Brier 0.204)가 `day10_model_comparison.csv` 의
  random_forest/wgd 행과 정확히 일치한다 — 기존 파이프라인을 그대로
  재사용했다는 뜻이고(계산 로직은 안 바꿈), MLflow 로 옮겨도 결과가
  달라지지 않는다는 것도 확인했다.
* 5개 outer fold 가 child run 으로, 그 fold별 하이퍼파라미터
  (`best_params`)와 지표가 개별 run 의 params/metrics 로 정확히
  기록됐다 — 지금까지 CSV 한 줄로 뭉뚱그려 봐야 했던 것을 MLflow UI
  에서 run 단위로 펼쳐 볼 수 있다.
* feature importance(`day07_aggregate_selection.py` 산출물과 같은
  내용)가 CSV artifact 로 parent run 에 붙어, run 하나만 열어도
  성능·하이퍼파라미터·feature importance 를 한번에 볼 수 있다.

## 한 걸음 겪은 문제

* MLflow 3.x 부터 순수 파일 기반 backend(`file:./mlruns`)가
  maintenance mode 로 바뀌어 새 run 기록 시 예외를 던진다. SQLite
  backend(`sqlite:///mlflow.db`)로 바꿔 해결했다 — 서버 세팅이 필요
  없다는 장점은 그대로 유지된다.
* 시스템 Python 은 Kali 의 externally-managed 정책(PEP 668)으로 pip
  설치가 막혀 있어, 프로젝트에 이미 있는 `.venv/`(system-site-packages
  옵션으로 만들어짐)에 설치했다. 앞으로 이 파일럿을 확장하려면
  `.venv/bin/python` 으로 실행해야 한다(시스템 `python` 에는 mlflow 가
  없다).

## 다음 결정

파일럿이 팀에서 유용하다고 판단되면:

1. `requirements.txt` 에 이미 추가된 `mlflow` 를 정식 의존성으로 확정
2. 다른 스크립트(예: `06_compare_models.py`, `19_pathway_representation.py`)
   도 점진적으로 MLflow 로깅을 추가 — 기존 CSV 저장은 유지한 채
   **병행**하는 것을 권장(문서가 이미 CSV 파일명을 많이 참조하고
   있어서 한 번에 전환하면 문서 링크가 다 깨진다)
3. 팀이 공유 tracking server 를 쓸지, 로컬 SQLite 로 각자 확인만 할지
   결정 — 후자면 지금 상태로 충분하고 추가 인프라가 필요 없다

필요 없다고 판단되면 이 브랜치를 그냥 버리면 된다 — main 은 전혀
바뀌지 않았다.
