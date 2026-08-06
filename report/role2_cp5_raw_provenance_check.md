# CP5 - Vai tro 2: Raw provenance & fairness check

## Muc tieu

Trong checkpoint 5, vai tro 2 chung minh ba dieu:

1. Raw source snapshot da duoc xac nhan va giu nguyen truoc khi corrupt clean data.
2. Mot sample paper_id co the truy vet ro rang tu raw -> clean -> embedding manifest.
3. Corruption flow khong fetch lai Crossref trong qua trinh compare baseline/corrupted/repaired, de giu cong bang cho benchmark.

## Evidence

- Raw snapshot hien co tai `data/raw/crossref_response.json` va `data/raw/crossref_records.json`.
- Sample paper_id duoc chon: `10.36227/techrxiv.177272838.89432844/v1`.
- Raw record va clean record deu co chung paper_id, title va abs_url.
- Artifact provenance duoc tao boi `src/ingestion/crossref.py` va luu tai `data/quality/raw_provenance_checkpoint5.json`.

## Sample lineage

```text
paper_id: 10.36227/techrxiv.177272838.89432844/v1
raw_title: A Survey of (Deep RAG) Deep Retrieval Augmented Generation and Reasoning in Large Language Models
clean_title: A Survey of (Deep RAG) Deep Retrieval Augmented Generation and Reasoning in Large Language Models
raw_abs_url: https://doi.org/10.36227/techrxiv.177272838.89432844/v1
clean_abs_url: https://doi.org/10.36227/techrxiv.177272838.89432844/v1
```

## Freeze rule

Corruption flow phai su dung frozen raw snapshot da co san. Khong goi `fetch_source_records(...)` hay refresh raw data trong qua trinh so sanh baseline/corrupted/repaired.
