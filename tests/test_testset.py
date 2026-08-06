import json

import pandas as pd

from evaluation.testset import build_test_set


def test_test_set_skips_optional_questions_without_ground_truth(tmp_path):
    dataframe = pd.DataFrame(
        [
            {
                "paper_id": "paper-1",
                "title": "First paper",
                "summary": "First summary.",
                "authors_joined": "Ada Lovelace",
                "published": "2025-01-01",
                "categories_joined": float("nan"),
            },
            {
                "paper_id": "paper-2",
                "title": "Second paper",
                "summary": "Second summary.",
                "authors_joined": None,
                "published": "2025-01-02",
                "categories_joined": "Machine Learning",
            },
        ]
    )
    output_path = tmp_path / "test_set.json"

    test_set = build_test_set(dataframe, output_path)

    assert [item["question_type"] for item in test_set] == [
        "summary",
        "authors",
        "date",
        "summary",
        "date",
        "categories",
    ]
    assert all(item["ground_truth"].strip().lower() != "nan" for item in test_set)
    assert json.loads(output_path.read_text(encoding="utf-8")) == test_set
