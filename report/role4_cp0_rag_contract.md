# CP0 - Vai trò 4: RAG & agent

## Phạm vi phụ trách

Vai trò 4 phụ trách phần RAG/retrieval:

- Tạo embedding bằng `sentence-transformers/all-MiniLM-L6-v2`.
- Lưu và truy vấn vector store bằng ChromaDB.
- Hỗ trợ semantic search trong corpus paper.
- Hỗ trợ exact lookup theo `paper_id` hoặc exact `title`.
- Cung cấp index/metadata để evaluation tính retrieval hit rate và agent trả lời factual question.

Các file chính:

- `src/retrieval/embeddings.py`
- `src/retrieval/index.py`
- `src/retrieval/agent.py`
- `src/retrieval/qa.py`
- `src/retrieval/llm.py`
- `data/embeddings/`
- `data/chroma/`

## Contract input từ cleaning

`LocalEmbeddingIndex.build(df, settings, embeddings_output_path)` nhận một cleaned dataframe. Dataframe này phải có đủ các cột sau:

| Cột | Mục đích |
| --- | --- |
| `paper_id` | Stable document ID, dùng cho lookup và `ground_truth_doc_ids` trong evaluation. |
| `title` | Tên paper, dùng cho exact title lookup và metadata. |
| `text_for_embedding` | Nội dung chính để tạo embedding. Không được rỗng. |
| `published` | Ngày xuất bản, dùng trả lời câu hỏi date/freshness. |
| `authors_joined` | Chuỗi tác giả đã chuẩn hóa, dùng trả lời câu hỏi authors. |
| `categories_joined` | Chuỗi category/subject đã chuẩn hóa, dùng trả lời câu hỏi categories. |
| `summary` | Tóm tắt paper, dùng trả lời câu hỏi summary. |
| `abs_url` | URL abstract/landing page, lưu trong metadata. |
| `pdf_url` | URL PDF nếu có, lưu trong metadata. |

Điều kiện cần chốt với vai trò 3:

- `paper_id` phải stable và unique sau cleaning.
- `text_for_embedding` phải có thông tin đủ để semantic search hoạt động, tối thiểu nên ghép title + summary + authors/categories nếu có.
- Không để `title`, `summary`, `text_for_embedding` rỗng ở các record được đưa vào index.
- Các field metadata nên là string hoặc giá trị đơn giản để ChromaDB lưu ổn định.

## Contract output của RAG/index

Khi build baseline index, output cần có:

- `data/chroma/`: ChromaDB persistent store.
- `data/embeddings/papers_embeddings.json`: manifest của baseline embedding/index.

Manifest cần có:

```json
{
  "backend": "chroma",
  "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
  "persist_path": "data/chroma",
  "collection_name": "papers-baseline",
  "documents": []
}
```

Collection naming trong `src/core/config.py`:

| Dataset trạng thái | Embedding manifest | Chroma collection |
| --- | --- | --- |
| Baseline | `data/embeddings/papers_embeddings.json` | `papers-baseline` |
| Corrupted | `data/embeddings/papers_embeddings_corrupted.json` | `papers-corrupted` |
| Repaired | `data/embeddings/papers_embeddings_repaired.json` | `papers-repaired` |

Lưu ý: corrupted/repaired phải build collection riêng, không ghi đè baseline.

## Search, lookup và QA behavior

`LocalEmbeddingIndex.search(query, top_k)`:

- Embed query bằng cùng model MiniLM.
- Query ChromaDB với cosine space.
- Trả về list `SearchResult`.
- Mỗi result có `paper_id`, `title`, `score`, `content`, `metadata`.

`LocalEmbeddingIndex.lookup(value)`:

- Exact lookup bằng lowercase `paper_id`.
- Nếu không match `paper_id`, exact lookup bằng lowercase `title`.
- Không fuzzy match.

`answer_question(...)` trong `src/retrieval/qa.py`:

- Nếu question có title trong dấu nháy đơn `'...'`, ưu tiên exact title lookup.
- Sau đó vẫn chạy semantic search để lấy top-k context.
- Trả lời theo rule:
  - authors question → `authors_joined`
  - date/published question → `published`
  - categories question → `categories_joined`
  - còn lại → câu đầu tiên của `summary`

`build_agent(...)` trong `src/retrieval/agent.py`:

- Tạo agent có 2 tool:
  - `semantic_search_papers`
  - `lookup_paper`
- Agent phải dùng tool trước khi trả lời câu hỏi factual.
- Agent cần LLM provider config trong `.env`.

## LLM provider cần biết

Provider được hỗ trợ trong `src/retrieval/llm.py`:

- `gemini`
- `openai`
- `anthropic`
- `openrouter`
- `ollama`
- `custom`

Mặc định `.env.example` đang dùng:

```dotenv
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.5-flash
GOOGLE_API_KEY=
```

Nếu chưa có API key, vẫn có thể smoke test `LocalEmbeddingIndex.search`, `lookup`, và `answer_question`; chỉ phần `build_agent` thật mới cần provider/credential.

## Smoke test chuẩn bị cho CP2

Sau khi vai trò 1/3 đã tạo clean data và pipeline build index xong, chạy các smoke test sau.

### 1. Load index

```python
from pathlib import Path

from core.config import load_settings
from retrieval.index import LocalEmbeddingIndex

settings = load_settings(Path("."))
index = LocalEmbeddingIndex.load(settings)

print(index.collection_name)
print(len(index.documents))
```

Kỳ vọng:

- `collection_name` là `papers-baseline`.
- `len(index.documents)` bằng số row cleaned được index.

### 2. Semantic search

```python
results = index.search("retrieval augmented generation large language model", top_k=3)

for item in results:
    print(item.paper_id, item.score, item.title)
```

Kỳ vọng:

- Có ít nhất 1 result.
- `paper_id`, `title`, `score` đọc được.
- Score không âm.

### 3. Exact lookup bằng `paper_id`

```python
first_doc = index.documents[0]
record = index.lookup(first_doc["paper_id"])

print(record["paper_id"])
print(record["title"])
```

Kỳ vọng:

- Lookup trả đúng record.

### 4. Exact lookup bằng `title`

```python
record = index.lookup(first_doc["title"])

print(record["paper_id"])
print(record["title"])
```

Kỳ vọng:

- Lookup trả đúng record.
- Nếu title bị normalize khác giữa cleaning và question, cần báo lại vai trò 3/5 để thống nhất.

### 5. QA smoke test không cần agent LLM

```python
from retrieval.qa import answer_question

question = f"What is the paper '{first_doc['title']}' about?"
result = answer_question(question, settings=settings, index=index)

print(result.answer)
print(result.retrieved_doc_ids)
```

Kỳ vọng:

- `answer` lấy từ summary.
- `retrieved_doc_ids[0]` nên là `first_doc["paper_id"]` do exact title lookup được ưu tiên.

## Câu nói bàn giao CP0 cho nhóm

Vai trò 4 đã đọc retrieval contract. Index cần cleaned dataframe có `paper_id`, `title`, `text_for_embedding` và metadata gồm `published`, `authors_joined`, `categories_joined`, `summary`, `abs_url`, `pdf_url`. Embedding dùng `sentence-transformers/all-MiniLM-L6-v2`, vector store dùng ChromaDB, baseline collection là `papers-baseline`; corrupted/repaired có collection riêng để không ghi đè baseline. Sau khi cleaning xong, mình sẽ build index và smoke test semantic search, exact lookup theo `paper_id/title`, và QA rule-based trước khi giao cho evaluation.

## CP0 checklist

- [x] Đọc `LocalEmbeddingIndex`, embeddings, agent, QA và LLM provider.
- [x] Xác định input schema cần từ cleaned dataframe.
- [x] Xác định output artifact: `data/chroma/` và `data/embeddings/*.json`.
- [x] Chốt embedding model: `sentence-transformers/all-MiniLM-L6-v2`.
- [x] Chốt collection naming: baseline/corrupted/repaired tách riêng.
- [x] Chốt metadata tối thiểu cần lưu trong Chroma.
- [x] Chuẩn bị smoke query/lookup để dùng sau khi index.

