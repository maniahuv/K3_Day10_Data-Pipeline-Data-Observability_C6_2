#!/usr/bin/env python3
"""Script sinh evaluation test set từ cleaned dataframe."""

from pathlib import Path
import sys

# Ensure src/ directory is in sys.path
root_dir = Path(__file__).resolve().parents[1]
src_dir = root_dir / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import pandas as pd
from core.config import load_settings
from evaluation.testset import build_test_set


def main() -> None:
    settings = load_settings(root_dir)
    clean_csv_path = settings.paths.clean_csv
    eval_testset_path = settings.paths.eval_testset

    if not clean_csv_path.exists():
        print(f"❌ File clean data chưa tồn tại tại: {clean_csv_path}")
        print("Vui lòng thực hiện bước clean data trước khi sinh test set.")
        sys.exit(1)

    print(f"📖 Đang đọc dữ liệu sạch từ: {clean_csv_path}")
    df = pd.read_csv(clean_csv_path)

    # Kiểm tra các cột cần thiết trong cleaned dataframe
    required_cols = {"paper_id", "title", "summary"}
    missing = required_cols - set(df.columns)
    if missing:
        print(f"❌ Cleaned dataframe thiếu các cột bắt buộc: {missing}")
        sys.exit(1)

    print(f"📊 Tổng số paper trong clean dataframe: {len(df)}")

    # Sinh test set với sample_size = 10 (tổng 40 câu hỏi)
    sample_size = 10
    test_set = build_test_set(df, eval_testset_path, sample_size=sample_size)

    print(f"✅ Đã tạo thành công {len(test_set)} câu hỏi test set!")
    print(f"💾 File test set được lưu tại: {eval_testset_path}")

    # In vài ví dụ câu hỏi preview
    print("\n--- Preview 3 câu hỏi đầu tiên ---")
    for item in test_set[:3]:
        print(f"[{item['id']}] ({item['question_type']}) Q: {item['question']}")
        print(f"   Ground Truth: {item['ground_truth'][:80]}...")
        print(f"   Paper ID: {item['ground_truth_doc_ids']}")


if __name__ == "__main__":
    main()
