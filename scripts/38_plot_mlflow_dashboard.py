"""MLflow 대시보드 스냅샷 — run 데이터를 직접 쿼리해서 그린다.

`mlflow ui` 화면을 스크린샷으로 대체할 수 없는 환경(헤드리스)에서,
같은 데이터를 MLflow client API 로 읽어와 UI 의 "Compare" 뷰가 보여줄
법한 그림을 재현한다 — CSV 를 다시 읽는 게 아니라 **MLflow 에 실제로
기록된 run 에서** 값을 가져온다는 점이 핵심.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import mlflow
import numpy as np
import pandas as pd

from src.viz.style import use_style

MODEL_ORDER = ["logistic", "elastic_net", "random_forest", "xgboost", "catboost"]
TARGET_ORDER = ["wgd", "cin", "loh"]
TARGET_LABEL = {"wgd": "WGD", "cin": "CIN", "loh": "LOH"}
MODEL_COLOR = {
    "logistic": "#9bbb59", "elastic_net": "#8064a2", "random_forest": "#c0504d",
    "xgboost": "#4bacc6", "catboost": "#f79646",
}


def fetch_runs() -> pd.DataFrame:
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    client = mlflow.tracking.MlflowClient()
    rows = []
    for exp in client.search_experiments():
        if exp.name == "Default":
            continue
        for r in client.search_runs(exp.experiment_id, filter_string="tags.model_family != ''"):
            rows.append({
                "target": r.data.params.get("target"),
                "model": r.data.params.get("model"),
                "model_label": r.data.tags.get("model_label"),
                "roc_auc": r.data.metrics.get("mean_roc_auc"),
                "balanced_accuracy": r.data.metrics.get("mean_balanced_accuracy"),
                "brier": r.data.metrics.get("mean_brier"),
                "run_id": r.info.run_id,
            })
    return pd.DataFrame(rows)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="/tmp/mlflow_dashboard_snapshot.png",
                   help="이 그림은 fig1~18 Figure 시퀀스가 아니라 파일럿 확인용 "
                        "스냅샷이라 results/figures/ 밖 임의 경로에 저장한다.")
    args = p.parse_args()

    use_style()
    df = fetch_runs()
    if df.empty:
        print("MLflow 에 기록된 run 이 없다 — 먼저 scripts/37_mlflow_pilot.py 를 돌린다.")
        return 1

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    width = 0.15
    x = np.arange(len(TARGET_ORDER))

    for ax, metric, title in zip(
        axes, ["roc_auc", "balanced_accuracy", "brier"],
        ["ROC-AUC", "Balanced Accuracy", "Brier (낮을수록 좋음)"],
    ):
        for i, model in enumerate(MODEL_ORDER):
            sub = df[df.model == model].set_index("target").reindex(TARGET_ORDER)
            label = sub.model_label.dropna().iloc[0] if sub.model_label.notna().any() else model
            ax.bar(x + (i - 2) * width, sub[metric], width, label=label, color=MODEL_COLOR[model])
        ax.set_xticks(x)
        ax.set_xticklabels([TARGET_LABEL[t] for t in TARGET_ORDER])
        ax.set_title(title)
        if metric == "brier":
            ax.set_ylim(0.15, 0.26)
        else:
            ax.set_ylim(0.6, 0.85)

    axes[0].legend(fontsize=8, loc="lower right", ncol=2)
    fig.suptitle(
        "MLflow 대시보드 스냅샷 — 5개 모델 × 3표현형, 15개 run 에서 직접 쿼리\n"
        "(mlflow.tracking.MlflowClient().search_runs() 로 가져온 mean_* 지표)",
        y=1.05, fontsize=11,
    )
    fig.tight_layout()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print(f"저장: {out_path}")
    print(f"\n조회된 run: {len(df)}개")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
