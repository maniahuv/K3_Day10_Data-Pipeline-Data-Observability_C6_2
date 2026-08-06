from pathlib import Path
from types import SimpleNamespace

import pandas as pd

from observability.quality import run_data_quality_checks


def test_quality_checks_warn_for_blank_text_duplicate_ids_and_negative_age(tmp_path):
    settings = SimpleNamespace(paths=SimpleNamespace(quality_dir=Path(tmp_path)))
    dataframe = pd.DataFrame(
        [
            {
                "paper_id": "10.1/example",
                "title": "Valid title",
                "summary": "",
                "text_for_embedding": "",
                "age_days": 1,
            },
            {
                "paper_id": "10.1/EXAMPLE",
                "title": "Another title",
                "summary": "Valid summary",
                "text_for_embedding": "Valid embedding text",
                "age_days": -1,
            },
        ]
    )

    report = run_data_quality_checks(dataframe, settings, "quality")

    assert report["status"] == "WARNING"
    assert report["paper_id_uniqueness"]["duplicate_count"] == 1
    assert report["missing_fields"]["summary"]["missing_count"] == 1
    assert report["missing_fields"]["text_for_embedding"]["missing_count"] == 1
    assert report["age_days"]["negative_count"] == 1
