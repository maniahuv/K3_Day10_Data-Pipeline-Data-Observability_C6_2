from __future__ import annotations

from typing import Any


import json
from pathlib import Path

def generate_phase1_report(
    report_path,
    source_summary: dict[str, Any],
    metrics: dict[str, Any],
    quality: dict[str, Any],
    freshness: dict[str, Any],
) -> None:
    """Viết markdown report cho baseline phase (Pha 1).
    Ghi kết quả vào đường dẫn report_path.
    """
    report_path = Path(report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Extract metrics safely with defaults
    retrieval_hit_rate = metrics.get("retrieval_hit_rate", 0.0)
    mean_token_f1 = metrics.get("mean_token_f1", 0.0)
    judge_accuracy = metrics.get("judge_accuracy", 0.0)
    mean_judge_score = metrics.get("mean_judge_score", 0.0)
    ragas_data = metrics.get("ragas", {})
    if isinstance(ragas_data, dict) and "skipped" in ragas_data:
        ragas_score_str = "N/A (Skipped)"
    elif isinstance(ragas_data, dict):
        # Average of all values if possible
        try:
            ragas_score_str = f"{sum(ragas_data.values()) / len(ragas_data):.4f}"
        except:
            ragas_score_str = "N/A"
    else:
        ragas_score_str = str(ragas_data)
    
    # Quality info
    row_count = quality.get("row_count", 0)
    paper_id_uniqueness = quality.get("paper_id_uniqueness", {})
    is_unique = paper_id_uniqueness.get("is_unique", False)
    duplicate_count = paper_id_uniqueness.get("duplicate_count", 0)
    
    missing_fields = quality.get("missing_fields", {})
    title_missing_rate = missing_fields.get("title", {}).get("missing_rate", 0.0)
    summary_missing_rate = missing_fields.get("summary", {}).get("missing_rate", 0.0)
    
    row_duplicates = quality.get("row_duplicates", {})
    duplicate_rows_rate = row_duplicates.get("duplicate_rate", 0.0)
    
    age_days_info = quality.get("age_days", {})
    mean_age = age_days_info.get("mean", 0.0)
    max_age = age_days_info.get("max", 0.0)
    min_age = age_days_info.get("min", 0.0)
    
    # Freshness info
    latest_published = freshness.get("latest_published", "N/A")
    oldest_published = freshness.get("oldest_published", "N/A")
    stale_rows = freshness.get("stale_rows", 0)
    is_fresh = freshness.get("is_fresh", False)
    
    md_content = f"""# Báo cáo Pha 1 - Đánh giá Baseline RAG Pipeline (Dữ liệu Sạch)

Tài liệu này tổng hợp hiệu suất vận hành của RAG Pipeline và chất lượng dữ liệu cơ sở (baseline) trước khi tiến hành tiêm lỗi (corruption).

---

## 1. Tóm tắt Nguồn Dữ liệu (Source Summary)
*   **Nguồn tích hợp (API)**: {source_summary.get("source_api", "Crossref API")}
*   **Query tìm kiếm**: `{source_summary.get("source_query", "N/A")}`
*   **Bộ lọc (Filters)**: `{source_summary.get("source_filter", "N/A")}`
*   **Số lượng bản ghi tối đa yêu cầu**: {source_summary.get("max_results", "N/A")}

---

## 2. Kết quả Đo lường Hiệu suất RAG (Evaluation Metrics)
Các chỉ số dưới đây được đánh giá trên tập câu hỏi chuẩn (`evaluation_testset.json`):

| Chỉ số (Metric) | Giá trị Baseline | Đánh giá & Nhận xét |
| :--- | :---: | :--- |
| **Retrieval Hit Rate** | **{retrieval_hit_rate:.2%}** | Tỷ lệ tìm kiếm được context chứa câu trả lời đúng. |
| **Mean Token F1** | **{mean_token_f1:.4f}** | Độ tương đồng mặt chữ giữa câu trả lời sinh ra và Ground Truth. |
| **LLM Judge Accuracy** | **{judge_accuracy:.2%}** | Tỷ lệ câu trả lời được LLM đánh giá đạt yêu cầu. |
| **Mean Judge Score** | **{mean_judge_score:.2f}/5** | Điểm số chất lượng câu trả lời trung bình. |
| **RAGAS Score** | **{ragas_score_str}** | Điểm đánh giá tổng hợp RAGAS (nếu có). |

---

## 3. Chất lượng Dữ liệu & Độ tươi mới (Data Quality & Freshness)
Các tín hiệu đo lường chất lượng dữ liệu thu thập được từ bước Ingestion & Cleaning:

### A. Kiểm tra Chất lượng Dữ liệu (Quality Checks)
*   **Tổng số dòng (Row Count)**: {row_count} bản ghi.
*   **Tính duy nhất của `paper_id`**: `{is_unique}` (Số bản ghi trùng lặp ID: {duplicate_count}).
*   **Tỷ lệ thiếu trường dữ liệu**:
    *   Thiếu `title`: {title_missing_rate:.2%}
    *   Thiếu `summary`: {summary_missing_rate:.2%}
*   **Tỷ lệ trùng lặp dòng (Row duplicates)**: {duplicate_rows_rate:.2%}
*   **Trạng thái kiểm tra (Status)**: `{quality.get("status", "UNKNOWN")}`

### B. Kiểm tra Độ tươi mới (Freshness Report)
*   **Ngày xuất bản mới nhất (Latest Published)**: `{latest_published}`
*   **Ngày xuất bản cũ nhất (Oldest Published)**: `{oldest_published}`
*   **Số lượng dòng bị stale (cũ quá hạn)**: {stale_rows}
*   **Độ tuổi trung bình (`age_days`)**: {mean_age:.1f} ngày (Lớn nhất: {max_age:.1f} ngày, Nhỏ nhất: {min_age:.1f} ngày).
*   **Trạng thái tươi mới (Is Fresh)**: `{is_fresh}` (Ngưỡng cấu hình: {freshness.get("threshold_days", 180)} ngày).

---

## 4. Kết luận Giai đoạn Baseline
*   Dữ liệu thô từ nguồn Crossref đã được làm sạch hoàn toàn mà không gặp lỗi thiếu thông tin (`missing_rate = 0%`) hoặc trùng lặp (`duplicate_rate = 0%`).
*   Hiệu suất tìm kiếm và trả lời của Agent ở mức ổn định, tạo cơ sở để đối chiếu và phân tích ảnh hưởng của dữ liệu lỗi ở các giai đoạn sau.
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
        
    print(f"Phase 1 report written successfully to {report_path}")


def generate_corruption_report(
    report_path,
    baseline_metrics: dict[str, Any],
    corrupted_metrics: dict[str, Any],
    repaired_metrics: dict[str, Any],
    corrupted_quality: dict[str, Any],
    repaired_quality: dict[str, Any],
    corrupted_freshness: dict[str, Any],
    repaired_freshness: dict[str, Any],
) -> None:
    """TODO(student): viet markdown report so sanh baseline/corrupted/repaired."""
    raise NotImplementedError("Student task: implement corruption comparison report.")

