# DVC 데이터 버전 관리 파일럿

`feature/dvc-pilot` 브랜치. 지금까지 `data/` 는 각 하위 폴더의
`README.md` 에 다운로드 URL만 적어두고 "각자 받으세요" 방식이었다
(`data/depmap/README.md`, `data/gdc/README.md`, `data/reference/README.md`).
DVC 로 대체할 수 있는지 평가하기 위한 파일럿이다. **기존 스크립트·문서는
전혀 건드리지 않았다** — `.gitignore` 조정과 `.dvc` 메타데이터 파일
추가만 했다.

## 왜 시도하나

이 방식은 실제로 한 번 사고를 냈다 — TCGA MAF 파일(`mc3.v0.2.8.PUBLIC.maf.gz`,
753MB)을 처음 받았을 때 다운로드가 중간에 끊겨 175MB(2,571개 샘플)만
받아졌는데, 이걸 곧바로 알아채지 못했다(전체 표본이 아니라 특정
암종만 빠진 형태라 착시가 있었음). `gzip -t` 로 무결성을 확인하고 나서야
발견해 재다운로드했다. DVC 는 파일 해시(md5)를 `.dvc` 메타데이터에
박아두고 `dvc pull` 이 그 해시로 무결성을 검증하므로, 이런 사고 자체가
구조적으로 드러나기 쉬워진다.

## 구성

* `.dvc/config` — 원격 저장소 설정. **지금은 로컬 경로
  (`/home/kali/adni-shared/dvc-remote-pilot`)를 가리키는 자리표시자다**
  — 실제 팀 공유 스토리지(네트워크 드라이브, S3 등)가 정해지면
  `dvc remote modify local-pilot url <새 경로>` 한 줄로 바꾸면 된다.
  이 경로가 팀원 전체에게 공유되는 위치인지는 확인되지 않았다.
* `data/{depmap,gdc,reference}/*.dvc` — 원본 데이터 파일 9개의 메타데이터
  (파일명·크기·md5 해시만 담은 텍스트, git 추적). 실제 데이터 바이트는
  이 파일에 없다.
* `.gitignore` — `data/*.dvc` 계열은 추적하고, 실제 데이터 파일은
  기존처럼 계속 무시하도록 예외 규칙을 추가했다.

## 실행

```bash
# 최초 1회
uv pip install dvc --python .venv/bin/python
.venv/bin/dvc init

# 원격 설정 (파일럿용 로컬 경로 — 실제 공유 위치로 나중에 교체)
.venv/bin/dvc remote add -d local-pilot /home/kali/adni-shared/dvc-remote-pilot

# 원본 데이터 추적 (README.md 는 그대로 git 추적, 나머지 파일만 DVC 로)
.venv/bin/dvc add \
  data/depmap/DepMap_release_README.txt data/depmap/Model.csv \
  data/depmap/OmicsGlobalSignatures.csv data/depmap/OmicsSomaticMutations.csv \
  data/depmap/OmicsSomaticMutationsMatrixDamaging.csv \
  data/depmap/OmicsSomaticMutationsMatrixHotspot.csv \
  data/gdc/mc3.v0.2.8.PUBLIC.maf.gz \
  data/gdc/TCGA_mastercalls.abs_tables_JSedit.fixed.txt \
  data/reference/hg38.2bit

# 원격에 업로드
.venv/bin/dvc push

# (팀원 입장에서) 저장소를 새로 받은 뒤 데이터만 내려받기
.venv/bin/dvc pull
```

## 확인된 것 — 실제로 push/pull 왕복 검증까지 했다

1. 원본 데이터 9개(총 2.3GB)를 `dvc add` 로 추적하고 `dvc push` 로
   로컬 파일럿 원격에 업로드 — 9개 파일 전송 확인.
2. **삭제 → pull → 체크섬 대조**로 실제 검증했다: `hg38.2bit`(835MB)와
   `Model.csv`를 지우기 전 md5 를 기록해두고 삭제한 뒤, `dvc pull` 로
   복구해 md5 를 다시 계산했다 — **완전히 일치**했다
   (`hg38.2bit`: `dcc3ea27079aa6dc3f9deccd7275e0f8`,
   `Model.csv`: `a15d75dffcc5219111ca39598948df9a`).
3. `dvc status` 가 "Data and pipelines are up to date" 를 보고했다.
4. 복구된 데이터로 `load_cohort()` 를 실행해 실제 파이프라인이 정상
   작동하는지까지 확인했다 — 세포주 1,631개, feature 20,132개로 기존과
   동일.

## 이번 파일럿에서 다루지 않은 것

* **파생 산출물은 추적하지 않았다** — `sbs96_signature_matrix.parquet`,
  `tcga_damaging_matrix.parquet`, `tcga_wgd_labels.parquet` 처럼
  스크립트가 만들어내는 중간 파일은 이번엔 빼뒀다. 이런 파일은
  `dvc add` 보다 `dvc.yaml`(파이프라인 stage — 입력 데이터·스크립트가
  바뀌면 `dvc repro` 가 자동으로 다시 만들어줌)로 관리하는 게 더
  맞는 방향인데, 이건 범위가 커서 파일럿 이후로 미뤘다.
* **원격 저장소가 진짜 공유 위치가 아니다** — 이 세션의 로컬 경로다.
  팀이 실제로 쓰려면 네트워크 드라이브나 S3 같은 위치를 정해야 한다.
* `results/`(11MB)는 그대로 git 에 커밋하는 현재 방식을 유지한다 —
  크기가 작아 DVC 로 옮길 이유가 없다.

## 다음 결정

파일럿이 유용하다고 판단되면:

1. 팀이 실제로 접근 가능한 원격 저장소 위치를 정한다(네트워크 드라이브 /
   S3 / GCS 등) — 정해지면 `dvc remote modify` 한 줄로 바꾸면 된다.
2. `data/*/README.md` 의 "다운로드 URL 안내" 문구를 `dvc pull` 안내로
   바꾼다(URL 자체는 출처 문서로 남겨두는 게 좋다 — 원격이 사라지면
   URL 이 유일한 복구 경로다).
3. 파생 산출물(signature matrix 등)까지 관리하고 싶으면 `dvc.yaml`
   파이프라인 stage 로 확장한다.

필요 없다고 판단되면 이 브랜치를 버리면 된다 — main 은 전혀 바뀌지
않았고, 로컬 파일럿 원격(`/home/kali/adni-shared/dvc-remote-pilot`)도
지우면 그만이다.
