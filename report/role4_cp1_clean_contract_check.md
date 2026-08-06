# CP1 - Vai trò 4: Clean contract check cho RAG/index

## Mục tiêu CP1

Vai trò 4 chưa build collection final ở CP1. Việc cần làm ở mốc này là kiểm tra cleaned dataset trước khi đưa vào Chroma index:

1. Đọc vài `text_for_embedding` thật để xem có đủ title/summary, không rỗng, không lặp vô ích.
2. Xác nhận dataframe có đủ `paper_id`, `title`, content và metadata index cần.
3. Chuẩn bị config index từ clean path, nhưng chưa build collection final.

## Trạng thái hiện tại

Đã pull main sau khi role 3 merge cleaning. Hiện repo có clean artifact thật:

- `data/clean/papers_clean.csv`
- `data/clean/papers_clean.json`

Đã chạy script kiểm CP1 trên `data/clean/papers_clean.csv`.

Kết quả:

```text
Rows: 22
Columns: paper_id, title, summary, authors, categories, primary_category,
published, updated, abs_url, pdf_url, comment, authors_joined,
categories_joined, summary_chars, age_days, text_for_embedding

PASS: cleaned dataframe satisfies role4 CP1 retrieval/index contract.
```

Sample `text_for_embedding` đã đọc được, có dạng title + summary, không rỗng:

```text
Title: SafeRAG: A Large-Language-Model-Based Multistage Retrieval-Augmented Framework...
Summary: Summary In high-risk industrial settings, leveraging large language models...
```

## Script đã chuẩn bị

Đã thêm script:

```text
script/check_role4_cp1_clean_contract.py
```

Script này sẽ:

- Đọc `data/clean/papers_clean.csv` hoặc `data/clean/papers_clean.json`.
- Kiểm tra các cột bắt buộc cho `LocalEmbeddingIndex`.
- Kiểm tra `paper_id` duplicate.
- Kiểm tra field rỗng ở `paper_id`, `title`, `text_for_embedding`, `summary`.
- Cảnh báo `text_for_embedding` quá ngắn.
- In sample `text_for_embedding` để review thủ công.
- In sẵn config index baseline nhưng không build collection.

## Cột bắt buộc cho RAG/index

```text
paper_id
title
text_for_embedding
published
authors_joined
categories_joined
summary
abs_url
pdf_url
```

Lưu ý: trong ảnh CP1 có chữ `content`, nhưng trong code repo hiện tại cleaned dataframe không cần cột `content`. `LocalEmbeddingIndex._build_documents()` sẽ map:

```text
row["text_for_embedding"] -> document["content"]
```

## Cách chạy sau khi có clean data

Nếu dùng `uv`:

```powershell
uv sync
uv run python script/check_role4_cp1_clean_contract.py
```

Nếu dùng venv/pip:

```powershell
python -m pip install -e .
python script/check_role4_cp1_clean_contract.py
```

## Config index đã xác nhận

```text
embedding_model = sentence-transformers/all-MiniLM-L6-v2
clean_csv = data/clean/papers_clean.csv
embeddings_manifest = data/embeddings/papers_embeddings.json
chroma_dir = data/chroma
baseline_collection = papers-baseline
```

## Câu báo nhóm

Vai trò 4 đã hoàn thành CP1 check cho RAG contract. Clean data hiện có 22 rows và đủ các field index cần. `text_for_embedding` đọc được, có title + summary, không rỗng. Baseline index config đã xác nhận: MiniLM, Chroma, manifest `data/embeddings/papers_embeddings.json`, collection `papers-baseline`. CP1 chưa build collection final; việc build index sẽ làm ở CP2.
