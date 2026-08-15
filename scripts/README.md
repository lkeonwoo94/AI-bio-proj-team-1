# 분석 파이프라인

각 스크립트는 저장소 루트에서 실행한다.

```bash
python scripts/01_check_data.py
```

## 환경

xgboost 는 시스템 패키지 관리자와 충돌(PEP 668)해 venv 에 설치했다.

```bash
python -m venv --system-site-packages .venv
.venv/bin/pip install xgboost
```

오래 걸리는 실행은 `-u` 를 붙인다. stdout 을 파일로 리다이렉트하면
파이썬이 블록 버퍼링을 해서 진행 로그가 끝날 때까지 보이지 않는다.

```bash
.venv/bin/python -u scripts/05_run_cv.py --model xgboost > xgb.log 2>&1 &
```

번호는 README §22 의 14일 일정과 대응한다.

| 스크립트 | 일정 | 하는 일 | 산출물 |
| --- | --- | --- | --- |
| `01_check_data.py` | Day 1 | 파일 존재·버전·컬럼명 확인, WGD/CIN/LOH 후보 컬럼 탐색 | `docs/depmap/*.md` |
| `02_qc_merge.py` | Day 2 | ModelID 중복·결측·교집합 QC | `results/tables/qc_*.csv` |
| `03_build_matrix.py` | Day 3 | hotspot+damaging matrix 구축, label·lineage 결합 | 분석 테이블 (캐시) |
| `04_eda.py` | Day 4 | 표현형 분포, mutation 빈도, CV 구조 확정 | Figure 2 |
| `05_run_cv.py` | Day 5–9 | nested CV 실행 (`--model`, `--target`, `--scheme`) | `results/tables/cv_*.csv` |
| `06_compare_models.py` | Day 10 | 모델별 성능 집계 | Figure 3 |
| `07_aggregate_selection.py` | Day 11 | fold 선택 빈도·순위 안정성 집계 | Figure 4 |
| `08_panel_curve.py` | Day 12 | 5/10/20/50/전체 패널 비교 | Figure 5 |
| `09_lineage_validation.py` | Day 13 | GroupKFold / Leave-One-Lineage-Out | Figure 6 |
| `10_final_report.py` | Day 14 | §26 다섯 질문에 대한 답 정리 | 콘솔 요약 |

## 대략적인 실행 시간 (24코어 기준)

| 모델 | 표현형 1개 | 비고 |
| --- | --- | --- |
| logistic | ~7초 | |
| elastic_net | ~2분 | saga solver. tol 1e-3 으로 완화함 |
| random_forest | ~5분 | |
| xgboost | ~6분 | |
| multitask_ann | ~3분 | |

`08_panel_curve.py` 는 fold 당 전체 모델 1회 + 패널 4회를 학습하므로
표현형 하나에 10분 이상 걸린다.

## 원칙

스크립트는 얇게 유지한다. 인자 파싱, 경로 해석, 결과 저장만 담당하고
실제 로직은 `src/` 에 둔다. 노트북에서도 `src/` 를 그대로 import 해서
스크립트와 노트북이 다른 코드를 돌리는 상황을 만들지 않는다.

`05_run_cv.py` 이후 모든 학습은 `src/cv` 가 만든 fold 안에서만 전처리·
feature selection·threshold 결정을 수행한다 (README §13).
