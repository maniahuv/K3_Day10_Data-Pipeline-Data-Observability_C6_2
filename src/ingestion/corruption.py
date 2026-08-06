from __future__ import annotations

from collections import Counter
from datetime import timedelta
from pathlib import Path

import pandas as pd

from core.utils import normalize_whitespace, write_json


NOISE_TOKEN = "[CORRUPTED_NOISE: synthetic-token]"
REQUIRED_COLUMNS = {
    "paper_id",
    "title",
    "summary",
    "published",
    "age_days",
    "authors_joined",
    "categories_joined",
    "summary_chars",
    "text_for_embedding",
}


def _rebuild_embedding_text(row: pd.Series) -> str:
    title = normalize_whitespace(str(row["title"]))
    summary = normalize_whitespace(str(row["summary"]))
    authors = normalize_whitespace(str(row["authors_joined"]))
    categories = normalize_whitespace(str(row["categories_joined"]))
    return "\n".join(
        part for part in (
            f"Title: {title}",
            f"Summary: {summary}" if summary else "",
            f"Authors: {authors}" if authors else "",
            f"Categories: {categories}" if categories else "",
        ) if part
    )


def _select_index(dataframe: pd.DataFrame, offset: int) -> int:
    return int(dataframe.index[offset % len(dataframe)])


def corrupt_clean_dataframe(df: pd.DataFrame, output_log_path: Path) -> pd.DataFrame:
    """Create a deterministic corrupted copy and persist an event-level audit log."""
    missing_columns = sorted(REQUIRED_COLUMNS - set(df.columns))
    if missing_columns:
        raise ValueError(f"Clean dataframe is missing required columns: {', '.join(missing_columns)}")
    if len(df) < 2:
        raise ValueError("At least two clean records are required to create a corrupted dataset.")

    corrupted = df.copy(deep=True).reset_index(drop=True)
    events: list[dict] = []

    def log_event(record_id: str, corruption_type: str, parameter: dict, before_count: int, after_count: int) -> None:
        events.append(
            {
                "record_id": record_id,
                "type": corruption_type,
                "parameter": parameter,
                "before_count": before_count,
                "after_count": after_count,
            }
        )

    before_drop = len(corrupted)
    latest_count = max(1, before_drop // 10)
    latest_indexes = (
        pd.to_datetime(corrupted["published"], errors="coerce")
        .sort_values(ascending=False, kind="stable")
        .index[:latest_count]
    )
    for index in latest_indexes:
        log_event(
            str(corrupted.at[index, "paper_id"]),
            "drop_latest_record",
            {"selection": "latest_published", "drop_count": latest_count},
            before_drop,
            before_drop - latest_count,
        )
    corrupted = corrupted.drop(index=latest_indexes).reset_index(drop=True)

    blank_index = _select_index(corrupted, 0)
    blank_paper_id = str(corrupted.at[blank_index, "paper_id"])
    corrupted.at[blank_index, "summary"] = ""
    corrupted.at[blank_index, "summary_chars"] = 0
    log_event(blank_paper_id, "blank_summary", {"replacement": ""}, len(corrupted), len(corrupted))

    noise_index = _select_index(corrupted, 1)
    noise_paper_id = str(corrupted.at[noise_index, "paper_id"])
    corrupted.at[noise_index, "summary"] = f"{corrupted.at[noise_index, 'summary']} {NOISE_TOKEN}".strip()
    corrupted.at[noise_index, "summary_chars"] = len(corrupted.at[noise_index, "summary"])
    log_event(noise_paper_id, "inject_noise", {"token": NOISE_TOKEN}, len(corrupted), len(corrupted))

    title_index = _select_index(corrupted, 2)
    title_paper_id = str(corrupted.at[title_index, "paper_id"])
    original_title = str(corrupted.at[title_index, "title"])
    truncated_title = original_title[:48].rstrip()
    corrupted.at[title_index, "title"] = truncated_title
    log_event(
        title_paper_id,
        "truncate_title",
        {"max_characters": 48, "original_characters": len(original_title)},
        len(corrupted),
        len(corrupted),
    )

    date_index = _select_index(corrupted, 3)
    date_paper_id = str(corrupted.at[date_index, "paper_id"])
    published = pd.to_datetime(corrupted.at[date_index, "published"], errors="raise").date()
    old_published = published - timedelta(days=365)
    corrupted.at[date_index, "published"] = old_published.isoformat()
    corrupted.at[date_index, "age_days"] = int(corrupted.at[date_index, "age_days"]) + 365
    log_event(date_paper_id, "age_published_date", {"days_added": 365}, len(corrupted), len(corrupted))

    corrupted["text_for_embedding"] = corrupted.apply(_rebuild_embedding_text, axis=1)

    before_duplicate = len(corrupted)
    duplicate_index = _select_index(corrupted, 4)
    duplicate_record = corrupted.iloc[[duplicate_index]].copy()
    duplicate_paper_id = str(duplicate_record.iloc[0]["paper_id"])
    corrupted = pd.concat([corrupted, duplicate_record], ignore_index=True)
    log_event(
        duplicate_paper_id,
        "duplicate_record",
        {"source_row_index": duplicate_index, "copies_added": 1},
        before_duplicate,
        len(corrupted),
    )

    counts_by_type = dict(Counter(event["type"] for event in events))
    write_json(
        Path(output_log_path),
        {
            "input_rows": len(df),
            "output_rows": len(corrupted),
            "counts_by_type": counts_by_type,
            "events": events,
        },
    )
    return corrupted


def verify_corruption(
    baseline: pd.DataFrame,
    corrupted: pd.DataFrame,
    log: dict,
) -> dict:
    """Xác nhận corrupted dataset khác baseline đúng như log mô tả.

    So sánh từng loại corruption event trong log với sự khác biệt thực tế
    giữa baseline và corrupted dataframe. Trả về dict tổng hợp kết quả
    kiểm tra cho từng loại corruption.
    """
    results: dict = {}
    events = log.get("events", [])
    events_by_type: dict[str, list[dict]] = {}
    for event in events:
        events_by_type.setdefault(event["type"], []).append(event)

    baseline_ids = set(baseline["paper_id"].str.strip().str.lower())
    corrupted_ids = corrupted["paper_id"].str.strip().str.lower()

    # 1. drop_latest_record: records bị xóa phải vắng mặt trong corrupted
    if "drop_latest_record" in events_by_type:
        dropped_ids = {e["record_id"].strip().lower() for e in events_by_type["drop_latest_record"]}
        still_present = dropped_ids & set(corrupted_ids[~corrupted_ids.duplicated(keep=False)])
        results["drop_latest_record"] = {
            "pass": len(still_present) == 0,
            "expected_dropped": len(dropped_ids),
            "still_present": sorted(still_present),
        }

    # 2. blank_summary: record phải có summary rỗng
    if "blank_summary" in events_by_type:
        blank_ids = {e["record_id"].strip().lower() for e in events_by_type["blank_summary"]}
        actual_blank = set(
            corrupted.loc[corrupted["summary"].fillna("").astype(str).str.strip().eq(""), "paper_id"]
            .str.strip().str.lower()
        )
        matched = blank_ids & actual_blank
        results["blank_summary"] = {
            "pass": blank_ids == matched,
            "expected_blank": sorted(blank_ids),
            "actual_blank_count": len(actual_blank),
        }

    # 3. inject_noise: record phải chứa NOISE_TOKEN
    if "inject_noise" in events_by_type:
        noise_ids = {e["record_id"].strip().lower() for e in events_by_type["inject_noise"]}
        actual_noisy = set(
            corrupted.loc[
                corrupted["summary"].fillna("").astype(str).str.contains(NOISE_TOKEN, regex=False),
                "paper_id",
            ].str.strip().str.lower()
        )
        results["inject_noise"] = {
            "pass": noise_ids <= actual_noisy,
            "expected_noisy": sorted(noise_ids),
            "actual_noisy_count": len(actual_noisy),
        }

    # 4. truncate_title: title phải ngắn hơn hoặc bằng max_characters
    if "truncate_title" in events_by_type:
        all_ok = True
        for event in events_by_type["truncate_title"]:
            rid = event["record_id"].strip().lower()
            max_chars = event["parameter"].get("max_characters", 48)
            match = corrupted.loc[corrupted_ids == rid]
            if match.empty or len(str(match.iloc[0]["title"])) > max_chars:
                all_ok = False
                break
        results["truncate_title"] = {"pass": all_ok}

    # 5. age_published_date: age_days phải tăng đúng days_added
    if "age_published_date" in events_by_type:
        all_ok = True
        for event in events_by_type["age_published_date"]:
            rid = event["record_id"].strip().lower()
            days_added = event["parameter"].get("days_added", 365)
            base_match = baseline.loc[baseline["paper_id"].str.strip().str.lower() == rid]
            corr_match = corrupted.loc[corrupted_ids == rid]
            if base_match.empty or corr_match.empty:
                all_ok = False
                break
            base_age = int(base_match.iloc[0]["age_days"])
            corr_age = int(corr_match.iloc[0]["age_days"])
            if corr_age != base_age + days_added:
                all_ok = False
                break
        results["age_published_date"] = {"pass": all_ok}

    # 6. duplicate_record: paper_id phải xuất hiện nhiều hơn 1 lần
    if "duplicate_record" in events_by_type:
        dup_ids = {e["record_id"].strip().lower() for e in events_by_type["duplicate_record"]}
        actual_dup_ids = set(corrupted_ids[corrupted_ids.duplicated(keep=False)])
        results["duplicate_record"] = {
            "pass": dup_ids <= actual_dup_ids,
            "expected_duplicated": sorted(dup_ids),
            "actual_duplicated_count": int(corrupted_ids.duplicated().sum()),
        }

    # 7. Row count: input_rows và output_rows khớp
    results["row_counts"] = {
        "pass": (
            log.get("input_rows") == len(baseline)
            and log.get("output_rows") == len(corrupted)
        ),
        "log_input": log.get("input_rows"),
        "log_output": log.get("output_rows"),
        "actual_baseline": len(baseline),
        "actual_corrupted": len(corrupted),
    }

    results["all_passed"] = all(
        v["pass"] for v in results.values() if isinstance(v, dict) and "pass" in v
    )
    return results
