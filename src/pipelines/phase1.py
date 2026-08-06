from __future__ import annotations


def main() -> None:
    """Baseline pipeline end-to-end cho Checkpoint 1 (Role 1)."""
    import sys
    from core.config import load_settings
    from ingestion.crossref import load_raw_records
    from ingestion.cleaning import build_clean_dataframe
    from datetime import datetime, UTC

    print("🚀 Bắt đầu Phase 1 Pipeline (Checkpoint 1 - Role 1)")

    # 1. Load settings
    settings = load_settings()

    # 2. Load raw records
    raw_records_path = settings.paths.raw_records_json
    if not raw_records_path.exists():
        print(f"❌ Lỗi (Blocker): Không tìm thấy dữ liệu raw tại {raw_records_path}!")
        sys.exit(1)
    
    raw_records = load_raw_records(raw_records_path)
    raw_count = len(raw_records)
    print(f"📦 Đã load {raw_count} raw records từ {raw_records_path.name}")

    if raw_count == 0:
        print("❌ Lỗi (Blocker): Dữ liệu raw trống!")
        sys.exit(1)

    # 3. Clean data (Do Role 3 thực hiện)
    print("🧹 Bắt đầu quá trình làm sạch dữ liệu (Gọi module cleaning)...")
    try:
        run_date = datetime.now(UTC)
        clean_df = build_clean_dataframe(raw_records, run_date)
    except NotImplementedError:
        print("\n🚧 [Blocker Evidence]: Role 3 chưa hoàn thiện hàm `build_clean_dataframe` trong `cleaning.py`!")
        print("🚧 Pipeline bị chặn lại ở bước Clean. Vui lòng hoàn thành Checkpoint 1 (Cleaning) trước khi đi tiếp.")
        sys.exit(1)
    
    clean_count = len(clean_df)
    print(f"✅ Quá trình làm sạch hoàn tất.")
    print(f"📊 Thống kê: Raw Count = {raw_count} | Clean Count = {clean_count}")

    # Truy vết lý do loại bỏ (từ cleaning_log của Role 3)
    cleaning_log = clean_df.attrs.get("cleaning_log", {})
    counts_by_reason = cleaning_log.get("counts_by_reason", {})
    if counts_by_reason:
        print("🔍 Chi tiết lý do loại bỏ record:")
        for reason, count in counts_by_reason.items():
            print(f"   - {reason}: {count} records")

    # Review (Bắt lỗi) drop rate
    drop_rate = (raw_count - clean_count) / raw_count
    print(f"📉 Tỷ lệ loại bỏ (Drop rate): {drop_rate:.2%}")

    if drop_rate > 0.5:
        print("\n❌ [Blocker Evidence]: Tỷ lệ drop > 50%. Có sự bất thường trong quy tắc làm sạch hoặc dữ liệu raw.")
        print("Vui lòng review lại Data Contract trước khi đi tiếp!")
        sys.exit(1)
    
    if clean_count == 0:
        print("\n❌ [Blocker Evidence]: Không còn bản ghi nào sau khi làm sạch!")
        sys.exit(1)

    # 4. Save clean CSV/JSON/Log bằng hàm của Role 3
    from ingestion.cleaning import save_clean_artifacts
    settings.paths.clean_csv.parent.mkdir(parents=True, exist_ok=True)
    
    # Giả sử chúng ta lưu log vào thư mục reports
    log_path = settings.paths.workspace_dir / "data" / "reports" / "cleaning_log.json"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    save_clean_artifacts(
        dataframe=clean_df,
        csv_path=settings.paths.clean_csv,
        json_path=settings.paths.clean_json,
        log_path=log_path
    )
    print(f"💾 Đã lưu dữ liệu clean vào {settings.paths.clean_csv.name}, {settings.paths.clean_json.name}")
    print(f"📄 Đã lưu log làm sạch vào {log_path.name}")

    # --- BẮT ĐẦU CHECKPOINT 2 ---
    print("\n🚀 Bắt đầu Handoff sang Checkpoint 2: Quality Gates, Indexing & Test Set")

    # 5. Quality Check & Freshness Report (Role 6)
    from observability.quality import run_data_quality_checks, build_freshness_report
    print("🔎 Đang chạy Quality Checks...")
    quality_report = run_data_quality_checks(clean_df, settings, report_name="baseline_quality")
    if quality_report.get("status") == "WARNING":
        print("⚠️ [Cảnh báo]: Quality check trả về WARNING. Có thể schema vẫn còn vấn đề.")
    
    print("⏳ Đang chạy Freshness Report...")
    freshness_report = build_freshness_report(clean_df, settings, report_path=settings.paths.freshness_report)
    if not freshness_report.get("is_fresh"):
        print(f"⚠️ [Cảnh báo]: Dữ liệu có {freshness_report.get('stale_rows')} records quá cũ (stale)!")

    # 6. Build Chroma Index (Role 4)
    from retrieval.index import LocalEmbeddingIndex
    print("🗄️ Đang xây dựng Local Embedding Index (ChromaDB)...")
    try:
        index = LocalEmbeddingIndex.build(
            df=clean_df,
            settings=settings,
            embeddings_output_path=settings.paths.embeddings_json
        )
        print(f"✅ Index xây dựng thành công tại: {settings.paths.chroma_dir}")
    except Exception as e:
        print(f"❌ [Blocker]: Lỗi khi build Chroma Index: {e}")
        sys.exit(1)

    # 7. Generate Test Set (Role 5)
    from evaluation.testset import build_test_set
    print("📝 Đang tạo bộ câu hỏi đánh giá (Test Set)...")
    try:
        test_set = build_test_set(clean_df, output_path=settings.paths.eval_testset)
        print(f"✅ Đã tạo {len(test_set)} câu hỏi test set lưu tại: {settings.paths.eval_testset.name}")
    except Exception as e:
        print(f"❌ [Blocker]: Lỗi khi tạo Test Set: {e}")
        sys.exit(1)

    # 8. Agent Smoke Test (Role 4)
    from retrieval.agent import build_agent, run_agent_question
    print("🤖 Đang khởi tạo Agent Smoke Test...")
    try:
        agent = build_agent(settings, index)
        
        # Chọn câu hỏi đầu tiên trong test set để hỏi thử
        if test_set:
            smoke_question = test_set[0]["question"]
            print(f"❓ Hỏi Agent: {smoke_question}")
            answer = run_agent_question(agent, smoke_question)
            print(f"💡 Trả lời: {answer}")
        else:
            print("⚠️ Không có câu hỏi nào trong test set để chạy Smoke Test.")
            
    except Exception as e:
        print(f"❌ [Blocker]: Lỗi khi chạy Agent Smoke Test (Có thể do thiếu API Key): {e}")
        sys.exit(1)

    print("\n🚧 [Checkpoint 2]: Đã hoàn tất Test Set, Index và Smoke Test.")
    print("🚧 Bạn có thể chuyển sang Checkpoint 3 (End-to-End Evaluation)!")
