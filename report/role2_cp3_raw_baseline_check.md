# CP3 - Vai tro 2: Raw baseline check

## Pham vi

Vai tro 2 phu trach lay Crossref, luu raw, va truy vet du lieu raw. Trong CP3, muc tieu la xac minh baseline van dung dung raw snapshot da khoa, giai thich duoc raw/clean count, va dam bao phase1 khong fetch lai Crossref ngoai y muon.

## 1. Raw response, raw records va lineage sample van doc duoc

Da doc duoc cac artifact:

| Artifact | Trang thai | Bang chung |
| --- | --- | --- |
| `data/raw/crossref_response.json` | PASS | 24 items trong `message.items`; sha256 prefix `4de2a97c88938dc7`. |
| `data/raw/crossref_records.json` | PASS | 24 parsed records; sha256 prefix `1c904e2c1a5639b0`. |
| `data/clean/papers_clean.json` | PASS | 22 clean records; sha256 prefix `75964414276a6aaa`. |
| `data/clean/papers_clean.csv` | PASS | 22 clean records; sha256 prefix `164328a4804aa909`. |
| `data/embeddings/papers_embeddings.json` | PASS | 22 baseline index documents; sha256 prefix `abb570a09bc04f7d`. |
| `data/results/baseline_metrics.json` | PASS | Baseline metrics exists; sha256 prefix `4496a73e0a2db58d`. |
| `data/results/baseline_answers.json` | PASS | Baseline answers exists; sha256 prefix `8041dd733712e05c`. |
| `data/quality/freshness_report.json` | PASS | Freshness report exists; sha256 prefix `8f67382b653d589b`. |

Lineage sample tiep tuc doc duoc:

```text
paper_id: 10.36227/techrxiv.177272838.89432844/v1
raw_readable: true
clean_readable: true
index_metadata_readable: true
raw_title_eq_clean: true
clean_title_eq_index: true
raw_abs_url_eq_index: true
```

Ket luan: sample lineage van on dinh tu raw snapshot sang clean data va baseline vector index metadata.

## 2. Raw/clean count va ly do chenh lech

So lieu hien tai:

```text
raw response items: 24
raw parsed records: 24
clean records: 22
baseline index documents: 22
removed rows: 2
drop rate: 8.33%
```

Ly do chenh lech duoc ghi trong `data/quality/cleaning_log.json`:

```json
{
  "invalid_published": 2
}
```

Hai record bi loai:

```text
10.21079/11681/50309 -> invalid_published
10.1111/exsy.70341 -> invalid_published
```

Ket luan: chenh lech raw/clean co ly do ro rang, duoc log lai, va khong phai mat du lieu am tham.

## 3. Phase1 khong fetch lai nguon ngoai y muon

Kiem tra `src/pipelines/phase1.py`:

```text
from ingestion.crossref import load_raw_records
raw_records_path = settings.paths.raw_records_json
raw_records = load_raw_records(raw_records_path)
```

Trong `phase1.py` khong co loi goi:

```text
fetch_source_records(...)
requests.get(...)
Crossref API call
```

Ket luan: phase1 hien doc `data/raw/crossref_records.json` tu snapshot co san, khong refresh `data/raw/crossref_response.json` hoac `data/raw/crossref_records.json` ngoai y muon.

## Baseline CP3 artifacts

Sau pull moi, cac artifact baseline end-to-end da co:

```text
data/results/baseline_metrics.json
data/results/baseline_answers.json
data/quality/freshness_report.json
data/reports/phase1_report.md
```

Baseline metrics hien tai:

```text
samples: 30
retrieval_hit_rate: 1.0
mean_token_f1: 1.0
judge_accuracy: 1.0
mean_judge_score: 5
ragas: skipped unless RUN_RAGAS=1
```

Ket luan: Role 2 CP3 PASS theo ba yeu cau, va repo hien cung da co artifact baseline CP3 de team review.
