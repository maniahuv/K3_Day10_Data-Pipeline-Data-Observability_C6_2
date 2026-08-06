# Group Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin bài nộp

| Thông tin         | Nội dung                  |
| ------------------ | -------------------------- |
| Khóa/Lớp         | K3                         |
| Tên nhóm         | C6_2               |
| Repository         | https://github.com/maniahuv/K3_Day10_Data-Pipeline-Data-Observability_C6_2 |
| Ngày hoàn thành | 2026-08-06                 |

### Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò chính | Module/deliverable sở hữu |
| --: | --- | --- | --- | --- |
| 1 | Vũ Hải Nam | 2A202601173 | Role 1 (Lead/Orchestrator) | `corruption_flow.py`, `phase1.py`, `core/config.py` |
| 2 | Ong Xuân Sơn | 2A202601327 | Role 2 (Ingestion) | `crossref.py`, `raw_records.json` |
| 3 | Nguyễn Duy Dũng | 2A202601505 | Role 3 (Cleaning/Corrupt) | `cleaning.py`, `corruption.py`, `papers_clean.json` |
| 4 | Giang Minh Phú | 2A202601729 | Role 4 (RAG/Embedding) | `retrieval/index.py`, Vector Database |
| 5 | Nguyễn Minh Nhật | 2A202601131 | Role 5 (Evaluation) | `evaluation/metrics.py`, `test_set.json` |
| 6 | Nguyễn Tiến Thành | 2A202601539 | Role 6 (Observability) | `observability/quality.py`, `reporting.py` |

## 2. Tóm tắt kết quả

**Tóm tắt của nhóm:**
Nhóm đã hoàn thành xuất sắc toàn bộ 6 Checkpoint cho 3 giai đoạn: Baseline, Corrupted và Repaired. 
- Ở **Baseline**, pipeline chạy mượt mà từ việc kéo Data qua Crossref, chuẩn hóa, đến nhúng vector, sinh ra bộ `test_set.json` (30 câu) và ghi nhận kết quả tuyệt đối (Hit Rate 100%, Judge Score ~4.5/5). 
- Ở **Corruption**, nhóm đã tiêm 6 loại lỗi (xóa abstract, nhiễu text, lỗi ngày tháng) làm ảnh hưởng nghiêm trọng đến cả Data Quality (Null rate tăng, Stale) và Agent (Token F1 rớt thảm từ 0.85 xuống 0.21, Judge Score còn 1.75). 
- Ở **Repair**, nhóm đã lội ngược dòng phục hồi thành công hoàn toàn dữ liệu bằng cách chạy lại (re-ingest) từ file Raw nguyên thủy (Raw records không bị ghi đè), giúp tất cả chỉ số Quality và Metrics của RAG quay về mốc 100% như lúc đầu. Blocker duy nhất ban đầu là Git Merge Conflict các file .json, đã được giải quyết bằng việc ignore data artifacts.

## 3. Kiến trúc và luồng dữ liệu

### Luồng end-to-end

```text
Crossref API
    -> raw response/raw records (Role 2)
    -> cleaning và data modeling (Role 3)
    -> embedding + ChromaDB index (Role 4)
    -> evaluation baseline (Role 5)
    -> quality/freshness reports (Role 6)
    -> corruption (Role 3)
    -> re-index và re-evaluate (Role 4 & 5)
    -> repair từ dữ liệu nguồn gốc Raw (Role 2 & 3)
    -> comparison report tổng hợp (Role 6)
```

### Trách nhiệm của từng khối

| Khối             | Input          | Xử lý chính             | Output/artifact          | Owner          |
| ----------------- | -------------- | -------------------------- | ------------------------ | -------------- |
| Ingestion         | Crossref API URL | Fetch, retry, parse ra Pydantic | `data/raw/crossref_records.json` | Ong Xuân Sơn |
| Cleaning          | `raw_records.json` | Xóa rỗng, ghép text, lọc trùng | `data/clean/papers_clean.json` | Role 3 |
| Embedding/index   | `papers_clean.json`| MiniLM, lưu vào ChromaDB | `data/chroma/papers-baseline/` | Role 4 |
| Evaluation        | Test set + ChromaDB| Đo Hit Rate, F1, LLM Judge | `baseline_metrics.json` | Nguyễn Minh Nhật |
| Observability     | `papers_clean.json`| Check rỗng, duplicate, tuổi đời| `baseline_quality.json` | Role 6 |
| Corruption/repair | `papers_clean.json`| Drop latest, nhiễu, fake date | `corrupted_metrics.json` | Role 3 |
| Orchestration     | `config.py` paths | Nối các module theo thứ tự | `corruption_report.md` | Vũ Hải Nam |

## 4. Cách tái hiện kết quả

### Cấu hình không chứa secret

| Biến/cấu hình             | Giá trị sử dụng |
| ---------------------------- | ------------------- |
| `LLM_PROVIDER`             | gemini |
| `LLM_MODEL`                | gemini-2.5-flash |
| Embedding model              | sentence-transformers/all-MiniLM-L6-v2 |
| Số lượng Crossref records | 24 |
| Retrieval`top_k`           | 4 |
| Freshness threshold          | 30 days |

### Lệnh cài đặt

```bash
uv sync
```

### Lệnh chạy

Baseline:
```bash
python script/run_phase1.py
```

Corruption & Repair flow:
```bash
python script/run_corruption_flow.py
```

### Kết quả tái hiện

| Lệnh             | Trạng thái                                    | Thời điểm chạy gần nhất | Bằng chứng                         |
| ----------------- | ----------------------------------------------- | ----------------------------- | ------------------------------------ |
| Baseline pipeline | Thành công | Vừa xong | `baseline_metrics.json` |
| Corruption flow   | Thành công | Vừa xong | `corruption_report.md` |

## 5. Ingestion, cleaning và data contract

### Nguồn dữ liệu

| Thuộc tính                | Giá trị                             |
| --------------------------- | ------------------------------------- |
| Source                      | Crossref REST API |
| Query/filter                | `agentic retrieval augmented generation large language model`, `has-abstract:true` |
| Thời điểm lấy dữ liệu | 2026-08-06 |
| Số record nhận được    | 24 |
| Cơ chế retry/backoff      | Timeout 10s, dùng Polite Pool (mailto) |

### Quy tắc cleaning

| Quy tắc                                 | Quality dimension liên quan | Số record bị tác động | Cách xác minh      |
| ---------------------------------------- | ---------------------------- | -------------------------: | -------------------- |
| Loại bỏ record không có abstract (summary)| Completeness | 0 (do API filter) | Kiểm tra rỗng trong DF |
| Lọc trùng lặp `paper_id` | Uniqueness | ~2 | Quality check duplicate |

## 6. Evaluation setup

| Thành phần                             | Cấu hình thực tế          |
| ---------------------------------------- | ----------------------------- |
| Số câu hỏi                            | 30 |
| Các`question_type`                    | `summary`, `authors`, `date`, `categories` |
| Ground-truth document ID                 | Lấy trực tiếp `paper_id` từ row dữ liệu tương ứng |
| Embedding model                          | all-MiniLM-L6-v2 |
| Vector store/collection                  | ChromaDB (`papers-baseline`) |
| Retrieval`top_k`                       | 4 |
| LLM provider/model                       | Gemini (gemini-2.5-flash) |
| Test set dùng chung cho ba trạng thái | `data/eval/test_set.json` |

Giải thích vì sao test set được giữ nguyên:
Giữ nguyên Test set (Đề thi) đảm bảo tiêu chuẩn khoa học (Apples-to-Apples). Nếu mỗi tập dữ liệu sinh ra một bộ câu hỏi riêng thì không thể đo lường sự sụt giảm hiệu năng (Degradation) do Corruption hay mức độ khôi phục do Repair.

## 7. Kết quả baseline

### Artifact checklist

| Artifact                 | Đường dẫn thực tế                | Trạng thái | Ghi chú   |
| ------------------------ | -------------------------------------- | ------------ | ---------- |
| Raw response/records     | `data/raw/`                          | Có | Giữ bản response thô và bản parsed |
| Cleaned dataset          | `data/clean/`                        | Có | `papers_clean.json` |
| Embedding manifest/index | `data/chroma/`                   | Có | Index lưu ở Chroma SQLite |
| Evaluation set           | `data/eval/`                         | Có | `test_set.json` |
| Baseline metrics         | `data/results/baseline_metrics.json` | Có | Hit Rate 100% |
| Quality/freshness        | `data/quality/`                      | Có | `baseline_quality.json` |
| Baseline report          | `data/reports/phase1_report.md`      | Có | Báo cáo Pha 1 |

### Baseline metrics

| Metric                 |       Giá trị | Diễn giải                             |
| ---------------------- | --------------: | --------------------------------------- |
| `retrieval_hit_rate` |     100.0% | Tỷ lệ context đúng được tìm thấy |
| `mean_token_f1`      |     0.85 | Độ trùng lặp từ ngữ câu trả lời AI và gốc |
| `judge_accuracy`     |     100.0% | Tỷ lệ LLM giám khảo chấm Pass (>= 3/5) |
| `mean_judge_score`   |     4.60 | Điểm ngữ nghĩa tuyệt đối 1-5 |

## 8. Data quality và freshness

### Quality checks

| Check        | Quality dimension | Ngưỡng/kỳ vọng | Kết quả baseline      | Bằng chứng |
| ------------ | ----------------- | ------------------ | ----------------------- | ------------ |
| Null Summary | Completeness | 0% | Pass (0%) | `baseline_quality.json` |
| Duplicate ID | Uniqueness | 0% | Pass (0%) | `baseline_quality.json` |

### Freshness

| Thuộc tính               | Giá trị                           |
| -------------------------- | ----------------------------------- |
| Freshness được đo tại | Dựa trên `published_date` của bản ghi mới nhất |
| Ngưỡng freshness         | 30 days |
| Trạng thái baseline      | FRESH |
| Lý do                     | Bản ghi mới nhất cập nhật trong vòng 30 ngày so với `run_date` |

## 9. Corruption scenarios và repair

| Corruption         | Cách tạo | Record bị tác động | Quality signal kỳ vọng | Tác động thực tế | Cách repair   |
| ------------------ | ---------- | ---------------------: | ------------------------ | --------------------- | -------------- |
| Blank summary | Xóa rỗng text | 1 | Null Rate > 0% | Metric F1 rớt, Null Check fail | Chạy lại từ raw |
| Inject Noise | Thêm token rác | 1 | Validity fail | LLM Hallucinate, Judge rớt điểm | Chạy lại từ raw |
| Age published | Trừ đi 365 ngày | 1 | Freshness > 30 ngày | Báo cáo Freshness STALE | Chạy lại từ raw |

Giải thích cách repair:
Thay vì vá víu file JSON hiện tại (vá lổ hổng), nhóm quyết định gọi lại hàm `load_raw_records()` của Role 2 để bốc dữ liệu gốc từ API, rồi qua tay Role 3 làm sạch lại từ đầu. Cách này mô phỏng chuẩn xác việc khôi phục toàn vẹn dữ liệu từ Data Lake (Bronze layer) lên Data Warehouse (Silver layer).

## 10. So sánh baseline, corrupted và repaired

| Metric/signal            | Baseline | Corrupted | Repaired | Thay đổi do corruption | Mức phục hồi | Nhận xét   |
| ------------------------ | -------: | --------: | -------: | -----------------------: | --------------: | ------------ |
| `retrieval_hit_rate`   |      100% |       85% |      100% |                      -15% |             100% | Index bị hỏng do title sai |
| `mean_token_f1`        |      0.85 |       0.21 |      0.85 |                      -0.64 |             100% | Rớt cực nặng do nhiễu text |
| `judge_accuracy`       |      100% |       20% |      100% |                      -80% |             100% | LLM trả lời sai hoàn toàn khi thiếu context |
| `mean_judge_score`     |      4.60 |       1.75 |      4.60 |                      -2.85 |             100% | Phục hồi như mới |
| Quality checks pass/fail |      PASS |       FAIL |      PASS |                      FAIL |             PASS | Phát hiện được null/dup |
| Freshness status         |      FRESH |       STALE |      FRESH |                      STALE |             FRESH | Lỗi chỉnh sửa Date |

Nêu ít nhất hai kết luận có quan hệ nhân quả:
1. `Blank summary` → `Null Rate check FAIL` → `mean_token_f1 giảm mạnh do AI không có đáp án`.
2. `Chạy lại từ Raw API Payload` → `Null Rate & Freshness về bình thường` → `Hit Rate & Judge Score phục hồi 100%`.

## 11. Vấn đề tích hợp quan trọng

- **Triệu chứng:** Khi chạy `corruption_flow.py`, hàm `LocalEmbeddingIndex.build` báo lỗi dư tham số `collection_name`.
- **Nguyên nhân:** Khác biệt Interface. Role 4 đã code cho phép tự động nội suy `collection_name` từ đường dẫn file JSON, nhưng Role 1 lại truyền tay vào.
- **Cách xử lý:** Xóa bỏ tham số `collection_name` khi gọi hàm build trong script của Role 1.
- **Cách xác minh:** `python script/run_corruption_flow.py` chạy mượt mà không crash.

## 12. Giới hạn và hướng cải thiện

| Giới hạn hiện tại | Ảnh hưởng   | Hướng cải thiện có thể kiểm chứng |
| --------------------- | -------------- | ----------------------------------------- |
| Phụ thuộc hoàn toàn vào file nội bộ | Gặp Git Conflict liên tục do các file JSON/SQLite. | Cấu hình `.gitignore` cho thư mục `data/` và dùng S3 bucket để chia sẻ Data artifacts. |
| Test Set bị Bias | Test Set sinh tự động bằng heuristics từ chính data (LLM-generated), có thể LLM Judge thiên vị. | Dùng RAGAS kết hợp con người gán nhãn thủ công khoảng 50 câu. |

## 13. Checklist trước khi nộp

- [x] Thông tin nhóm và repository chính xác.
- [x] Phân công khớp với module, artifact và kết quả thực tế.
- [x] Lệnh tái hiện đã được chạy lại trên phiên bản dùng để nộp.
- [x] Baseline, corrupted và repaired dùng cùng evaluation set.
- [x] Bảng metrics khớp với các file trong `data/results/`.
- [x] Quality/freshness conclusions khớp với `data/quality/`.
- [x] Các đường dẫn báo cáo và artifact truy cập được.
- [x] Mỗi thành viên đã hoàn thành báo cáo vai trò riêng.
- [x] Không có `.env`, API key, token hoặc secret trong source, report, log hay ảnh.
