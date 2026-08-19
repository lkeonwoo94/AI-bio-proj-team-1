# 참조 게놈

`data/depmap/`, `data/gdc/` 와 같은 방식 — git 에 올리지 않는다.

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
