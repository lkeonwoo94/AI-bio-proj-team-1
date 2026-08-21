# DepMap 데이터

이 디렉터리의 데이터 파일은 **git 에 올리지 않는다** (`.gitignore` 처리).
이 README 만 추적되며, 각자 아래 파일을 직접 받아 이 폴더에 넣는다.

## 팀 공유 사본

`data/depmap/` + `data/gdc/` + `data/reference/` 전체를 [Dropbox
링크](https://www.dropbox.com/t/2Qq3gja1nqVe2btg)에서 한 번에 받을 수
있다 — 원본을 각자 새로 받는 것보다 빠르다. 다만 Dropbox 전송 링크는
기간이 지나면 만료될 수 있으므로, 이 링크가 끊기면 아래 원본 출처에서
다시 받는다(release 버전은 항상 `configs/data.yaml` 로 확인).

## 받아야 할 파일

https://depmap.org/portal/data_page/ 에서 내려받는다.

| 파일 | 용도 |
| --- | --- |
| `OmicsSomaticMutationsMatrixHotspot.csv` | 입력 feature — hotspot mutation |
| `OmicsSomaticMutationsMatrixDamaging.csv` | 입력 feature — damaging mutation |
| `OmicsGlobalSignatures.csv` | 정답 label — WGD / CIN / LOH |
| `Model.csv` | ModelID, cancer lineage |
| `OmicsSomaticMutations.csv` | 원시 MAF(Chrom/Pos/Ref/Alt, LikelyLoF/Hotspot 플래그 포함) — mutation signature 실험용(Future Work 2), 용량 큼 |

파일명이 릴리스에 따라 다를 수 있으므로, 실제 받은 이름은
`configs/data.yaml` 의 `files` 항목에 반영한다.
릴리스 버전도 `configs/data.yaml` 의 `release` 에 기록해 팀원 간 버전을 맞춘다.

## 확인

저장소 루트에서 다음을 실행하면 어떤 파일이 비어 있는지 알려준다.

```bash
python scripts/01_check_data.py
```

## 다른 위치에 두고 싶다면

환경변수로 덮어쓸 수 있다.

```bash
export DEPMAP_DATA_ROOT=/path/to/DepMap
```

## 주의

ADNI 데이터는 재배포가 금지되어 있으므로 이 저장소 안에 두지 않는다.
