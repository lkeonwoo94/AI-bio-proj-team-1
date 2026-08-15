"""그림 공통 스타일.

모든 그림 스크립트는 다른 작업을 하기 전에 use_style() 을 먼저 호출한다.
matplotlib 기본 폰트에는 한글이 없어 그대로 두면 축·범례가 네모로 깨진다.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

from src.config import REPO_ROOT

FIGURES = REPO_ROOT / "results" / "figures"

# 세 표현형에 일관되게 쓰는 색
PHENOTYPE_COLORS = {"wgd": "#c0504d", "cin": "#4f81bd", "loh": "#9bbb59"}
NEUTRAL = "#7f7f7f"

_KOREAN_CANDIDATES = ("NanumGothic", "NanumBarunGothic", "NanumSquare",
                      "Noto Sans CJK KR", "Malgun Gothic")


def _korean_font() -> str | None:
    available = {f.name for f in fm.fontManager.ttflist}
    for name in _KOREAN_CANDIDATES:
        if name in available:
            return name
    return None


def use_style() -> None:
    font = _korean_font()
    if font:
        plt.rcParams["font.family"] = font
    plt.rcParams.update({
        "axes.unicode_minus": False,   # 한글 폰트에서 마이너스 기호가 깨지는 것 방지
        "figure.dpi": 110,
        "savefig.dpi": 150,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.25,
        "grid.linestyle": "-",
        "font.size": 10,
        "axes.titlesize": 11,
        "legend.frameon": False,
    })


def save(fig, name: str) -> Path:
    FIGURES.mkdir(parents=True, exist_ok=True)
    path = FIGURES / name
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path
