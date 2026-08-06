# Baseline Validation Checkpoint

- Status: **PASSED**
- Generated at UTC: `2026-08-06T05:16:07.876485+00:00`
- Clean rows: `22`
- Raw records: `24`
- Embedding documents: `22`
- Test samples: `30`

## Baseline Signals

| Group | Signal | Value |
| :--- | :--- | :--- |
| Data quality | Status | `PASSED` |
| Data quality | Row count | `22` |
| Data quality | Paper ID unique | `True` |
| Data quality | Paper ID duplicate count | `0` |
| Data quality | Missing title rate | `0.00%` |
| Data quality | Missing summary rate | `0.00%` |
| Data quality | Row duplicate rate | `0.00%` |
| Freshness | Is fresh | `True` |
| Freshness | Stale rows | `0` |
| Freshness | Threshold days | `180` |
| Freshness | Latest published | `2026-08-01T00:00:00` |
| Freshness | Oldest published | `2026-02-12T00:00:00` |
| Freshness | Mean age days | `81.7` |
| Freshness | Max age days | `175.0` |
| Freshness | Min age days | `5.0` |
| RAG evaluation | Samples | `30` |
| RAG evaluation | Retrieval hit rate | `100.00%` |
| RAG evaluation | Mean token F1 | `1.0000` |
| RAG evaluation | Judge accuracy | `100.00%` |
| RAG evaluation | Mean judge score | `5.00/5` |
| RAG evaluation | RAGAS | `Skipped` |

## Report-To-Artifact Checks

| Check | Source | Expected | Actual | Status |
| :--- | :--- | :--- | :--- | :---: |
| clean CSV row count == clean JSON rows | CSV vs JSON | `22` | `22` | **PASS** |
| clean CSV row count == quality row_count | CSV vs quality JSON | `22` | `22` | **PASS** |
| quality report variants match row_count | baseline_quality vs baseline_quality_checks | `22` | `22` | **PASS** |
| clean CSV row count == freshness total_rows | CSV vs freshness JSON | `22` | `22` | **PASS** |
| clean CSV row count == embedding manifest documents | CSV vs embeddings manifest | `22` | `22` | **PASS** |
| test set samples == metrics samples | test set vs metrics JSON | `30` | `30` | **PASS** |
| answers samples == metrics samples | answers vs metrics JSON | `30` | `30` | **PASS** |
| paper_id uniqueness count | CSV vs quality JSON | `22` | `22` | **PASS** |
| paper_id is unique | CSV vs quality JSON | `True` | `True` | **PASS** |
| paper_id duplicate count | CSV vs quality JSON | `0` | `0` | **PASS** |
| missing title count | CSV vs quality JSON | `0` | `0` | **PASS** |
| missing summary count | CSV vs quality JSON | `0` | `0` | **PASS** |
| row duplicate count | CSV vs quality JSON | `0` | `0` | **PASS** |
| latest published | CSV vs freshness JSON | `2026-08-01T00:00:00` | `2026-08-01T00:00:00` | **PASS** |
| oldest published | CSV vs freshness JSON | `2026-02-12T00:00:00` | `2026-02-12T00:00:00` | **PASS** |
| stale rows | CSV vs freshness JSON | `0` | `0` | **PASS** |
| report retrieval_hit_rate | phase1_report.md vs JSON | `100.00%` | `\| **Retrieval Hit Rate** \| **100.00%** \| Tỷ lệ tìm kiếm được context chứa câu trả lời đúng. \|` | **PASS** |
| report mean_token_f1 | phase1_report.md vs JSON | `1.0000` | `\| **Mean Token F1** \| **1.0000** \| Độ tương đồng mặt chữ giữa câu trả lời sinh ra và Ground Truth. \|` | **PASS** |
| report judge_accuracy | phase1_report.md vs JSON | `100.00%` | `\| **LLM Judge Accuracy** \| **100.00%** \| Tỷ lệ câu trả lời được LLM đánh giá đạt yêu cầu. \|` | **PASS** |
| report mean_judge_score | phase1_report.md vs JSON | `5.00/5` | `\| **Mean Judge Score** \| **5.00/5** \| Điểm số chất lượng câu trả lời trung bình. \|` | **PASS** |
| report ragas | phase1_report.md vs JSON | `Skipped` | `\| **RAGAS Score** \| **Skipped** \| Điểm đánh giá tổng hợp RAGAS (nếu có). \|` | **PASS** |
| report row_count | phase1_report.md vs JSON | `22` | `*   **Tổng số dòng (Row Count)**: 22 bản ghi.` | **PASS** |
| report paper_id_unique | phase1_report.md vs JSON | `True` | `*   **Tính duy nhất của `paper_id`**: `True` (Số bản ghi trùng lặp ID: 0).` | **PASS** |
| report title_missing_rate | phase1_report.md vs JSON | `0.00%` | `*   Thiếu `title`: 0.00%` | **PASS** |
| report summary_missing_rate | phase1_report.md vs JSON | `0.00%` | `*   Thiếu `summary`: 0.00%` | **PASS** |
| report row_duplicate_rate | phase1_report.md vs JSON | `0.00%` | `*   **Tỷ lệ trùng lặp dòng (Row duplicates)**: 0.00%` | **PASS** |
| report quality_status | phase1_report.md vs JSON | `PASSED` | `*   **Trạng thái kiểm tra (Status)**: `PASSED`` | **PASS** |
| report latest_published | phase1_report.md vs JSON | `2026-08-01T00:00:00` | `*   **Ngày xuất bản mới nhất (Latest Published)**: `2026-08-01T00:00:00`` | **PASS** |
| report oldest_published | phase1_report.md vs JSON | `2026-02-12T00:00:00` | `*   **Ngày xuất bản cũ nhất (Oldest Published)**: `2026-02-12T00:00:00`` | **PASS** |
| report stale_rows | phase1_report.md vs JSON | `0` | `*   **Số lượng dòng bị stale (cũ quá hạn)**: 0` | **PASS** |
| report mean_age_days | phase1_report.md vs JSON | `81.7` | `*   **Độ tuổi trung bình (`age_days`)**: 81.7 ngày (Lớn nhất: 175.0 ngày, Nhỏ nhất: 5.0 ngày).` | **PASS** |
| report max_age_days | phase1_report.md vs JSON | `175.0` | `*   **Độ tuổi trung bình (`age_days`)**: 81.7 ngày (Lớn nhất: 175.0 ngày, Nhỏ nhất: 5.0 ngày).` | **PASS** |
| report min_age_days | phase1_report.md vs JSON | `5.0` | `*   **Độ tuổi trung bình (`age_days`)**: 81.7 ngày (Lớn nhất: 175.0 ngày, Nhỏ nhất: 5.0 ngày).` | **PASS** |
| report is_fresh | phase1_report.md vs JSON | `True` | `*   **Trạng thái tươi mới (Is Fresh)**: `True` (Ngưỡng cấu hình: 180 ngày).` | **PASS** |
| report freshness_threshold | phase1_report.md vs JSON | `180` | `*   **Trạng thái tươi mới (Is Fresh)**: `True` (Ngưỡng cấu hình: 180 ngày).` | **PASS** |

## Decision

Baseline is considered complete only when every check above is PASS. Use `data/results/baseline_checkpoint.json` as the frozen baseline reference for the next corruption and repair comparison pass.
