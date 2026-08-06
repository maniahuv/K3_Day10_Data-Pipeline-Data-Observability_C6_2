from __future__ import annotations


def main() -> None:
    from core.config import load_settings
    import pandas as pd
    import sys
    from core.utils import write_json

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

    # 3b. Build raw snapshot provenance report (Role 2)
    from ingestion.crossref import build_raw_snapshot_report
    try:
        clean_records = clean_df.to_dict(orient="records")
        embeddings_manifest = []
        if settings.paths.embeddings_json.exists():
            embeddings_manifest = pd.read_json(settings.paths.embeddings_json, orient="records").to_dict(orient="records")
        sample_paper_id = "10.36227/techrxiv.177272838.89432844/v1"
        provenance_report = build_raw_snapshot_report(
            settings=settings,
            clean_records=clean_records,
            embeddings_manifest=embeddings_manifest,
            sample_paper_id=sample_paper_id,
        )
        provenance_path = settings.paths.quality_dir / "raw_provenance_checkpoint5.json"
        write_json(provenance_path, provenance_report)
        print(f"🧭 Đã lưu raw provenance evidence vào {provenance_path.name}")
    except Exception as exc:
        print(f"⚠️ Không thể tạo raw provenance report: {exc}")

    # 4. Rebuild index va evaluate (Role 4 & Role 5)
    print("\n🗄️ Đang xây dựng lại Index cho tập dữ liệu bị bẩn (Role 4)...")
    from retrieval.index import LocalEmbeddingIndex
    try:
        corrupted_index = LocalEmbeddingIndex.build(
            df=corrupted_df,
            settings=settings,
            embeddings_output_path=settings.paths.corrupted_embeddings_json,
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

    # --- BẮT ĐẦU CHECKPOINT 6 ---
    print("\n🚀 [CP6] Bắt đầu luồng Phục hồi (Repair) & So sánh (Role 1)")

    # 6. Repair lai tu raw records (Role 2 & 3)
    print("\n🔧 Đang phục hồi dữ liệu từ nguồn Raw (Role 2 & 3)...")
    from ingestion.crossref import load_raw_records
    from ingestion.cleaning import build_clean_dataframe
    from datetime import datetime, UTC
    import json

    try:
        raw_records = load_raw_records(settings.paths.raw_records_json)
        run_date = datetime.now(UTC)
        repaired_df = build_clean_dataframe(raw_records, run_date)
        print(f"✅ Đã phục hồi xong. Số bản ghi hiện tại: {len(repaired_df)}")

        settings.paths.repaired_clean_json.parent.mkdir(parents=True, exist_ok=True)
        repaired_df.to_json(settings.paths.repaired_clean_json, orient="records", force_ascii=False, indent=2)
        repaired_df.to_csv(settings.paths.repaired_clean_csv, index=False)
        print(f"💾 Đã lưu repaired dataset vào {settings.paths.repaired_clean_json.name}")
    except Exception as e:
        print(f"❌ Lỗi khi phục hồi dữ liệu: {e}")
        sys.exit(1)

    print("\n🗄️ Đang xây dựng lại Index cho tập dữ liệu đã phục hồi (Role 4)...")
    try:
        repaired_index = LocalEmbeddingIndex.build(
            df=repaired_df,
            settings=settings,
            embeddings_output_path=settings.paths.repaired_embeddings_json,
        )
        print(f"✅ Đã tạo Index mới riêng biệt: {settings.repaired_collection_name}")
    except Exception as e:
        print(f"❌ Lỗi khi tạo Index repaired: {e}")
        sys.exit(1)

    print("\n⚖️ Đang Evaluate Agent trên dữ liệu đã phục hồi (Role 5)...")
    try:
        repaired_bundle = evaluate_pipeline(
            settings=settings,
            index=repaired_index,
            test_set_path=settings.paths.eval_testset,
            metrics_output_path=settings.paths.repaired_metrics,
            answers_output_path=settings.paths.repaired_answers,
        )
        print(f"📈 Kết quả Repaired - Hit Rate: {repaired_bundle.summary.get('retrieval_hit_rate'):.2%} | Token F1: {repaired_bundle.summary.get('mean_token_f1'):.4f}")
    except Exception as e:
        print(f"❌ Lỗi khi evaluate repaired data: {e}")
        sys.exit(1)

    print("\n🔎 Đang thu thập tín hiệu Quality & Freshness trên tập phục hồi (Role 6)...")
    try:
        repaired_quality = run_data_quality_checks(repaired_df, settings, report_name="repaired_quality")
        repaired_freshness = build_freshness_report(repaired_df, settings, report_path=settings.paths.quality_dir / "repaired_freshness_report.json")
    except Exception as e:
        print(f"❌ Lỗi khi chạy Quality Check trên repaired data: {e}")
        sys.exit(1)

    print("\n📄 Đang tạo Báo cáo So sánh Baseline - Corrupted - Repaired (Role 6)...")
    from observability.reporting import generate_corruption_report
    try:
        with open(settings.paths.baseline_metrics, "r", encoding="utf-8") as f:
            baseline_metrics = json.load(f)

        generate_corruption_report(
            report_path=settings.paths.comparison_report,
            baseline_metrics=baseline_metrics,
            corrupted_metrics=eval_bundle.summary,
            repaired_metrics=repaired_bundle.summary,
            corrupted_quality=corrupted_quality,
            repaired_quality=repaired_quality,
            corrupted_freshness=corrupted_freshness,
            repaired_freshness=repaired_freshness,
        )
        print(f"✅ Đã tạo Báo cáo So sánh tại: {settings.paths.comparison_report}")
    except Exception as e:
        print(f"❌ Lỗi khi sinh Báo cáo So sánh: {e}")
        sys.exit(1)

    print("\n🎉 [Checkpoint 6]: Hoàn tất toàn bộ chu trình Data Pipeline & Observability!")
