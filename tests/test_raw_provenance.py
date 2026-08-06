import json
from types import SimpleNamespace

from ingestion.crossref import build_raw_snapshot_report


def test_build_raw_snapshot_report_creates_frozen_snapshot_evidence(tmp_path):
    raw_response_path = tmp_path / "crossref_response.json"
    raw_records_path = tmp_path / "crossref_records.json"
    raw_response_path.write_text(
        json.dumps({"message": {"items": [{"DOI": "10.1000/test", "title": "Example"}]}}),
        encoding="utf-8",
    )
    raw_records_path.write_text(
        json.dumps(
            [
                {
                    "paper_id": "10.1000/test",
                    "title": "Example",
                    "summary": "summary",
                    "authors": [],
                    "categories": [],
                    "primary_category": "",
                    "published": "2026-01-01",
                    "updated": "2026-01-02",
                    "abs_url": "https://doi.org/10.1000/test",
                    "pdf_url": "",
                    "comment": "journal",
                }
            ]
        ),
        encoding="utf-8",
    )

    settings = SimpleNamespace(
        source_api="Crossref REST API",
        refresh_source=False,
        paths=SimpleNamespace(
            raw_api_response=raw_response_path,
            raw_records_json=raw_records_path,
        ),
    )

    report = build_raw_snapshot_report(
        settings,
        clean_records=[{"paper_id": "10.1000/test", "title": "Example"}],
        embeddings_manifest=[{"metadata": {"paper_id": "10.1000/test", "title": "Example"}}],
        sample_paper_id="10.1000/test",
    )

    assert report["raw_snapshot_frozen"] is True
    assert report["response_items"] == 1
    assert report["raw_records_count"] == 1
    assert report["sample_lineage"]["raw_to_clean"] is True
    assert report["sample_lineage"]["clean_to_embedding"] is True
