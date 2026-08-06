# Định nghĩa các Tín hiệu Chất lượng Dữ liệu (Data Quality Signals)

Tài liệu này định nghĩa chi tiết 5 tín hiệu đo lường chất lượng dữ liệu và độ tươi mới (freshness) trong pipeline RAG. Các tín hiệu này được áp dụng trực tiếp tại module `src/observability/quality.py`.

---

## 1. Số lượng dòng (Row Count)
*   **Định nghĩa**: Tổng số lượng bản ghi (papers) hiện có trong dataset đang được xử lý.
*   **Cách tính**: Đo kích thước của DataFrame.
    ```python
    row_count = len(df)
    ```
*   **Mục đích giám sát**: 
    *   Phát hiện lỗi sụt giảm dữ liệu đột biến do quá trình fetch API thất bại hoặc filter quá tay.
    *   Đặt ngưỡng cảnh báo (ví dụ: số dòng tối thiểu phải $\ge 50$).

---

## 2. Tỷ lệ giá trị rỗng (Null Rate / Missing Values)
*   **Định nghĩa**: Tỷ lệ phần trăm các dòng có giá trị bị thiếu (Null/NaN) trên các cột quan trọng (`title`, `summary`, `text_for_embedding`, `paper_id`).
*   **Cách tính**: Tính trung bình số ô Null của từng cột hoặc toàn bảng.
    ```python
    null_rates = df[['paper_id', 'title', 'summary', 'text_for_embedding']].isnull().mean().to_dict()
    ```
*   **Mục đích giám sát**:
    *   Đảm bảo các trường bắt buộc để tạo embedding (`text_for_embedding`) và định danh tài liệu (`paper_id`) luôn đầy đủ 100%.
    *   Cảnh báo nếu tỷ lệ rỗng vượt mức cho phép (ngưỡng khuyến nghị: `0%` cho `paper_id`/`title`, `< 5%` cho `summary`).

---

## 3. Tỷ lệ trùng lặp (Duplicate Rate)
*   **Định nghĩa**: Tỷ lệ phần trăm các dòng bị lặp lại trong dataset dựa trên cột định danh (`paper_id`) hoặc tiêu đề (`title`).
*   **Cách tính**:
    ```python
    duplicate_count = df.duplicated(subset=['paper_id']).sum()
    duplicate_rate = duplicate_count / len(df) if len(df) > 0 else 0.0
    ```
*   **Mục đích giám sát**:
    *   Tránh đưa các bản ghi trùng lặp vào cơ sở dữ liệu vector store (ChromaDB), gây tốn bộ nhớ lưu trữ và làm loãng kết quả tìm kiếm top-k (nhiều kết quả giống hệt nhau sẽ lấp đầy context window).
    *   Ngưỡng cảnh báo: `duplicate_rate > 0%` cần thực hiện loại bỏ trùng lặp (deduplication).

---

## 4. Độ cũ dữ liệu (Age in Days / `age_days`)
*   **Định nghĩa**: Khoảng cách thời gian (tính theo ngày) từ ngày công bố công trình (`published`) đến thời điểm hiện tại khi chạy pipeline.
*   **Cách tính**:
    ```python
    # Chuyển đổi published sang datetime
    published_dt = pd.to_datetime(df['published'], errors='coerce')
    current_time = pd.Timestamp.now()
    age_days = (current_time - published_dt).dt.days
    
    # Các metrics thống kê
    mean_age_days = age_days.mean()
    max_age_days = age_days.max()
    min_age_days = age_days.min()
    ```
*   **Mục đích giám sát**:
    *   Đo lường độ cũ của tri thức được nạp vào RAG.
    *   Xác định số lượng dòng bị coi là "stale" (quá cũ - ví dụ `age_days > 365 * 5` năm) để có chiến lược cập nhật tri thức mới hoặc cảnh báo khi hệ thống cần thông tin thời sự.

---

## 5. Nhãn thời gian nguồn (Source Timestamp / Ingestion Timestamp)
*   **Định nghĩa**: Thời điểm dữ liệu được lấy từ nguồn Crossref API và ghi nhận vào hệ thống pipeline.
*   **Cách tính**: Lấy nhãn thời gian hiện tại khi chạy ingestion script và gán làm metadata cho log/dataset.
    ```python
    ingestion_timestamp = pd.Timestamp.now().isoformat()
    ```
*   **Mục đích giám sát**:
    *   Thiết lập vết lịch sử nguồn (data lineage) giúp xác định chính xác thời điểm dữ liệu được nạp.
    *   Hỗ trợ đối soát và kiểm tra xem hệ thống có đang sử dụng các file cache quá cũ mà quên nạp mới hay không.
