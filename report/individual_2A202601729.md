# Member Role Report — Day 10: Data Pipeline & Data Observability

> Mỗi thành viên trong nhóm tự hoàn thành mẫu này để báo cáo đúng vai trò, phần việc và mức hiểu của mình. Không sao chép nguyên báo cáo chung hoặc báo cáo của thành viên khác. Thay nội dung trong dấu `[ ]` và xóa các dòng hướng dẫn không cần thiết trước khi nộp.

## 1. Thông tin cá nhân

| Thông tin         | Nội dung                                      |
| ------------------ | -------------------------------------------- |
| Họ và tên       | Giang Minh Phú                                  |
| MSSV               | 2A202601729                                  |
| Khóa/Lớp         | K3                                 |
| Tên nhóm         | C6_2                           |
| Vai trò chính    | role 4 - RAG & agent                      |
| Repository         |   https://github.com/maniahuv/K3_Day10_Data-Pipeline-Data-Observability_C6_2                     |
| Ngày hoàn thành | 2026-08-06                                 |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao  | Trạng thái |
| ------------------ | --------------------- | ---------------- | ----------------- | ---------- |
| RAG index contract và clean-data readiness | `report/role4/role4_cp0_rag_contract.md`, `script/role4/check_role4_cp1_clean_contract.py` | Clean dataset từ role ingestion/cleaning | Xác nhận schema cần cho embedding: `paper_id`, `title`, `text_for_embedding`, metadata | Hoàn thành |
| Baseline retrieval index | `script/role4/run_role4_cp2_rag_smoke.py`, `src/retrieval/index.py` | `data/clean/papers_clean.csv` | Chroma collection `papers-baseline`, manifest `data/embeddings/papers_embeddings.json`, smoke report | Hoàn thành |
| RAG agent smoke test | `script/role4/run_role4_cp2_agent_smoke.py`, `src/retrieval/agent.py` | Baseline index và LLM provider từ `.env` | Bằng chứng agent dùng tool `semantic_search_papers` trước khi trả lời | Hoàn thành |
| Baseline/corrupted/repaired index verification | `script/role4/run_role4_cp3_baseline_audit.py`, `script/role4/run_role4_cp5_corrupted_index_check.py`, `script/role4/run_role4_cp6_repaired_index_check.py` | Baseline, corrupted và repaired clean artifacts | Báo cáo kiểm tra 3 collection/path tách biệt, lookup/search/agent smoke | Hoàn thành |

Chỉ nhận ownership cho phần bạn trực tiếp thực hiện. Liên hệ rõ phần việc của bạn với đầu vào, đầu ra và các thành viên phụ thuộc vào phần đó.

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động                         | Thành viên/module được hỗ trợ | Kết quả |
| ------------------------------------ | ----------------------------- | ------- |
| Kiểm tra contract clean data trước khi index | Role 3 - Cleaning/repair | Phát hiện rõ role4 cần `text_for_embedding` không rỗng, `paper_id` ổn định và metadata đủ để Chroma lưu trữ |
| Cung cấp smoke query/lookup evidence cho evaluation | Role 5 - Evaluation | Có baseline/corrupted/repaired retrieval evidence để đối chiếu metric |
| Xác nhận đường dẫn artifact và collection tách biệt | Role 1 - Integration/report | Có report riêng trong `report/role4/` và evidence JSON trong `data/results/` |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| --------------------------- | ----------------------------- | ------------------------- | ----------------------- |
| Đọc contract retrieval và xác định input/output role4 | `report/role4/role4_cp0_rag_contract.md` | Chốt dùng MiniLM, Chroma, collection naming `papers-baseline`, `papers-corrupted`, `papers-repaired` | Đối chiếu file report CP0 |
| Kiểm tra clean data đủ điều kiện embedding | `script/role4/check_role4_cp1_clean_contract.py`, `report/role4/role4_cp1_clean_contract_check.md` | Clean dataset có 22 dòng, đủ cột, `text_for_embedding` không rỗng | `uv run python script/role4/check_role4_cp1_clean_contract.py` |
| Build baseline index và smoke semantic search/lookup | `script/role4/run_role4_cp2_rag_smoke.py`, `data/results/role4_cp2_smoke.json` | Search và exact lookup chạy được trên `papers-baseline` | `uv run python script/role4/run_role4_cp2_rag_smoke.py` |
| Kiểm tra agent dùng tool trước khi trả lời | `script/role4/run_role4_cp2_agent_smoke.py`, `data/results/role4_cp2_agent_smoke.json` | Agent trả lời câu hỏi SafeRAG và có tool-call evidence | `uv run python script/role4/run_role4_cp2_agent_smoke.py` |
| Kiểm tra baseline sau CP3 | `script/role4/run_role4_cp3_baseline_audit.py`, `data/results/role4_cp3_baseline_audit.json` | Manifest baseline khớp clean dataset, collection đúng, testset mapping không thiếu ID | `uv run python script/role4/run_role4_cp3_baseline_audit.py` |
| Tạo corrupted collection và kiểm tra baseline không bị mutate | `script/role4/run_role4_cp5_corrupted_index_check.py`, `data/results/role4_cp5_corrupted_index_check.json` | `papers-corrupted` tách khỏi `papers-baseline`; baseline vẫn đọc được | `uv run python script/role4/run_role4_cp5_corrupted_index_check.py` |
| Tạo repaired collection và kiểm tra agent trên dữ liệu repaired | `script/role4/run_role4_cp6_repaired_index_check.py`, `data/results/role4_cp6_repaired_index_check.json` | CP6 PASS, `papers-repaired` có 22 rows, agent dùng tool và trả về document repaired | `uv run python script/role4/run_role4_cp6_repaired_index_check.py` |

Nêu một output cụ thể mà phần việc của bạn tạo ra hoặc giúp xác minh:

Output quan trọng nhất của vai trò 4 là bộ chỉ mục vector Chroma cho ba trạng thái dữ liệu: baseline, corrupted và repaired. Mỗi trạng thái có manifest embedding riêng trong `data/embeddings/` và collection riêng trong Chroma. Các file evidence trong `data/results/role4_cp*.json` chứng minh semantic search, exact lookup và agent tool-use đều hoạt động đúng.

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết

Vai trò 4 giải quyết phần biến clean data thành tri thức có thể truy vấn cho RAG agent. Nếu dữ liệu sạch/corrupted/repaired bị đưa chung vào một collection hoặc thiếu metadata, evaluation sẽ không còn công bằng vì không biết câu trả lời đến từ trạng thái dữ liệu nào. Vì vậy phần của tôi tập trung vào việc tạo index tách biệt, kiểm tra search/lookup và xác nhận agent thật sự dùng tool retrieval trước khi trả lời.

### Cách triển khai

Dữ liệu clean được đọc từ CSV/JSON, mỗi paper được chuyển thành một document gồm `record_id`, `paper_id`, `title`, `content` và metadata. Nội dung embedding chính là `text_for_embedding`, được tạo từ title, summary và authors để semantic search có đủ ngữ cảnh. Embedding model dùng `sentence-transformers/all-MiniLM-L6-v2`; vector database dùng Chroma persistent client.

Ba trạng thái dữ liệu được tách bằng collection name:

- Baseline: `papers-baseline`
- Corrupted: `papers-corrupted`
- Repaired: `papers-repaired`

Agent được xây bằng LangChain, có hai tool chính: `semantic_search_papers` và `lookup_paper`. Khi nhận câu hỏi factual, agent phải gọi tool trước, rồi mới trả lời dựa trên kết quả retrieval.

### Input, output và contract

| Thành phần                   | Mô tả |
| ------------------------------ | ----- |
| Input                          | `data/clean/papers_clean.csv`, `data/clean/papers_clean_corrupted.csv`, `data/clean/papers_clean_repaired.csv`; yêu cầu có `paper_id`, `title`, `text_for_embedding`, `published`, `authors_joined`, `categories_joined`, `summary`, `abs_url`, `pdf_url` |
| Output                         | Chroma collections `papers-baseline`, `papers-corrupted`, `papers-repaired`; manifests `data/embeddings/papers_embeddings*.json`; reports/evidence trong `report/role4/` và `data/results/` |
| Module phụ thuộc             | `src/retrieval/index.py`, `src/retrieval/embeddings.py`, `src/retrieval/agent.py`, `src/core/config.py` |
| Module sử dụng output        | `src/evaluation/qa.py`, `src/evaluation/metrics.py`, pipeline/report comparison của nhóm |
| Điều kiện lỗi cần xử lý | Thiếu repaired artifact, collection Chroma chưa tồn tại, embedding manifest chưa khớp collection, agent trả lời mà không gọi tool |

### Cách xác minh

```bash
uv run python script/role4/check_role4_cp1_clean_contract.py
uv run python script/role4/run_role4_cp2_rag_smoke.py
uv run python script/role4/run_role4_cp2_agent_smoke.py
uv run python script/role4/run_role4_cp3_baseline_audit.py
uv run python script/role4/run_role4_cp5_corrupted_index_check.py
uv run python script/role4/run_role4_cp6_repaired_index_check.py
```

- **Kết quả mong đợi:** Các script trả status `pass`, ba collection/path tách biệt, search/lookup trả document đúng, agent có tool call trước khi trả lời.
- **Kết quả thực tế:** CP6 PASS; `repaired_rows = 22`, `collections_ok = true`, `paths_distinct = true`, `used_tool_before_answer = true`, `returned_repaired_doc = true`.
- **Artifact/log:** `data/results/role4_cp6_repaired_index_check.json`, `report/role4/role4_cp6_repaired_index_check.md`.

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Cần đánh giá baseline, corrupted và repaired trên cùng pipeline RAG nhưng không được để các trạng thái dữ liệu ghi đè lẫn nhau trong Chroma.
- **Các phương án đã cân nhắc:** Dùng một collection duy nhất và rebuild mỗi lần; hoặc dùng ba collection riêng cho baseline/corrupted/repaired.
- **Phương án đã chọn:** Dùng ba collection riêng: `papers-baseline`, `papers-corrupted`, `papers-repaired`.
- **Lý do:** Cách này dễ tái lập, dễ đối chiếu và giảm rủi ro metric bị sai do collection cũ bị mutate. Nó cũng giúp role evaluation và observability đọc đúng trạng thái dữ liệu cần đo.
- **Bằng chứng quyết định phù hợp:** CP5 chứng minh build `papers-corrupted` không làm baseline bị mutate; CP6 chứng minh `papers-repaired` tách path và collection, agent vẫn dùng tool và lấy đúng document repaired.

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:** `Collection [papers-baseline] does not exist` và trước đó CP6 bị `BLOCKED` vì thiếu `data/clean/papers_clean_repaired.csv`.
- **Lệnh hoặc bước tái hiện:** `uv run python script/role4/run_role4_cp6_repaired_index_check.py`.
- **Nguyên nhân gốc:** Chroma persistent data trong local có thể chưa có collection đúng dù manifest tồn tại; đồng thời CP6 phụ thuộc role cleaning/repair tạo repaired dataset trước.
- **Cách xử lý:** Script CP6 được thiết kế kiểm tra input trước. Nếu thiếu repaired data thì ghi report `BLOCKED`. Khi data đã có, script tự load hoặc rebuild baseline/corrupted từ CSV, sau đó build repaired collection từ repaired CSV.
- **Cách xác minh sau khi sửa:** Chạy lại script CP6 sau khi pull data repaired; kết quả `status: pass`, `collections_ok: true`, `paths_distinct: true`, agent dùng tool và tool trả về document repaired.
- **Điều học được:** Với vector database local, không nên chỉ tin vào file manifest; cần kiểm tra collection thật trong Chroma và có cơ chế rebuild tái lập được từ clean artifacts.

Nếu chưa xử lý xong:

- **Phạm vi bị ảnh hưởng:** Không còn blocker mở cho phần role4 CP6.
- **Những gì đã loại trừ:** Đã kiểm tra thiếu data repaired, sai tên path repaired, collection Chroma chưa tồn tại và agent không gọi tool.
- **Bước tiếp theo:** Nếu nhóm cần nộp cuối, chỉ cần merge nhánh role4 và đối chiếu với báo cáo tổng hợp.

## 7. Hiểu biết về luồng end-to-end

Giải thích ngắn gọn bằng lời của bạn:

1. Dữ liệu đi từ Crossref đến vector index như thế nào?
2. Evaluation set và ground-truth document IDs dùng để đo retrieval/answer quality ra sao?
3. Quality checks khác freshness monitoring ở điểm nào trong bài lab?
4. Vì sao phải dùng cùng test set cho baseline, corrupted và repaired?
5. Repair được xem là thành công dựa trên artifact và metric nào?

**Câu trả lời:**

Dữ liệu bắt đầu từ Crossref raw response, sau đó role ingestion parse thành record chuẩn. Role cleaning tạo clean dataset có `paper_id` ổn định, title, summary, authors, ngày xuất bản và `text_for_embedding`. Vai trò 4 lấy clean dataset đó để tạo embedding bằng MiniLM và lưu vào Chroma. Khi agent nhận câu hỏi, agent gọi tool semantic search hoặc lookup để lấy context từ collection rồi mới trả lời.

Evaluation set gồm các câu hỏi cố định và `ground_truth_doc_ids`. Khi chạy baseline, corrupted và repaired, cùng một bộ câu hỏi được dùng lại để đảm bảo phép so sánh công bằng. Nếu đổi test set giữa các trạng thái thì không biết metric thay đổi do dữ liệu hay do câu hỏi khác.

Quality checks đo tính đúng và ổn định của dataset như row count, null, duplicate, `paper_id` uniqueness và field bắt buộc. Freshness monitoring đo độ mới của dữ liệu theo timestamp/ngày xuất bản, ví dụ `age_days`. Hai phần này bổ sung cho nhau: quality nói dữ liệu có sạch/đủ/không trùng không, freshness nói dữ liệu có còn cập nhật không.

Repair được xem là thành công khi repaired dataset phục hồi về số dòng và chất lượng gần baseline, không còn lỗi duplicate/missing nghiêm trọng, metrics RAG hồi phục và role4 có thể build `papers-repaired` riêng. Trong kết quả hiện tại, repaired có 22 rows, quality status `PASSED`, retrieval hit rate trở lại 1.0 và agent smoke trên repaired collection PASS.

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal          | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
| ---------------------- | -------: | --------: | -------: | ------------------------- |
| `retrieval_hit_rate` | 1.00 | 0.80 | 1.00 | Corruption làm giảm khả năng lấy đúng tài liệu; repair khôi phục về baseline. |
| `mean_token_f1`      | 1.00 | 0.743 | 1.00 | Nội dung bị thiếu/nhiễu làm câu trả lời kém khớp ground truth; repaired phục hồi hoàn toàn. |
| `judge_accuracy`     | 1.00 | 0.733 | 1.00 | Judge đánh giá corrupted thấp hơn rõ rệt do answer dựa trên context xấu. |
| `mean_judge_score`   | 5.00 | 4.13 | 5.00 | Điểm judge giảm ở corrupted và quay lại mức tối đa sau repair. |
| Quality checks         | PASSED | WARNING | PASSED | Corrupted có duplicate, thiếu summary và row count giảm; repaired trở lại sạch. |
| Freshness status       | PASSED | WARNING | PASSED | Corrupted có age_days max tăng tới 402; repaired quay về max 175 như baseline. |

### Kết luận từ số liệu

Hoàn thành hai chuỗi nguyên nhân–bằng chứng sau:

1. Corruption làm mất/nhân bản/nhiễu dữ liệu → quality status chuyển từ `PASSED` sang `WARNING`, row count giảm từ 22 xuống 21, có duplicate và missing summary → retrieval hit rate giảm từ 1.00 xuống 0.80, token F1 giảm còn khoảng 0.743, judge accuracy còn khoảng 0.733.
2. Repair phục hồi dữ liệu từ nguồn sạch/raw → quality status quay lại `PASSED`, row count trở lại 22, duplicate và missing summary về 0 → retrieval hit rate, token F1, judge accuracy và mean judge score quay lại mức baseline.

Corruption ảnh hưởng rõ nhất là các lỗi làm mất hoặc làm sai nội dung dùng để embedding, vì RAG phụ thuộc trực tiếp vào context được retrieve. Nếu document bị drop, trùng, summary rỗng hoặc text bị nhiễu thì agent vẫn có thể gọi tool nhưng tool trả context kém, dẫn đến câu trả lời giảm chất lượng.

Kết quả khác với kỳ vọng ban đầu là query smoke top 3 của baseline/corrupted/repaired vẫn giống nhau trong CP5/CP6. Điều này không có nghĩa corruption không ảnh hưởng, mà do query smoke cụ thể không chạm mạnh vào record bị corrupt. Metric evaluation trên 30 câu hỏi cho thấy ảnh hưởng thật rõ hơn: retrieval hit rate và answer quality đều giảm ở corrupted.

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất

1. Vector index phải có contract rõ ràng với clean data: thiếu `paper_id`, `title`, `text_for_embedding` hoặc metadata sẽ làm search/lookup và evaluation khó tin cậy.
2. Data quality/observability không chỉ là báo cáo phụ; nó giúp giải thích vì sao metric RAG giảm khi dữ liệu bị corrupt.
3. RAG agent không tự sửa được context xấu. Agent có thể dùng tool đúng nhưng nếu vector index chứa dữ liệu lỗi thì câu trả lời vẫn bị ảnh hưởng.

### Nếu có thêm thời gian

Tôi sẽ thêm bộ smoke query bao phủ trực tiếp các record bị corrupt, ví dụ query theo paper bị drop hoặc summary bị rỗng. Cải thiện này giúp CP5/CP6 nhìn rõ hơn sự khác biệt retrieval giữa corrupted và repaired thay vì chỉ dựa vào query baseline chung.

## 10. Cam kết của thành viên

Đánh dấu sau khi tự kiểm tra:

- [ x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [ x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [ x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [ x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [ x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [ x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Giang Minh Phú
**Ngày xác nhận:** 2026-08-06
