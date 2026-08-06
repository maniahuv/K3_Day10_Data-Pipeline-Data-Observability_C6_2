# Báo cáo cá nhân - Day 10: Data Pipeline & Data Observability

> Báo cáo này được hoàn thiện theo mẫu báo cáo cá nhân của nhóm, tập trung vào phần việc Role 6: giám sát dữ liệu, chất lượng dữ liệu, độ mới dữ liệu và báo cáo so sánh tác động của corrupted/repaired data.

## 1. Thông tin cá nhân

| Thông tin | Nội dung |
| --- | --- |
| Họ và tên | Nguyễn Tiến Thành |
| MSSV | 2A202601539 |
| Khóa/Lớp | K3 |
| Tên nhóm | C6_2 |
| Vai trò chính | Role 6 - Giám sát dữ liệu, data quality, freshness và comparison report |
| Repository | https://github.com/maniahuv/K3_Day10_Data-Pipeline-Data-Observability_C6_2 |
| Ngày hoàn thành | 2026-08-06 |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| --- | --- | --- | --- | --- |
| Data quality checks | `src/observability/quality.py` - `run_data_quality_checks` | DataFrame baseline/corrupted/repaired | JSON quality report theo từng trạng thái dữ liệu | Hoàn thành |
| Freshness monitoring | `src/observability/quality.py` - `build_freshness_report` | Dataset có `published` hoặc `age_days` | Freshness report với latest/oldest/stale rows/is_fresh | Hoàn thành |
| Baseline observability | `script/generate_baseline_observability.py`, `data/quality/baseline_quality*.json`, `data/quality/freshness_report.json` | Clean baseline dataset | Báo cáo quality/freshness cho dữ liệu sạch | Hoàn thành |
| Corrupted observability | `script/generate_corrupted_observability_report.py`, `data/quality/corrupted_quality.json`, `data/quality/corrupted_freshness_report.json` | Corrupted clean dataset | Báo cáo riêng cho corrupted dataset | Hoàn thành |
| Signal evidence và comparison | `data/quality/corrupted_signal_evidence.json`, `data/reports/corruption_report.md` | Metrics, quality, freshness, corruption log | Bảng so sánh baseline/corrupted/repaired và giới hạn kết luận | Hoàn thành |
| Recovery assessment | `src/observability/reporting.py` | Baseline/corrupted/repaired artifacts | Kết luận recovery hoàn toàn/chưa hoàn toàn dựa trên signal thật | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Module được hỗ trợ | Kết quả |
| --- | --- | --- |
| Cung cấp signal chất lượng cho nhóm evaluation | `data/results/*_metrics.json`, `data/quality/*.json` | Có bằng chứng để nối lỗi dữ liệu với thay đổi metric RAG |
| Hỗ trợ báo cáo tổng hợp corruption/recovery | `data/reports/corruption_report.md` | Có bảng comparison và phần giới hạn kết luận, tránh kết luận quá mức |
| Đối chiếu repaired data với baseline | `data/quality/repaired_quality.json`, `data/quality/repaired_freshness_report.json` | Xác nhận repaired không còn signal xấu hơn baseline trong các chỉ số đã đo |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| --- | --- | --- | --- |
| Chạy quality checks cho baseline | `run_data_quality_checks`, `data/quality/baseline_quality.json` | Baseline có 22 rows, 0 duplicate, 0 missing summary/text, status `PASSED` | Đọc JSON baseline quality |
| Chạy freshness report cho baseline | `build_freshness_report`, `data/quality/freshness_report.json` | Baseline fresh, `stale_rows = 0`, latest published `2026-08-01` | Đọc freshness report |
| Chạy quality/freshness riêng cho corrupted dataset | `data/quality/corrupted_quality.json`, `data/quality/corrupted_freshness_report.json` | Corrupted status `WARNING`, có missing summary, duplicate, stale row | Chạy `python script/generate_corrupted_observability_report.py` |
| Nối corruption log với quality signal | `data/results/corruption_log.json`, `data/quality/corrupted_signal_evidence.json` | Ghi rõ 7 corruption events và các delta quality/RAG metric | Đọc `corrupted_signal_evidence.json` |
| Tạo comparison report | `data/reports/corruption_report.md`, `src/observability/reporting.py` | Có bảng baseline/corrupted/repaired cho evaluation, quality và freshness | Đọc report markdown |
| Ghi signal không đổi và giới hạn kết luận | `data/reports/corruption_report.md` | Không overclaim; nêu rõ RAGAS skipped và corruption là bundle nhiều lỗi | Đọc phần `Conclusion Limits` |

Output quan trọng nhất của Role 6 là bộ báo cáo observability có thể truy vết từ dữ liệu thật:

- `data/quality/baseline_quality.json`
- `data/quality/corrupted_quality.json`
- `data/quality/repaired_quality.json`
- `data/quality/freshness_report.json`
- `data/quality/corrupted_freshness_report.json`
- `data/quality/repaired_freshness_report.json`
- `data/quality/corrupted_signal_evidence.json`
- `data/reports/corruption_report.md`

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết

Pipeline RAG không chỉ cần chạy được end-to-end mà còn cần chứng minh dữ liệu đầu vào có đủ chất lượng để tin vào kết quả retrieval/answer. Khi dataset bị corrupt, nếu chỉ nhìn metric RAG thì khó biết metric giảm do lỗi dữ liệu, do index, do test set hay do agent. Role 6 giải quyết phần này bằng cách đo các tín hiệu chất lượng và độ mới dữ liệu, sau đó nối các tín hiệu đó với metric evaluation và corruption log.

### Cách triển khai

`run_data_quality_checks` nhận một DataFrame và sinh ra các signal chính:

- `row_count`
- `paper_id_uniqueness`
- missing rate của `title`, `summary`, `text_for_embedding`
- duplicate row rate
- thống kê `age_days`
- `summary_length`
- status tổng hợp `PASSED` hoặc `WARNING`

`build_freshness_report` đo độ mới dữ liệu bằng ngày publish hoặc `age_days`. Report ghi `latest_published`, `oldest_published`, `stale_rows`, `threshold_days` và `is_fresh`.

Với corrupted/repaired, script `generate_corrupted_observability_report.py` đọc các artifact thật đã có, chạy lại quality/freshness cho dataset hiện tại, đọc metrics từ `data/results/*_metrics.json`, đọc corruption log, sau đó tạo `corrupted_signal_evidence.json` và `corruption_report.md`. Báo cáo comparison không tự suy diễn: metric nào không có delta thì không kết luận, signal nào không đổi thì ghi riêng để tránh overclaim.

### Input, output và contract

| Thành phần | Mô tả |
| --- | --- |
| Input | Clean/corrupted/repaired dataset trong `data/clean/`, metrics trong `data/results/`, corruption log và baseline/repaired quality artifacts |
| Output | JSON quality/freshness/evidence và markdown comparison report |
| Module phụ thuộc | `pandas`, `core.config.Settings`, `core.utils.read_json/write_json`, `observability.quality` |
| Module sử dụng output | Báo cáo nhóm, Role 5 evaluation, phần phân tích corruption/recovery |
| Điều kiện lỗi cần xử lý | Missing columns, missing dataset, stale rows, duplicate IDs, blank text, repaired metric còn thấp hơn baseline |

### Cách xác minh

```powershell
.\.venv\Scripts\python.exe script\generate_corrupted_observability_report.py
.\.venv\Scripts\python.exe -m compileall src\observability\reporting.py script\generate_corrupted_observability_report.py
```

- Kết quả mong đợi: sinh được corrupted/repaired quality/freshness reports, signal evidence JSON và comparison report.
- Kết quả thực tế: các artifact đã tồn tại trong `data/quality/` và `data/reports/corruption_report.md`.
- Lưu ý: không ghi API key, `.env`, token hoặc secret vào report.

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Cần kết luận corruption/recovery dựa trên bằng chứng thật, không chỉ dựa vào nhận xét thủ công.
- **Các phương án đã cân nhắc:** (1) viết report thủ công từ vài metric chính; (2) tạo report từ persisted metrics, quality, freshness và corruption log.
- **Phương án đã chọn:** Phương án (2), tạo report từ artifact thật.
- **Lý do:** Có thể tái chạy, dễ kiểm chứng, giảm rủi ro copy sai số liệu và buộc kết luận phải bám vào signal đo được.
- **Bằng chứng:** `corrupted_signal_evidence.json` ghi delta cụ thể cho quality/RAG metric; `corruption_report.md` trình bày bảng baseline/corrupted/repaired và phần giới hạn kết luận.

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng:** Corrupted dataset có metric giảm, nhưng nếu báo cáo chỉ nói “corruption làm giảm chất lượng” mà không nối với quality/freshness signal thì dễ kết luận quá mức. Ngoài ra, một số signal như `text_for_embedding_missing_rate` không đổi dù summary bị blank.
- **Lệnh hoặc bước tái hiện:** Đọc `data/results/corrupted_metrics.json`, `data/quality/corrupted_quality.json` và `data/results/corruption_log.json` riêng lẻ.
- **Nguyên nhân gốc:** Các artifact nằm rời rạc, chưa có một lớp tổng hợp nối corruption event -> quality/freshness signal -> evaluation metric.
- **Cách xử lý:** Tạo evidence JSON và comparison report. Report chỉ đánh dấu metric thay đổi khi có delta thật, đồng thời ghi signal không đổi để tránh overclaim.
- **Cách xác minh sau khi sửa:** `corrupted_signal_evidence.json` có `quality_signal_deltas`, `rag_metric_deltas`, `repaired_quality_signal_deltas`, `repaired_rag_metric_deltas`; `corruption_report.md` có bảng comparison và conclusion limits.
- **Điều học được:** Observability tốt không chỉ là có nhiều số liệu, mà là biết nối số liệu đúng mức và ghi rõ giới hạn của kết luận.

## 7. Hiểu biết về luồng end-to-end

1. Dữ liệu đi từ Crossref raw response sang clean dataset. Cleaning chuẩn hóa `paper_id`, title, summary, published date và tạo `text_for_embedding`.
2. Role RAG/index dùng clean dataset để tạo embedding và Chroma collection cho baseline, corrupted và repaired.
3. Evaluation set giữ cố định `ground_truth_doc_ids` để đo retrieval hit rate và answer quality trên cùng bộ câu hỏi.
4. Quality checks đo tính đầy đủ/toàn vẹn của dataset như missing, duplicate, row count và `age_days`; freshness monitoring đo dữ liệu có stale hay không theo ngưỡng ngày.
5. Corruption tạo lỗi có chủ đích, làm signal quality/freshness xấu đi và metric RAG giảm. Repair được xem là thành công khi repaired dataset, quality/freshness và metric evaluation quay về baseline trong phạm vi đã đo.

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal | Baseline | Corrupted | Repaired | Nhận xét cá nhân |
| --- | ---: | ---: | ---: | --- |
| `retrieval_hit_rate` | 1.00 | 0.80 | 1.00 | Corrupted làm retrieval giảm 20 điểm phần trăm; repaired khôi phục về baseline. |
| `mean_token_f1` | 1.0000 | 0.7426 | 1.0000 | Nội dung trả lời kém khớp ground truth khi dữ liệu có missing/noise/drop. |
| `judge_accuracy` | 1.00 | 0.7333 | 1.00 | Judge accuracy giảm ở corrupted và phục hồi sau repair. |
| `mean_judge_score` | 5.0000 | 4.1333 | 5.0000 | Điểm judge giảm rõ ở corrupted, repaired quay lại mức baseline. |
| Quality status | `PASSED` | `WARNING` | `PASSED` | Corrupted có 1 duplicate ID, 1 missing summary và row count giảm. |
| Freshness status | `True` | `False` | `True` | Corrupted có 1 stale row, max `age_days` tăng từ 175 lên 402. |

### Kết luận từ số liệu

Chuỗi bằng chứng chính:

1. Corruption tạo `drop_latest_record`, `blank_summary`, `inject_noise`, `truncate_title`, `age_published_date`, `duplicate_record` -> quality/freshness xấu đi: row count `22 -> 21`, summary missing `0% -> 4.76%`, duplicate `0 -> 1`, max `age_days` `175 -> 402`, stale rows `0 -> 1` -> RAG metrics giảm.
2. Repair đưa dữ liệu về trạng thái đo được như baseline: row count `22`, duplicate `0`, missing summary `0%`, stale rows `0`, quality `PASSED`, freshness `True` -> retrieval và answer metrics quay về baseline.

Corruption ảnh hưởng rõ nhất là nhóm lỗi làm mất hoặc sai lệch thông tin đưa vào retrieval: drop record, blank summary, noise và stale date. RAG agent phụ thuộc vào context retrieved; khi context xấu, agent vẫn có thể chạy nhưng chất lượng câu trả lời giảm.

Giới hạn kết luận: kết quả này chỉ đúng trên artifact và test set hiện tại. RAGAS đang skipped, nên không dùng RAGAS để kết luận. Corruption log chứa nhiều loại lỗi cùng lúc, vì vậy chưa thể quy kết chính xác mỗi metric giảm do một lỗi đơn lẻ nếu không chạy ablation riêng.

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất

1. Data quality phải đo được bằng signal cụ thể, không nên chỉ ghi cảm tính là dữ liệu sạch hay bẩn.
2. Freshness là một lớp giám sát riêng: dữ liệu có đủ field vẫn có thể xấu nếu quá cũ hoặc publish date bị sai.
3. Khi so sánh baseline/corrupted/repaired, phải dùng cùng test set và cùng metric để thay đổi phản ánh trạng thái dữ liệu thay vì thay đổi cách đánh giá.

### Nếu có thêm thời gian

Tôi sẽ bổ sung ablation report cho từng loại corruption riêng biệt. Ví dụ chạy riêng `blank_summary`, riêng `duplicate_record`, riêng `age_published_date` để đo lỗi nào ảnh hưởng nhiều nhất tới retrieval hit rate, token F1 và judge score.

## 10. Cam kết của thành viên

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Nguyễn Tiến Thành

**Ngày xác nhận:** 2026-08-06
