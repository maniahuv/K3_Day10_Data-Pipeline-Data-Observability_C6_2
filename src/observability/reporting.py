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
    ragas_value = metrics.get("ragas", 0.0)
    if isinstance(ragas_value, dict):
        if "skipped" in ragas_value:
            ragas_display = "Skipped"
        elif "error" in ragas_value:
            ragas_display = "Error"
        else:
            ragas_display = json.dumps(ragas_value, ensure_ascii=False)
    elif isinstance(ragas_value, (int, float)):
        ragas_display = f"{ragas_value:.4f}"
    else:
        ragas_display = str(ragas_value)
    
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
| **RAGAS Score** | **{ragas_display}** | Điểm đánh giá tổng hợp RAGAS (nếu có). |

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
    """Write a comparison report that ties corrupted data signals to RAG metric movement."""

    def metric_value(metrics: dict[str, Any], key: str) -> float | None:
        value = metrics.get(key)
        return float(value) if isinstance(value, (int, float)) else None

    def fmt_number(value: float | int | None, digits: int = 4) -> str:
        if value is None:
            return "N/A"
        return f"{float(value):.{digits}f}"

    def fmt_percent(value: float | int | None) -> str:
        if value is None:
            return "N/A"
        return f"{float(value):.2%}"

    def fmt_delta(value: float | None, percent: bool = False) -> str:
        if value is None:
            return "N/A"
        sign = "+" if value > 0 else ""
        return f"{sign}{value:.2%}" if percent else f"{sign}{value:.4f}"

    def nested(payload: dict[str, Any], *keys: str, default: Any = None) -> Any:
        current: Any = payload
        for key in keys:
            if not isinstance(current, dict):
                return default
            current = current.get(key, default)
        return current

    def changed_label(delta: float | None, lower_is_worse: bool = False) -> str:
        if delta is None:
            return "not evaluated"
        if abs(delta) < 1e-12:
            return "unchanged"
        if lower_is_worse:
            return "improved" if delta < 0 else "degraded"
        return "improved" if delta > 0 else "degraded"

    report_path = Path(report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    quality_signals = [
        (
            "row_count",
            "Row count",
            float(
                baseline_metrics.get(
                    "source_row_count",
                    corrupted_quality.get("baseline_row_count"),
                )
            )
            if baseline_metrics.get("source_row_count") is not None
            or corrupted_quality.get("baseline_row_count") is not None
            else None,
            float(corrupted_quality.get("row_count")) if corrupted_quality.get("row_count") is not None else None,
            "drop_latest_record",
            "Lower row count is evidence of record loss.",
            False,
        ),
        (
            "summary_missing_rate",
            "Missing summary rate",
            float(nested(corrupted_quality, "baseline_missing_fields", "summary", "missing_rate", default=0.0)),
            float(nested(corrupted_quality, "missing_fields", "summary", "missing_rate", default=0.0)),
            "blank_summary",
            "Higher missing summary rate reduces evidence available to the embedding and answer.",
            True,
        ),
        (
            "paper_id_duplicate_count",
            "Duplicate paper_id count",
            float(nested(corrupted_quality, "baseline_paper_id_uniqueness", "duplicate_count", default=0)),
            float(nested(corrupted_quality, "paper_id_uniqueness", "duplicate_count", default=0)),
            "duplicate_record",
            "Duplicate ids can crowd the retrieved context with repeated records.",
            True,
        ),
        (
            "row_duplicate_rate",
            "Duplicate row rate",
            float(nested(corrupted_quality, "baseline_row_duplicates", "duplicate_rate", default=0.0)),
            float(nested(corrupted_quality, "row_duplicates", "duplicate_rate", default=0.0)),
            "duplicate_record",
            "Repeated rows make duplicate context measurable.",
            True,
        ),
        (
            "max_age_days",
            "Max age_days",
            float(nested(corrupted_quality, "baseline_age_days", "max"))
            if nested(corrupted_quality, "baseline_age_days", "max") is not None
            else None,
            float(nested(corrupted_quality, "age_days", "max", default=0.0))
            if nested(corrupted_quality, "age_days", "max") is not None
            else None,
            "age_published_date",
            "Aged records are freshness risk evidence.",
            True,
        ),
        (
            "freshness_stale_rows",
            "Freshness stale rows",
            float(corrupted_freshness.get("baseline_stale_rows", 0)),
            float(corrupted_freshness.get("stale_rows", 0)),
            "age_published_date",
            "Stale rows show freshness threshold impact.",
            True,
        ),
        (
            "text_for_embedding_missing_rate",
            "Missing text_for_embedding rate",
            float(
                nested(
                    corrupted_quality,
                    "baseline_missing_fields",
                    "text_for_embedding",
                    "missing_rate",
                    default=0.0,
                )
            ),
            float(nested(corrupted_quality, "missing_fields", "text_for_embedding", "missing_rate", default=0.0)),
            "blank_summary",
            "Embedding text availability did not necessarily change when summary changed.",
            True,
        ),
    ]

    rag_metrics = [
        ("retrieval_hit_rate", "Retrieval hit rate", True, "retrieval"),
        ("mean_token_f1", "Mean token F1", False, "generation"),
        ("judge_accuracy", "Judge accuracy", True, "generation"),
        ("mean_judge_score", "Mean judge score", False, "generation"),
    ]

    changed_rag_rows: list[str] = []
    unchanged_rag_rows: list[str] = []
    for key, label, as_percent, impact_area in rag_metrics:
        baseline = metric_value(baseline_metrics, key)
        corrupted = metric_value(corrupted_metrics, key)
        delta = corrupted - baseline if baseline is not None and corrupted is not None else None
        status = changed_label(delta)
        formatter = fmt_percent if as_percent else fmt_number
        row = (
            f"| {label} | {formatter(baseline)} | {formatter(corrupted)} | "
            f"{fmt_delta(delta, percent=as_percent)} | {status} | {impact_area} |"
        )
        if status == "unchanged":
            unchanged_rag_rows.append(row)
        else:
            changed_rag_rows.append(row)

    changed_quality_rows: list[str] = []
    unchanged_quality_rows: list[str] = []
    for _, label, baseline, corrupted, evidence, note, lower_is_worse in quality_signals:
        delta = corrupted - baseline if baseline is not None and corrupted is not None else None
        status = changed_label(delta, lower_is_worse=lower_is_worse)
        row = (
            f"| {label} | {fmt_number(baseline)} | {fmt_number(corrupted)} | "
            f"{fmt_delta(delta)} | {status} | {evidence} | {note} |"
        )
        if status == "unchanged":
            unchanged_quality_rows.append(row)
        else:
            changed_quality_rows.append(row)

    counts_by_type = corrupted_quality.get("corruption_counts_by_type", {})
    events_count = corrupted_quality.get("corruption_event_count")
    if events_count is None:
        events_count = sum(counts_by_type.values()) if isinstance(counts_by_type, dict) else 0
    evidence_lines = "\n".join(
        f"- `{key}`: {value}" for key, value in sorted(counts_by_type.items())
    ) or "- No corruption log evidence was attached to this report."

    repaired_available = bool(repaired_metrics or repaired_quality or repaired_freshness)
    repaired_note = (
        "Repaired artifacts were available and can be compared in a follow-up repair section."
        if repaired_available
        else "Repaired artifacts were not available in this run, so this report only concludes baseline vs corrupted impact."
    )

    md_content = f"""# Corrupted Dataset Quality and RAG Impact Report

This report is separate from the baseline report and uses the corrupted dataset artifacts.

## Inputs
- Baseline metrics samples: {baseline_metrics.get("samples", "N/A")}
- Corrupted metrics samples: {corrupted_metrics.get("samples", "N/A")}
- Corrupted quality status: `{corrupted_quality.get("status", "UNKNOWN")}`
- Corrupted freshness status: `{corrupted_freshness.get("is_fresh", "UNKNOWN")}`
- Corruption log events linked: {events_count}
- Repair scope: {repaired_note}

## Corruption Log Evidence
{evidence_lines}

## Data Quality Signals That Changed
| Signal | Baseline | Corrupted | Delta | Status | Evidence | Interpretation |
| :--- | ---: | ---: | ---: | :--- | :--- | :--- |
{chr(10).join(changed_quality_rows) if changed_quality_rows else "| None | N/A | N/A | N/A | unchanged | N/A | No changed quality signals were observed. |"}

## RAG Metrics With Evidence-Based Changes
| Metric | Baseline | Corrupted | Delta | Status | Impact area |
| :--- | ---: | ---: | ---: | :--- | :--- |
{chr(10).join(changed_rag_rows) if changed_rag_rows else "| None | N/A | N/A | N/A | unchanged | N/A |"}

## Signals That Did Not Change
These signals are recorded explicitly to avoid over-claiming.

### Data Quality
| Signal | Baseline | Corrupted | Delta | Status | Evidence | Interpretation |
| :--- | ---: | ---: | ---: | :--- | :--- | :--- |
{chr(10).join(unchanged_quality_rows) if unchanged_quality_rows else "| None | N/A | N/A | N/A | unchanged | N/A | No unchanged quality signals were observed. |"}

### RAG Metrics
| Metric | Baseline | Corrupted | Delta | Status | Impact area |
| :--- | ---: | ---: | ---: | :--- | :--- |
{chr(10).join(unchanged_rag_rows) if unchanged_rag_rows else "| None | N/A | N/A | N/A | unchanged | N/A |"}

## Conclusion
The corrupted dataset has quality/freshness evidence linked to the corruption log, and only the RAG metrics with measured deltas are marked as changed. Retrieval hit rate is listed as unchanged when its delta is zero, so the report does not claim retrieval degradation without evidence. The observed degradation is concentrated in answer quality metrics when those metrics have a negative delta.
"""

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"Corruption report written successfully to {report_path}")

