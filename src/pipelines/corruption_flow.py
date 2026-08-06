from __future__ import annotations


def main() -> None:
    from core.config import load_settings
    import pandas as pd
    import sys

    settings = load_settings()
    print("🚀 [CP5] Bắt đầu luồng Corruption & Evaluation (Role 1)")

    # 1. Load baseline clean data
    clean_path = settings.paths.clean_json
    if not clean_path.exists():
        print(f"❌ Lỗi: Không tìm thấy file {clean_path}. Vui lòng chạy phase1 trước!")
        sys.exit(1)
    
    clean_df = pd.read_json(clean_path, orient="records")
    print(f"📦 Đã nạp {len(clean_df)} bản ghi Baseline sạch.")

    # 2. Tao corrupted dataframe (Role 3)
    from ingestion.corruption import corrupt_clean_dataframe
    print("\n🦠 Đang tiêm lỗi (Corruption) vào dữ liệu (Role 3)...")
    try:
        corrupted_df = corrupt_clean_dataframe(clean_df, settings.paths.corruption_log)
        print(f"✅ Đã tiêm lỗi xong. Số bản ghi hiện tại: {len(corrupted_df)}")
    except NotImplementedError:
        print("\n🚧 [Blocker Evidence]: Role 3 chưa hoàn thiện hàm `corrupt_clean_dataframe`!")
        print("🚧 Bạn hãy vào file `src/ingestion/corruption.py` để triển khai logic phá hoại dữ liệu (Checkpoint 5) nhé.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Lỗi khi chạy tiêm lỗi: {e}")
        sys.exit(1)

    # 3. Save corrupted artifacts
    settings.paths.corrupted_clean_json.parent.mkdir(parents=True, exist_ok=True)
    corrupted_df.to_json(settings.paths.corrupted_clean_json, orient="records", force_ascii=False, indent=2)
    corrupted_df.to_csv(settings.paths.corrupted_clean_csv, index=False)
    print(f"💾 Đã lưu corrupted dataset vào {settings.paths.corrupted_clean_json.name}")

    # 4. Rebuild index va evaluate (Role 4 & Role 5)
    print("\n🗄️ Đang xây dựng lại Index cho tập dữ liệu bị bẩn (Role 4)...")
    from retrieval.index import LocalEmbeddingIndex
    try:
        corrupted_index = LocalEmbeddingIndex.build(
            df=corrupted_df,
            settings=settings,
            embeddings_output_path=settings.paths.corrupted_embeddings_json,
            collection_name=settings.corrupted_collection_name
        )
        print(f"✅ Đã tạo Index mới riêng biệt: {settings.corrupted_collection_name}")
    except Exception as e:
        print(f"❌ Lỗi khi tạo Index corrupted: {e}")
        sys.exit(1)

    print("\n⚖️ Đang Evaluate Agent trên dữ liệu bẩn (Role 5)...")
    from evaluation.metrics import evaluate_pipeline
    try:
        eval_bundle = evaluate_pipeline(
            settings=settings,
            index=corrupted_index,
            test_set_path=settings.paths.eval_testset,
            metrics_output_path=settings.paths.corrupted_metrics,
            answers_output_path=settings.paths.corrupted_answers
        )
        print(f"📉 Kết quả Corrupted - Hit Rate: {eval_bundle.summary.get('retrieval_hit_rate'):.2%} | Token F1: {eval_bundle.summary.get('mean_token_f1'):.4f}")
    except Exception as e:
        print(f"❌ Lỗi khi evaluate corrupted data: {e}")
        sys.exit(1)

    # 5. Run quality checks/freshness tren corrupted data (Role 6)
    print("\n🔎 Đang thu thập tín hiệu Quality & Freshness trên tập bẩn (Role 6)...")
    from observability.quality import run_data_quality_checks, build_freshness_report
    try:
        corrupted_quality = run_data_quality_checks(corrupted_df, settings, report_name="corrupted_quality")
        corrupted_freshness = build_freshness_report(corrupted_df, settings, report_path=settings.paths.quality_dir / "corrupted_freshness_report.json")
        print("✅ Đã xuất báo cáo tín hiệu lỗi.")
    except Exception as e:
        print(f"❌ Lỗi khi chạy Quality Check trên corrupted data: {e}")
        sys.exit(1)

    print("\n🎉 [Checkpoint 5]: Role 1 đã dàn xếp xong kịch bản Corruption.")
    print("🚧 Hiện tại kịch bản có thể chạy thông suốt, nhưng hãy đợi Role 3 implement logic phá hoại dữ liệu!")
