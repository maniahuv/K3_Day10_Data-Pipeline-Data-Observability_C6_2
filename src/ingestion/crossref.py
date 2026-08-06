from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
import re
import time
from typing import Any

from core.utils import normalize_whitespace, read_json, write_json

import requests

from core.config import Settings


@dataclass(frozen=True)
class PaperRecord:
    paper_id: str
    title: str
    summary: str
    authors: list[str]
    categories: list[str]
    primary_category: str
    published: str
    updated: str
    abs_url: str
    pdf_url: str
    comment: str


def _clean_html(value: str) -> str:
    if not value:
        return ""
    cleaned = re.sub(r"<[^>]+>", " ", str(value))
    return normalize_whitespace(cleaned)


def _normalize_string(value: Any) -> str:
    if value is None:
        return ""
    return normalize_whitespace(str(value))


def _normalize_string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [normalize_whitespace(str(item)) for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [normalize_whitespace(value)]
    return []


def _build_paper_id(doi: str, title: str) -> str:
    doi_text = normalize_whitespace(str(doi or "")).lower()
    if doi_text:
        doi_text = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi_text, flags=re.I)
        return doi_text
    title_text = normalize_whitespace(title or "").lower()
    if title_text:
        return re.sub(r"[^a-z0-9]+", "-", title_text).strip("-")
    return ""


def _parse_date_field(value: Any) -> str:
    if not value:
        return ""
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value).date().isoformat()
        except ValueError:
            return normalize_whitespace(value)
    if isinstance(value, dict):
        if date_time := value.get("date-time"):
            try:
                return datetime.fromisoformat(date_time).date().isoformat()
            except ValueError:
                return normalize_whitespace(date_time)
        if parts := value.get("date-parts"):
            return _join_date_parts(parts)
    if isinstance(value, list):
        return _join_date_parts(value)
    return ""


def _join_date_parts(parts: Any) -> str:
    if not isinstance(parts, list) or not parts:
        return ""
    first = parts[0] if isinstance(parts[0], list) else parts
    if not isinstance(first, list):
        return ""
    normalized = [str(int(part)).zfill(2) for part in first[:3] if isinstance(part, (int, float)) or str(part).isdigit()]
    if not normalized:
        return ""
    if len(normalized) == 1:
        return normalized[0]
    if len(normalized) == 2:
        return f"{normalized[0]}-{normalized[1]}"
    return f"{normalized[0]}-{normalized[1]}-{normalized[2]}"


def _extract_date(message: dict[str, Any]) -> tuple[str, str]:
    published = ""
    updated = ""
    for key in ("published-print", "published-online", "issued", "created"):
        if key in message and not published:
            published = _parse_date_field(message[key])
    for key in ("indexed", "updated", "created", "issued"):
        if key in message and not updated:
            updated = _parse_date_field(message[key])
    return published, updated


def _find_pdf_url(message: dict[str, Any]) -> str:
    for link in message.get("link", []) if isinstance(message.get("link", []), list) else []:
        content_type = str(link.get("content-type", "")).lower()
        if "pdf" in content_type or content_type == "application/pdf":
            return _normalize_string(link.get("URL", ""))
    return ""


def parse_crossref_payload(payload: dict) -> list[PaperRecord]:
    """Parse Crossref payload thanh list PaperRecord."""
    items = payload.get("message", {}).get("items", []) if isinstance(payload, dict) else []
    records: list[PaperRecord] = []

    for item in items:
        if not isinstance(item, dict):
            continue

        title_candidates = _normalize_string_list(item.get("title", []))
        title = title_candidates[0] if title_candidates else ""
        summary = _clean_html(item.get("abstract", ""))
        authors = [
            _normalize_string(" ".join((author.get("given", ""), author.get("family", ""))).strip())
            for author in item.get("author", [])
            if isinstance(author, dict)
        ]
        categories = _normalize_string_list(item.get("subject", []))
        primary_category = categories[0] if categories else ""
        published, updated = _extract_date(item)
        abs_url = _normalize_string(item.get("URL", ""))
        pdf_url = _find_pdf_url(item)
        comment = _normalize_string(item.get("type", ""))
        paper_id = _build_paper_id(item.get("DOI", ""), title)

        if not paper_id or not title:
            continue

        records.append(
            PaperRecord(
                paper_id=paper_id,
                title=title,
                summary=summary,
                authors=authors,
                categories=categories,
                primary_category=primary_category,
                published=published,
                updated=updated,
                abs_url=abs_url,
                pdf_url=pdf_url,
                comment=comment,
            )
        )

    return records


def fetch_source_records(settings: Settings) -> list[PaperRecord]:
    """Fetch source API, luu raw response va parse thanh records."""
    api_url = "https://api.crossref.org/works"
    params: dict[str, Any] = {
        "query": settings.source_query,
        "rows": settings.max_results,
    }
    if settings.source_filter:
        params["filter"] = settings.source_filter

    headers = {
        "User-Agent": "day10-data-observability-lab-student/0.1 (mailto:student@example.com)",
        "Accept": "application/json",
    }

    session = requests.Session()
    attempt = 1
    max_attempts = 6
    backoff_seconds = 1
    last_exception: Exception | None = None

    while attempt <= max_attempts:
        try:
            response = session.get(api_url, params=params, headers=headers, timeout=20)
            if response.status_code == 200:
                payload = response.json()
                write_json(settings.paths.raw_api_response, payload)
                records = parse_crossref_payload(payload)
                write_json(settings.paths.raw_records_json, [asdict(record) for record in records])
                return records

            if response.status_code in {429, 503, 502}:
                time.sleep(backoff_seconds)
                backoff_seconds *= 2
                attempt += 1
                continue

            response.raise_for_status()
        except requests.RequestException as exc:
            last_exception = exc
            if attempt >= max_attempts:
                raise
            time.sleep(backoff_seconds)
            backoff_seconds *= 2
            attempt += 1

    raise RuntimeError("Failed to fetch Crossref source records.") from last_exception


def load_raw_records(path: Path) -> list[PaperRecord]:
    """Doc JSON snapshot va map thanh `PaperRecord`."""
    payload = read_json(path)
    if not isinstance(payload, list):
        raise ValueError(f"Expected a list of raw records at {path}, got {type(payload).__name__}.")

    records: list[PaperRecord] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        records.append(PaperRecord(**item))

    return records


def build_raw_snapshot_report(
    settings: Settings,
    clean_records: list[dict[str, Any]],
    embeddings_manifest: list[dict[str, Any]],
    sample_paper_id: str,
) -> dict[str, Any]:
    """Tạo bằng chứng provenance/raw snapshot cho checkpoint 5.

    Mục tiêu: xác nhận raw snapshot đã được lưu trước khi corrupt data và
    cho phép truy vết một paper_id từ raw -> clean -> embedding manifest.
    """
    raw_response_path = settings.paths.raw_api_response
    raw_records_path = settings.paths.raw_records_json

    if not raw_response_path.exists() or not raw_records_path.exists():
        raise FileNotFoundError("Raw snapshot artifacts are missing for provenance check.")

    raw_response = read_json(raw_response_path)
    raw_records = read_json(raw_records_path)
    response_items = raw_response.get("message", {}).get("items", []) if isinstance(raw_response, dict) else []

    raw_records_count = len(raw_records) if isinstance(raw_records, list) else 0
    response_items_count = len(response_items) if isinstance(response_items, list) else 0

    raw_match = next((item for item in raw_records if isinstance(item, dict) and item.get("paper_id") == sample_paper_id), None)
    clean_match = next((item for item in clean_records if isinstance(item, dict) and item.get("paper_id") == sample_paper_id), None)
    embedding_match = next(
        (
            item
            for item in embeddings_manifest
            if isinstance(item, dict)
            and isinstance(item.get("metadata"), dict)
            and item.get("metadata", {}).get("paper_id") == sample_paper_id
        ),
        None,
    )

    report = {
        "raw_snapshot_frozen": True,
        "refresh_source_allowed": bool(settings.refresh_source),
        "source_api": settings.source_api,
        "response_items": response_items_count,
        "raw_records_count": raw_records_count,
        "sample_paper_id": sample_paper_id,
        "sample_lineage": {
            "raw_to_clean": bool(raw_match and clean_match),
            "clean_to_embedding": bool(clean_match and embedding_match),
            "raw_title": raw_match.get("title") if raw_match else None,
            "clean_title": clean_match.get("title") if clean_match else None,
            "embedding_title": embedding_match.get("metadata", {}).get("title") if embedding_match else None,
            "raw_abs_url": raw_match.get("abs_url") if raw_match else None,
            "clean_abs_url": clean_match.get("abs_url") if clean_match else None,
            "embedding_abs_url": embedding_match.get("metadata", {}).get("abs_url") if embedding_match else None,
        },
        "freeze_rule": "Do not refresh raw artifacts during baseline/corruption comparison; use the frozen snapshot for lineage and fairness.",
    }
    return report
