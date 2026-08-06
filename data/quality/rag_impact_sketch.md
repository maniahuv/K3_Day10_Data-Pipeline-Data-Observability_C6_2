# Phác thảo Báo cáo Chứng minh Dữ liệu xấu làm giảm hiệu suất RAG

Báo cáo này phác thảo cách thức chứng minh mối quan hệ nhân quả: **Chất lượng dữ liệu đầu vào (data quality) đi xuống trực tiếp kéo theo sự sụt giảm hiệu suất của hệ thống RAG (agent performance)**.

---

## 1. Mục tiêu (Objective)
Chứng minh định lý kinh điển của ngành dữ liệu: **"Garbage In, Garbage Out"** trong ngữ cảnh Retrieval-Augmented Generation. Cụ thể, đo lường định lượng mức độ sụt giảm của khả năng tìm kiếm (retrieval) và khả năng trả lời (generation) khi dữ liệu bị tiêm các loại lỗi thực tế (corruption).

---

## 2. Thiết kế Thử nghiệm (Experiment Design)
Đánh giá hệ thống trên **cùng một bộ test set cố định** (`evaluation_testset.json`) qua 3 trạng thái dữ liệu:
1.  **Baseline**: Dữ liệu sạch (Cleaned data).
2.  **Corrupted**: Dữ liệu lỗi (Bị tiêm lỗi: null summary, duplicate rows, stale published date, truncated title).
3.  **Repaired**: Dữ liệu sau khi được sửa chữa (Cleaned & restored).

---

## 3. Khung Số liệu So sánh (Comparative Metrics Framework)

| Nhóm Metric | Chỉ số (Metric) | Baseline (Sạch) | Corrupted (Lỗi) | Repaired (Đã sửa) | Giải thích & Tác động |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Data Quality** | Row Count | 100 | 100 (hoặc giảm do mất mát) | 100 | Phát hiện mất mát dữ liệu |
| | Null Rate (`summary`) | 0.0% | 30.0% | 0.0% | Tỷ lệ rỗng của tóm tắt thông tin |
| | Duplicate Rate | 0.0% | 15.0% | 0.0% | Tỷ lệ bản ghi bị trùng lặp |
| | Max Age (`age_days`) | 180 ngày | 5000 ngày | 180 ngày | Độ tươi mới (Staleness) |
| **RAG Retrieval**| **Retrieval Hit Rate** | **~90%** | **~45%** | **~88%** | Tỷ lệ tìm kiếm đúng tài liệu chứa câu trả lời |
| **RAG Generation**| **Mean Token F1** | **~0.82** | **~0.35** | **~0.80** | Độ trùng khớp ngôn từ giữa LLM và Ground Truth |
| | **Judge Accuracy** | **~88%** | **~30%** | **~85%** | Tỷ lệ câu trả lời được LLM Judge đánh giá là Đúng |
| | **Mean Judge Score** | **~4.5/5** | **~2.1/5** | **~4.4/5** | Điểm số chất lượng câu trả lời trung bình |

---

## 4. Phân tích Tác động của từng loại lỗi cụ thể (Root Cause Analysis)

### Kịch bản A: Null / Trống cột `summary` hoặc `text_for_embedding`
*   **Cơ chế tác động**: Khi sinh vector embedding cho tài liệu rỗng hoặc quá ngắn, mô hình embedding không nắm bắt được thông tin ngữ nghĩa.
*   **Hậu quả**:
    *   **Retrieval**: Khi người dùng hỏi, kết quả tìm kiếm tương đồng ngữ nghĩa trả về các chunk rỗng hoặc chunk không liên quan.
    *   **Generation**: LLM không nhận được ngữ cảnh hữu ích, buộc phải tự bịa ra câu trả lời (hallucination) hoặc trả lời "Tôi không biết", dẫn đến F1 và Judge Score giảm thảm hại.

### Kịch bản B: Trùng lặp tài liệu (Duplicate Records)
*   **Cơ chế tác động**: ChromaDB lưu trữ nhiều bản sao giống nhau của cùng một bài báo dưới các ID khác nhau.
*   **Hậu quả**:
    *   Khi query top-k (ví dụ k=3), hệ thống tìm kiếm sẽ trả về 3 bản ghi giống hệt nhau.
    *   Cửa sổ ngữ cảnh (context window) của LLM bị chiếm dụng hoàn toàn bởi thông tin trùng lặp, đẩy các thông tin hữu ích từ các tài liệu khác ra ngoài. LLM thiếu thông tin đa chiều để trả lời hoàn chỉnh.

### Kịch bản C: Dữ liệu quá hạn / Sai lệch ngày tháng (`age_days` & Stale dates)
*   **Cơ chế tác động**: Ngày xuất bản (`published`) bị chỉnh sửa thành thời điểm quá khứ xa xưa (stale).
*   **Hậu quả**:
    *   Đối với các câu hỏi so sánh hoặc đòi hỏi tính cập nhật (ví dụ: *"Đề xuất gần đây nhất về X là gì?"*), RAG Agent dựa vào metadata ngày tháng để sắp xếp/lọc dữ liệu sẽ lấy sai bài viết cũ, dẫn đến câu trả lời lỗi thời và sai thực tế.

---

## 5. Kết luận & Khuyến nghị (Conclusion & Recommendations)
*   **Kết luận**: Chất lượng dữ liệu quyết định giới hạn trên của hiệu suất RAG. Không có mô hình LLM nào có thể sửa chữa được ngữ cảnh bị rỗng hoặc sai lệch đầu vào.
*   **Khuyến nghị**: 
    1. Thiết lập các chốt chặn dữ liệu (data quality gates) ngay tại ingestion pipeline bằng Great Expectations hoặc validator tự viết.
    2. Cảnh báo dừng pipeline hoặc đưa vào luồng cách ly (quarantine flow) nếu các cảnh báo chất lượng dữ liệu vượt ngưỡng.
