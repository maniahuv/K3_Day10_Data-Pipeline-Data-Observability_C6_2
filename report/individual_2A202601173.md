# Báo Cáo Cá Nhân (Individual Report) — Day 10: Data Pipeline & Data Observability

> **Thông tin phân công**: Nhóm 6 người — **Vai trò 1: Integration & Orchestrator (Lead)** (Phụ trách Dàn xếp Pipeline & Quản lý Git).

---

## 1. Thông tin cá nhân

| Thông tin | Nội dung |
| :--- | :--- |
| **Họ và tên** | Vũ Hải Nam |
| **MSSV** | 2A202601173 |
| **Khóa / Lớp** | K3 |
| **Tên nhóm** | C6_2 |
| **Vai trò chính** | **Role 1: Team Lead (Phụ trách Dàn nhạc, Data Contract & Orchestration)** |
| **Repository** | https://github.com/maniahuv/K3_Day10_Data-Pipeline-Data-Observability_C6_2 |
| **Ngày hoàn thành**| 2026-08-06 |

---

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu (Ownership)

| Module / Deliverable | File / Hàm phụ trách | Input nhận vào | Output bàn giao (Artifacts) | Trạng thái |
| :--- | :--- | :--- | :--- | :--- |
| **Data Contract & Configuration** | `src/core/config.py` | Biến môi trường (`.env`) | Object `settings` chứa toàn bộ đường dẫn (paths) tập trung, không hard-code. | Hoàn thành |
| **Phase 1 Orchestrator (Baseline)** | `src/pipelines/phase1.py` | Lời gọi hàm từ Role 2, 3, 4, 5, 6 | Pipeline chạy mượt mà từ Raw $\rightarrow$ Clean $\rightarrow$ RAG $\rightarrow$ Eval $\rightarrow$ Báo cáo. | Hoàn thành |
| **Phase 2 Orchestrator (Corrupt & Repair)** | `src/pipelines/corruption_flow.py` | Module Corruption (Role 3), hàm Repair | Tự động hóa quá trình sinh lỗi, đánh giá dữ liệu hỏng, và phục hồi (Repaired). | Hoàn thành |
| **Source Control (Git Master)** | `GitHub Repository` | Pull Requests từ 5 thành viên | Codebase sạch sẽ ở nhánh `main`, giải quyết các conflict cấu hình. | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính
* **Hỗ trợ toàn đội (Scrum Master)**: Thiết lập bộ khung (Skeleton) ban đầu cho tất cả các file. Đặt bẫy `raise NotImplementedError` để tạo "khung thành" cho các Role khác biết vị trí cần đắp Code vào.
* **Hỗ trợ Role 6 (Observability)**: Truyền đúng và đủ các biến `baseline_metrics`, `corrupted_quality`, v.v., vào hàm tổng hợp Báo cáo để Role 6 có dữ liệu sinh Markdown.

---

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File / Artifact liên quan | Kết quả bàn giao | Cách xác minh |
| :--- | :--- | :--- | :--- |
| Thiết kế Data Contract | `src/core/config.py` | Tất cả đường dẫn file JSON/CSV/MD đều gom chung vào 1 class `Paths`, các thành viên không dẫm chân lên file của nhau. | Mở file `config.py` kiểm tra thuộc tính Paths. |
| Xây dựng Baseline Pipeline | `script/run_phase1.py` | Script liên kết tự động 5 bước của Data Pipeline. | `python script/run_phase1.py` chạy không lỗi. |
| Xây dựng Corruption Pipeline | `script/run_corruption_flow.py` | Gộp chung Checkpoint 5 (Tiêm lỗi) và Checkpoint 6 (Phục hồi) vào một luồng chạy thống nhất. | `python script/run_corruption_flow.py` chạy ra report. |

---

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết
Khi 6 người cùng lập trình song song trên một Data Pipeline, nếu mạnh ai nấy lưu file, đặt tên file, và định nghĩa schema theo ý mình thì lúc gộp code chắc chắn hệ thống sẽ nổ tung. Nhiệm vụ của Role 1 là đi trước một bước: Trải nhựa đường (định nghĩa cấu trúc thư mục, đường dẫn, interface hàm) và ra luật giao thông (không hard-code, bẫy lỗi rõ ràng) để 5 người còn lại ráp xe chạy trơn tru.

### Cách triển khai
1. **Centralized Configuration**:
   * Dùng thư viện Pydantic/Dataclass (trong `config.py`) để chứa tất cả đường dẫn (`clean_csv`, `corrupted_json`, `eval_testset`). Thay vì gõ chuỗi `"data/raw/..."` khắp nơi, mọi người chỉ cần gọi `settings.paths.raw_records_json`.
2. **Kịch bản dàn nhạc (Orchestrator)**:
   * Viết `phase1.py` và `corruption_flow.py` theo mô hình tuần tự. 
   * Import hàm của các Role khác vào, truyền `df` và `settings` cho họ xử lý, nhận lại kết quả.
   * Dùng `try...except` bao bọc từng module. Nếu một Role chưa làm xong (bị `NotImplementedError`), Pipeline không văng lỗi mù mờ mà in ra cảnh báo vàng `🚧 [Blocker Evidence]: Role X chưa hoàn thiện hàm Y!`.
3. **Mô hình "Nối Toa Tàu" trong Checkpoint 6**:
   * Thay vì tách riêng kịch bản Corrupt và kịch bản Repair, tôi gộp chung vào 1 file `corruption_flow.py`. Máy sẽ tự chạy Tiêm Lỗi, Đánh giá, sau đó bốc dữ liệu Raw ra Repair, Đánh giá tiếp, và quăng hết vào Hàm báo cáo cuối.

### Input, Output và Contract

| Thành phần | Mô tả |
| :--- | :--- |
| **Input** | Code (Hàm) từ 5 thành viên còn lại. Biến môi trường API keys. |
| **Output** | Màn hình Terminal Console với Log sinh động, theo dõi tiến trình chạy từ đầu tới cuối. Các file `*_report.md`. |
| **Module phụ thuộc** | Phụ thuộc vào TẤT CẢ các module trong hệ thống (`ingestion`, `retrieval`, `evaluation`, `observability`). |
| **Module sử dụng Output** | Không có (Đây là module chóp bu - Top Level). |
| **Điều kiện lỗi cần xử lý** | Bắt lỗi `NotImplementedError` từ đàn em. Bắt lỗi `Exception` chung khi hệ thống chạy sập để ngắt script an toàn (`sys.exit(1)`). |

---

## 5. Một quyết định kỹ thuật quan trọng

* **Bối cảnh**: Ở Checkpoint 5 và 6, hệ thống phải chạy song song 3 bộ Vector Index (Baseline, Corrupted, Repaired). Làm sao để Role 4 (RAG) không bị nhầm lẫn và ghi đè file ChromaDB của nhau?
* **Quyết định (Đã chọn)**: Trong `config.py`, tôi khai báo sẵn 3 tên Collection khác nhau (`papers-baseline`, `papers-corrupted`, `papers-repaired`). Khi Role 1 gọi hàm `LocalEmbeddingIndex.build()`, tôi sẽ truyền đúng cái path của file JSON tương ứng vào. Hàm nội suy của Role 4 sẽ dựa vào Path đó để tự suy ra Collection Name.
* **Lý do**: Quyết định này gọi là "Convention over Configuration". Thay vì bắt người gọi hàm phải truyền lắt nhắt tên Collection, ta gán cứng một quy ước từ đầu. Điều này giữ cho code của Role 4 trong sáng, và dữ liệu 3 pha của hệ thống bị cô lập (Isolated) hoàn toàn, đảm bảo tính công bằng khi chấm điểm.

---

## 6. Một lỗi hoặc blocker đã xử lý

* **Triệu chứng / Lỗi nguyên văn**:
  `Merge conflict in data/chroma/chroma.sqlite3` và `ValueError: Expected object or value` khi đọc `papers_clean.json`.
* **Nguyên nhân gốc**: 
  - Là người cầm key nhánh `main`, khi tôi gộp (merge) code từ các nhánh của mọi người, Git tự động cố gắng merge cả các file sinh ra (artifacts) như `.sqlite3` hoặc `.json`. Việc dính tag `<<<<<<< HEAD` vào file JSON làm hỏng toàn bộ cấu trúc file.
  - Lỗi thứ 2 là do tôi lỡ dùng thuộc tính `lines=True` trong Pandas để đọc file chuẩn JSON array.
* **Cách xử lý**: 
  - Về Git: Đáng lẽ thư mục `data/` nên được đưa vào `.gitignore` (chỉ trừ thư mục rỗng). Tuy nhiên, để sửa cháy, tôi đã dùng lệnh lấy phiên bản theoris hoặc reset và dọn dẹp các file rác.
  - Về Code: Sửa lại `pd.read_json(clean_path, orient="records")` thay vì `lines=True`. Mọi thứ trở lại trơn tru.

---

## 7. Hiểu biết về luồng end-to-end

1. **Dữ liệu đi từ Crossref đến vector index như thế nào?**
   * (Ingest) Kéo JSON $\rightarrow$ (Clean) Chuẩn hóa thành DataFrame $\rightarrow$ Role 1 gọi lệnh Save để ghi ra đĩa $\rightarrow$ (RAG) Đọc file DataFrame đó biến thành Embeddings $\rightarrow$ Ghi vào ChromaDB. Orchestrator (Role 1) đứng ngoài giật dây trình tự này.
2. **Evaluation set và ground-truth document IDs dùng để đo retrieval/answer quality ra sao?**
   * Role 1 truyền Index cho Role 5. Role 5 lấy Test Set chọc vào Index, truy vấn ID. Nếu ID trùng với Ground Truth thì tính là 1 Hit. LLM sẽ lấy Context đó để trả lời và đọ F1 với Ground Truth.
3. **Quality checks khác freshness monitoring ở điểm nào trong bài lab?**
   * Cả 2 đều là Observability (Đo lường). Quality check soi cấu trúc (rỗng, trùng lặp). Freshness soi độ mới của dữ liệu (tuổi thọ bài báo).
4. **Vì sao phải dùng cùng test set cho baseline, corrupted và repaired?**
   * Theo thiết kế Data Contract ngay từ đầu, Test Set được sinh ra 1 lần ở Baseline. Các bước sau (Corrupt, Repair) tôi ép buộc script phải tái sử dụng đường dẫn `settings.paths.eval_testset` thay vì sinh lại, nhằm tạo thước đo tuyệt đối.
5. **Repair được xem là thành công dựa trên artifact và metric nào?**
   * Thành công khi Script của tôi ở CP6 chạy xong, file `corruption_report.md` hiện ra con số Delta giữa Repaired và Baseline bằng ~0 (Tức là dữ liệu và hiệu năng đã quay về mốc 100% hoàn hảo).

---

## 8. Phân tích kết quả

| Phân tích từ góc độ Orchestrator (Role 1) | Nhận xét |
| :--- | :--- |
| **Kiến trúc Pipeline** | Hệ thống chịu lỗi (Fault-tolerant) rất tốt. Khi một module của Data Engineer bị lỗi hỏng (Corrupted), hệ thống Quality Check lập tức giương cờ (FAIL), và Metrics Evaluation phản ánh ngay lập tức sự tụt dốc của AI. |
| **Giá trị của Data Contract** | Việc quản lý biến môi trường và đường dẫn Path tại một chỗ (`config.py`) đã cứu nhóm khỏi thảm họa "đường dẫn tương đối", giúp script chạy được trên máy của mọi thành viên. |

---

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất
1. **Thiết kế lỏng (Loose Coupling)**: Các Role không cần biết Code của nhau viết thế nào, chỉ cần nắm rõ Đầu vào (Input) và Đầu ra (Output) theo Hợp đồng Dữ liệu là có thể ráp nối thành công.
2. **Quản lý Artifacts trong Git**: Các file data tự sinh (.csv, .json, .sqlite3) tuyệt đối không nên commit lên Git để tránh merge conflict thảm họa. Chỉ commit Source Code.
3. **Try-Except có chủ đích**: Đặt bẫy lỗi `NotImplementedError` là nghệ thuật để giao việc cho các thành viên khác mà không làm sập chương trình chính.

### Nếu có thêm thời gian
* Tôi sẽ tích hợp công cụ **Airflow** hoặc **Prefect** thay vì tự viết script `phase1.py` bằng Python thuần. Công cụ chuyên nghiệp sẽ có giao diện UI dạng DAGs (Directed Acyclic Graph) để trực quan hóa xem task nào bị lỗi (như đoạn tiêm lỗi Corrupted) và tự động Retries.
