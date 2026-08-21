# 참조 게놈

`data/depmap/`, `data/gdc/` 와 같은 방식 — git 에 올리지 않는다.

## 팀 공유 사본

`data/depmap/` + `data/gdc/` + `data/reference/` 전체를 [Dropbox
링크](https://www.dropbox.com/t/2Qq3gja1nqVe2btg)에서 한 번에 받을 수
있다 — `hg38.2bit` 가 800MB 라 이쪽이 더 빠르다. Dropbox 전송 링크는
기간이 지나면 만료될 수 있으니, 끊기면 아래 원본 출처를 쓴다.

## 받아야 할 파일

| 파일 | 내용 | 출처 |
| --- | --- | --- |
| `hg38.2bit` | hg38 전체 게놈 서열 (~800MB) | [UCSC](https://hgdownload.soe.ucsc.edu/goldenPath/hg38/bigZips/hg38.2bit) |

DepMap mutation 은 hg38 에 정렬되어 있다(DepMap_release_README.txt).
mutation signature(trinucleotide context) 계산에 쓴다 — 변이 위치의
앞뒤 염기를 읽어야 하는데 원시 MAF 에는 그 정보가 없다.

```bash
curl -L -o hg38.2bit https://hgdownload.soe.ucsc.edu/goldenPath/hg38/bigZips/hg38.2bit
```

읽는 라이브러리: `py2bit` (`pip install py2bit`).

## 확인

```bash
python -c "import py2bit; tb=py2bit.open('data/reference/hg38.2bit'); print(len(tb.chroms()), '개 염색체')"
```
