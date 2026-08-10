# Study_Info — 프로토콜 문서와 ADNIMERGE2

## 프로토콜/CRF 문서 (PDF 14개)

ADNI 단계별(ADNI1 → ADNIGO → ADNI2 → ADNI3 → ADNI4) Procedures Manual과 CRF(증례기록서)
서식, 그리고 ADNI4의 대면(In Clinic)/원격(Remote) 프로토콜 버전별 문서입니다.

| 파일 | 내용 |
|---|---|
| `ADNI1_Procedures_Manual.pdf` / `ADNI1_CRFs_20180724.pdf` | ADNI1 절차·CRF |
| `ADNI_GO_Procedures_Manual.pdf` / `ADNI_GO_CRFs_20140606.pdf` | ADNIGO 절차·CRF |
| `ADNI2_Procedures_Manual.pdf` | ADNI2 절차 |
| `ADNI3_Procedures_Manual_v3.0.pdf` | ADNI3 절차 |
| `ADNI4_Procedures_Manual_v4.3_05MAR2025.pdf` | ADNI4 절차 (최신 v4.3) |
| `ADNI4_In_Clinic_Protocol_v2/v3` | ADNI4 대면 방문 프로토콜 버전별 |
| `ADNI4_Remote_Protocol_v2/v3` | ADNI4 원격(RMT) 프로토콜 버전별 — [remotely_collected_data.md](remotely_collected_data.md)와 연결 |
| `Adni_Data_Matrix_20140527.pdf` | 단계·방문별 수집 항목 매트릭스(어느 방문에 어떤 검사가 있었는지) |
| `ADNI_Minimum_Metadata.pdf` | 최소 필수 메타데이터 명세 |
| `ADNI_Methods_Template.docx` | 논문 Methods 절 작성용 표준 템플릿 |

논문 Methods 절이나 특정 방문의 검사 구성을 확인할 때 인용할 원 문서입니다.

## 표준화 리스트

- `ADNI_1.5T_MRI_Standardized_Lists.zip` / `ADNI_3T_MRI_Standardized_Lists.zip` — 자기장 세기별(1.5T/3T) 표준 스캔 시리즈 목록. 안쪽 압축 별도 해제 필요.

## ADNIMERGE2 R 패키지 

- ATRI Biostatistics 배포, R 패키지 (업스트림: <https://github.com/atri-biostats/ADNIMERGE2>)
- `ADNIMERGE2/data/`에 `.rda` 217개 — 원본 CSV 여러 개를 CDISC SDTM/ADaM 스타일로 정리·병합한 파생 테이블 모음
- `ADNIMERGE2/R/`에 `pacc.R`, `score-function.R`, `analysis-data-prep.R` 등 점수 산출 코드가 그대로 포함돼 있어 계산 규칙을 재현 가능
- `ADNIMERGE2/inst/doc/`에 등록(Enrollment)·종단분석(Longitudinal) vignette
- `ADNIMERGE2/man/`에 각 테이블 문서(Rd)
- **원본 CSV를 손으로 병합하지 말고 이 패키지의 정리된 테이블을 쓰는 것이 정석입니다.**
- 대표 테이블: `ADSL`(참가자 1인당 1행 마스터), `LB`(검사실 수치), `ADQS`/`QS`(설문·척도), `DXSUM`(진단 이력), `RECCMEDS`(병용약물), `MRIQC`(MRI 품질관리) 등
- `ADNIMERGE2_R_Package_Methods_20260105.pdf` — 패키지 산출 방법론 문서

`ADSL`은 참가자 키가 `USUBJID`(`ADNI-001-00221` 형식)로, 원본 CSV 계열의 `RID`/`PTID`와 다릅니다.
두 계통을 조인하려면 접두사를 떼어 변환해야 하며, 패키지의 `convert_usubjid_to_rid()` 함수가 이 작업을 합니다.

### ADNIMERGE2 (ATRI Biostatistics 배포 v0.1.1)를 풀면 나오는 data/ADSL.rda 개요
ADSL 코호트 [adsl_cohort.md](adsl_cohort.md) 참고.

## 운영성 CSV 3개

PDF·R 패키지 위주인 이 카테고리에서 실제 원본 CSV는 3개뿐이며, 분석 대상이라기보다 **분석 전 확인용** 자료입니다.

| 파일 | 내용 |
|---|---|
| `DELMRSCANS_22Jan2026.csv` | 삭제된 MRI 스캔 목록 (`SUBJECTID`, `SCANDATE`, `SERIESDSCR`, `IMAGEID`, `DELETEDATE`). [imaging.md](imaging.md)의 `IMAGEID`와 대조해 실제 존재하지 않는 영상을 걸러낼 때 사용 |
| `PIFINAL_22Jan2026.csv` | ADNI3 연구책임자(PI) 최종 확인 서명 기록. 분석에는 쓰이지 않음 |
| `RORR_22Jan2026.csv` | 참가자에게 개별 연구 결과를 통보한 기록(Results Return) — 통보 종류(`TYPE`), 요청자(`REQUESTED`), 동의 주체(`CONSENT`) |

## 참고

- `-4`는 ADNI 전반에서 결측을 뜻하는 sentinel 값입니다. 수치로 그대로 읽지 말고 로딩 직후 `NA`로 치환해야 합니다.

