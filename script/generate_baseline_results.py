from __future__ import annotations

from datetime import datetime, UTC
import sys
from pathlib import Path

# Thêm src/ vào sys.path để import các module của dự án
project_root = Path(__file__).resolve().parent.parent
src_dir = project_root / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from core.config import load_settings
from evaluation.metrics import evaluate_pipeline
from evaluation.testset import build_test_set
from ingestion.cleaning import build_clean_dataframe
from ingestion.crossref import fetch_source_records, load_raw_records
from retrieval.index import LocalEmbeddingIndex


def main() -> None:
    """
    Script thực thi đánh giá Baseline và sinh ra 2 file kết quả JSON:
    1. data/results/baseline_answers.json : Chi tiết các câu hỏi, câu trả lời của AI Agent và retrieved context
    2. data/results/baseline_metrics.json : Thống kê tổng hợp các chỉ số (Hit Rate, Token F1, Judge Score, RAGAS)
    """
    print("🚀 Bắt đầu quá trình Đánh giá Baseline (Baseline Evaluation)...")

    # 1. Load Cấu hình
    settings = load_settings()
    raw_records_path = settings.paths.raw_records_json

    # 2. Đảm bảo có dữ liệu Raw
    if not raw_records_path.exists():
        print(f"📦 Không tìm thấy raw records tại {raw_records_path.name}, tiến hành tải từ Crossref API...")
        raw_records = fetch_source_records(settings)
    else:
        raw_records = load_raw_records(raw_records_path)
    
    print(f"📦 Đã sẵn sàng {len(raw_records)} raw records.")

    # 3. Làm sạch dữ liệu (Clean Data)
    print("🧼 Đang sơ chế và làm sạch dữ liệu...")
    run_date = datetime.now(UTC)
    clean_df = build_clean_dataframe(raw_records, run_date)
    print(f"✅ Đã làm sạch xong. Số bản ghi hợp lệ: {len(clean_df)}")

    # 4. Xây dựng Vector Store Index cho Baseline (papers-baseline)
    print("⚡ Đang tạo Vector Embeddings & ChromaDB Collection (papers-baseline)...")
    index = LocalEmbeddingIndex.build(clean_df, settings)
    print("✅ Đã index xong dữ liệu vào ChromaDB.")

    # 5. Chuẩn bị Test Set (Bộ câu hỏi kiểm thử)
    test_set_path = settings.paths.eval_testset
    test_set_path.parent.mkdir(parents=True, exist_ok=True)
    
    if not test_set_path.exists():
        print("📝 Đang tạo mới bộ Test Set cho đánh giá...")
        build_test_set(clean_df, test_set_path)
    else:
        print(f"📝 Đã tìm thấy bộ Test Set cố định tại: {test_set_path.name}")

    # 6. Đánh giá Pipeline & Tạo 2 file kết quả JSON
    metrics_path = settings.paths.baseline_metrics
    answers_path = settings.paths.baseline_answers
    
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    answers_path.parent.mkdir(parents=True, exist_ok=True)

    print("\n🤖 Đang chạy RAG Agent & LLM Judge để đánh giá Baseline...")
    bundle = evaluate_pipeline(
        settings=settings,
        index=index,
        test_set_path=test_set_path,
        metrics_output_path=metrics_path,
        answers_output_path=answers_path,
    )

    print("\n🎉 ĐÁNH GIÁ BASELINE HOÀN TẤT!")
    print(f"📄 File 1 (Answers JSON) : {answers_path}")
    print(f"📄 File 2 (Metrics JSON) : {metrics_path}")
    print("\n📊 BẢNG TỔNG HỢP CHỈ SỐ BASELINE:")
    print(f"   • Số mẫu đánh giá (Samples)     : {bundle.summary.get('samples')}")
    print(f"   • Retrieval Hit Rate            : {bundle.summary.get('retrieval_hit_rate'):.2%}")
    print(f"   • Mean Token F1 Score           : {bundle.summary.get('mean_token_f1'):.4f}")
    print(f"   • LLM Judge Accuracy            : {bundle.summary.get('judge_accuracy'):.2%}")
    print(f"   • Mean LLM Judge Score          : {bundle.summary.get('mean_judge_score'):.2f} / 5.0")


if __name__ == "__main__":
    main()
