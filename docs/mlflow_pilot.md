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

## 실행 — 가상환경은 `uv` 로 구성

시스템 Python(Kali)은 PEP 668 로 pip 설치 자체가 막혀 있어, `uv` 로
`.venv/` 를 만들고 그 안에만 설치한다. **`--system-site-packages` 를
반드시 켠다** — apt 로 이미 깔려 있는 `pandas`(2.2.3+dfsg),
`scikit-learn`(1.4.2+dfsg) 를 그대로 재사용하기 위해서다. 이게 왜
중요한지는 아래 "겪은 문제" 참고.

```bash
# 최초 1회 — venv 생성 + mlflow-skinny 설치
uv venv .venv --system-site-packages --python 3.13
uv pip install mlflow-skinny --python .venv/bin/python

# xgboost/catboost 도 필요하면(다른 스크립트용) numpy/pandas 를 명시적으로
# 고정해서 같이 설치 — 안 고정하면 uv 가 최신 numpy/pandas 를 새로 받는다.
uv pip install "numpy==1.26.4" "pandas==2.2.3" xgboost catboost \
  --python .venv/bin/python

# 파일럿 실행 (기본: WGD만, Random Forest)
.venv/bin/python scripts/37_mlflow_pilot.py
.venv/bin/python scripts/37_mlflow_pilot.py --targets wgd cin loh   # 전체

# UI 로 확인 (http://127.0.0.1:5000) — .venv 를 건드리지 않는 uvx 로 실행
uvx --from mlflow mlflow ui --backend-store-uri sqlite:///mlflow.db
```

**정정**: 처음에는 `mlflow-skinny` 에 `fastapi`/`starlette`/`uvicorn`
이 포함돼 있어 `.venv/bin/mlflow ui` 로도 UI 가 뜬다고 적었는데, 틀렸다.
`curl` 로 HTTP 200 을 받긴 했지만 **그 응답 본문이 실제 UI 가 아니라
"landing page (index.html) not found" 에러 페이지**였다(상태 코드만
확인하고 내용을 안 봐서 놓쳤다). `mlflow-skinny` 는 UI 정적 파일
(`index.html`, JS/CSS 번들)을 아예 포함하지 않는다 — 그건 full
`mlflow` 패키지에만 들어있다.

**해결책**: full `mlflow` 를 실험용 `.venv` 에 바로 설치하면 앞서 겪은
것과 같은 이유로 `sklearn`/`pandas` 버전이 다시 드리프트될 위험이
있다. 대신 `uvx --from mlflow mlflow ui ...` 로 **완전히 격리된 임시
환경**에서 UI 서버만 띄운다 — `.venv` 는 전혀 안 건드리고, 매번 실행할
때마다 uv 캐시에서 즉시 재사용된다(최초 1회만 다운로드). `curl` 로
응답 본문에 `<title>MLflow</title>` 와 JS 번들 참조가 있는지까지
확인해서 이번엔 진짜로 검증했다.

`torch`(multi-task ANN 용)는 기본으로 설치하지 않았다 — CUDA 관련
nvidia 패키지를 대량으로 끌고 오고(수백MB\~1GB대), numpy 버전 요구
사항이 까다로워 실제로 pandas/numpy 를 강제로 새 버전으로 올리는
원인이 됐다(아래 참고). 필요하면 `numpy`/`pandas` 를 먼저 고정한 뒤
`uv pip install torch --python .venv/bin/python` 로 따로 시도한다.

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
* 나머지 4개 모델(Logistic, Elastic Net, XGBoost, CatBoost)도 3개
  표현형 전부 돌려 총 **15개 parent run**(5모델×3표현형)을 채웠다 —
  모든 조합의 `mean_roc_auc` 가 `day10_model_comparison.csv` 와
  소수점 셋째 자리까지 정확히 일치했다.

### 대시보드 꾸미기

기본 실행 상태는 run 이름이 모델명뿐이라(`random_forest`) 목록이
길어지면 구분하기 어렵다. `mlflow.tracking.MlflowClient()` 로 기존
15개 run 을 다음과 같이 정리했다(재계산 없이 메타데이터만 갱신 —
`update_run`/`set_tag` 는 이미 기록된 run 에도 적용된다):

* run 이름을 `{model}_{target}`(예: `random_forest_wgd`)로 변경,
  fold child run 은 `{model}_{target}_fold{N}` 으로.
* 태그 추가: `representation`(gene/pathway/signature 구분용, 지금은
  `gene` 뿐), `target_label`(WGD/CIN/LOH), `model_label`(사람이 읽는
  이름), `model_family`(linear/tree — UI 필터·색상 구분용).
* `mlflow.note.content` 태그로 run 설명 추가 — MLflow UI 가 이 태그를
  자동으로 "Description" 칸에 보여준다.

앞으로 새로 실행하는 run(`scripts/37_mlflow_pilot.py`)은 처음부터
이 이름·태그를 달고 기록되도록 스크립트 자체를 고쳤다.

**대시보드 스냅샷** — 헤드리스 환경이라 `mlflow ui` 화면을 직접
스크린샷할 수 없어서, 같은 데이터를 `MlflowClient().search_runs()`
로 쿼리해 그림으로 재현하는 스크립트(`scripts/38_plot_mlflow_dashboard.py`)
를 만들었다. CSV 를 다시 읽는 게 아니라 **MLflow 저장소에 실제로
기록된 15개 run 에서** ROC-AUC/Balanced Accuracy/Brier 를 가져와
그린다 — MLflow 가 진짜 정답 소스가 됐다는 것을 보여주는 그림이다.

```bash
.venv/bin/python scripts/38_plot_mlflow_dashboard.py --out /path/to/snapshot.png
```

## 겪은 문제

* MLflow 3.x 부터 순수 파일 기반 backend(`file:./mlruns`)가
  maintenance mode 로 바뀌어 새 run 기록 시 예외를 던진다. SQLite
  backend(`sqlite:///mlflow.db`)로 바꿔 해결했다 — 서버 세팅이 필요
  없다는 장점은 그대로 유지된다.
* 시스템 Python 은 Kali 의 externally-managed 정책(PEP 668)으로 pip
  설치가 막혀 있어, `.venv/`(system-site-packages 옵션)에 설치했다.
  앞으로 이 파일럿을 실행하려면 `.venv/bin/python` 을 써야 한다.
* **`uv pip install -r requirements.txt` 를 그대로 돌리면 위험하다.**
  `--system-site-packages` 로 만든 venv 라도, `uv` 는 이미 apt 로 깔려
  있는 `pandas`(2.2.3)/`scikit-learn`(1.4.2) 를 무시하고 PyPI 최신
  버전(`pandas==3.0.5`, `scikit-learn==1.9.0`)을 새로 받아 venv 안에
  덮어썼다 — 게다가 `torch` 의존성 때문에 CUDA 관련 nvidia 패키지까지
  줄줄이 딸려와 venv 가 5.2GB 까지 불어났다. 이 프로젝트의 모든 결과는
  `scikit-learn 1.4.2` 기준으로 재현성을 검증해왔기 때문에(예:
  `RandomForestClassifier` 의 기본 동작이 버전마다 달라질 수 있음),
  이 상태로 실험을 돌리면 지금까지의 수치와 미묘하게 달라질 위험이
  있었다.
  실제로 이 문제를 만들면서 **기존에 있던 `.venv/`(752MB, 원래
  pandas/sklearn 은 apt 버전과 같았고 xgboost/catboost/torch 도 이미
  설치돼 있었음)를 실수로 삭제**했다 — 정확히 어떤 버전이 들어있었는지
  기록해두지 않은 채로. 복구는 다음 순서로 했다:
  1. `mlflow-skinny`(사용하지 않는 `sklearn`/`skops` 등 안 끌고 옴)만
     따로 설치해 pandas/sklearn 버전을 건드리지 않는 것을 확인.
  2. `xgboost`/`catboost` 는 `numpy==1.26.4`/`pandas==2.2.3` 를 **명시적으로
     고정**한 채 설치해 버전 드리프트를 막았다.
  3. 파일럿 스크립트를 다시 돌려 fold 별 ROC-AUC(0.800/0.785/0.719/
     0.803/0.719, 평균 0.765)가 삭제 전과 **정확히 같다**는 것으로
     `pandas`/`scikit-learn` 버전이 원래대로 돌아왔음을 재확인했다.
  4. `torch` 는 복구하지 않았다(위 참고) — multi-task ANN 스크립트를
     쓸 일이 있으면 그때 numpy/pandas 를 고정한 채로 따로 설치한다.

  **교훈**: `uv` 로 기존 apt 기반 환경을 다루는 프로젝트에서는 절대
  `uv pip install -r requirements.txt` 를 통째로 돌리지 말고, 새로
  필요한 패키지만 골라서(가능하면 numpy/pandas/scikit-learn 버전을
  명시적으로 고정하고) 설치해야 한다.

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
