# DepMap 시각화 (팀원 제공, 탐색적 분석)

팀원이 별도로(`D:\범부처`, 이 저장소를 `AI-bio-proj-team-1/` 서브폴더로 두고)
만든 탐색적 시각화 — UMAP, CCA, 유전자-표현형 연관성 검정(Chi-square/Fisher +
FDR 보정), 유전자 dendrogram.

## 주의 — nested-CV 결과가 아니다

원본 스크립트(`시각화 코드_1.py`) docstring에 명시된 대로, 이 분석은
outcome/model 기반 feature selection 없이 **mutation 빈도만으로 필터링한
전체 코호트 탐색적 분석**이다. CIN/LOH 의 high/low 는 전체 코호트 중앙값
기준이며, 본 저장소의 nested-CV 성능 추정치(`day10_model_comparison.csv`
등)를 대체하지 않는다.

## 구성

| 경로 | 내용 |
| --- | --- |
| `시각화 코드_1.py` | UMAP / 연관성 검정 / dendrogram / CCA 생성 코드 |
| `이미지_subplot 코드_2.py` | WGD/CIN/LOH 결과를 한 그림에 합치는 subplot 코드 |
| `시각화 이미지 설명.pdf` | 각 그림에 대한 설명 |
| `figures/` | 생성된 이미지 6개 (UMAP, CCA, 연관성/모델선택 테이블, dendrogram) |
| `tables/` | 연관성 검정 결과(`association_{wgd,cin,loh}.csv`), CCA(`cca.csv`), 모델 vs 연관성 비교(`model_vs_association_summary.csv`) |

## 실행하려면

스크립트가 `ROOT / "AI-bio-proj-team-1"` 를 이 저장소 경로로 가정하므로,
그대로 실행하려면 이 저장소를 서브폴더로 두거나 `REPO` 경로를 맞게 고쳐야
한다. 원본 폰트 설정(`Malgun Gothic`)은 Windows 전용이라 Linux 에서는
한글이 깨질 수 있다.

## 파이프라인 버전 (adapt)

같은 분석을 이 저장소의 `load_cohort()` / `use_style()` / `save()` 규약에
맞춰 다시 작성해 `scripts/`, `results/figures/`, `results/tables/` 에
넣었다 — 별도 캐시 파일이나 하드코딩된 경로 없이 `python scripts/NN_*.py`
로 바로 실행된다.

| 스크립트 | 내용 | 산출물 |
| --- | --- | --- |
| `scripts/42_mutation_association.py` | 유전자-표현형 연관성 검정(Chi-square/Fisher + BH-FDR) | `day42_association_{wgd,cin,loh}.csv` |
| `scripts/43_plot_mutation_association.py` | 위 결과 시각화 | Figure 21 (상위 30개 막대), Figure 22 (상위 10개 상세 표) |
| `scripts/44_mutation_umap.py` | mutation UMAP 좌표 계산 (jaccard, umap-learn 필요) | `day44_mutation_umap_coords.csv` |
| `scripts/45_plot_mutation_umap.py` | 위 좌표 시각화 | Figure 23 |
| `scripts/46_mutation_cca.py` | mutation ↔ 유전체 불안정성 CCA (이진화/연속값 비교) | `day46_cca.csv`, `day46_cca_coordinates.csv` |
| `scripts/47_plot_mutation_cca.py` | 위 CCA 시각화 | Figure 24, Figure 24b |
| `scripts/48_plot_selection_dendrogram.py` | 기존 `day12_panel_picks_{model}.csv` 재사용, fold 선택 패턴 dendrogram | Figure 25 |

`scripts/44`는 `umap-learn`이 필요하다 (`requirements.txt`에 `umap-learn==0.5.6`
로 고정 — 0.5.7+ 는 `sklearn>=1.6` API를 요구해 이 저장소의 `sklearn 1.4.2`와
맞지 않는다).
