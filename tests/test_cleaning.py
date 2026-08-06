from datetime import UTC, datetime
import json
from pathlib import Path

from ingestion.cleaning import build_clean_dataframe, save_clean_artifacts
from ingestion.crossref import PaperRecord


def test_raw_fixture_is_cleaned_and_logged(tmp_path):
    fixture_path = Path("tests/fixtures/raw_records_sample.json")
    records = [PaperRecord(**item) for item in json.loads(fixture_path.read_text(encoding="utf-8"))]

    dataframe = build_clean_dataframe(records, datetime(2025, 2, 10, tzinfo=UTC))
    log = dataframe.attrs["cleaning_log"]

    assert len(dataframe) == 1
    row = dataframe.iloc[0]
    assert row["paper_id"] == "10.1234/sample.1"
    assert row["authors_joined"] == "Ada Lovelace"
    assert row["categories_joined"] == "Machine Learning"
    assert row["age_days"] == 39
    assert row["text_for_embedding"] == (
        "Title: A sample paper\n"
        "Summary: Useful summary.\n"
        "Authors: Ada Lovelace\n"
        "Categories: Machine Learning"
    )
    assert log["counts_by_reason"] == {
        "duplicate_paper_id": 1,
        "missing_summary": 1,
        "invalid_published": 1,
    }

    csv_path = tmp_path / "papers_clean.csv"
    json_path = tmp_path / "papers_clean.json"
    log_path = tmp_path / "cleaning_log.json"
    saved_log = save_clean_artifacts(dataframe, csv_path, json_path, log_path)

    assert csv_path.exists()
    assert json.loads(json_path.read_text(encoding="utf-8"))[0]["paper_id"] == "10.1234/sample.1"
    assert saved_log["removed_rows"] == 3
    assert json.loads(log_path.read_text(encoding="utf-8"))["output_rows"] == 1
