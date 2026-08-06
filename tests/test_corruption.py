import json

import pandas as pd

from ingestion.corruption import NOISE_TOKEN, corrupt_clean_dataframe, verify_corruption


def test_corruption_preserves_baseline_and_writes_auditable_log(tmp_path):
    baseline = pd.DataFrame(
        [
            {
                "paper_id": f"paper-{index}",
                "title": f"A sufficiently long title for paper {index}",
                "summary": f"Summary for paper {index}.",
                "published": f"2026-07-{index:02d}",
                "age_days": index,
                "authors_joined": "Ada Lovelace",
                "categories_joined": "Machine Learning",
                "summary_chars": 20,
                "text_for_embedding": f"baseline-{index}",
            }
            for index in range(1, 7)
        ]
    )
    baseline_before = baseline.copy(deep=True)
    log_path = tmp_path / "corruption_log.json"

    corrupted = corrupt_clean_dataframe(baseline, log_path)
    log = json.loads(log_path.read_text(encoding="utf-8"))

    pd.testing.assert_frame_equal(baseline, baseline_before)
    assert len(corrupted) == len(baseline)
    assert corrupted["paper_id"].duplicated().sum() == 1
    assert (corrupted["summary"] == "").sum() == 1
    assert corrupted["summary"].str.contains(NOISE_TOKEN, regex=False).sum() == 1
    assert corrupted["title"].str.len().le(48).sum() >= 1
    assert corrupted["age_days"].max() >= 365
    assert set(log["counts_by_type"]) == {
        "drop_latest_record",
        "blank_summary",
        "inject_noise",
        "truncate_title",
        "age_published_date",
        "duplicate_record",
    }
    assert all({"record_id", "type", "parameter", "before_count", "after_count"} <= event.keys() for event in log["events"])


def test_verify_corruption_confirms_all_changes_match_log(tmp_path):
    baseline = pd.DataFrame(
        [
            {
                "paper_id": f"paper-{index}",
                "title": f"A sufficiently long title for paper {index}",
                "summary": f"Summary for paper {index}.",
                "published": f"2026-07-{index:02d}",
                "age_days": index,
                "authors_joined": "Ada Lovelace",
                "categories_joined": "Machine Learning",
                "summary_chars": 20,
                "text_for_embedding": f"baseline-{index}",
            }
            for index in range(1, 7)
        ]
    )
    log_path = tmp_path / "corruption_log.json"

    corrupted = corrupt_clean_dataframe(baseline, log_path)
    log = json.loads(log_path.read_text(encoding="utf-8"))

    result = verify_corruption(baseline, corrupted, log)

    assert result["all_passed"] is True
    assert result["drop_latest_record"]["pass"] is True
    assert result["blank_summary"]["pass"] is True
    assert result["inject_noise"]["pass"] is True
    assert result["truncate_title"]["pass"] is True
    assert result["age_published_date"]["pass"] is True
    assert result["duplicate_record"]["pass"] is True
    assert result["row_counts"]["pass"] is True
