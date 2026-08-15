"""설정 로딩과 데이터 경로 해석.

데이터는 저장소 밖에 있으므로 경로를 코드에 흩어두지 않고 여기로 모은다.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = REPO_ROOT / "configs"


@lru_cache(maxsize=None)
def load_config(name: str) -> dict:
    """configs/<name>.yaml 을 읽는다."""
    path = CONFIG_DIR / f"{name}.yaml"
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def data_root() -> Path:
    """데이터 루트. 환경변수 DEPMAP_DATA_ROOT 가 있으면 우선한다."""
    env = os.environ.get("DEPMAP_DATA_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    return (REPO_ROOT / load_config("data")["data_root"]).resolve()


def data_path(key: str) -> Path:
    """configs/data.yaml 의 files 항목 키로 실제 파일 경로를 얻는다.

    파일이 없으면 어떤 파일을 어디에 두어야 하는지 알려주며 실패한다.
    """
    files = load_config("data")["files"]
    if key not in files:
        raise KeyError(f"알 수 없는 데이터 키: {key!r} (사용 가능: {sorted(files)})")

    path = data_root() / files[key]
    if not path.exists():
        raise FileNotFoundError(
            f"{key} 파일이 없습니다: {path}\n"
            f"DepMap 포털에서 {files[key]} 를 받아 {data_root()} 에 두거나, "
            f"DEPMAP_DATA_ROOT 환경변수로 다른 위치를 지정하세요."
        )
    return path


def missing_data_files() -> dict[str, Path]:
    """아직 내려받지 않은 데이터 파일 목록. Day 1 점검용."""
    files = load_config("data")["files"]
    root = data_root()
    return {k: root / v for k, v in files.items() if not (root / v).exists()}
