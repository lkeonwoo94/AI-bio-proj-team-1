"""MLflow 실험 추적 유틸 — 파일럿(`feature/mlflow-tracking-pilot` 브랜치).

기존에는 `day10_model_comparison.csv`, `day26_signature_panel_metrics.csv`
처럼 **파일명 prefix로 실험을 구분**해왔다. 이 방식은 스크립트를
재실행할 때 모델명 suffix 를 빠뜨려 이전 결과를 덮어쓰는 사고가 실제로
여러 번 있었다(예: Elastic Net 결과가 Random Forest 재실행으로 덮여
git history 에서 복구한 사건). MLflow 는 run 마다 자동으로 격리되므로
이런 사고가 구조적으로 어려워진다 — 이 파일럿은 그 가설을 실제로
확인하기 위한 것이다.

**적용 범위**: 이 유틸은 `scripts/37_mlflow_pilot.py` 에서만 쓴다.
기존 스크립트(01~36)는 전혀 건드리지 않았다 — 지금까지 만든 CSV·문서·
재현 커맨드는 그대로 유효하다. 파일럿이 팀에서 유용하다고 판단되면
그때 다른 스크립트로 점진적으로 확장한다.

실험/런 이름 규칙
-----------------
- MLflow experiment 이름: ``"{target}_{representation}"``
  (예: ``"wgd_gene"``, ``"cin_signature"``) — 표현형×입력표현 조합마다
  하나. 지금까지 문서에서 "표현형별로 비교표를 만든다"는 습관과 맞춘
  것이다.
- run 이름: parent = 모델명(``"random_forest"``), child = ``"fold{N}"``.
  outer 5-fold 구조를 nested run 으로 그대로 옮긴다.
"""

from __future__ import annotations

from pathlib import Path

import mlflow

from src.config import REPO_ROOT

TRACKING_DIR = REPO_ROOT / "mlruns"          # artifact(그림·CSV) 저장 위치
TRACKING_DB = REPO_ROOT / "mlflow.db"        # run/metric/param 메타데이터


def init_tracking() -> None:
    """로컬 SQLite 기반 tracking store 를 쓴다 — 서버 세팅 불필요.

    MLflow 3.x 부터 순수 파일 기반 backend("file:./mlruns")는
    maintenance mode 로 바뀌어 새 run 기록에 예외를 던진다
    (`mlflow.exceptions.MlflowException: ... is in maintenance mode`).
    권장 대안인 SQLite backend 를 쓴다 — 서버 없이 로컬 파일 하나로
    돌아간다는 점은 동일하고, `mlflow ui` 로 그대로 확인할 수 있다.

    파일럿 단계라 팀 공유 서버 없이 로컬에서만 확인한다. 나중에 팀
    전체가 쓰기로 하면 이 함수만 바꿔서 원격 tracking server URI 를
    가리키면 된다 — 호출하는 쪽(파일럿 스크립트) 코드는 안 바뀐다.
    """
    TRACKING_DIR.mkdir(exist_ok=True)
    mlflow.set_tracking_uri(f"sqlite:///{TRACKING_DB}")


def experiment_name(target: str, representation: str = "gene") -> str:
    return f"{target}_{representation}"


def log_fold_metrics(row, metric_columns: list[str]) -> None:
    """`run_nested_cv()` 가 반환하는 metrics DataFrame 의 한 행을 로깅한다."""
    if "best_params" in row.index:
        mlflow.log_param("best_params", str(row["best_params"]))
    if "n_features_kept" in row.index:
        mlflow.log_param("n_features_kept", int(row["n_features_kept"]))
    for col in metric_columns:
        value = row.get(col)
        if value is not None:
            mlflow.log_metric(col, float(value))


def log_artifact_df(df, filename: str, tmp_dir: Path) -> None:
    """DataFrame 을 임시 CSV 로 썼다가 MLflow artifact 로 올린다."""
    tmp_dir.mkdir(parents=True, exist_ok=True)
    path = tmp_dir / filename
    df.to_csv(path, index=False)
    mlflow.log_artifact(str(path))
