# Báo Cáo Cá Nhân — Role 3: Schema, Dữ liệu lỗi và Phục hồi

> Báo cáo được đối chiếu với các commit có Git author `Dung` trên nhánh `dung/role3`. Thông tin cá nhân do thành viên bổ sung trong báo cáo.

## 1. Thông tin cá nhân

| Thông tin | Nội dung |
| --- | --- |
| Họ và tên | Nguyễn Duy Dũng |
| MSSV | 2A202601505 |
| Khóa/Lớp | K3 |
| Tên nhóm | C6_2 |
| Vai trò chính | Role 3 — schema, dữ liệu lỗi và phục hồi dữ liệu |
| Repository         | https://github.com/maniahuv/K3_Day10_Data-Pipeline-Data-Observability_C6_2 |
| Ngày hoàn thành | 2026-08-06               |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input | Output bàn giao | Trạng thái |
| --- | --- | --- | --- | --- |
| Clean-data contract | `docs/clean-schema-contract.md` | `PaperRecord` từ raw snapshot | Quy tắc schema, null/date/dedupe/authors/categories, fixture mẫu | Hoàn thành |
| Cleaning và audit | `src/ingestion/cleaning.py` — `build_clean_dataframe`, `save_clean_artifacts` | Raw `PaperRecord`, ngày chạy | Clean CSV/JSON, `cleaning_log.json` | Hoàn thành |
| Quality contract | `src/observability/quality.py` | Clean dataframe | Kiểm tra null, duplicate ID, `age_days`, `text_for_embedding` | Hoàn thành; hỗ trợ kề cận CP3 |
| Corruption có kiểm chứng | `src/ingestion/corruption.py` — `corrupt_clean_dataframe`, `verify_corruption` | Clean dataframe | Corrupted dataframe, event log, verification result | Hoàn thành |
| Recovery từ raw | `data/clean/papers_clean_repaired.*`, `data/results/repair_validation.json` | `data/raw/crossref_records.json` | Repaired artifacts, cleaning/quality/freshness evidence | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Module được hỗ trợ | Kết quả và bằng chứng |
| --- | --- | --- |
| Sửa ground truth evaluation rỗng/`NaN` | `src/evaluation/testset.py`, `data/eval/test_set.json` | Chỉ tạo câu hỏi author/category khi có dữ liệu; commit `0ed4b54`. Đây là hỗ trợ CP2, không nhận ownership Evaluation. |
| Tăng cường quality check | `src/observability/quality.py` | Không hard-code `PASSED`; kiểm tra title/summary/embedding rỗng, duplicate canonical ID và `age_days` không hợp lệ; commit `f8dc4c2`. |

## 3. Kết quả theo vai trò

| Nhiệm vụ | File/hàm/artifact | Kết quả bàn giao | Cách xác minh |
| --- | --- | --- | --- |
| Chốt clean contract CP0 | `docs/clean-schema-contract.md`, `tests/fixtures/raw_records_sample.json` | 16 cột clean; required fields, ISO date, canonical ID và derived fields được mô tả rõ | Đọc contract; test fixture có valid, duplicate, missing summary và invalid date |
| Chuẩn hóa và lưu clean CP1 | `src/ingestion/cleaning.py`, `data/clean/papers_clean.json`, `data/quality/cleaning_log.json` | 22 clean rows từ 24 raw records; loại 2 record có `invalid_published` | `pytest -q tests/test_cleaning.py` và `data/quality/cleaning_log.json` |
| Kiểm chứng contract CP3 | `src/observability/quality.py`, `data/quality/baseline_quality.json` | Baseline: 22 rows, 0 duplicate ID, 0 empty embedding, `PASSED` | `pytest -q tests/test_quality.py` |
| Tạo corruption CP5 | `src/ingestion/corruption.py`, `data/results/corruption_log.json`, `data/results/corruption_verification.json` | 6 loại event: drop latest, blank summary, noise, truncate title, old date và duplicate; verification `all_passed: true` | `pytest -q tests/test_corruption.py` |
| Phục hồi CP6 | `data/clean/papers_clean_repaired.json`, `data/results/repair_validation.json`, `data/reports/role3_cp6_repair_summary.md` | Rebuild từ raw, không copy/sửa tay baseline; repaired 22 rows, schema/core fields khớp clean, quality `PASSED` | Đọc validation artifact; chạy bộ test cleaning/corruption/quality |

Các commit chính: `72e3600`, `9eceaac`, `3b522e7`, `f8dc4c2`, `e5f0a7c`, `78d1e44`, `24ec3e3`, `a28b09f`.

### Đối chiếu checkpoint CP0–CP6

| Checkpoint | Yêu cầu Role 3 | Bằng chứng thực hiện |
| --- | --- | --- |
| CP0 | Chốt target schema, null/date/duplicate/authors/categories; chỉ ra `text_for_embedding`, `age_days`; chuẩn bị sample raw → clean | `docs/clean-schema-contract.md`, `tests/fixtures/raw_records_sample.json`, commit `72e3600` |
| CP1 | Normalize title/summary/authors/categories, parse published date, stable-ID dedupe, build derived fields, ghi clean artifact/log | `src/ingestion/cleaning.py`, `tests/test_cleaning.py`, `data/clean/papers_clean.*`, `data/quality/cleaning_log.json`, commits `9eceaac`, `3b522e7` |
| CP2 | Xác minh embedding không rỗng/ID không trùng và rà soát evaluation rows | Clean artifact có 22 ID unique, 0 empty embedding; hỗ trợ xử lý ground truth rỗng trong `src/evaluation/testset.py`, commit `0ed4b54` |
| CP3 | Kiểm tra schema/`age_days`/embedding trong artifact; quality check phản ánh dữ liệu thật | `src/observability/quality.py`, `tests/test_quality.py`, `data/quality/baseline_quality.json`, commit `f8dc4c2` |
| CP4 | Nghỉ và chọn corruption có chủ đích | Thiết kế 6 corruption types được hiện thực ở CP5; không có deliverable code riêng cho CP4 |
| CP5 | Corrupt missing/latest drop/noise/old date/duplicate; event log; đối chiếu baseline và corrupted | `src/ingestion/corruption.py`, `tests/test_corruption.py`, `data/results/corruption_log.json`, `data/results/corruption_verification.json`, commits `e5f0a7c`, `78d1e44` |
| CP6 | Re-run cleaning từ raw, kiểm tra repaired schema/count/quality và trình bày khác biệt ba trạng thái | `data/clean/papers_clean_repaired.*`, `data/quality/repaired_*.json`, `data/results/repair_validation.json`, `data/reports/role3_cp6_repair_summary.md`, commit `a28b09f` |

## 4. Giải thích phần kỹ thuật

### Vấn đề cần giải quyết

Raw Crossref có thể thiếu trường bắt buộc, chứa date lỗi hoặc ID trùng. Nếu đưa trực tiếp vào embedding/index thì gây duplicate document, embedding không đáng tin cậy và không thể audit nguyên nhân row bị loại. Pipeline cần tạo lỗi có chủ đích, sau đó chứng minh recovery thực sự đi lại từ raw.

### Cách triển khai

`build_clean_dataframe` chuẩn hóa whitespace; canonical hóa `paper_id` bằng `casefold`; lọc `paper_id`, title, summary hoặc published date không hợp lệ; giữ record đầu tiên của ID trùng; chuẩn hóa list authors/categories theo thứ tự gốc; tạo `primary_category`, `summary_chars`, `age_days` và `text_for_embedding` có nhãn. Mọi record bị loại được ghi reason trong `DataFrame.attrs["cleaning_log"]` rồi lưu bằng `save_clean_artifacts`.

`corrupt_clean_dataframe` làm việc trên bản copy sâu và ghi event-level log có `record_id`, type, parameter, before/after count. `verify_corruption` đối chiếu từng event với khác biệt thật giữa baseline và corrupted, thay vì chỉ dựa vào log.

CP6 gọi lại cleaning từ `data/raw/crossref_records.json`; validation xác nhận repaired schema và core fields khớp clean. Không dùng baseline làm nguồn repair.

### Input, output và contract

| Thành phần | Mô tả |
| --- | --- |
| Input | Parsed `PaperRecord` từ raw Crossref snapshot và `run_date` timezone UTC |
| Output clean | 16 cột: ID, metadata, normalized authors/categories, `summary_chars`, `age_days`, `text_for_embedding` |
| Module phụ thuộc | `ingestion.crossref.PaperRecord`, `core.utils`, `pandas` |
| Module dùng output | Role 4 tạo vector index; Role 5 tạo/evaluate test set; Role 6 đọc quality/freshness artifacts |
| Lỗi xử lý | Missing required field, invalid/future published date, duplicate canonical ID; missing schema khi corrupt |

### Cách xác minh

```powershell
$env:PYTHONPATH = 'src'
pytest -q tests/test_cleaning.py tests/test_corruption.py tests/test_quality.py
```

- Kết quả đã ghi nhận: `4 passed`.
- Artifact: `data/quality/cleaning_log.json`, `data/results/corruption_verification.json`, `data/results/repair_validation.json`.

## 5. Quyết định kỹ thuật quan trọng

- **Bối cảnh:** Cần bảo đảm `paper_id` ổn định và tránh đánh giá nhầm repair vì copy baseline.
- **Phương án cân nhắc:** (1) dedupe theo ID nguyên văn và phục hồi bằng baseline; (2) canonical hóa case-insensitive ID, log record bị loại và rebuild từ raw.
- **Phương án đã chọn:** Phương án (2).
- **Lý do:** Canonical ID giảm duplicate do khác casing; raw là nguồn truy xuất được, nên recovery tái lập được và không che giấu lỗi corruption.
- **Bằng chứng:** `data/results/repair_validation.json` ghi `raw_record_count: 24`, repaired 22 rows, `repaired_schema_matches_clean_contract: true` và `repaired_matches_clean_on_core_fields: true`.

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng:** Các check CP3 có thể trả `PASSED` dù summary/embedding rỗng, ID duplicate khác casing hoặc `age_days` âm.
- **Nguyên nhân gốc:** Điều kiện status không tổng hợp đầy đủ các signal chất lượng; duplicate không canonical hóa nhất quán.
- **Cách xử lý:** Bổ sung các check động cho blank title/summary/embedding, canonical `paper_id`, invalid/negative `age_days`; không hard-code trạng thái pass trong `src/observability/quality.py`.
- **Xác minh:** `tests/test_quality.py` và artifact baseline/repaired `PASSED`; corrupted có 1 duplicate, 1 missing summary và status `WARNING`.
- **Bài học:** Status quality chỉ có giá trị khi được suy ra trực tiếp từ các signal đã đo, đồng thời ID cần cùng quy tắc canonical ở cleaning và quality check.

## 7. Hiểu biết về luồng end-to-end

1. Crossref payload được lưu raw; Role 3 normalize/lọc thành clean artifacts và `text_for_embedding`; Role 4 tạo embedding/vector index từ clean data.
2. Role 5 tạo test set có `ground_truth_doc_ids`; retrieved IDs được đối chiếu với ground truth để tính hit rate, còn câu trả lời được tính F1/judge metrics.
3. Quality check đo tính hợp lệ/tính toàn vẹn tại thời điểm kiểm tra (null, duplicate, schema, age); freshness tập trung vào độ mới theo published date và stale rows.
4. Dùng cùng test set ở baseline/corrupted/repaired để thay đổi metric phản ánh trạng thái dữ liệu, không phải do bộ đề thay đổi.
5. Recovery thành công ở phạm vi Role 3 khi repaired được build từ raw, khớp contract/core clean fields và quality/freshness hồi phục; metric RAG là bằng chứng downstream của Role 5.

## 8. Phân tích kết quả

| Metric/signal | Baseline | Corrupted | Repaired | Nhận xét |
| --- | ---: | ---: | ---: | --- |
| `retrieval_hit_rate` | 1.0 | 0.8 | 1.0 | Artifact Role 5; giảm khi corruption và hồi phục sau repair. |
| `mean_token_f1` | 1.0 | 0.7426 | 1.0 | Artifact Role 5; không phải metric do Role 3 triển khai. |
| `judge_accuracy` | 1.0 | 0.7333 | 1.0 | Artifact Role 5. |
| `mean_judge_score` | 5.0 | 4.1333 | 5.0 | Artifact Role 5. |
| Quality status | `PASSED` | `WARNING` | `PASSED` | Corrupted có 1 duplicate ID và 1 missing summary; repaired không còn vi phạm. |
| Freshness status | fresh | stale | fresh | Corrupted có 1 stale row; repaired không có stale row. |

Chuỗi bằng chứng: corruption chủ đích tạo duplicate, summary rỗng và old date → quality/freshness chuyển `WARNING`/stale và metrics Role 5 giảm → rebuild từ raw đưa quality/freshness và metrics trở lại baseline. Các số metric RAG được đọc từ `data/results/*_metrics.json`; việc chạy evaluation thuộc Role 5 nên không khẳng định Role 3 đã trực tiếp tạo các metric đó.

## 9. Điều học được và hướng cải thiện

1. Contract dữ liệu cần quy định required field, date và canonical ID trước khi index.
2. Audit log theo record/reason giúp truy vết khác biệt row count và chứng minh corruption/recovery.
3. So sánh baseline/corrupted/repaired chỉ đáng tin khi raw source, schema validation và test set được giữ truy vết rõ ràng.

Nếu có thêm thời gian: bổ sung property-based tests cho nhiều biến thể Unicode/casing của `paper_id`, date timezone và list authors/categories; đo bằng số trường hợp invalid/duplicate được phát hiện mà không gây false positive.

## 10. Cam kết thành viên

- [ ] Tự xác nhận thông tin cá nhân và nội dung báo cáo trước khi nộp.
- [x] Kết luận kỹ thuật trong báo cáo có commit, test hoặc artifact đối chiếu.
- [x] Không ghi secret, token hoặc nội dung `.env`.
- [x] Phân biệt ownership Role 3 với phần hỗ trợ ngoài phạm vi.

**Họ và tên:** Nguyễn Duy Dũng.

**Ngày xác nhận:** Chưa xác nhận; cần người nộp điền.
