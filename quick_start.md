# Quick_Start — 데이터 사전 (DATADIC)

번들 `Quick_Start.zip` (7.4 MB, 파일 2개) 의 압축 해제 결과입니다.

> 전체 번들 구조는 [README.md](README.md) · Study_Info 카테고리는 [study_info.md](study_info.md)

**데이터 구조 파악의 출발점.** 어떤 CSV의 어떤 컬럼이 무슨 뜻인지 모를 때 여기서 조회합니다.

---

## 디렉터리 내용

```
$ ls -al adni/Quick_Start/
total 7248
drwxr-xr-x 2 kali kali    4096 Aug  7 17:20 .
drwxr-xr-x 4 kali kali    4096 Aug  7 17:20 ..
-rw-r--r-- 1 kali kali  162467 Aug  7 17:20 ADNI_Quickstart_Guide_20250527.pdf
-rw-r--r-- 1 kali kali 7248191 Aug  7 17:20 DATADIC_21Jan2026.csv
```

`DATADIC_21Jan2026.csv` = **34,930행 × 13열**의 전체 데이터 사전.
컬럼: `PHASE, CRFNAME, TBLNAME, FLDNAME, TEXT, TYPE, LENGTH, DD_CRF_VERSION, CODE, UNITS, STATUS, CODE_CHANGES, MAPPING_NOTES`
→ **336개 테이블**의 모든 변수 정의·자료형·코딩값·단위·단계별 코드 변경 이력.
어떤 CSV의 어떤 컬럼이 무슨 뜻인지 모를 때 여기서 조회합니다.

필드 수 상위 테이블 (오믹스 계열이 압도적):

| 테이블 | 필드 수 | 설명 |
|---|---:|---|
| `EMORY_CSF_TMT_MS` | 3,914 | Emory CSF TMT 질량분석 프로테오믹스 |
| `ADMC_DUKE_SERUM_METABOLON_HD4` | 1,358 | Duke 비표적 혈청 메타볼로믹스 |
| `ADMCLIPIDOMICSMEIKLELABLONG` | 789 | Meikle lab 종단 리피도믹스 |
| `NEUROPATH` | 734 | NACC 신경병리 양식 v11 |
| `UCSFASLFS` | 700 | ASL 관류 CBF, FreeSurfer ROI별 |
| `UCBERKELEYAV45_8MM` | 601 | amyloid PET SUVR |
| `UCBERKELEYAV1451_8MM` | 584 | tau PET SUVR |

`PHASE` 태그 분포: 단일 단계(ADNI1/GO/2/3/4 각 1.8k–2.8k), 다단계 공유 8,823, 미태깅 14,490.
미태깅이 많은 이유는 외부 연구실 제공 오믹스/영상 테이블이 특정 프로토콜에 묶이지 않기 때문입니다.

---

## 조회 방법

전체 압축을 풀지 않고 메모리로 바로 읽습니다.

```python
import zipfile, io, pandas as pd

with zipfile.ZipFile("data/ADNI_data_Do_NOT_redistribute.zip") as outer:
    with outer.open("Quick_Start.zip") as f:
        inner = zipfile.ZipFile(io.BytesIO(f.read()))

with inner.open("DATADIC_21Jan2026.csv") as f:
    datadic = pd.read_csv(f, low_memory=False)

print(datadic.shape)   # (34930, 13)
```

```python
# 특정 테이블의 변수 목록
datadic[datadic.TBLNAME == "MOCA"][["FLDNAME", "TEXT", "CODE"]]

# 컬럼명 역검색 — "이 컬럼 어느 테이블 거지?"
datadic[datadic.FLDNAME == "CDRSB"][["TBLNAME", "TEXT", "UNITS"]].drop_duplicates()

# 설명 텍스트 검색 — "해마 부피 변수가 어디 있지?"
datadic[datadic.TEXT.str.contains("hippocamp", case=False, na=False)][
    ["TBLNAME", "FLDNAME", "TEXT"]
]

# 코딩값 확인 — "1이 남자야 여자야?"
datadic[(datadic.TBLNAME == "PTDEMOG") & (datadic.FLDNAME == "PTGENDER")].CODE.iloc[0]
```
