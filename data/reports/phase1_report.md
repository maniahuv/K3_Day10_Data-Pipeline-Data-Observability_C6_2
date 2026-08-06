# Báo cáo Pha 1 - Đánh giá Baseline RAG Pipeline (Dữ liệu Sạch)

Tài liệu này tổng hợp hiệu suất vận hành của RAG Pipeline và chất lượng dữ liệu cơ sở (baseline) trước khi tiến hành tiêm lỗi (corruption).

---

## 1. Tóm tắt Nguồn Dữ liệu (Source Summary)
*   **Nguồn tích hợp (API)**: Crossref REST API
*   **Query tìm kiếm**: `agentic retrieval augmented generation large language model`
*   **Bộ lọc (Filters)**: `from-pub-date:2026-02-07,has-abstract:true`
*   **Số lượng bản ghi tối đa yêu cầu**: 24

---

## 2. Kết quả Đo lường Hiệu suất RAG (Evaluation Metrics)
Các chỉ số dưới đây được đánh giá trên tập câu hỏi chuẩn (`evaluation_testset.json`):

| Chỉ số (Metric) | Giá trị Baseline | Đánh giá & Nhận xét |
| :--- | :---: | :--- |
| **Retrieval Hit Rate** | **100.00%** | Tỷ lệ tìm kiếm được context chứa câu trả lời đúng. |
| **Mean Token F1** | **1.0000** | Độ tương đồng mặt chữ giữa câu trả lời sinh ra và Ground Truth. |
| **LLM Judge Accuracy** | **100.00%** | Tỷ lệ câu trả lời được LLM đánh giá đạt yêu cầu. |
| **Mean Judge Score** | **5.00/5** | Điểm số chất lượng câu trả lời trung bình. |
| **RAGAS Score** | **N/A (Skipped)** | Điểm đánh giá tổng hợp RAGAS (nếu có). |

---

## 3. Chất lượng Dữ liệu & Độ tươi mới (Data Quality & Freshness)
Các tín hiệu đo lường chất lượng dữ liệu thu thập được từ bước Ingestion & Cleaning:

### A. Kiểm tra Chất lượng Dữ liệu (Quality Checks)
*   **Tổng số dòng (Row Count)**: 22 bản ghi.
*   **Tính duy nhất của `paper_id`**: `True` (Số bản ghi trùng lặp ID: 0).
*   **Tỷ lệ thiếu trường dữ liệu**:
    *   Thiếu `title`: 0.00%
    *   Thiếu `summary`: 0.00%
*   **Tỷ lệ trùng lặp dòng (Row duplicates)**: 0.00%
*   **Trạng thái kiểm tra (Status)**: `PASSED`

### B. Kiểm tra Độ tươi mới (Freshness Report)
*   **Ngày xuất bản mới nhất (Latest Published)**: `2026-08-01T00:00:00`
*   **Ngày xuất bản cũ nhất (Oldest Published)**: `2026-02-12T00:00:00`
*   **Số lượng dòng bị stale (cũ quá hạn)**: 0
*   **Độ tuổi trung bình (`age_days`)**: 81.7 ngày (Lớn nhất: 175.0 ngày, Nhỏ nhất: 5.0 ngày).
*   **Trạng thái tươi mới (Is Fresh)**: `True` (Ngưỡng cấu hình: 180 ngày).

---

## 4. Kết luận Giai đoạn Baseline
*   Dữ liệu thô từ nguồn Crossref đã được làm sạch hoàn toàn mà không gặp lỗi thiếu thông tin (`missing_rate = 0%`) hoặc trùng lặp (`duplicate_rate = 0%`).
*   Hiệu suất tìm kiếm và trả lời của Agent ở mức ổn định, tạo cơ sở để đối chiếu và phân tích ảnh hưởng của dữ liệu lỗi ở các giai đoạn sau.
