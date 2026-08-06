# Báo Cáo Cá Nhân (Individual Report) — Day 10: Data Pipeline & Data Observability

> **Thông tin phân công**: Nhóm 6 người — **Vai trò 2: Ingestion Owner** (Phụ trách Ingestion & Dữ liệu Raw).

---

## 1. Thông tin cá nhân

| Thông tin | Nội dung |
| :--- | :--- |
| **Họ và tên** | Ong Xuân Sơn |
| **MSSV** | 2A202601327 |
| **Khóa / Lớp** | K3 |
| **Tên nhóm** | C6_2 |
| **Vai trò chính** | **Role 2: Ingestion Owner (Phụ trách Ingestion & Raw Data)** |
| **Repository** | https://github.com/maniahuv/K3_Day10_Data-Pipeline-Data-Observability_C6_2 |
| **Ngày hoàn thành**| 2026-08-06 |

---

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu (Ownership)

| Module / Deliverable | File / Hàm phụ trách | Input nhận vào | Output bàn giao (Artifacts) | Trạng thái |
| :--- | :--- | :--- | :--- | :--- |
| **API Integration (Crossref)** | `src/ingestion/crossref.py`<br>`fetch_from_crossref()` | URL, Headers (mailto), Query, Filters từ `settings` | `data/raw/crossref_response.json`<br>(Payload thô) | Hoàn thành |
| **Schema Parsing & Validation** | `src/ingestion/crossref.py`<br>`parse_crossref_response()` | JSON thô từ API Crossref | `data/raw/crossref_records.json`<br>(Danh sách các PaperRecord đã parse) | Hoàn thành |
| **Bảo toàn Dữ liệu (Provenance)** | `src/ingestion/crossref.py`<br>`load_raw_records()` | `crossref_records.json` | Danh sách PaperRecord để Role 3 phục hồi dữ liệu | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính
* **Hỗ trợ Role 3 (Cleaning Owner)**: Cung cấp chính xác định dạng Pydantic Schema (`PaperRecord`) để Role 3 biết được cấu trúc dữ liệu thô (field nào có thể null, mảng authors, v.v) nhằm dễ dàng thực thi bước Cleaning.
* **Hỗ trợ Role 1 (Lead)**: Đảm bảo luồng đọc Raw Data ở CP6 không gọi lại API mà load lại từ file `crossref_records.json` nhằm đảm bảo nguyên tắc so sánh Apples-to-Apples.

---

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File / Artifact liên quan | Kết quả bàn giao | Cách xác minh |
| :--- | :--- | :--- | :--- |
| Gọi API Crossref an toàn | `data/raw/crossref_response.json` | Tải thành công payload JSON từ Crossref với truy vấn `agentic retrieval augmented generation large language model`. | `cat data/raw/crossref_response.json` |
| Parse & Ép kiểu dữ liệu | `data/raw/crossref_records.json` | Parse thành công danh sách các bài báo có kèm `paper_id`, `title`, `summary`, `authors`. | `cat data/raw/crossref_records.json \| jq '.[0]'` |
| Kịch bản Repair từ Raw | `src/pipelines/corruption_flow.py` | Cung cấp hàm `load_raw_records` để Role 1 điều phối đọc lại file nguyên bản cho Pha 3 (Repair). | Chạy script báo thành công load bản ghi. |

---

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết
Crossref API chứa lượng dữ liệu khổng lồ với cấu trúc JSON rất phức tạp, lồng nhau nhiều tầng và đôi khi thiếu trường (như không có Abstract hoặc Authors). Nhiệm vụ của Role 2 là gọi API một cách "Polite" (văn minh), lọc đúng chủ đề cần lấy, và ép kiểu toàn bộ mớ JSON lộn xộn đó thành các Object rõ ràng, mạch lạc để làm nguyên liệu đầu vào cho cả Data Pipeline.

### Cách triển khai
1. **HTTP Client & Polite Pool**:
   * Cấu hình thư viện `requests` sử dụng `headers = {"User-Agent": "..."}` và email để truy cập vào nhóm Polite Pool của Crossref nhằm tránh bị Rate Limit / Block API.
2. **Dynamic Query & Filtering**:
   * Truyền tham số `query` và `filter=has-abstract:true,from-pub-date:...` để đảm bảo bài báo lấy về đều có tóm tắt (Abstract) phục vụ cho Vector Search.
3. **Pydantic Schema Extraction**:
   * Viết class `PaperRecord` (Pydantic Model) để định nghĩa cứng các kiểu dữ liệu.
   * Viết logic trích xuất an toàn: dùng `.get()` hoặc list comprehension để lấy `author` (vì API trả về chuỗi họ và tên tách rời), bóc tách `DOI` làm `paper_id`, và lấy `abstract` làm `summary`.

### Input, Output và Contract

| Thành phần | Mô tả |
| :--- | :--- |
| **Input** | Các tham số truy vấn từ `core/config.py` (query, từ khóa, filter, số bản ghi). |
| **Output** | Danh sách cấu trúc dữ liệu `PaperRecord` và 2 file JSON được ghi ra ổ đĩa ở thư mục `data/raw/`. |
| **Module phụ thuộc** | `requests`, thư viện Pydantic. |
| **Module sử dụng Output** | `src/ingestion/cleaning.py` (Role 3), `src/pipelines/corruption_flow.py` (Role 1 khi Repair). |
| **Điều kiện lỗi cần xử lý** | Lỗi HTTP 4xx, 5xx $\rightarrow$ raise Exception dừng pipeline. Lỗi thiếu DOI/Title $\rightarrow$ gán rỗng, nhường cho Cleaning Owner xử lý drop. |

---

## 5. Một quyết định kỹ thuật quan trọng

* **Bối cảnh**: Khi gọi API Crossref về, tôi nhận được một file JSON cực kỳ to và cồng kềnh (hàng nghìn dòng metadata không dùng đến). Nên lưu file nào xuống đĩa?
* **Quyết định (Đã chọn)**: Ghi ra **cả 2 file**: `crossref_response.json` (giữ nguyên gốc rễ 100% từng byte do API trả về) và `crossref_records.json` (chỉ chứa các field đã được trích xuất và ép kiểu qua Pydantic).
* **Lý do**: File Raw thứ nhất (`response.json`) đóng vai trò "Bronze Layer" (Data Lake), giúp debug nếu thuật toán parse bị sai. File Raw thứ hai (`records.json`) đóng vai trò "Silver Layer" giúp các khâu tiếp theo (Cleaning) tải dữ liệu siêu nhanh và nhẹ nhàng mà không cần parse lại từ đầu, đặc biệt hữu ích khi chạy Checkpoint 6 (Repair).

---

## 6. Một lỗi hoặc blocker đã xử lý

* **Triệu chứng / Lỗi nguyên văn**:
  `KeyError: 'abstract'` hoặc báo lỗi thiếu trường tác giả khi khởi tạo đối tượng `PaperRecord`.
* **Nguyên nhân gốc**: Không phải bài báo nào trên Crossref cũng tuân thủ chuẩn form. Rất nhiều bài (dù đã pass bộ lọc `has-abstract:true`) vẫn trả về JSON bị khuyết đi key `abstract` hoặc `author` trống rỗng.
* **Cách xử lý**: Không gọi trực tiếp `item['abstract']`. Thay vào đó, tôi sử dụng `item.get('abstract', '')` và dùng hàm thay thế các thẻ HTML `<jats:p>` lộn xộn trong chuỗi abstract thành văn bản thuần. Nếu không có tác giả thì trả về mảng rỗng `[]` thay vì raise exception, nhường quyền định đoạt (giữ hay bỏ) cho Role 3 (Cleaning).

---

## 7. Hiểu biết về luồng end-to-end

1. **Dữ liệu đi từ Crossref đến vector index như thế nào?**
   * Role 2 (Ingestion) lấy JSON từ API Crossref $\rightarrow$ Lọc ra field cần thiết (PaperRecord) $\rightarrow$ Role 3 (Cleaning) loại bỏ rác/trùng lặp tạo `papers_clean.json` $\rightarrow$ Role 4 (RAG) chuyển hóa text thành các vector số thực lưu vào ChromaDB.
2. **Evaluation set và ground-truth document IDs dùng để đo retrieval/answer quality ra sao?**
   * Bằng cách đối chiếu các `paper_id` mà tôi đã trích xuất từ Crossref (bản chất là DOI của bài báo). Nếu Vector DB tìm đúng bài báo có DOI đó khớp với câu hỏi Test Set thì RAG được tính 1 điểm Hit.
3. **Quality checks khác freshness monitoring ở điểm nào trong bài lab?**
   * Quality kiểm tra chất lượng tại cấu trúc (Data form): trường null, duplicate. Freshness đánh giá về thời gian: dữ liệu API kéo về có bị quá đát (quá cũ) hay không.
4. **Vì sao phải dùng cùng test set cho baseline, corrupted và repaired?**
   * Đảm bảo tính khoa học (Apples-to-Apples). Phải dùng chung một thước đo thì mới thấy được Ingestion bị Corrupted ảnh hưởng thế nào đến đích cuối cùng.
5. **Repair được xem là thành công dựa trên artifact và metric nào?**
   * Repaired thành công khi quy trình đọc lại file Raw của tôi (`crossref_records.json`), chạy qua luồng Clean mới nhất, làm điểm `hit_rate` và `judge_score` khôi phục lại trạng thái cũ ( Baseline ).

---

## 8. Phân tích kết quả

| Metric / Signal | Đóng góp / Nhận xét của Role 2 (Ingestion Owner) |
| :--- | :--- |
| **Tính nguyên vẹn của Raw Data** | Mặc dù Role 3 tiêm lỗi tan nát dữ liệu trong `papers_clean_corrupted.json`, nhưng 2 file Raw do tôi lưu vẫn nguyên vẹn 100%. Đây là cứu cánh duy nhất để Checkpoint 6 có thể thực hiện "Repair". |
| **Độ đa dạng dữ liệu** | Việc bắt chính xác `DOI` và `abstract` đã đảm bảo bộ Test Set có các ngữ cảnh đa dạng, khiến điểm LLM Judge Baseline đạt được độ chính xác tuyệt đối (100% Accuracy). |

---

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất
1. **Data Lake vs Data Warehouse**: Tầm quan trọng của việc luôn luôn sao lưu Payload thô (Raw) trước khi đụng vào ép kiểu. Nó chính là phao cứu sinh để Data Pipeline có thể khôi phục (Repair) khi các Data Mart ở tầng trên bị hỏng hóc.
2. **Đừng tin tưởng API ngoài**: Data từ API bên thứ ba (Third-party) cực kỳ rác và thiếu ổn định. Validation Schema (Pydantic) là vách ngăn bảo vệ hệ thống khỏi crash.
3. **Separation of Concerns**: Ingestion chỉ có nhiệm vụ Bắt dữ liệu và Ép kiểu cơ bản. Việc lọc bỏ (Drop) bài báo do hỏng/thiếu field là việc của khâu Cleaning.

### Nếu có thêm thời gian
* Tôi sẽ implement cơ chế tự động xoay vòng API Key (Rotation) nếu sử dụng nhiều Nguồn cung cấp bài báo (ví dụ nối thêm PubMed, arXiv API) để dữ liệu đổ về Raw Layer phong phú hơn.
