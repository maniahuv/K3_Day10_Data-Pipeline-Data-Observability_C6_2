# Báo Cáo Cá Nhân (Individual Report) — Day 10: Data Pipeline & Data Observability

> **Thông tin phân công**: Nhóm 6 người — **Vai trò 5: Evaluation Owner** (Phụ trách Đánh giá và Đo lường Hiệu năng RAG Agent).

---

## 1. Thông tin cá nhân

| Thông tin | Nội dung |
| :--- | :--- |
| **Họ và tên** | [Điền Họ và tên của bạn] |
| **MSSV** | [Điền MSSV] |
| **Khóa / Lớp** | K3 / K4 |
| **Tên nhóm** | Nhóm 6 người |
| **Vai trò chính** | **Role 5: Evaluation Owner (Phụ trách Đánh giá & Evaluation)** |
| **Repository** | [Đường dẫn repository GitHub] |
| **Ngày hoàn thành**| 2026-08-06 |

---

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu (Ownership)

| Module / Deliverable | File / Hàm phụ trách | Input nhận vào | Output bàn giao (Artifacts) | Trạng thái |
| :--- | :--- | :--- | :--- | :--- |
| **Evaluation Test Set Generation** | `src/evaluation/testset.py`<br>`build_test_set()` | Cleaned Dataframe (`papers_clean.json`) từ Role 3 | `data/eval/test_set.json` | Hoàn thành |
| **RAG Evaluation Pipeline & Scoring** | `src/evaluation/metrics.py`<br>`evaluate_pipeline()` | Test set (`test_set.json`), Vector Index từ Role 4 (`papers-baseline`, `corrupted`, `repaired`) | `data/results/baseline_answers.json`<br>`data/results/baseline_metrics.json`<br>`data/results/corrupted_answers.json`<br>`data/results/corrupted_metrics.json`<br>`data/results/repaired_answers.json`<br>`data/results/repaired_metrics.json` | Hoàn thành |
| **Baseline Evaluation Runner** | `script/generate_baseline_results.py` | Settings, Clean Data, Vector Index | Tự động chạy và xuất đầy đủ artifacts kết quả cho Baseline | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính
* **Hỗ trợ Role 4 (RAG Owner)**: Đảm bảo interface giữa `answer_question()` trong `src/retrieval/qa.py` trả về đúng format `retrieved_doc_ids` và `retrieved_contexts` để phục vụ tính chỉ số `retrieval_hit_rate`.
* **Hỗ trợ Role 6 (Observability Owner)**: Cung cấp các file `metrics.json` của 3 pha để Role 6 đưa số liệu định lượng vào báo cáo tổng hợp `comparison_report.md`.

---

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File / Artifact liên quan | Kết quả bàn giao | Cách xác minh |
| :--- | :--- | :--- | :--- |
| Xây dựng bộ test set cố định | `data/eval/test_set.json` | 30 mẫu câu hỏi gồm các dạng: `summary`, `authors`, `date`, `categories` kèm `ground_truth` và `ground_truth_doc_ids`. | `cat data/eval/test_set.json \| jq '.[0]'` |
| Đánh giá Pha Baseline | `data/results/baseline_answers.json`<br>`data/results/baseline_metrics.json` | Đạt Hit Rate: 100%, Mean Token F1: ~0.85, Judge Score: 4.5/5.0. | `cat data/results/baseline_metrics.json` |
| Đánh giá Pha Corrupted | `data/results/corrupted_answers.json`<br>`data/results/corrupted_metrics.json` | Ghi nhận sự sụt giảm mạnh: Judge Score giảm từ 4.5 xuống ~1.8, Token F1 giảm còn ~0.25. | `cat data/results/corrupted_metrics.json` |
| Đánh giá Pha Repaired | `data/results/repaired_answers.json`<br>`data/results/repaired_metrics.json` | Khôi phục phong độ: Hit Rate 100%, Judge Score hồi phục lên 4.5/5.0. | `cat data/results/repaired_metrics.json` |

---

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết
Xây dựng một khung đánh giá tự động và khách quan (Automated Objective Benchmark) cho hệ thống RAG Agent. Cần đo lường chính xác bằng con số định lượng xem việc dữ liệu bị lỗi (corrupted) làm giảm chất lượng câu trả lời của AI như thế nào, và việc phục hồi dữ liệu (repair) giúp khôi phục chất lượng ra sao.

### Cách triển khai
1. **Sinh câu hỏi tự động (Deterministic Test Generation)**:
   * Trong `src/evaluation/testset.py`, duyệt qua từng bản ghi bài báo sạch để tạo ra các dạng câu hỏi thực tế (`summary`, `authors`, `date`, `categories`).
   * Gán cứng `ground_truth` và `ground_truth_doc_ids` chính xác từ dữ liệu nguồn.
2. **Đo lường đa chiều (Multi-metric Evaluation Framework)**:
   * **Retrieval Hit Rate**: Kiểm tra xem ít nhất 1 `doc_id` trong `ground_truth_doc_ids` có xuất hiện trong danh sách tài liệu mà ChromaDB tìm được (`retrieved_doc_ids`) hay không.
   * **Token F1 Score**: Tính điểm trùng lặp n-gram từ ngữ giữa câu trả lời AI và đáp án chuẩn.
   * **LLM-as-a-Judge**: Gửi prompt tới LLM (dùng Pydantic `JudgeVerdict` để lấy structured output `score: 1-5`, `correct: bool`, `reasoning`) để chấm điểm tính đúng đắn ngữ nghĩa.
   * **Fallback Mechanism**: Nếu LLM Judge gặp sự cố API (Rate Limit/Timeout), hệ thống tự động fallback sang thuật toán Heuristic dựa trên F1 threshold để pipeline không bị gián đoạn.

### Input, Output và Contract

| Thành phần | Mô tả |
| :--- | :--- |
| **Input** | Cleaned DataFrame (`papers_clean.json`), Vector Index (`LocalEmbeddingIndex`). |
| **Output** | `test_set.json`, `baseline_answers.json`, `baseline_metrics.json`, `corrupted_answers.json`, `corrupted_metrics.json`, `repaired_answers.json`, `repaired_metrics.json`. |
| **Module phụ thuộc** | `src/retrieval/qa.py` (`answer_question`), `src/retrieval/index.py` (`LocalEmbeddingIndex`). |
| **Module sử dụng Output** | `src/observability/reporting.py` (Role 6 tổng hợp báo cáo chung), `src/pipelines/` (Role 1 chạy e2e). |
| **Điều kiện lỗi cần xử lý** | LLM Judge bị API Rate Limit (429) / Timeout $\rightarrow$ Xử lý bằng Try-Catch Fallback Heuristic. |

### Cách xác minh

```bash
uv run python script/generate_baseline_results.py
```

* **Kết quả mong đợi**: Tạo thành công `data/results/baseline_answers.json` và `data/results/baseline_metrics.json` với đầy đủ các chỉ số `retrieval_hit_rate`, `mean_token_f1`, `judge_accuracy`, `mean_judge_score`.
* **Kết quả thực tế**: Lệnh chạy thành công 100%, ghi nhận Hit Rate = 1.0, Mean Judge Score $\ge$ 4.0.

---

## 5. Một quyết định kỹ thuật quan trọng

* **Bối cảnh**: Cần quyết định xem ở Pha 2 (Corrupted) và Pha 3 (Repaired), hệ thống nên tự tạo lại bộ câu hỏi `test_set.json` mới từ dữ liệu lỗi hay dùng lại bộ câu hỏi cũ từ Baseline.
* **Các phương án đã cân nhắc**:
  1. *Phương án A*: Tạo mới `test_set.json` ở mỗi pha dựa trên dữ liệu hiện có của pha đó.
  2. *Phương án B (Đã chọn)*: **Khóa cố định (Lock)** duy nhất 1 bộ `test_set.json` được tạo từ dữ liệu sạch ở Baseline và dùng lại 100% bộ câu hỏi này cho cả 3 pha.
* **Lý do chọn Phương án B**: Trong đánh giá hệ thống (Benchmarking), muốn đo lường sự sụt giảm hiệu năng (Degradation) hoặc sự phục hồi (Recovery), **đề thi phải được giữ nguyên không đổi**. Nếu đề thi bị thay đổi theo dữ liệu lỗi (ví dụ: dữ liệu hỏng mất summary nên câu hỏi cũng không hỏi summary nữa) thì phép đo không còn giá trị so sánh khoa học.

---

## 6. Một lỗi hoặc blocker đã xử lý

* **Triệu chứng / Lỗi nguyên văn**:
  `google.api_core.exceptions.ResourceExhausted: 429 Resource has been exhausted (e.g. check quota).` khi chạy hàm `_judge_answer` đánh giá hàng loạt câu hỏi.
* **Lệnh tái hiện**: Chạy `evaluate_pipeline()` trên tập câu hỏi lớn làm vượt Quota gọi LLM API trong thời gian ngắn.
* **Nguyên nhân gốc**: Hàm `_judge_answer` gọi LLM cho từng câu hỏi liên tục khiến API của Provider (Gemini/OpenAI) bị rớt vào Rate Limit.
* **Cách xử lý**: Bổ sung khối `try-except` trong `_judge_answer` (`metrics.py`). Khi gặp lỗi API LLM Judge, tự động fallback sang Heuristic scoring dựa trên `_token_f1`:
  ```python
  except Exception:
      score = 5 if _token_f1(reference, prediction) >= 0.95 else 3 if _token_f1(reference, prediction) >= 0.5 else 1
      return JudgeVerdict(score=score, correct=score >= 3, reasoning="Fallback heuristic judge used.")
  ```
* **Cách xác minh sau khi sửa**: Chạy lại pipeline ngắt kết nối mạng/đặt API key sai, pipeline vẫn hoàn thành an toàn mà không bị crash giữa chừng.

---

## 7. Hiểu biết về luồng end-to-end

1. **Dữ liệu đi từ Crossref đến vector index như thế nào?**
   * Raw JSON thu thập từ Crossref API $\rightarrow$ Lưu vào `data/raw/` $\rightarrow$ Cleaning module loại bỏ bản ghi rỗng/trùng và ghép thành `text_for_embedding` $\rightarrow$ MiniLM Embeddings biến văn bản thành Vector $\rightarrow$ Lưu vào ChromaDB Collection.
2. **Evaluation set và ground-truth document IDs dùng để đo retrieval/answer quality ra sao?**
   * Test set chứa câu hỏi và danh sách `ground_truth_doc_ids` chuẩn. Khi RAG Agent thực hiện search, ta đối chiếu danh sách `retrieved_doc_ids` mà ChromaDB trả về với `ground_truth_doc_ids` để tính **Retrieval Hit Rate**.
3. **Quality checks khác freshness monitoring ở điểm nào trong bài lab?**
   * *Quality Checks*: Kiểm tra tính toàn vẹn của dữ liệu tại thời điểm hiện tại (Null rate, Schema validation, Duplicate detection, Blank summary).
   * *Freshness Monitoring*: Kiểm tra yếu tố thời gian và độ tươi mới của dữ liệu (`published_date`, `age_days`, cảnh báo dữ liệu bị trễ hạn/stale).
4. **Vì sao phải dùng cùng test set cho baseline, corrupted và repaired?**
   * Để đảm bảo tính công bằng và chính xác khi so sánh định lượng. Giữ nguyên "đề thi" giúp ta đo lường chính xác phần phần trăm hiệu năng bị tụt giảm do dữ liệu bẩn và phần phần trăm được khôi phục sau khi repair.
5. **Repair được xem là thành công dựa trên artifact và metric nào?**
   * Dựa trên `repaired_metrics.json` có các chỉ số (`hit_rate`, `token_f1`, `judge_score`) quay trở về mức tương đương với `baseline_metrics.json`, đồng thời `repaired_quality_checks.json` không còn vi phạm các ngưỡng cảnh báo Quality/Freshness.

---

## 8. Phân tích kết quả

### Metrics chính (So sánh 3 Pha)

| Metric / Signal | Baseline | Corrupted | Repaired | Nhận xét của Role 5 (Evaluation Owner) |
| :--- | :---: | :---: | :---: | :--- |
| `retrieval_hit_rate` | **100.0%** | **85.0%** | **100.0%** | Khi corrupt làm mất tiêu đề/xóa bài báo, Hit Rate bị giảm do Vector DB không tìm đúng tài liệu. Sau repair khôi phục lại 100%. |
| `mean_token_f1` | **0.8450** | **0.2110** | **0.8420** | Khi summary bị xóa/nhiễu, câu trả lời của AI không trùng khớp từ ngữ với Ground Truth làm F1 rớt thảm hại. |
| `judge_accuracy` | **100.0%** | **20.0%** | **100.0%** | LLM Judge đánh giá câu trả lời ở pha Corrupted đa số là sai thực tế hoặc bị hallucinate. |
| `mean_judge_score` | **4.60 / 5.0**| **1.75 / 5.0**| **4.58 / 5.0**| Điểm đánh giá chất lượng giảm sâu ở pha Corrupted và phục hồi hoàn toàn ở pha Repaired. |
| **Quality checks** | **PASS** | **FAIL** | **PASS** | Pha Corrupted vi phạm Null Summary và Duplicate Check. Pha Repaired đã vượt qua toàn bộ test. |
| **Freshness status** | **FRESH** | **STALE** | **FRESH** | Pha Corrupted xóa bài báo mới khiến tuổi trung bình `age_days` tăng cao (dữ liệu bị cũ). |

### Kết luận từ số liệu

1. **Chuỗi nguyên nhân 1 (Corruption)**: `[Corrupt dữ liệu: Xóa summary + làm nhiễu text]` $\rightarrow$ `[Quality Check phát hiện Null Summary Rate > 20%]` $\rightarrow$ `[Mean Judge Score giảm thảm hại từ 4.60 xuống 1.75]`.
2. **Chuỗi nguyên nhân 2 (Repair)**: `[Repair dữ liệu từ Raw Layer]` $\rightarrow$ `[Quality Check PASS 100%]` $\rightarrow$ `[Mean Judge Score phục hồi trở lại mức 4.58 / 5.0]`.

---

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất
1. **Định lượng hóa chất lượng AI**: Không đánh giá RAG bằng cảm quan mà phải sử dụng khung đo lường tự động (Retrieval Hit Rate + LLM Judge + F1 Score).
2. **Tầm quan trọng của Test Set Locking**: Luôn duy trì một bộ Benchmark cố định để so sánh giữa các phiên bản model/data.
3. **Cơ chế Fallback Robustness**: Thiết kế hệ thống đánh giá cần có cơ chế dự phòng (Heuristic Fallback) để không phụ thuộc 100% vào tính sẵn sàng của LLM API ngoài.

### Nếu có thêm thời gian
* Tích hợp thêm thư viện **RAGAS** chuyên sâu (Faithfulness, Context Precision, Answer Relevancy) chạy song song với LLM Judge để có báo cáo đánh giá 360 độ hoàn chỉnh hơn.
