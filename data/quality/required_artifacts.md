# Danh sách Artifacts bắt buộc sau Baseline và Dữ liệu Lỗi Flow

Tài liệu này liệt kê toàn bộ các file kết quả (artifacts) cần phải có sau khi hoàn thành chạy **Pha 1 (Baseline với dữ liệu sạch)** và **Pha 2 (Dữ liệu lỗi - Corruption & Repair Flow)**.

---

## 1. Sau khi chạy Baseline (Phase 1)
Sau khi chạy thành công baseline pipeline (ví dụ qua lệnh `python script/run_phase1.py`), hệ thống phải sinh ra các artifacts sau:

### A. Dữ liệu Ingestion & Cleaning
*   `data/raw/raw_crossref_response.json`: Phản hồi thô nguyên bản từ Crossref API.
*   `data/raw/raw_crossref_records.json`: Danh sách các record thô đã được parse thành cấu trúc JSON phẳng ban đầu.
*   `data/clean/cleaned_papers.csv` hoặc `cleaned_papers.json`: Tập dữ liệu sạch đã loại bỏ trường không hợp lệ, chuẩn hóa các trường thông tin và sẵn sàng cho embedding.

### B. Embedding & Vector Store Index
*   `data/embeddings/papers_embeddings.json`: File lưu trữ/manifest thông tin vector embedding phục vụ cho baseline collection (`papers-baseline`).

### C. Bộ câu hỏi Đánh giá (Evaluation Set)
*   `data/eval/evaluation_testset.json`: File chứa tập câu hỏi mẫu gồm `question`, `ground_truth`, `ground_truth_doc_ids` phục vụ chấm điểm.

### D. Kết quả đo lường & Giám sát
*   `data/results/baseline_metrics.json`: Các chỉ số đánh giá chất lượng RAG trên baseline (Hit Rate, Token F1, Judge Score,...).
*   `data/quality/baseline_quality_checks.json`: Kết quả kiểm tra chất lượng dữ liệu sạch (row count, null rate, duplicate rate,...).
*   `data/quality/baseline_freshness_report.json`: Báo cáo độ tươi mới dữ liệu của baseline (latest/oldest published date, stale count,...).

### E. Báo cáo Tóm tắt
*   `data/reports/phase1_report.md`: Báo cáo chi tiết Pha 1 tổng hợp kết quả baseline.

---

## 2. Sau khi chạy Dữ liệu Lỗi Flow (Corruption & Repair)
Sau khi chạy xong corruption flow (ví dụ qua lệnh `python script/run_corruption_flow.py`), hệ thống phải bổ sung đầy đủ các artifacts sau:

### A. Dữ liệu Lỗi (Corrupted Phase)
*   `data/clean/corrupted_papers.csv`: Dữ liệu đã bị tiêm lỗi chủ động (xóa summary, trùng lặp dòng, làm stale ngày tháng,...).
*   `data/results/corruption_log.json`: Ghi nhật ký chi tiết các hành động corrupt đã thực hiện (như tỷ lệ dòng bị corrupt, số lượng bản ghi bị xóa).
*   `data/results/corrupted_metrics.json`: Chỉ số đánh giá RAG khi hệ thống truy vấn trên cơ sở dữ liệu lỗi.
*   `data/quality/corrupted_quality_checks.json`: Kết quả kiểm tra chất lượng dữ liệu lỗi, chỉ ra các cảnh báo vượt ngưỡng (null rate tăng, duplicate xuất hiện).
*   `data/quality/corrupted_freshness_report.json`: Báo cáo độ tươi mới của dữ liệu lỗi (cho thấy dữ liệu bị stale nặng).

### B. Dữ liệu Sửa lỗi (Repaired Phase)
*   `data/clean/repaired_papers.csv`: Dữ liệu sau khi áp dụng thuật toán/luồng sửa lỗi từ nguồn raw/baseline.
*   `data/results/repaired_metrics.json`: Chỉ số đánh giá RAG sau khi cơ sở tri thức đã được sửa lỗi.
*   `data/quality/repaired_quality_checks.json`: Kết quả kiểm tra chất lượng dữ liệu sau sửa lỗi (phải quay lại mức an toàn giống baseline).
*   `data/quality/repaired_freshness_report.json`: Báo cáo độ tươi mới của dữ liệu sau sửa đổi.

### C. Báo cáo So sánh Tổng hợp
*   `data/reports/corruption_report.md`: Báo cáo so sánh trực quan hiệu suất RAG và chất lượng dữ liệu qua 3 trạng thái: **Baseline vs. Corrupted vs. Repaired**.
