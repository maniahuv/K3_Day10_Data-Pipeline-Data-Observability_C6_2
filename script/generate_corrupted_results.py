from __future__ import annotations

from datetime import datetime, UTC
import sys
from pathlib import Path
import pandas as pd

# Thêm src/ vào sys.path
project_root = Path(__file__).resolve().parent.parent
src_dir = project_root / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from core.config import load_settings
from core.utils import read_json, write_json
from evaluation.metrics import evaluate_pipeline
from ingestion.cleaning import build_clean_dataframe
from ingestion.crossref import load_raw_records
from retrieval.index import LocalEmbeddingIndex


def create_corrupted_dataframe(clean_df: pd.DataFrame, log_output_path: Path) -> pd.DataFrame:
    """Tạo corrupted dataframe giả lập lỗi dữ liệu thực tế."""
    corrupted_df = clean_df.copy()
    corruption_log = {
        "timestamp": datetime.now(UTC).isoformat(),
        "total_records_before": len(corrupted_df),
        "actions": []
    }

    # 1. Xóa summary của 30% bản ghi đầu tiên
    num_blank = max(1, int(len(corrupted_df) * 0.3))
    corrupted_df.iloc[:num_blank, corrupted_df.columns.get_loc("summary")] = ""
    corruption_log["actions"].append(f"Blanked summary for {num_blank} records.")

    # 2. Thêm text nhiễu rác vào summary của một số bản ghi
    for idx in range(num_blank, min(num_blank + 3, len(corrupted_df))):
        corrupted_df.iloc[idx, corrupted_df.columns.get_loc("summary")] = "NOISE TEXT INVALID DATA CORRUPTED " * 5
    corruption_log["actions"].append(f"Injected noise text into records.")

    # 3. Tạo lại trường text_for_embedding từ dữ liệu bị hỏng
    corrupted_df["text_for_embedding"] = (
        "Title: " + corrupted_df["title"].fillna("") + 
        " | Summary: " + corrupted_df["summary"].fillna("")
    )
    
    corruption_log["total_records_after"] = len(corrupted_df)
    write_json(log_output_path, corruption_log)
    return corrupted_df


def main() -> None:
    """
    Script thực thi Đánh giá trên Dữ liệu Lỗi (Corrupted Evaluation) bằng bộ Test Set CŨ:
    1. Đọc dữ liệu sạch, tạo dữ liệu lỗi (Corrupted Data).
    2. Build Index vào ChromaDB collection mới ('papers-corrupted').
    3. ĐỌC LẠI BỘ TEST SET CŨ (data/eval/test_set.json) đã dùng ở Baseline.
    4. Chạy evaluate_pipeline và xuất ra:
       - data/results/corrupted_answers.json
       - data/results/corrupted_metrics.json
    """
    print("🚀 Bắt đầu Đánh giá trên Dữ liệu Lỗi (Corrupted Evaluation)...")
    settings = load_settings()

    # 1. Đọc dữ liệu sạch
    raw_records_path = settings.paths.raw_records_json
    if not raw_records_path.exists():
        print(f"❌ Không tìm thấy raw records tại {raw_records_path}. Vui lòng chạy phase 1 trước!")
        sys.exit(1)
        
    raw_records = load_raw_records(raw_records_path)
    clean_df = build_clean_dataframe(raw_records, datetime.now(UTC))

    # 2. Giả lập dữ liệu hỏng (Corrupt Data)
    print("💥 Đang giả lập các lỗi dữ liệu (Blank Summary, Text Noise)...")
    corrupted_log_path = settings.paths.corruption_log
    corrupted_log_path.parent.mkdir(parents=True, exist_ok=True)
    corrupted_df = create_corrupted_dataframe(clean_df, corrupted_log_path)
    print(f"📄 Đã ghi nhận nhật ký lỗi tại: {corrupted_log_path.name}")

    # 3. Nạp dữ liệu lỗi vào Vector Store Collection mới ('papers-corrupted')
    print("⚡ Đang tạo Vector Embeddings cho Corrupted Collection ('papers-corrupted')...")
    corrupted_index = LocalEmbeddingIndex.build(
        corrupted_df,
        settings,
        embeddings_output_path=settings.paths.corrupted_embeddings_json
    )

    # 4. BẮT BUỘC DÙNG LẠI BỘ TEST SET CŨ (test_set.json)
    test_set_path = settings.paths.eval_testset
    if not test_set_path.exists():
        print(f"❌ Lỗi: Không tìm thấy bộ test set cũ tại {test_set_path}!")
        print("Bắt buộc phải chạy Baseline để sinh bộ test set cố định trước.")
        sys.exit(1)
        
    print(f"📌 Đã load bộ Test Set CŨ từ Baseline: {test_set_path.name}")

    # 5. Chạy Đánh giá và Tạo 2 file corrupted answers/metrics
    answers_path = settings.paths.corrupted_answers
    metrics_path = settings.paths.corrupted_metrics
    answers_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)

    print("\n🤖 Đang chạy RAG Agent & LLM Judge trên Dữ Liệu Lỗi...")
    bundle = evaluate_pipeline(
        settings=settings,
        index=corrupted_index,
        test_set_path=test_set_path,
        metrics_output_path=metrics_path,
        answers_output_path=answers_path,
    )

    print("\n🎉 ĐÁNH GIÁ CORRUPTED HOÀN TẤT!")
    print(f"📄 File 1 (Corrupted Answers JSON) : {answers_path}")
    print(f"📄 File 2 (Corrupted Metrics JSON) : {metrics_path}")
    print("\n📊 BẢNG TỔNG HỢP CHỈ SỐ CORRUPTED:")
    print(f"   • Số mẫu đánh giá (Samples)     : {bundle.summary.get('samples')}")
    print(f"   • Retrieval Hit Rate            : {bundle.summary.get('retrieval_hit_rate'):.2%}")
    print(f"   • Mean Token F1 Score           : {bundle.summary.get('mean_token_f1'):.4f}")
    print(f"   • LLM Judge Accuracy            : {bundle.summary.get('judge_accuracy'):.2%}")
    print(f"   • Mean LLM Judge Score          : {bundle.summary.get('mean_judge_score'):.2f} / 5.0")


if __name__ == "__main__":
    main()
