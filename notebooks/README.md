# 노트북

| 파일 | 내용 |
| --- | --- |
| `01_full_pipeline.ipynb` | 데이터 로드부터 최종 biomarker panel·결론까지 전체 파이프라인 15개 절 |
| `02_key_results.ipynb` | 핵심 결과만 간결하게 — 모델 비교, confusion matrix, 최소 패널, 후속 실험 3종 요약, TCGA 검증, 최종 패널 |

두 노트북 다 **이미 실행된 상태**로 커밋돼 있다(출력·그림이 노트북 안에
그대로 저장돼 있어 GitHub에서 바로 렌더링된다) — nbclient로 직접 실행해
에러 없음을 확인했다.

## 왜 무거운 계산을 다시 안 돌리는가

이 프로젝트의 핵심 계산(5개 모델 × 3표현형 nested CV, pathway/signature/결합
실험, TCGA 검증 등)은 outer 5-fold × inner 5-fold 구조라 모델에 따라 수
분\~십수 분씩 걸린다. 노트북을 열 때마다 이걸 전부 다시 돌리면 비현실적이라,
`scripts/`의 개별 스크립트가 이미 계산해 `results/tables/`·`results/figures/`에
저장해 둔 결과(모두 git 추적)를 노트북이 **불러와서 재현·시각화**한다. 각
절 마크다운에 실제로 그 결과를 만든 재현 커맨드를 적어뒀다 — 처음부터 다시
돌리고 싶으면 그 커맨드를 실행하면 된다.

## 직접 실행하려면

```bash
# 가상환경 (uv) — 자세한 배경은 ../docs/mlflow_pilot.md 참고
uv venv .venv --system-site-packages --python 3.13
uv pip install "numpy==1.26.4" "pandas==2.2.3" xgboost catboost --python .venv/bin/python
uv pip install ipykernel nbclient nbformat jupyter --python .venv/bin/python
.venv/bin/python -m ipykernel install --user --name python3 --display-name python3

# 노트북 서버 실행 (직접 클릭해서 셀 실행)
.venv/bin/python -m jupyter notebook notebooks/

# 또는 커맨드라인에서 전체 재실행
.venv/bin/python -c "
import nbformat
from nbclient import NotebookClient
nb = nbformat.read('notebooks/01_full_pipeline.ipynb', as_version=4)
NotebookClient(nb, timeout=180, kernel_name='python3',
               resources={'metadata': {'path': 'notebooks'}}).execute()
nbformat.write(nb, 'notebooks/01_full_pipeline.ipynb')
"
```

`--system-site-packages` 를 반드시 켠다 — apt 로 이미 깔려 있는 pandas
(2.2.3+dfsg)/scikit-learn(1.4.2+dfsg) 를 재사용하기 위해서다. `numpy`/`pandas`
버전을 고정하지 않고 `uv pip install -r requirements.txt` 를 그대로 돌리면
버전이 최신으로 드리프트되는 문제가 있었다 — 자세한 내용은
`../docs/mlflow_pilot.md` "겪은 문제" 절 참고.
