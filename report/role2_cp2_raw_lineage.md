# CP2 - Vai tro 2: Raw lineage & source evidence

## Pham vi

Vai tro 2 phu trach lay Crossref, luu raw, va truy vet du lieu raw. Trong CP2, muc tieu la giu snapshot nguon on dinh va ho tro team kiem tra mot `paper_id` xuyen suot:

```text
raw records -> clean records -> vector index metadata
```

## Trang thai artifact

| Artifact | Trang thai | Ghi chu |
| --- | --- | --- |
| `data/raw/crossref_response.json` | Co | Raw API response snapshot da luu. |
| `data/raw/crossref_records.json` | Co | 24 parsed raw records. |
| `data/clean/papers_clean.json` | Co | 22 clean records. |
| `data/clean/papers_clean.csv` | Co | 22 clean records. |
| `data/embeddings/papers_embeddings.json` | Co | Baseline embedding manifest, collection `papers-baseline`, 22 documents. |
| `data/chroma/` baseline collection | Co | Chroma DB da co artifact cho baseline collection. |
| `data/eval/test_set.json` | Co | 40 evaluation questions. |
| `data/results/role4_cp2_smoke.json` | Co | Role 4 smoke test PASS. |

## Paper lineage sample

Paper duoc chon de doi chieu:

```text
paper_id: 10.36227/techrxiv.177272838.89432844/v1
title: A Survey of (Deep RAG) Deep Retrieval Augmented Generation and Reasoning in Large Language Models
source url: https://doi.org/10.36227/techrxiv.177272838.89432844/v1
```

### Raw evidence

Trong `data/raw/crossref_records.json`, record nay co:

```text
published: 2026-03-05
updated: 2026-06-12
authors: Lihui Liu
summary: Retrieval-Augmented Generation (RAG) has emerged as a powerful paradigm...
```

### Clean evidence

Trong `data/clean/papers_clean.json`, cung `paper_id` nay co:

```text
published: 2026-03-05
updated: 2026-06-12
authors_joined: Lihui Liu
summary_chars: 1309
age_days: 154
text_for_embedding: bat dau bang Title + Summary cua cung paper
```

Ket luan: lineage `raw -> clean` hop le cho sample nay. `paper_id`, title, published date, updated date, source URL va summary deu duoc bao toan/derive dung theo clean contract.

## Vector index metadata check

Da xac minh `clean -> vector index metadata` trong `data/embeddings/papers_embeddings.json`:

```text
collection_name: papers-baseline
embedding_model: sentence-transformers/all-MiniLM-L6-v2
documents: 22
```

Manifest co document metadata cho cung `paper_id`:

```text
metadata.paper_id == 10.36227/techrxiv.177272838.89432844/v1
metadata.title == A Survey of (Deep RAG) Deep Retrieval Augmented Generation and Reasoning in Large Language Models
metadata.published == 2026-03-05
metadata.authors_joined == Lihui Liu
metadata.abs_url == https://doi.org/10.36227/techrxiv.177272838.89432844/v1
content/text == text_for_embedding tu clean data
collection_name == papers-baseline
```

Ket luan: lineage sample nay da di du `raw -> clean -> vector index metadata`.

## Evidence khi evaluator/agent tra loi sai

Neu evaluator hoac agent tra loi sai ve paper sample nay, dung cac bang chung sau:

1. Source snapshot: `data/raw/crossref_records.json`
2. Clean record: `data/clean/papers_clean.json`
3. DOI/source URL: `https://doi.org/10.36227/techrxiv.177272838.89432844/v1`
4. Field doi chieu: `paper_id`, `title`, `published`, `updated`, `authors_joined`, `summary`, `abs_url`

Khong can fetch lai Crossref de tranh thay doi baseline. Neu can them bang chung, doc tu raw snapshot da luu.

## Freeze rule

Trong CP2, khong chay lai `fetch_source_records` va khong refresh `data/raw/crossref_response.json` / `data/raw/crossref_records.json` khi team dang build baseline. Baseline hien dang dua tren:

```text
raw response items: 24
raw parsed records: 24
clean records: 22
baseline index documents: 22
eval test set questions: 40
removed records: 2 invalid_published
```

Neu bat buoc refresh source, phai thong bao team va tao snapshot/version moi rieng de khong lam metric baseline thay doi giua chung.
