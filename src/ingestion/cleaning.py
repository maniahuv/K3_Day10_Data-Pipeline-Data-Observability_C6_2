from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from core.utils import compact_join, normalize_whitespace, write_csv, write_json
from ingestion.crossref import PaperRecord


CLEAN_COLUMNS = [
    "paper_id",
    "title",
    "summary",
    "authors",
    "categories",
    "primary_category",
    "published",
    "updated",
    "abs_url",
    "pdf_url",
    "comment",
    "authors_joined",
    "categories_joined",
    "summary_chars",
    "age_days",
    "text_for_embedding",
]


def _normalize_list(values: list[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for value in values:
        cleaned = normalize_whitespace(value)
        key = cleaned.casefold()
        if cleaned and key not in seen:
            normalized.append(cleaned)
            seen.add(key)
    return normalized


def _parse_optional_date(value: str | None) -> str:
    if not value:
        return ""
    try:
        return date.fromisoformat(value).isoformat()
    except (TypeError, ValueError):
        return ""


def build_clean_dataframe(records: list[PaperRecord], run_date: datetime) -> pd.DataFrame:
    """Normalize parsed records and attach an auditable cleaning log.

    The log is exposed through ``DataFrame.attrs["cleaning_log"]`` and can be
    persisted with :func:`save_clean_artifacts`.
    """
    run_day = run_date.astimezone(UTC).date() if run_date.tzinfo else run_date.date()
    filter_counts: dict[str, int] = {}
    removed_records: list[dict[str, str]] = []
    rows: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    def discard(record: PaperRecord, reason: str) -> None:
        filter_counts[reason] = filter_counts.get(reason, 0) + 1
        removed_records.append({"paper_id": normalize_whitespace(record.paper_id), "reason": reason})

    for record in records:
        paper_id = normalize_whitespace(record.paper_id).casefold()
        title = normalize_whitespace(record.title)
        summary = normalize_whitespace(record.summary)
        if not paper_id:
            discard(record, "missing_paper_id")
            continue
        if not title:
            discard(record, "missing_title")
            continue
        if not summary:
            discard(record, "missing_summary")
            continue
        try:
            published_day = date.fromisoformat(record.published)
        except (TypeError, ValueError):
            discard(record, "invalid_published")
            continue
        if published_day > run_day:
            discard(record, "future_published")
            continue
        if paper_id in seen_ids:
            discard(record, "duplicate_paper_id")
            continue

        authors = _normalize_list(record.authors)
        categories = _normalize_list(record.categories)
        authors_joined = compact_join(authors)
        categories_joined = compact_join(categories)
        text_for_embedding = "\n".join(
            part for part in (
                f"Title: {title}",
                f"Summary: {summary}",
                f"Authors: {authors_joined}" if authors_joined else "",
                f"Categories: {categories_joined}" if categories_joined else "",
            ) if part
        )
        rows.append(
            {
                "paper_id": paper_id,
                "title": title,
                "summary": summary,
                "authors": authors,
                "categories": categories,
                "primary_category": categories[0] if categories else "",
                "published": published_day.isoformat(),
                "updated": _parse_optional_date(record.updated),
                "abs_url": normalize_whitespace(record.abs_url),
                "pdf_url": normalize_whitespace(record.pdf_url),
                "comment": normalize_whitespace(record.comment),
                "authors_joined": authors_joined,
                "categories_joined": categories_joined,
                "summary_chars": len(summary),
                "age_days": (run_day - published_day).days,
                "text_for_embedding": text_for_embedding,
            }
        )
        seen_ids.add(paper_id)

    dataframe = pd.DataFrame(rows, columns=CLEAN_COLUMNS)
    if not dataframe.empty:
        dataframe = dataframe.sort_values(["published", "paper_id"], ascending=[False, True]).reset_index(drop=True)
    dataframe.attrs["cleaning_log"] = {
        "input_rows": len(records),
        "output_rows": len(dataframe),
        "removed_rows": len(removed_records),
        "counts_by_reason": filter_counts,
        "removed_records": removed_records,
    }
    return dataframe


def save_clean_artifacts(
    dataframe: pd.DataFrame,
    csv_path: Path,
    json_path: Path,
    log_path: Path,
) -> dict[str, Any]:
    """Persist the clean dataset and the filter/deduplication audit log."""
    write_csv(dataframe, csv_path)
    write_json(json_path, dataframe.to_dict(orient="records"))
    cleaning_log = dict(dataframe.attrs.get("cleaning_log", {}))
    cleaning_log["csv_path"] = str(csv_path)
    cleaning_log["json_path"] = str(json_path)
    write_json(log_path, cleaning_log)
    return cleaning_log
