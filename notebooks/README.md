# 노트북

| 파일 | 내용 | Colab |
| --- | --- | --- |
| `01_full_pipeline.ipynb` | 데이터 로드부터 최종 biomarker panel·결론까지 전체 파이프라인 16개 절 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/lkeonwoo94/AI-bio-proj-team-1/blob/main/notebooks/01_full_pipeline.ipynb) |
| `02_key_results.ipynb` | 핵심 결과만 간결하게 — 모델 비교, confusion matrix, feature importance, 최소 패널, 후속 실험 3종 요약, TCGA 검증, 탐색적 분석, 최종 패널 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/lkeonwoo94/AI-bio-proj-team-1/blob/main/notebooks/02_key_results.ipynb) |

위 배지를 누르면 설치 없이 바로 실행할 수 있다. 첫 셀(§0)이 저장소를 클론하고
데이터를 확보한 뒤, 필요한 패키지와 한글 폰트까지 깔아준다.

> 두 배지 모두 주소 앞에 `https://colab.research.google.com/github/` 를 붙인
> 형태다. 이러면 **항상 `main` 의 최신 노트북**을 불러온다. 반대로 Colab 에서
> "드라이브에 사본 저장" 한 링크(`colab.research.google.com/drive/...`)는
> 저장소와 끊긴 별개 사본이라, 이후 push 해도 갱신되지 않는다.
>
> 배지를 눌렀는데 옛 내용이 보이면 Colab 이 캐시한 것이다 — `Ctrl+Shift+R`
> 로 새로고침하거나, 이미 열려 있던 탭을 닫고 새 탭에서 다시 연다.

## 데이터를 어떻게 찾는가 (§0 셀)

1. **로컬** — `data/interim/cohort_*.parquet` 또는 `data/depmap/*.csv` 가 있으면
   그대로 쓴다. 이 경우 드라이브는 아예 건드리지 않는다.
2. **공개 Google Drive 폴더** — 로컬에 없으면 여기서 받는다. 드라이브
   *마운트* 가 아니라 **다운로드**라서, 폴더 주인이 아닌 사람(교수님·팀원)이
   열어도 그대로 실행된다.

폴더를 통째로 받지는 않는다. 그 폴더에는 `hg38.2bit`(800MB), MC3 MAF(750MB),
`OmicsSomaticMutations.csv`(581MB) 까지 들어 있어 2GB 가 넘고, 전부 받으면
구글이 연속 요청을 막아 `gdown` 이 *"Cannot retrieve the public link / have had
many accesses"* 로 실패한다. 그래서 파일 목록만 먼저 받아 **필요한 것만**
골라 내려받는다(총 15MB 남짓).

| 받는 파일 | 위치 | 쓰임 |
| --- | --- | --- |
| `cohort_{X,y,groups}.parquet` | `data/interim/` | 코호트 (없으면 원본 CSV 4개로 폴백) |
| `sbs96_signature_matrix.parquet` | `data/depmap/` | mutation signature(96-class) 절 |
| `tcga_{damaging_matrix,wgd_labels}.parquet` | `data/gdc/` | TCGA 외부 검증 절 |

signature 와 TCGA 는 **파생 데이터가 이미 만들어져 있어서**, `hg38.2bit` 나
750MB MAF 원본 없이도 해당 절을 재현할 수 있다.

## 노트북이 저장소 코드를 그대로 쓴다

노트북 안에 로직 사본을 두지 않고 `src/` 를 import 한다
(`load_cohort` / `run_nested_cv` / `get_model` / `aggregate_selection` /
`viz.style`). 어차피 `results/tables/` 때문에 저장소를 클론하므로, 사본을 두면
코드가 두 벌이 되고 나중에 `src/` 를 고쳤을 때 노트북만 옛 로직으로 남는
드리프트 위험만 생긴다. import 방식이면 **노트북 수치 = 저장소 파이프라인
수치**가 구조적으로 보장된다.

주의: `src/viz/style.py` 는 스크립트용이라 import 시 matplotlib 백엔드를
`Agg` 로 바꾼다. 그대로 두면 노트북에 그림이 하나도 안 나오므로, import 직후
`%matplotlib inline` 으로 되돌린다.

## 무엇을 실제로 학습하고, 무엇을 불러오는가

**노트북 안에서 실제로 계산하는 것**

* **모델 비교(Figure 3)** — outer 5-fold × inner 5-fold nested CV 를 직접 돌린다.
  `RUN_MODELS` 리스트로 범위를 조절한다(01 은 6개 모델 전부, 02 는 Logistic +
  Random Forest).
* **Figure 4 (feature selection 안정성)** — 위 학습이 fold 마다 기록한 중요도를
  집계한 것이라 추가 학습이 없다.
* **Figure 16 (confusion matrix)** — outer fold 의 test 예측을 모아서(pool) 만든다.
* **탐색적 분석** — 유전자-표현형 연관성 검정(Fig 21/22), UMAP(Fig 23/23b),
  CCA(Fig 24/24b/24c), 군집(Fig 25/25b) 모두 노트북에서 계산한다.

**`results/tables/*.csv` 를 불러오는 것**

lineage 검증(LOLO 24개 암종), 패널 크기 곡선, 회귀, pathway, signature, 결합
패널, TCGA 등 나머지 절은 `scripts/` 가 이미 계산해 저장해 둔 결과를 읽어
그림만 다시 그린다. 이 계산들은 각각 수 분\~십수 분씩 걸려서 노트북을 열
때마다 돌리기에는 비현실적이다. 각 절 마크다운에 그 결과를 만든 재현 커맨드를
적어뒀으니, 처음부터 다시 돌리고 싶으면 그 커맨드를 쓰면 된다.

## 로컬에서 실행하려면

```bash
# 가상환경 (uv) — 자세한 배경은 ../docs/mlflow_pilot.md 참고
uv venv .venv --system-site-packages --python 3.13
uv pip install "numpy==1.26.4" "pandas==2.2.3" xgboost catboost --python .venv/bin/python
uv pip install ipykernel nbclient nbformat jupyter "umap-learn==0.5.6" --python .venv/bin/python
.venv/bin/python -m ipykernel install --user --name python3 --display-name python3

# 노트북 서버 실행 (직접 클릭해서 셀 실행)
.venv/bin/python -m jupyter notebook notebooks/

# 또는 커맨드라인에서 전체 재실행
.venv/bin/python -c "
import nbformat
from nbclient import NotebookClient
nb = nbformat.read('notebooks/01_full_pipeline.ipynb', as_version=4)
NotebookClient(nb, timeout=1800, kernel_name='python3',
               resources={'metadata': {'path': 'notebooks'}}).execute()
nbformat.write(nb, 'notebooks/01_full_pipeline.ipynb')
"
```

`--system-site-packages` 를 반드시 켠다 — apt 로 이미 깔려 있는 pandas
(2.2.3+dfsg)/scikit-learn(1.4.2+dfsg) 를 재사용하기 위해서다. `numpy`/`pandas`
버전을 고정하지 않고 `uv pip install -r requirements.txt` 를 그대로 돌리면
버전이 최신으로 드리프트되는 문제가 있었다 — 자세한 내용은
`../docs/mlflow_pilot.md` "겪은 문제" 절 참고.

`umap-learn` 은 `0.5.6` 으로 고정한다. 0.5.7+ 는 `sklearn>=1.6` 의
`check_array(ensure_all_finite=...)` API 를 쓰는데 이 저장소는 sklearn 1.4.2 라
`TypeError` 가 난다.
