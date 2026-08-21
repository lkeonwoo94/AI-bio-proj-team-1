# TCGA / GDC 데이터

`data/depmap/` 과 같은 방식이다 — 이 디렉터리의 데이터 파일은 **git 에
올리지 않는다**. 이 README 만 추적되며, TCGA 독립 코호트 검증
(`final_conclusion.md` "Future Work 3")에 쓴다.

## 팀 공유 사본

`data/depmap/` + `data/gdc/` + `data/reference/` 전체를 [Dropbox
링크](https://www.dropbox.com/t/2Qq3gja1nqVe2btg)에서 한 번에 받을 수
있다 — MAF 파일이 750MB 라 원본 재다운로드보다 이쪽이 끊길 위험이
적다. Dropbox 전송 링크는 기간이 지나면 만료될 수 있으니, 끊기면
아래 원본 출처를 쓴다.

## 받아야 할 파일

| 파일 | 내용 | 출처 |
| --- | --- | --- |
| `mc3.v0.2.8.PUBLIC.maf.gz` | 전체 TCGA somatic mutation MAF (~750MB) | [GDC API](https://api.gdc.cancer.gov/data/1c8cfe5f-e52d-41ba-94da-f15ea1337efc) |
| `TCGA_mastercalls.abs_tables_JSedit.fixed.txt` | ABSOLUTE 결과 — ploidy/purity/WGD status | [GDC API](https://api.gdc.cancer.gov/data/4f277128-f793-4354-a13d-30cc7fe9f6b5) |

둘 다 [GDC PanCanAtlas 페이지](https://gdc.cancer.gov/about-data/publications/pancanatlas)
에 공개돼 있어 승인 없이 받을 수 있다.

## 주의

* MAF 파일이 커서(~750MB) 다운로드가 끊기기 쉽다. 받은 뒤 반드시
  무결성을 확인한다: `gzip -t mc3.v0.2.8.PUBLIC.maf.gz`
* barcode 매핑 함정: ABSOLUTE 의 `sample` 컬럼과 MAF 의
  `Tumor_Sample_Barcode` 는 뒤쪽 plate/center 코드가 달라 전체 문자열로
  join 하면 거의 매칭되지 않는다. `src/data/tcga.py` 가 앞 15자로
  잘라서 처리한다 — 자세한 내용은 그 파일의 docstring 참고.
* CIN/LOH 에 대응하는 라벨(aneuploidy score, LOH fraction)은 이
  ABSOLUTE 파일에 없다. Taylor et al. 2018(Cancer Cell) supplementary
  table 에 있을 것으로 보이나 정확한 테이블 번호를 확인하지 못했다 —
  받으면 `final_conclusion.md` 의 해당 절을 갱신한다.

## 확인

```bash
python -c "from src.data.tcga import load_tcga_cohort; X, y = load_tcga_cohort(); print(X.shape, y.value_counts())"
```
