from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from core.utils import first_sentence, write_json


def _clean_cell(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def build_test_set(df: pd.DataFrame, output_path, sample_size: int = 10, min_docs: int = 1) -> list[dict[str, Any]]:
    """Tạo bộ evaluation set từ cleaned dataframe.

    Args:
        df: Cleaned dataframe chứa thông tin paper_id, title, summary, authors_joined, published, categories_joined.
        output_path: Đường dẫn lưu file JSON test set.
        sample_size: Số lượng bài báo đại diện được chọn để sinh câu hỏi.
        min_docs: Số lượng bài báo tối thiểu bắt buộc phải có trong df.

    Returns:
        Danh sách các dictionary đại diện cho từng mẫu test set.
    """
    if df is None or len(df) < min_docs:
        raise ValueError(f"Cleaned dataframe must contain at least {min_docs} document(s), got {len(df) if df is not None else 0}.")

    # Chọn một số paper đại diện từ dataframe
    selected_df = df.head(sample_size) if len(df) >= sample_size else df

    test_set: list[dict[str, Any]] = []

    for _, row in selected_df.iterrows():
        paper_id = _clean_cell(row["paper_id"])
        title = _clean_cell(row["title"])
        doc_ids = [paper_id]

        summary_val = first_sentence(_clean_cell(row.get("summary", "")))
        authors_val = _clean_cell(row.get("authors_joined", ""))
        date_val = _clean_cell(row.get("published", ""))
        categories_val = _clean_cell(row.get("categories_joined", ""))

        # 1. Summary Question
        test_set.append(
            {
                "id": f"q_{len(test_set) + 1:03d}",
                "question_type": "summary",
                "question": f"What is the summary of '{title}'?",
                "ground_truth": summary_val,
                "ground_truth_doc_ids": doc_ids,
            }
        )

        if authors_val:
            test_set.append(
                {
                    "id": f"q_{len(test_set) + 1:03d}",
                    "question_type": "authors",
                    "question": f"Who authored '{title}'?",
                    "ground_truth": authors_val,
                    "ground_truth_doc_ids": doc_ids,
                }
            )

        # 3. Date Question
        test_set.append(
            {
                "id": f"q_{len(test_set) + 1:03d}",
                "question_type": "date",
                "question": f"When was '{title}' published?",
                "ground_truth": date_val,
                "ground_truth_doc_ids": doc_ids,
            }
        )

        if categories_val:
            test_set.append(
                {
                    "id": f"q_{len(test_set) + 1:03d}",
                    "question_type": "categories",
                    "question": f"What categories does '{title}' belong to?",
                    "ground_truth": categories_val,
                    "ground_truth_doc_ids": doc_ids,
                }
            )

    out_p = Path(output_path)
    write_json(out_p, test_set)
    return test_set

