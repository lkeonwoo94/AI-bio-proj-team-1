# Quick Start — 30분 만에 첫 분석까지

ADNI 데이터를 처음 만지는 팀원용 실습 가이드입니다.
저장소 전체 개요와 데이터 구조는 [README.md](README.md) 를 먼저 보세요.

문서에 나오는 코드는 전부 실행해서 출력을 확인한 것입니다. 그대로 복사해 쓰면 됩니다.

---

## 0. 준비물

| 항목 | 비고 |
|---|---|
| ADNI 계정 | [LONI IDA](https://ida.loni.usc.edu/) 에서 신청, 승인까지 며칠 걸림 |
| 디스크 여유 | 번들 1.14 GB + 압축 해제 시 최대 1.6 GB |
| Python | 3.10 이상, `pandas` |
| R | 4.2 이상, `dplyr` (ADNIMERGE2 쓸 경우) |

> **먼저 읽을 것**: 이 데이터는 재배포 금지입니다. 원본이든 참가자 수준 파생물이든
> 저장소에 커밋하거나 메신저로 주고받지 마세요. 자세한 규칙은 README의 "데이터 취급 규칙" 절에 있습니다.

---

## 1. 데이터 배치 (5분)

LONI에서 받은 ZIP을 `data/` 에 그대로 둡니다. **압축을 풀 필요 없습니다.**

```bash
mkdir -p data
mv ~/Downloads/ADNI_data_Do_NOT_redistribute.zip data/
```

`data/` 는 `.gitignore` 처리되어 있습니다. 확인:

```bash
git check-ignore -v data/ADNI_data_Do_NOT_redistribute.zip
# .gitignore:11:*.zip    data/ADNI_data_Do_NOT_redistribute.zip
```

무결성 확인 (선택):

```bash
sha256sum data/ADNI_data_Do_NOT_redistribute.zip
# 2a3579bb066c2b5fc73e46f6da13f5ea72d1bd81e31cf1011197ef81f39df61f
```

---

## 2. 번들 구조 훑어보기 (2분)

카테고리 ZIP 12개가 중첩된 구조입니다. 목록만 봅니다.

```bash
unzip -l data/ADNI_data_Do_NOT_redistribute.zip
```

```
   451175566  2026-01-22 18:32   ADSP_PHC.zip
    91014203  2026-01-22 17:12   Assessments.zip
     2221635  2026-01-22 18:28   Curated_Data___Docs.zip
   160540817  2026-01-22 18:28   Genetic.zip
   541136776  2026-01-22 17:39   Imaging.zip
    46362851  2026-01-22 18:47   Medical_History.zip
      284720  2026-01-22 18:51   Neuropathology_Results.zip
     7410942  2026-01-22 16:11   Quick_Start.zip
    61900845  2026-01-22 19:12   Remotely_Collected_Data.zip
   169887411  2026-01-22 18:51   Study_Info.zip
     5969225  2026-01-22 18:48   Subject_Characteristics.zip
    57628527  2026-01-22 18:29   Test_Data_for_Challenges_except_imaging_vertices.zip
```

특정 카테고리 안을 보려면:

```bash
unzip -p data/ADNI_data_Do_NOT_redistribute.zip Quick_Start.zip > /tmp/qs.zip && unzip -l /tmp/qs.zip
```

---

## 3. Python — 전체 해제 없이 CSV 읽기 (5분)

1.6 GB를 디스크에 풀지 않고 필요한 파일만 메모리로 읽는 헬퍼입니다.

```python
import zipfile, io, pandas as pd

BUNDLE = "data/ADNI_data_Do_NOT_redistribute.zip"

def load_adni_csv(category, filename, bundle=BUNDLE, **kw):
    """중첩 ZIP에서 CSV 하나를 메모리로 바로 읽는다.

    category : 최상위 ZIP 이름 (확장자 제외).  예) "Quick_Start"
    filename : 그 안의 CSV 파일명.            예) "DATADIC_21Jan2026.csv"
    """
    with zipfile.ZipFile(bundle) as outer:
        with outer.open(f"{category}.zip") as f:
            inner = zipfile.ZipFile(io.BytesIO(f.read()))
    with inner.open(filename) as f:
        return pd.read_csv(f, low_memory=False, **kw)

datadic = load_adni_csv("Quick_Start", "DATADIC_21Jan2026.csv")
print(datadic.shape)      # (34930, 13)
```

카테고리 안에 무슨 파일이 있는지 모를 때:

```python
def list_adni_files(category, bundle=BUNDLE):
    with zipfile.ZipFile(bundle) as outer:
        with outer.open(f"{category}.zip") as f:
            inner = zipfile.ZipFile(io.BytesIO(f.read()))
    return [n for n in inner.namelist() if not n.endswith("/")]

list_adni_files("Assessments")[:5]
```

> **팁**: 같은 카테고리에서 여러 파일을 읽을 거면 위 함수는 매번 ZIP을 다시 엽니다.
> 반복이 많으면 `inner` 를 한 번만 만들어 재사용하세요.

---

## 4. 데이터 사전(DATADIC) 사용법 (3분)

**모르는 컬럼이 나오면 여기서 찾습니다.** 336개 테이블의 모든 변수 정의가 들어 있습니다.

```python
# 특정 테이블의 변수 목록
datadic[datadic.TBLNAME == "MOCA"][["FLDNAME", "TEXT", "CODE"]].head()
```

```
FLDNAME                  TEXT CODE
   PTID        Participant ID  NaN
    RID Participant roster ID  NaN
VISCODE            Visit code  NaN
```

```python
# 컬럼명으로 역검색 — "이 컬럼 어느 테이블 거지?"
datadic[datadic.FLDNAME == "CDRSB"][["TBLNAME", "TEXT", "UNITS"]].drop_duplicates()

# 설명 텍스트로 검색 — "해마 부피 변수가 어디 있지?"
datadic[datadic.TEXT.str.contains("hippocamp", case=False, na=False)][
    ["TBLNAME", "FLDNAME", "TEXT"]
].head(10)

# 코딩값 확인 — "1이 남자야 여자야?"
datadic[(datadic.TBLNAME == "PTDEMOG") & (datadic.FLDNAME == "PTGENDER")].CODE.iloc[0]
```

주요 컬럼: `TBLNAME`(테이블), `FLDNAME`(변수명), `TEXT`(설명), `TYPE`(자료형),
`CODE`(코딩값), `UNITS`(단위), `CODE_CHANGES`(단계별 코드 변경 이력).

---

## 5. R — ADNIMERGE2 설치 (10분)

**원본 CSV를 손으로 병합하지 마세요.** ATRI가 정리해 둔 R 패키지를 씁니다.
217개 테이블, 총 2,727,235행이 CDISC 표준 형식으로 들어 있습니다.

### 5-1. tar.gz 꺼내기

```bash
mkdir -p data/extracted
unzip -p data/ADNI_data_Do_NOT_redistribute.zip Study_Info.zip > /tmp/si.zip
unzip -o -j /tmp/si.zip ADNIMERGE2.tar.gz -d data/extracted/
tar -xzf data/extracted/ADNIMERGE2.tar.gz -C data/extracted/
```

### 5-2. 설치

```r
install.packages("data/extracted/ADNIMERGE2.tar.gz", repos = NULL, type = "source")
library(ADNIMERGE2)
data(ADSL)
dim(ADSL)   # 5146 x 55
```

설치가 번거로우면 `.rda` 를 직접 읽어도 됩니다:

```r
load("data/extracted/ADNIMERGE2/data/ADSL.rda")
```

> `metacore` 네임스페이스 경고가 뜨는데 데이터 읽기에는 지장 없습니다. 무시하세요.

---

## 6. 꼭 알아야 할 테이블 6개

| 테이블 | 크기 | 용도 |
|---|---:|---|
| `ADSL` | 5,146 × 55 | **참가자 1인 1행 마스터.** 인구학 + 기저 점수 + APOE + amyloid |
| `DXSUM` | 15,881 × 42 | **종단 진단 이력.** 방문별 CN/MCI/Dementia |
| `ADQS` | 320,021 × 36 | **종단 인지점수(long format).** `PARAMCD` 로 척도 선택 |
| `PACC` | 19,571 × 26 | PACC 복합점수 및 구성 하위점수 |
| `REGISTRY` | 28,858 × 27 | 방문 등록·상태 |
| `VISITS` | 69 × 5 | 방문 코드 ↔ 방문명 매핑 |

`ADQS` 의 `PARAMCD` 상위 값 (레코드 수):

```
MPACCDIGIT 19,571 | MPACCTRAILSB 19,571 | DIGITSCR 17,622 | LDELTOTL 17,622
LIMMTOTL 17,622 | RAVLTIMM 17,622 | TRABSCOR 17,622 | CDGLOBAL 14,617
CDRSB 14,617 | MMSCORE 14,599 | GDTOTAL 13,694 | FAQTOTAL 13,272
```

`ADQS` 는 long format이라 `PARAMCD` 로 거르고 `AVAL`(값), `ADY`(기준일로부터 일수),
`ABLFL`(기저 여부 Y/N), `BASE`/`CHG`(기저값/변화량)를 씁니다.

---

## 7. 함정 세 가지 — 반드시 읽을 것

### 7-1. `ADSL` 에는 `RID` 가 없다

`ADSL` 의 참가자 키는 `USUBJID`(`ADNI-001-00221` 형식)이고,
`DXSUM` 등 원본 계열 테이블은 `RID`(정수) / `PTID`(`011_S_0002` 형식)를 씁니다.

```r
# 패키지 함수 사용
ADSL$RID <- convert_usubjid_to_rid(ADSL$USUBJID)

# 또는 직접
ADSL$RID <- as.numeric(sub("^ADNI-[0-9]{3}-", "", ADSL$USUBJID))
```

변환 후 `DXSUM` 의 참가자 3,788명이 `ADSL` 에 100% 매칭되는 것을 확인했습니다.

### 7-2. `ADSL$DX` 결측 41%는 "진단 없음"이 아니다

`ADSL` 은 특정 시점 스냅샷이라 `DX` 가 2,116명 비어 있습니다.
**진단으로 군을 나눌 거면 `DXSUM` 을 쓰세요.**

```
DXSUM$DIAGNOSIS:  CN 6,275 | MCI 6,565 | Dementia 2,996 | NA 45
```

### 7-3. 노트북 출력에 데이터가 남는다

`df.head()` 출력에 참가자 ID가 그대로 찍힙니다. **커밋 전 반드시 출력을 지우세요.**

```bash
jupyter nbconvert --clear-output --inplace notebooks/*.ipynb
```

---

## 8. 워크드 예제 — 기저 진단별 CDR-SB

여기까지 왔으면 실제로 돌아가는 분석 하나를 끝낸 겁니다.

```r
library(dplyr)

load("data/extracted/ADNIMERGE2/data/ADSL.rda")
load("data/extracted/ADNIMERGE2/data/ADQS.rda")

cdr <- ADQS %>%
  filter(PARAMCD == "CDRSB", ABLFL == "Y") %>%
  group_by(DX) %>%
  summarise(n = n(), mean_CDRSB = round(mean(AVAL, na.rm = TRUE), 2), .groups = "drop")

print(cdr)
```

```
# A tibble: 4 × 3
  DX        n mean_CDRSB
  <fct> <int>      <dbl>
1 CN     1214       0.05
2 MCI    1337       1.54
3 DEM     477       4.37
4 <NA>      2       1
```

CN 0.05 → MCI 1.54 → 치매 4.37 로 단조 증가합니다. 데이터가 제대로 로드됐다는 신호입니다.

방문 횟수 분포도 봐 둘 만합니다 (종단 분석 설계에 필요):

```r
load("data/extracted/ADNIMERGE2/data/DXSUM.rda")

ADSL$RID <- as.numeric(sub("^ADNI-[0-9]{3}-", "", ADSL$USUBJID))
n_visits <- DXSUM %>% filter(!is.na(DIAGNOSIS)) %>% count(RID, name = "n_visits")

j <- inner_join(select(ADSL, RID, AGE, SEX, EDUC, APOE, DX), n_visits, by = "RID")
summary(j$n_visits)
```

3,777명이 매칭되고 방문 횟수 중앙값 4회, 최대 20회입니다.

---

## 9. 유용한 패키지 함수

`ADNIMERGE2` 는 데이터뿐 아니라 함수도 제공합니다 (`ls("package:ADNIMERGE2")` 로 전체 확인).

| 함수 | 용도 |
|---|---|
| `convert_usubjid_to_rid()` | `USUBJID` → `RID` 변환 |
| `create_usubjid()` | 역방향 변환 |
| `compute_pacc_score()` | PACC 복합점수 산출 |
| `compute_neurobat_subscore()` | 신경심리검사 하위점수 |
| `calculate_zscore()` | z-점수 변환 |
| `get_adni_enrollment()` | 등록 코호트 추출 |
| `get_adni_blscreen_dxsum()` | 기저 스크리닝 진단 |
| `get_baseline_vistcode()` | 단계별 기저 방문 코드 |
| `datadict_as_tibble()` | 데이터 사전 조회 |

패키지 vignette 8종이 `inst/doc/` 에 있습니다. 특히 볼 만한 것:

- `ADNI-Enrollment.Rmd` — 코호트 구성 방법
- `ADNI-Longitudinal.Rmd` — 종단 분석 설계
- `ADNIMERGE2-PACC.Rmd` — PACC 산출 상세

```r
vignette("ADNI-Longitudinal", package = "ADNIMERGE2")
```

---

## 10. 다음 단계

1. `DXSUM` 으로 CN → MCI → 치매 전환 시점 정의, 생존분석
2. `ADQS` 종단 CDR-SB / PACC 궤적을 선형혼합모형으로 (`lme4`)
3. `Genetic` 카테고리에서 APOE ε4 대립유전자 수를 붙여 층화 분석
4. `Imaging` 카테고리의 해마 부피 · amyloid PET SUVR 연동
   (이때 `Study_Info/DELMRSCANS_22Jan2026.csv` 의 삭제 스캔 10,324건 제외)

---

## 막혔을 때

| 증상 | 확인할 것 |
|---|---|
| 컬럼 의미를 모르겠다 | DATADIC 검색 (4절) |
| 조인 결과가 0행 | ID 형식 불일치 (7-1절) |
| 진단군 표본이 너무 적다 | `ADSL$DX` 대신 `DXSUM` (7-2절) |
| `metacore` 경고 | 무시해도 됨 |
| 방문 코드가 뭔지 모르겠다 | `VISITS` 테이블 |
| 그 외 | 팀 채널 또는 GitHub Issues |
