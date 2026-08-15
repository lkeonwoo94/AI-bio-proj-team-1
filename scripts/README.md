# 분석 파이프라인

각 스크립트는 저장소 루트에서 실행한다.

```bash
python scripts/01_check_data.py
```

번호는 README §22 의 14일 일정과 대응한다.

| 스크립트 | 일정 | 하는 일 | 산출물 |
| --- | --- | --- | --- |
| `01_check_data.py` | Day 1 | 파일 존재·버전·컬럼명 확인, WGD/CIN/LOH 후보 컬럼 탐색 | `docs/depmap/*.md` |
| `02_qc_merge.py` | Day 2 | ModelID 중복·결측·교집합 QC | `results/tables/qc_*.csv` |
| `03_build_matrix.py` | Day 3 | hotspot+damaging matrix 구축, label·lineage 결합 | 분석 테이블 (캐시) |
| `04_eda.py` | Day 4 | 표현형 분포, mutation 빈도, CV 구조 확정 | Figure 2 |
| `05_run_cv.py` | Day 5–9 | nested CV 실행 (`--model`, `--target` 로 지정) | `results/tables/cv_*.csv` |
| `06_compare_models.py` | Day 10 | 모델별 성능 집계 | Figure 3 |
| `07_aggregate_selection.py` | Day 11 | fold 선택 빈도·순위 안정성 집계 | Figure 4 |
| `08_panel_curve.py` | Day 12 | 5/10/20/50/전체 패널 비교 | Figure 5 |
| `09_lineage_validation.py` | Day 13 | GroupKFold / Leave-One-Lineage-Out | Figure 6 |
| `10_final_report.py` | Day 14 | 최종 패널·성능·한계 정리 | 발표자료 표 |

## 원칙

스크립트는 얇게 유지한다. 인자 파싱, 경로 해석, 결과 저장만 담당하고
실제 로직은 `src/` 에 둔다. 노트북에서도 `src/` 를 그대로 import 해서
스크립트와 노트북이 다른 코드를 돌리는 상황을 만들지 않는다.

`05_run_cv.py` 이후 모든 학습은 `src/cv` 가 만든 fold 안에서만 전처리·
feature selection·threshold 결정을 수행한다 (README §13).
